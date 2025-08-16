import os

from core.data_integrator import DataIntegrator
from utils.generate_sample_files import generate_sample_files


def main():
    
    # 生成样本文件
    output_dir = r'2024苏家屯\0628\多光谱'
    generate_sample_files(output_dir)

    # 设置输入和输出路径
    data_files = [
        {'path': r'2024苏家屯\0628\多光谱\result_index.csv', 'type': 'csv'},
        {'path': r'2024苏家屯\0628\多光谱\result_index.shp', 'type': 'shp'},
        {'path': r'2024苏家屯\0628\多光谱\result_index.xlsx', 'type': 'excel'},
        {'path': r'2024苏家屯\0628\多光谱\result_index.geojson', 'type': 'geojson'},
    ]
    
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
        output.append((r'2024苏家屯\0628\多光谱\result.csv', 'csv'))
        output.append((r'2024苏家屯\0628\多光谱\result.geojson', 'geojson'))
        output.append((r'2024苏家屯\0628\多光谱\result.xlsx', 'excel'))
        output.append((r'2024苏家屯\0628\多光谱\result.shp', 'shp'))

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