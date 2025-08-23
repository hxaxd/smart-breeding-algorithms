import rasterio
import geopandas as gpd
from shapely.geometry import Polygon
from typing import Tuple, List
from utils.file_utils import check_file_exists, create_dir_if_not_exists


class TileProcessor:
    def __init__(self, tif_path: str):
        """初始化，加载TIF底图
        
        Args:
            tif_path: TIF文件路径
        """
        if not check_file_exists(tif_path):
            raise FileNotFoundError(f"TIF文件不存在: {tif_path}")
        
        self.tif_path = tif_path
        try:
            with rasterio.open(tif_path) as src:
                self.transform = src.transform
                self.crs = src.crs
                self.width = src.width
                self.height = src.height
                self.bounds = src.bounds
        except Exception as e:
            raise IOError(f"无法打开TIF文件: {str(e)}")

    def split_tiles(self, 
                   geo_coords: List[Tuple[float, float]] | None = None,
                   shape: Polygon | None = None, 
                   m: int = 1, n: int = 1, 
                   shrink_ratio: Tuple[float, float] = (0.8, 0.8),
                   id_order: str = 'top-left',
                   start_id: int = 0) -> gpd.GeoDataFrame:
        """切割区块（支持二维归一化）
        
        Args:
            geo_coords: 地理坐标点列表，包含至少4个点 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            shape: 几何形状（当geo_coords为None时使用）
            m: 横向切割数
            n: 纵向切割数
            shrink_ratio: (x方向比例, y方向比例) 区块缩小比例
            id_order: ID生成顺序 ('top-left'或'bottom-right')
        
        Returns:
            包含所有区块轮廓的GeoDataFrame
        """
        from utils.geo_utils import calculate_homography, denormalize_coordinates
        import numpy as np
        
        if m <= 0 or n <= 0:
            raise ValueError("横向和纵向切割数必须大于0")
        
        if not (0 < shrink_ratio[0] <= 1 and 0 < shrink_ratio[1] <= 1):
            raise ValueError("缩小比例必须在(0, 1]范围内")
        
        if id_order not in ['top-left', 'bottom-right']:
            raise ValueError("ID生成顺序必须是'top-left'或'bottom-right'")
        
        # 确保至少提供了一种坐标输入
        if geo_coords is None and shape is None:
            raise ValueError("必须提供geo_coords或shape参数")
        
        tiles = []

        # 从shape中获取顶点坐标
        if shape is not None:
            if not shape.is_valid:
                raise ValueError("提供的shape不是有效多边形")
            
            # 获取多边形的顶点坐标
            coords = list(shape.exterior.coords)
            if len(coords) < 4:
                raise ValueError("shape至少需要4个顶点")

            src_pts = np.array(coords[:4])
        
        if geo_coords is not None:
            # 使用二维归一化方法
            # 确保至少有4个点
            if len(geo_coords) < 4:
                raise ValueError("至少需要提供4个地理坐标点")

            polygon = Polygon(geo_coords)
            if not polygon.is_valid:
                raise ValueError("提供的坐标点不能形成有效多边形")
            
            # 使用前4个点进行计算
            src_pts = np.array(geo_coords[:4])
            
        # 定义目标归一化坐标（单位正方形）
        dst_pts = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
            
        # 计算单应性变换矩阵
        H = calculate_homography(src_pts, dst_pts)
            
        # 生成均匀网格点
        x = np.linspace(0, 1, m + 1)
        y = np.linspace(0, 1, n + 1)
            
        for i in range(m):
            for j in range(n):
                # 在归一化空间中计算区块边界
                left = x[i]
                right = x[i + 1]
                bottom = y[j]
                top = y[j + 1]
                    
                # 缩小区块
                width = right - left
                height = top - bottom
                left += width * (1 - shrink_ratio[0]) / 2
                right -= width * (1 - shrink_ratio[0]) / 2
                bottom += height * (1 - shrink_ratio[1]) / 2
                top -= height * (1 - shrink_ratio[1]) / 2
                
                # 生成归一化空间中的矩形顶点
                norm_rect = np.array([[left, bottom], [right, bottom], [right, top], [left, top]])                    
                # 应用逆单应性变换，将归一化坐标转换回地理坐标
                geo_rect = denormalize_coordinates(norm_rect, H)
                
                # 创建多边形
                polygon = Polygon(geo_rect)

                current_id = 0
                    
                # 根据顺序生成ID
                if id_order == 'bottom-right':
                    # 从右下角开始编号
                    current_id = start_id + m * n - (j * m + i)
                else:
                    # 从左上角开始编号
                    current_id = start_id + j * m + i + 1
                    
                tiles.append({
                    'FID': current_id,
                    'geometry': polygon
                })
        
        # 创建GeoDataFrame
        gdf = gpd.GeoDataFrame(tiles, crs=self.crs)
        return gdf

    def save_tiles_to_shp(self, tiles: gpd.GeoDataFrame, output_path: str) -> bool:
        """保存区块轮廓到shapefile
        
        Args:
            tiles: 包含区块轮廓的GeoDataFrame
            output_path: 输出文件路径
        
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            dir_path = output_path.rsplit('/', 1)[0] if '/' in output_path else ''
            if dir_path and not check_file_exists(dir_path):
                create_dir_if_not_exists(dir_path)
                
            # 保存到shapefile
            tiles.to_file(output_path)
            return True
        except Exception as e:
            raise Exception(f"保存区块轮廓到shapefile时出错: {str(e)}")
