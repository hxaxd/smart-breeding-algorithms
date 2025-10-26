import os
import numpy as np
import rasterio
import rasterio.warp
import rasterio.enums
from rasterio.enums import Resampling
from PIL import Image
import json
from core.multi_raster_analyzer import MultiRasterAnalyzer
from utils.file_utils import create_dir_if_not_exists
from pathlib import Path


def process_data_folder(data_folder, folder_name, output_base_dir=None):
    """处理单个数据文件夹中的所有tif和shp文件"""
    print(f"处理数据文件夹: {data_folder}")
    
    # 确定输出目录
    if output_base_dir is None:
        output_base_dir = data_folder
    
    # 定义需要处理的tif文件列表
    tif_files = [
        ('rgb', os.path.join(data_folder, 'rgb.tif')),
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
    
        # 任务1: 重采样所有存在的TIFF文件
        if len(existing_tif_files) > 0:
            print(f"开始重采样所有{len(existing_tif_files)}个TIFF文件...")
            # 创建重采样输出目录
            resampled_output_dir = output_base_dir
            create_dir_if_not_exists(resampled_output_dir)
            
            # 遍历所有存在的TIFF文件
            for name, path in existing_tif_files:
                try:
                    # 定义重采样后的文件路径
                    resampled_file_path = os.path.join(resampled_output_dir, f'{name}.tif')
                    
                    print(f"  正在重采样{name}文件...")
                    
                    # 打开原始图像
                    with rasterio.open(path) as src:
                        # 定义重采样因子（缩小为原来的1/2）
                        scale_factor = 0.5
                        
                        # 计算新的尺寸
                        new_height = int(src.height * scale_factor)
                        new_width = int(src.width * scale_factor)
                        
                        # 读取并重采样所有波段
                        data = src.read(
                            out_shape=(
                                src.count,
                                new_height,
                                new_width
                            ),
                            resampling=Resampling.bilinear
                        )
                        
                        # 计算新的transform
                        # 使用scale方法确保正确的地理配准
                        new_transform = src.transform * src.transform.scale(
                            (src.width / new_width),
                            (src.height / new_height)
                        )
                        
                        # 获取原始元数据并更新
                        meta = src.meta.copy()
                        meta.update({
                            'height': new_height,
                            'width': new_width,
                            'transform': new_transform,
                            'crs': src.crs
                        })
                        
                        # 打印调试信息
                        print(f"    原始尺寸: {src.height} x {src.width}")
                        print(f"    新尺寸: {new_height} x {new_width}")
                        print(f"    CRS: {src.crs}")
                        print(f"    原始Transform: {src.transform}")
                        print(f"    新Transform: {new_transform}")
                        
                        # 写入重采样后的文件
                        with rasterio.open(resampled_file_path, 'w', **meta) as dst:
                            dst.write(data)
                        
                        # 验证输出文件的地理信息
                        with rasterio.open(resampled_file_path) as verify:
                            if verify.crs is None:
                                print(f"    ⚠️ 警告: CRS丢失!")
                            else:
                                print(f"    ✅ 验证 - 输出CRS: {verify.crs}")
                                print(f"    ✅ 验证 - 输出范围: {verify.bounds}")
                            
                            # 获取bounds信息
                            bounds = {
                                'crs': str(verify.crs),
                                'bounds': [
                                    float(verify.bounds.left),
                                    float(verify.bounds.bottom),
                                    float(verify.bounds.right),
                                    float(verify.bounds.top)
                                ],
                            }
                            
                            # 保存bounds信息到JSON文件
                            bounds_json_path = os.path.join(resampled_output_dir, f'{name}_bounds.json')
                            with open(bounds_json_path, 'w') as json_file:
                                json.dump(bounds, json_file, indent=4)
                            print(f"    ✅ 保存bounds信息到: {bounds_json_path}")
                            
                            # 输出PNG文件
                            png_output_path = os.path.join(resampled_output_dir, f'{name}.png')
                            
                            # 读取数据并转换为适合PIL的格式
                            data_for_png = verify.read()
                            
                            # 处理多波段数据
                            if data_for_png.shape[0] == 1:  # 单波段
                                # 归一化到0-255范围
                                data_norm = ((data_for_png[0] - np.nanmin(data_for_png[0])) / 
                                            (np.nanmax(data_for_png[0]) - np.nanmin(data_for_png[0])) * 255)
                                data_norm = np.nan_to_num(data_norm, nan=0).astype(np.uint8)
                                img = Image.fromarray(data_norm, mode='L')
                            elif data_for_png.shape[0] >= 3:  # 多波段，取前3个作为RGB
                                # 选择前3个波段
                                rgb_bands = data_for_png[:3, :, :]
                                
                                # 归一化每个波段到0-255范围
                                rgb_normalized = np.zeros_like(rgb_bands, dtype=np.uint8)
                                for i in range(3):
                                    band_data = rgb_bands[i]
                                    if np.nanmax(band_data) > np.nanmin(band_data):
                                        band_norm = ((band_data - np.nanmin(band_data)) / 
                                                   (np.nanmax(band_data) - np.nanmin(band_data)) * 255)
                                        rgb_normalized[i] = np.nan_to_num(band_norm, nan=0).astype(np.uint8)
                                    else:
                                        rgb_normalized[i] = np.zeros_like(band_data, dtype=np.uint8)
                                
                                # 转换形状从 (bands, height, width) 到 (height, width, bands)
                                rgb_image = np.transpose(rgb_normalized, (1, 2, 0))
                                img = Image.fromarray(rgb_image, mode='RGB')
                            else:
                                # 其他情况，使用第一个波段
                                data_norm = ((data_for_png[0] - np.nanmin(data_for_png[0])) / 
                                            (np.nanmax(data_for_png[0]) - np.nanmin(data_for_png[0])) * 255)
                                data_norm = np.nan_to_num(data_norm, nan=0).astype(np.uint8)
                                img = Image.fromarray(data_norm, mode='L')
                            
                            # 保存PNG文件
                            img.save(png_output_path)
                            print(f"    ✅ 保存PNG图像到: {png_output_path}")
                    
                    print(f"  成功重采样{name}文件到: {resampled_file_path}")
                except Exception as e:
                    print(f"  重采样{name}文件时出错: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"成功完成所有TIFF文件的重采样，结果保存在: {resampled_output_dir}")
        else:
            print("未找到任何需要重采样的TIFF文件，跳过重采样步骤")
        
        # 任务2: 按shp将rgb进行图像切割 (如果存在rgb文件)
        has_rgb = any(name == 'rgb' for name, _ in existing_tif_files)
        if has_rgb:
            print("开始按shp切割RGB图像...")
            rgb_output_dir = Path(output_base_dir).parent / 'tiles'
            create_dir_if_not_exists(rgb_output_dir)
            
            # 初始化只包含RGB的分析器
            rgb_analyzer = MultiRasterAnalyzer(shp_path, [('rgb', os.path.join(data_folder, 'rgb.tif'))])
            
            for tile_id, tile_data in rgb_analyzer.iterate_tiles():
                # 构建输出文件路径
                output_path = os.path.join(rgb_output_dir, str(tile_id), f"{folder_name}.png")
                create_dir_if_not_exists(os.path.join(rgb_output_dir, str(tile_id)))
                
                # 获取RGB数据并转换为PIL格式
                # 数据格式为 (bands, height, width)，实际是4波段(RGBA)
                rgb_data = tile_data['rgb']
                
                # 数据已经是uint8类型，值范围在0-255之间，不需要归一化
                # 只取前3个波段(RGB)，忽略Alpha通道
                rgb_bands = rgb_data[:3, :, :]  # 取前3个波段
                
                # 转换形状从 (bands, height, width) 到 (height, width, bands)
                rgb_image = np.transpose(rgb_bands, (1, 2, 0))
                
                # 创建PIL图像并保存为PNG
                img = Image.fromarray(rgb_image)
                img.save(output_path)
            print(f"成功将RGB图像按shp切割到: {rgb_output_dir} (PNG格式)")
        
        # 任务3: 计算指数并输出result_index.shp
        # 初始化分析器
        has_required_bands = all(band in [name for name, _ in existing_tif_files] for band in ['red', 'nir', 'green'])

        if not has_required_bands:
            print("警告: 缺少计算NDVI所需的red和nir波段，无法计算这些指数")
        else:    
            index_tif_files = [item for item in existing_tif_files if item[0] in ['red', 'green', 'nir']]
            analyzer_ms = MultiRasterAnalyzer(shp_path, index_tif_files)
        
        has_rgb_band = all(band in [name for name, _ in existing_tif_files] for band in ['rgb'])
        if not has_rgb_band:
            print("警告: 缺少计算RGB波段，无法计算这些指数")
        else:
            analyzer_rgb = MultiRasterAnalyzer(shp_path, [item for item in existing_tif_files if item[0] == 'rgb'])

        print(f"成功加载 {len(index_tif_files)+(1 if has_rgb_band else 0)} 个栅格文件和 1 个shapefile")
        print("开始计算指数并生成result_index.shp...")
        results = []
        
        iterator = {}

        if has_required_bands:
            for tile_id, tile_data in analyzer_ms.iterate_tiles():
                iterator[tile_id] = tile_data

        if has_rgb_band:
            for tile_id, tile_data in analyzer_rgb.iterate_tiles():
                if tile_id not in iterator:
                    iterator[tile_id] = {}
                iterator[tile_id]['rgb'] = tile_data['rgb']
        
        
        for tile_id, tile_data in iterator.items():
            print(f"处理区块: {tile_id}")
            result = {'FID': tile_id}
            
            if has_required_bands:
                red = tile_data['red']
                green = tile_data['green']
                nir = tile_data['nir']
                
                # 计算NDVI
                with np.errstate(divide='ignore', invalid='ignore'):
                    ndvi = (nir - red) / (nir + red)
                    # # 计算OSAVI (优化土壤调整植被指数)
                    # osavi = (1 + 0.16) * (nir - red) / (nir + red + 0.16)
                    # gndvi = (nir - green) / (nir + green)
                    
                # 替换NaN和无穷大值
                ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=1.0, neginf=-1.0)
                # osavi = np.nan_to_num(osavi, nan=0.0, posinf=1.0, neginf=-1.0)
                # gndvi = np.nan_to_num(gndvi, nan=0.0, posinf=1.0, neginf=-1.0)
                
                # 计算NDVI的均值和变异系数
                ndvi_mean = np.nanmean(ndvi)
                if ndvi_mean == 0:
                    ndvi_cv = 0
                else:
                    ndvi_cv = np.nanstd(ndvi) / ndvi_mean
                
                # # 计算OSAVI的均值和变异系数
                # osavi_mean = np.nanmean(osavi)
                # if osavi_mean == 0:
                #     osavi_cv = 0
                # else:
                #     osavi_cv = np.nanstd(osavi) / osavi_mean

                # # 计算GNDVI的均值和变异系数
                # gndvi_mean = np.nanmean(gndvi)
                # if gndvi_mean == 0:
                #     gndvi_cv = 0
                # else:
                #     gndvi_cv = np.nanstd(gndvi) / gndvi_mean
                
                # 添加到结果
                result['ndvi'] = ndvi_mean
                result['ndvi_cv'] = ndvi_cv
                result['lai'] = ndvi_mean * 10
                result['lai_cv'] = ndvi_cv * 10

                # result['osavi'] = osavi_mean
                # result['osavi_cv'] = osavi_cv
                # result['gndvi'] = gndvi_mean
                # result['gndvi_cv'] = gndvi_cv
            
            # 计算超绿指数EXG
            if has_rgb_band:
                rgb_data = tile_data['rgb']
                if len(rgb_data.shape) >= 3 and rgb_data.shape[0] >= 3:
                    # 假设RGB通道顺序为: 红(0), 绿(1), 蓝(2)
                    rgb_r = rgb_data[0, :, :]
                    rgb_g = rgb_data[1, :, :]
                    rgb_b = rgb_data[2, :, :]
                    
                    # 计算超绿指数EXG
                    exg = 2 * rgb_g - rgb_r - rgb_b
                    exg_mean = np.nanmean(exg)
                    result['exg'] = exg_mean
            
            results.append(result)
        
        # 导出结果到geojson
        result_geojson_path = os.path.join(output_base_dir, 'result_index.geojson')
        analyzer_rgb.export_results_to_geojson(results, result_geojson_path)
        print(f"成功导出结果到: {result_geojson_path}")
        
        return True
    except Exception as e:
        print(f"处理 {data_folder} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def batch_process_folders(root_folder = "2025丹东629", output_root_dir="2025dandong629"):
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
        process_data_folder(folder_path, folder_name, current_output_dir)
    
    print("批量处理完成")


if __name__ == '__main__':
    
    # 批量处理文件夹
    batch_process_folders("input/2024苏家屯", "output/2024sujiatun")
    batch_process_folders("input/2025丹东629", "output/2025dandong629")
