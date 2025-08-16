import os
import csv
import json


def generate_sample_files(output_dir):
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义要生成的记录数量
    num_records = 1404
    
    # 生成CSV文件
    csv_path = os.path.join(output_dir, 'sample.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # 写入表头
        writer.writerow(['FID', 'CSV'])
        # 写入数据行
        for i in range(1, num_records + 1):
            writer.writerow([i, 'csv'])
    print(f"成功生成CSV文件: {csv_path}")
    
    
    # 生成真正的GeoJSON格式文件
    real_geojson_path = os.path.join(output_dir, 'sample.geojson')
    features = []
    for i in range(1, num_records + 1):
        feature = {
            "type": "Feature",
            "properties": {
                "FID": i,
                "geojson": "geojson"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0]  # 占位坐标
            }
        }
        features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(real_geojson_path, 'w', encoding='utf-8') as geojson_file:
        json.dump(geojson_data, geojson_file, ensure_ascii=False, indent=2)
    print(f"成功生成GeoJSON文件: {real_geojson_path}")

