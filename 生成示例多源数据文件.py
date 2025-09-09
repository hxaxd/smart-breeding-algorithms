from utils.generate_sample_files import generate_csv, generate_xlsx, generate_geojson
   
if __name__ == '__main__':   
    # 生成样本文件
    output_dir = r'2024苏家屯\20240628\多光谱'
    
    # 生成CSV文件
    csv_path = generate_csv(output_dir, num_records=1404)
    print(f"成功生成CSV文件: {csv_path}")
    
    # 生成Excel文件
    xlsx_path = generate_xlsx(output_dir, num_records=1404)

    print(f"成功生成Excel文件: {xlsx_path}")
    
    # 生成GeoJSON文件
    geojson_path = generate_geojson(output_dir, num_records=1404)

    print(f"成功生成GeoJSON文件: {geojson_path}")