from core.tile_processor import TileProcessor
from utils.file_utils import create_dir_if_not_exists


def main():

    # 设置输入和输出路径
    tif_path = "input/result.tif"  # 替换为实际的TIF文件路径
    create_dir_if_not_exists("output")
    output_shp = "output/result.shp" # 替换为期望的输出文件名
    
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
        tiles = processor.split_tiles(
            geo_coords=geo_coords,
            m=1, n=5, # 行列
            shrink_ratio=(0.8, 0.8), # 小区行列收缩比例
            id_order='top-left', # 编号顺序
            # 'top-left' 从左上角开始编号
            # 'bottom-right' 从右下角开始编号
            start_id=0 # 起始ID
        )
        print(f"成功切割为 {len(tiles)} 个区块")
    except Exception as e:
        print(f"切割区块失败: {str(e)}")
        return
    

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