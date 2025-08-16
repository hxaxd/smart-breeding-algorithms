from core.tile_processor import TileProcessor
import pandas as pd


def main():

    # 设置输入和输出路径
    tif_path = r"2024苏家屯\0628\多光谱\rgb.tif"  # 替换为实际的TIF文件路径
    output_shp = r"2024苏家屯\0628\多光谱\shape.shp" # 替换为期望的输出文件名
    
    # 初始化TileProcessor
    try:
        processor = TileProcessor(tif_path)
        print(f"成功加载TIF文件: {tif_path}")
        print(f"图像尺寸: {processor.width} x {processor.height}")
        print(f"地理边界: {processor.bounds}")
    except Exception as e:
        print(f"初始化TileProcessor失败: {str(e)}")
        return
    
    # 定义四个地理坐标点（示例坐标，请根据实际数据修改）
    # 这些点应该形成一个四边形区域
    geo_coords = [
        (123.30425725, 41.64233339),  # 西北
        (123.30442390, 41.64232080),  # 东北
        (123.304318616, 41.641444947), # 东南
        (123.30415355, 41.64145984),   # 西南
    ]
    
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
        print(f"切割区块失败: {str(e)}")
        return

    geo_coords = [
        (123.3041535, 41.6414598),   # 西北
        (123.3042756, 41.6414472),  # 东北
        (123.3041917, 41.6407102), # 东南
        (123.3040586, 41.6407197),  # 西南
    ]

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
        print(f"切割区块失败: {str(e)}")
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
    main()