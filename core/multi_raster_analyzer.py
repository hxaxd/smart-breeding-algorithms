import rasterio
import geopandas as gpd
import numpy as np
import os
import rasterio
from typing import List, Dict, Tuple, Iterator
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from utils.file_utils import check_file_exists, create_dir_if_not_exists


class MultiRasterAnalyzer:
    def __init__(self, shp_path: str, raster_paths: List[Tuple[str, str]]):
        """初始化，加载shp和底图，执行重合性校验
        
        Args:
            shp_path: 区块边界shp文件路径
            raster_paths: 底图文件路径列表
        """
        # 检查文件是否存在
        if not check_file_exists(shp_path):
            raise FileNotFoundError(f"shp文件不存在: {shp_path}")
        
        for name, path in raster_paths:
            if not check_file_exists(path):
                raise FileNotFoundError(f"底图文件不存在: {path}")
        
        # 加载shp文件
        try:
            self.tiles = gpd.read_file(shp_path)
            self.crs = self.tiles.crs
        except Exception as e:
            raise IOError(f"无法打开shp文件: {str(e)}")
        
        # 验证区块ID字段是否存在
        if 'FID' not in self.tiles.columns:
            raise ValueError("shp文件中缺少FID字段")
        
        # 加载底图
        self.raster_paths = raster_paths
        self.rasters = {}
        
        try:
            for name, path in raster_paths:
                
                # 打开底图并存储
                src = rasterio.open(path)
                self.rasters[name] = src
                
                # 检查CRS是否一致
                if src.crs != self.crs:
                    raise ValueError(f"底图{path}的坐标系统与shp文件不一致")
        except Exception as e:
            # 关闭已打开的底图
            for src in self.rasters.values():
                src.close()
            raise IOError(f"无法打开底图文件: {str(e)}")
        
        # 验证底图是否完全重合
        if not self.validate_overlap():
            # 关闭已打开的底图
            for src in self.rasters.values():
                src.close()
            raise ValueError("底图不完全重合")

    def validate_overlap(self) -> bool:
        """验证所有底图与shp文件是否完全重合
        
        Returns:
            是否完全重合
        """
        raster_paths = self.raster_paths
        if len(raster_paths) < 2:
            return True
        try:
            first = rasterio.open(raster_paths[0][1])
            first_bounds = first.bounds
            first_shape = first.shape
            first_crs = first.crs
            first.close()
            
            for name, path in raster_paths[1:]:
                with rasterio.open(path) as ds:
                    if not (ds.bounds == first_bounds and \
                            ds.shape == first_shape and \
                            ds.crs == first_crs):
                        return False
            
            return True
        except Exception as e:
            print(f"验证底图重合性时出错: {str(e)}")
            return False
    
    

    def iterate_tiles(self) -> Iterator[Tuple[np.int64, Dict[str, np.ndarray]]]:
        """遍历所有区块，返回(区块ID, {底图名: 像素数组})
        
        Yields:
            (区块ID, {底图名: 像素数组})
        """
        for idx, row in self.tiles.iterrows():
            tile_id = row['FID']
            tile_geom = row['geometry']
            
            # 获取每个底图的像素数据
            tile_data = {}
            for name, src in self.rasters.items():
                data = self._extract_tile_without_resampling(src, tile_geom)
                tile_data[name] = data
            
            yield tile_id, tile_data

    def _extract_tile_without_resampling(self, raster: rasterio.DatasetReader, tile_geom) -> np.ndarray:
        """无重采样提取区块像素
        
        Args:
            raster: 底图数据集
            tile_geom: 区块几何形状
        
        Returns:
            区块像素数据
        """
        # 获取区块边界框的像素范围
        minx, miny, maxx, maxy = tile_geom.bounds
        window = from_bounds(minx, miny, maxx, maxy, raster.transform)
        
        # 读取原始像素数据
        data = raster.read(window=window)
        
        # 创建与区块几何形状匹配的掩膜
        mask = geometry_mask(
            [tile_geom],
            out_shape=data.shape[1:],
            transform=raster.window_transform(window),
            invert=True
        )
        
        return data * mask

    def export_results_to_shapefile(self, result_data: List[Dict], output_path: str) -> bool:
        """将分析结果导出到shapefile
        
        Args:
            result_data: 结果数据，字典数组，每个字典格式为{'FID': 数字, '自定义字段': 值}
            output_path: 输出shapefile路径
        
        Returns:
            是否导出成功
        """
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                create_dir_if_not_exists(output_dir)
                
            # 创建一个原始数据的副本
            output_gdf = self.tiles.copy()
            
            # 处理结果数据
            for item in result_data:
                fid = item['FID']
                
                if fid is None:
                    continue
                
                # 检查FID是否存在
                if fid not in output_gdf['FID'].values:
                    continue
                
                
                # 添加或更新字段
                for key, value in item.items():
                    if key != 'FID':
                        output_gdf.loc[output_gdf['FID'] == fid, key] = value
            
            # 保存到shapefile
            output_gdf.to_file(output_path)
            return True
        except Exception as e:
            raise Exception(f"导出结果到shapefile时出错: {str(e)}")


    def __del__(self):
        """析构函数，关闭所有打开的底图"""
        for src in self.rasters.values():
            src.close()