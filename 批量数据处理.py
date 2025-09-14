import os
import numpy as np
import rasterio
import rasterio.warp
import rasterio.enums
from core.multi_raster_analyzer import MultiRasterAnalyzer
from utils.file_utils import create_dir_if_not_exists
from pathlib import Path


def process_data_folder(data_folder, folder_name, root_folder, output_base_dir=None):
    """处理单个数据文件夹中的所有tif和shp文件"""
    print(f"处理数据文件夹: {data_folder}")
    
    # 确定输出目录
    if output_base_dir is None:
        output_base_dir = data_folder
    
    # 定义需要处理的tif文件列表
    tif_files = [
        # ('rgb', os.path.join(data_folder, 'rgb.tif')),
        ('green', os.path.join(data_folder, 'green.tif')),
        ('red', os.path.join(data_folder, 'red.tif')),
        ('rededge', os.path.join(data_folder, 'rededge.tif')),
        ('nir', os.path.join(data_folder, 'nir.tif'))
    ]
    
    # 过滤掉不存在的文件
    existing_tif_files = [(name, path) for name, path in tif_files if os.path.exists(path)]
    
    # 检查shp文件是否存在
    shp_path = os.path.join(data_folder, 'shape.shp')
    if not os.path.exists(shp_path):
        print(f"警告: 在 {data_folder} 中未找到 shape.shp 文件，跳过此文件夹")
        return False
    
    if len(existing_tif_files) == 0:
        print(f"警告: 在 {data_folder} 中未找到任何tif文件，跳过此文件夹")
        return False
    
    try:
    
        # # 任务1: 重采样所有存在的TIFF文件
        # if len(existing_tif_files) > 0:
        #     print(f"开始重采样所有{len(existing_tif_files)}个TIFF文件...")
        #     # 创建重采样输出目录
        #     resampled_output_dir = os.path.join(output_base_dir, 'resampled')
        #     create_dir_if_not_exists(resampled_output_dir)
            
        #     # 遍历所有存在的TIFF文件
        #     for name, path in existing_tif_files:
        #         try:
        #             # 定义重采样后的文件路径
        #             resampled_file_path = os.path.join(resampled_output_dir, f'{name}_resampled.tif')
                    
        #             print(f"  正在重采样{name}文件...")
                    
        #             # 打开原始图像
        #             with rasterio.open(path) as src:
        #                 # 获取原始图像元数据
        #                 meta = src.meta.copy()
                        
        #                 # 定义重采样后的分辨率（缩小为原来的1/2）
        #                 new_height = src.height // 2
        #                 new_width = src.width // 2
                        
        #                 # 更新元数据中的高度、宽度和转换矩阵
        #                 meta.update({
        #                     'height': new_height,
        #                     'width': new_width,
        #                     'transform': rasterio.Affine(
        #                         src.transform.a * 2,
        #                         src.transform.b,
        #                         src.transform.c,
        #                         src.transform.d,
        #                         src.transform.e * 2,
        #                         src.transform.f
        #                     )
        #                 })
                        
        #                 # 重采样并写入新文件
        #                 with rasterio.open(resampled_file_path, 'w', **meta) as dst:
        #                     # 使用双线性插值方法重采样
        #                     for i in range(1, src.count + 1):
        #                         dst.write(
        #                             rasterio.warp.reproject(
        #                                 source=rasterio.band(src, i),
        #                                 destination=np.zeros((new_height, new_width), dtype=meta['dtype']),
        #                                 src_transform=src.transform,
        #                                 src_crs=src.crs,
        #                                 dst_transform=meta['transform'],
        #                                 dst_crs=src.crs,
        #                                 resampling=rasterio.enums.Resampling.bilinear
        #                             )[0],
        #                             i
        #                         )
                    
        #             print(f"  成功重采样{name}文件到: {resampled_file_path}")
        #         except Exception as e:
        #             print(f"  重采样{name}文件时出错: {str(e)}")
        #             continue
            
        #     print(f"成功完成所有TIFF文件的重采样，结果保存在: {resampled_output_dir}")
        # else:
        #     print("未找到任何需要重采样的TIFF文件，跳过重采样步骤")
        
        # # 任务2: 按shp将rgb进行图像切割 (如果存在rgb文件)
        # has_rgb = any(name == 'rgb' for name, _ in existing_tif_files)
        # if has_rgb:
        #     print("开始按shp切割RGB图像...")
        #     rgb_output_dir = os.path.join(root_folder, 'tiles')
        #     create_dir_if_not_exists(rgb_output_dir)
            
        #     # 重新初始化只包含RGB的分析器
        #     rgb_analyzer = MultiRasterAnalyzer(shp_path, [('rgb', os.path.join(data_folder, 'rgb.tif'))])
            
        #     for tile_id, tile_data in rgb_analyzer.iterate_tiles():
        #         # 构建输出文件路径
        #         output_path = os.path.join(rgb_output_dir, str(tile_id), f"{folder_name}.tif")
        #         create_dir_if_not_exists(os.path.join(rgb_output_dir, str(tile_id)))
                
        #         # 获取RGB底图的元数据
        #         rgb_raster = rgb_analyzer.rasters['rgb']
        #         meta = rgb_raster.meta.copy()
        #         # 获取当前图块的边界
        #         tile_bounds = rgb_analyzer.tiles[rgb_analyzer.tiles['FID'] == int(tile_id)].geometry.iloc[0].bounds
                
        #         # 更新元数据
        #         meta.update({
        #             'driver': 'GTiff',
        #             'height': tile_data['rgb'].shape[1],
        #             'width': tile_data['rgb'].shape[2],
        #             'transform': rasterio.windows.transform(
        #                 rasterio.windows.from_bounds(
        #                 *tile_bounds,
        #                 rgb_raster.transform
        #             ),
        #             rgb_raster.transform
        #             )
        #         })
                
        #         # 写入文件
        #         with rasterio.open(output_path, 'w', **meta) as dst:
        #             dst.write(tile_data['rgb'])
        #     print(f"成功将RGB图像按shp切割到: {rgb_output_dir}")
        
        # 任务3: 计算指数并输出result_index.shp
        # 初始化分析器
        analyzer = MultiRasterAnalyzer(shp_path, existing_tif_files)
        print(f"成功加载 {len(existing_tif_files)} 个栅格文件和 1 个shapefile")
        print("开始计算指数并生成result_index.shp...")
        results = []
        
        # 检查是否有足够的波段计算所需指数
        has_required_bands = all(band in [name for name, _ in existing_tif_files] for band in ['red', 'nir'])
        has_green_band = 'green' in [name for name, _ in existing_tif_files]
        
        if not has_required_bands:
            print("警告: 缺少计算NDVI和OSAVI所需的red和nir波段，无法计算这些指数")
        
        for tile_id, tile_data in analyzer.iterate_tiles():
            print(f"处理区块: {tile_id}")
            result = {'FID': tile_id}
            
            if has_required_bands:
                red = tile_data['red']
                green = tile_data['green']
                nir = tile_data['nir']
                
                # 计算NDVI
                with np.errstate(divide='ignore', invalid='ignore'):
                    # ndvi = (nir - red) / (nir + red)
                    # # 计算OSAVI (优化土壤调整植被指数)
                    # osavi = (1 + 0.16) * (nir - red) / (nir + red + 0.16)
                    gndvi = (nir - green) / (nir + green)
                    
                # 替换NaN和无穷大值
                # ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=1.0, neginf=-1.0)
                # osavi = np.nan_to_num(osavi, nan=0.0, posinf=1.0, neginf=-1.0)
                gndvi = np.nan_to_num(gndvi, nan=0.0, posinf=1.0, neginf=-1.0)
                
                # # 计算NDVI的均值和变异系数
                # ndvi_mean = np.nanmean(ndvi)
                # if ndvi_mean == 0:
                #     ndvi_cv = 0
                # else:
                #     ndvi_cv = np.nanstd(ndvi) / ndvi_mean
                
                # # 计算OSAVI的均值和变异系数
                # osavi_mean = np.nanmean(osavi)
                # if osavi_mean == 0:
                #     osavi_cv = 0
                # else:
                #     osavi_cv = np.nanstd(osavi) / osavi_mean

                # 计算GNDVI的均值和变异系数
                gndvi_mean = np.nanmean(gndvi)
                if gndvi_mean == 0:
                    gndvi_cv = 0
                else:
                    gndvi_cv = np.nanstd(gndvi) / gndvi_mean
                
                # 添加到结果
                # result['ndvi'] = ndvi_mean
                # result['ndvi_cv'] = ndvi_cv
                # result['osavi'] = osavi_mean
                # result['osavi_cv'] = osavi_cv
                result['gndvi'] = gndvi_mean
                # result['gndvi_cv'] = gndvi_cv
            
            # # 计算超绿指数EXG
            # if has_green_band and 'rgb' in tile_data:
            #     rgb_data = tile_data['rgb']
            #     if len(rgb_data.shape) >= 3 and rgb_data.shape[0] >= 3:
            #         # 假设RGB通道顺序为: 红(0), 绿(1), 蓝(2)
            #         rgb_r = rgb_data[0, :, :]
            #         rgb_g = rgb_data[1, :, :]
            #         rgb_b = rgb_data[2, :, :]
                    
            #         # 归一化RGB值
            #         rgb_r = rgb_r / np.max(rgb_r) if np.max(rgb_r) > 0 else rgb_r
            #         rgb_g = rgb_g / np.max(rgb_g) if np.max(rgb_g) > 0 else rgb_g
            #         rgb_b = rgb_b / np.max(rgb_b) if np.max(rgb_b) > 0 else rgb_b
                    
            #         # 计算超绿指数EXG
            #         exg = 2 * rgb_g - rgb_r - rgb_b
            #         exg_mean = np.nanmean(exg)
            #         result['exg'] = exg_mean
            
            results.append(result)
        
        # 导出结果到shapefile
        result_shp_path = os.path.join(output_base_dir, 'result_index.shp')
        analyzer.export_results_to_shapefile(results, result_shp_path)
        print(f"成功导出结果到: {result_shp_path}")
        
        return True
    except Exception as e:
        print(f"处理 {data_folder} 时出错: {str(e)}")
        return False


def batch_process_folders(root_folder = "2025丹东629", output_root_dir=None):
    """批量处理根文件夹下的所有子文件夹"""
    print(f"开始批量处理文件夹: {root_folder}")
    
    # 遍历根文件夹下的所有子文件夹
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        
        # 检查是否是目录
        if not os.path.isdir(folder_path):
            continue
        
        # 确定当前子文件夹的输出目录
        if output_root_dir is None:
            current_output_dir = Path(folder_path) / "output"
        else:
            current_output_dir = os.path.join(output_root_dir, folder_name)
            create_dir_if_not_exists(current_output_dir)
        
        # 处理当前文件夹
        process_data_folder(folder_path, folder_name, root_folder, current_output_dir)
    
    print("批量处理完成")


if __name__ == '__main__':
    
    # 批量处理文件夹
    batch_process_folders()