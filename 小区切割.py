from core.tile_processor import TileProcessor
import pandas as pd
from config.geo import sujiatun2024


def main(time: str):

    # 设置输入和输出路径
    tif_path = rf"2024苏家屯\2024{time}\rgb.tif"  # 替换为实际的TIF文件路径
    output_shp = rf"2024苏家屯\2024{time}\shape.shp" # 替换为期望的输出文件名
    
    # 初始化TileProcessor
    try:
        processor = TileProcessor(tif_path)
        print(f"成功加载TIF文件: {tif_path}")
        print(f"图像尺寸: {processor.width} x {processor.height}")
        print(f"地理边界: {processor.bounds}")
    except Exception as e:
        print(f"初始化TileProcessor失败: {str(e)}")
        return
    
    geo_coords = sujiatun2024[f"{time}1"]
    
    # 使用二维归一化切割区块
    try:
        tiles1 = processor.split_tiles(
            geo_coords=geo_coords,
            m=8, n=108, # 行列
            shrink_ratio=(0.8, 0.8), # 小区行列收缩比例
            id_order='top-left', # 编号顺序
            # 'top-left' 从左上角开始编号
            # 'bottom-right' 从右下角开始编号
            start_id=0 # 起始ID - 1
        )
        print(f"成功切割为 {len(tiles1)} 个区块")
    except Exception as e:
        print(f"切割区块1失败: {str(e)}")
        return

    geo_coords = sujiatun2024[f"{time}2"]

    try:
        tiles2 = processor.split_tiles(
            geo_coords=geo_coords,
            m=6, n=90, # 行列
            shrink_ratio=(0.8, 0.8), # 小区行列收缩比例
            id_order='top-left', # 编号顺序
            # 'top-left' 从左上角开始编号
            # 'bottom-right' 从右下角开始编号
            start_id=864 # 起始ID - 1
        )
        print(f"成功切割为 {len(tiles2)} 个区块")
    except Exception as e:
        print(f"切割区块2失败: {str(e)}")
        return

    # 合并两个GeoDataFrame
    tiles = pd.concat([tiles1, tiles2], ignore_index=True)

    try:
        if processor.save_tiles_to_shp(tiles, output_shp):
            print(f"成功保存区块到: {output_shp}")
        else:
            print("保存区块失败")
    except Exception as e:
        print(f"保存区块时出错: {str(e)}")
        return
    
    # 打印前5个区块的信息
    print("前5个区块信息:")
    print(tiles.head())


if __name__ == "__main__":
    main("0927")
