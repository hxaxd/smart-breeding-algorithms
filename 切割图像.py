import os
import rasterio

from core.multi_raster_analyzer import MultiRasterAnalyzer
from utils.file_utils import create_dir_if_not_exists


def main():

    # 设置输入和输出路径
    tif_paths = [
        ('rgb', r'2024苏家屯\20240628\rgb.tif')
    ]
    shp_path = r'2024苏家屯\20240628\shape.shp'  # 替换为实际的shapefile路径
    
    
    try:
        # 初始化分析器
        analyzer = MultiRasterAnalyzer(shp_path, tif_paths)
        print(f"成功加载 {len(tif_paths)} 个栅格文件和 1 个shapefile")
        
        # 提取区块图像为TIFF文件
        print("开始提取区块图像数据...")
        for tile_id, tile_data in analyzer.iterate_tiles():
            # 为每个区块创建子目录
            tile_dir = os.path.join(r'2024苏家屯\20240628\tile', f"tile_{tile_id}")
            create_dir_if_not_exists(tile_dir)
            
            for name, data in tile_data.items():
                # 构建输出文件路径
                output_path = os.path.join(tile_dir, f"{name}.tif")
                
                # 获取第一个底图的元数据
                first_raster = next(iter(analyzer.rasters.values()))
                meta = first_raster.meta.copy()
                # 获取当前图块的边界
                tile_bounds = analyzer.tiles[analyzer.tiles['FID'] == int(tile_id)].geometry.iloc[0].bounds

                
                # 更新元数据
                meta.update({
                    'driver': 'GTiff',
                    'height': data.shape[1],
                    'width': data.shape[2],
                    'transform': rasterio.windows.transform(
                        rasterio.windows.from_bounds(
                        *tile_bounds,
                        first_raster.transform
                    ),
                    first_raster.transform
                    )
                })
                
                # 写入文件
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(data)
        
        success = True
    except Exception as e:
        print(f"提取区块图像数据时出错: {str(e)}")
        success = False
    if success:
            print(f"成功提取所有区块图像数据到: output")
    else:
        print("提取区块图像数据失败")

if __name__ == '__main__':
    main()