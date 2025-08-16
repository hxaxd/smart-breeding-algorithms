import numpy as np

from core.multi_raster_analyzer import MultiRasterAnalyzer
from utils.file_utils import create_dir_if_not_exists

from utils.stats_utils import (
    calculate_mean,
    calculate_std,
    calculate_mode,
    calculate_variance,
    calculate_median,
    calculate_iqr,
    calculate_range,
    calculate_skewness,
    calculate_kurtosis,
    calculate_coefficient_of_variation,
    calculate_uniformity
)



def main():
    # 设置输入和输出路径
    tif_paths = [
        ('red', 'input/red.tif'),  # 红光波段TIF文件路径
        ('nir', 'input/nir.tif'),  # 近红外波段TIF文件路径
        # ('green', 'input/green_band.tif'),  # 绿光波段TIF文件路径
        # ('blue', 'input/blue_band.tif'),  # 蓝光波段TIF文件路径
        # ('rededge', 'input/rededge_band.tif'),  # 红边波段TIF文件路径
        # ('RGB', 'input/RGB_band.tif'),  # 可见光TIF文件路径
        # ('HRGB', 'input/HRGB_band.tif'),  # 高清晰度RGBTIF文件路径
        # ('rededge1', 'input/rededge1_band.tif'),  # 红边1波段TIF文件路径
        # ('rededge2', 'input/rededge2_band.tif'),  # 红边2波段TIF文件路径
        # ('rededge3', 'input/rededge3_band.tif'),  # 红边3波段TIF文件路径
        # ('swir1', 'input/swir1_band.tif'),  # 短波红外1波段TIF文件路径
        # ('swir2', 'input/swir2_band.tif'),  # 短波红外2波段TIF文件路径
    ]
    shp_path = 'input/result.shp'  # 替换为实际的shapefile路径
    
    # 创建输出目录
    create_dir_if_not_exists('output')
    
    try:
        # 初始化分析器
        analyzer = MultiRasterAnalyzer(shp_path, tif_paths)
        print(f"成功加载 {len(tif_paths)} 个栅格文件和 1 个shapefile")
        
        # 遍历所有区块计算植被指数和植被指数均匀度
        print("开始计算植被指数和植被指数均匀度...")
        results = []
        for tile_id, tile_data in analyzer.iterate_tiles():
            print(f"处理区块: {tile_id}")

            red = tile_data['red']
            nir = tile_data['nir']
            # green = tile_data['green']
            # rededge = tile_data['rededge']
            # rgb_r = tile_data['RGB'][0,:,:]
            # rgb_g = tile_data['RGB'][1,:,:]
            # rgb_b = tile_data['RGB'][2,:,:]
            # blue = tile_data['blue']
            # hrgb = tile_data['HRGB']
            # rededge1 = tile_data['rededge1']
            # rededge2 = tile_data['rededge2']
            # rededge3 = tile_data['rededge3']
            # swir1 = tile_data['swir1']
            # swir2 = tile_data['swir2']
            # 字段名长度请勿大于10个字符


            # 计算植被指数
            with np.errstate(divide='ignore', invalid='ignore'):
                ndvi = (nir - red) / (nir + red)
                # evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
                # rvi = nir/red
                # gndvi = (nir - green) / (nir + green)
                # tvi = 60 * (nir - green) - 100 * (red - green)
                # dvi = nir-red
                # savi = (1 + 0.5) * (nir - red) / (nir + red + 0.5)
                # ndwi = (green - nir) / (green + nir)
                # msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2
                # gcvi = (nir / green) - 1
                # rndvi = (rededge1 - red) / (rededge1 + red)
                # ndre = (nir - rededge1) / (nir + rededge1)
                # rri1 = nir/rededge1
                # rri2 = rededge1/nir
                # msrre = (nir - rededge1 - 1) / (sqrt(nir - rededge1) + 1)
                # clre = (nir / rededge1) - 1
                # ireci = (rededge3 - red) / (rededge1 / rededge2)
                # lswi = (nir - swir1) / (nir + swir1)
                # exg = 2 * rgb_g - rgb_r - rgb_b
                # 字段名长度请勿大于5个字符

            indexs = {  'ndvi':ndvi,
                        # 'evi':evi,
                        # 'rvi':rvi,
                        # 'gndvi':gndvi,
                        # 'tvi':tvi,
                        # 'dvi':dvi,
                        # 'savi':savi,
                        # 'ndwi':ndwi,
                        # 'msavi':msavi,
                        # 'gcvi':gcvi,
                        # 'rndvi':rndvi,
                        # 'ndre':ndre,
                        # 'rri1':rri1,
                        # 'rri2':rri2,
                        # 'msrre':msrre,
                        # 'clre':clre,
                        # 'ireci':ireci,
                        # 'lswi':lswi,
                        # 'exg':exg,
                    }

            # 将NaN和无穷大值替换为合理值
            for name, index in indexs.items():
                indexs[name] = np.nan_to_num(index, nan=0.0, posinf=1.0, neginf=-1.0)

            # 计算各项统计指标
            index_mean = calculate_mean(indexs)          # 平均值
            index_std = calculate_std(indexs)            # 标准差
            index_mode = calculate_mode(indexs)          # 众数
            index_var = calculate_variance(indexs)       # 方差
            index_median = calculate_median(indexs)      # 中位数
            index_iqr = calculate_iqr(indexs)            # 四分位距
            index_range = calculate_range(indexs)        # 极差
            index_skew = calculate_skewness(indexs)      # 偏度
            index_kurt = calculate_kurtosis(indexs)      # 峰度
            index_cov = calculate_coefficient_of_variation(indexs)  # 变异系数
            index_uni = calculate_uniformity(indexs)     # 均匀度


            # 保存结果
            result = {
                'FID': tile_id,
                **index_mean,
                **index_std,
                **index_mode,
                **index_var,
                **index_median,
                **index_iqr,
                **index_range,
                **index_skew,
                **index_kurt,
                **index_cov,
                **index_uni,
            }
            results.append(result)
        
        print(f"计算完成，共处理 {len(results)} 个区块")
        
        analyzer.export_results_to_shapefile(results, 'output/result_index.shp')
        print("结果已导出到output/result_index.shp")
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")


if __name__ == '__main__':
    main()