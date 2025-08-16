import os

from core.data_integrator import DataIntegrator
from utils.file_utils import create_dir_if_not_exists


def main():
    # 设置输入和输出路径
    data_files = [
        {'path': 'input/result.csv', 'type': 'csv'},
        {'path': 'input/result.shp', 'type': 'shp'},
        {'path': 'input/result.xlsx', 'type': 'excel'},
        {'path': 'input/result.geojson', 'type': 'geojson'},
    ]

    # 创建输出目录
    create_dir_if_not_exists('output')
    
    try:
        # 初始化数据集成器
        integrator = DataIntegrator(tile_id_field='FID') # 区块ID字段名

        print("数据集成器初始化成功")
        
        # 添加数据文件
        for file_info in data_files:
            file_path = file_info['path']
            file_type = file_info['type']
            success = integrator.add_data(file_path, file_type)
            if success:
                print(f"成功添加数据文件: {file_path}")
            else:
                print(f"添加数据文件失败: {file_path}")
        
        # 合并数据
        merged_df = integrator.merge_data()
        print(f"数据合并完成，共 {len(merged_df)} 行数据")
        print(f"合并后的字段: {', '.join(merged_df.columns)}")
        
        output = []
        # 导出数据
        output.append(('output/result.csv', 'csv'))
        output.append(('output/result.geojson', 'geojson'))
        output.append(('output/result.xlsx', 'excel'))
        output.append(('output/result1.shp', 'shp'))

        for output_path, output_type in output:
            success = integrator.export_data(output_path, output_type)
            if success:
                print(f"成功导出数据到: {output_path}")
            else:
                print(f"导出数据到 {output_path} 失败")
        print("数据集成器处理完成")

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")


if __name__ == '__main__':
    main()