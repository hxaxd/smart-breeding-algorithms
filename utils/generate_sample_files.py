import os
import csv
import json


def generate_csv(output_dir, num_records=1404):
    """生成CSV文件"""
    csv_path = os.path.join(output_dir, 'result_index.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['FID', 'CSV'])
        for i in range(1, num_records + 1):
            writer.writerow([i, 'csv'])
    return csv_path


def generate_xlsx(output_dir, num_records=1404):
    """生成Excel文件"""
    import pandas as pd
    xlsx_path = os.path.join(output_dir, 'result_index.xlsx')
    data = {'FID': range(1, num_records + 1), 'XLSX': ['xlsx'] * num_records}
    df = pd.DataFrame(data)
    df.to_excel(xlsx_path, index=False)
    return xlsx_path


def generate_geojson(output_dir, num_records=1404):
    """生成GeoJSON文件"""
    geojson_path = os.path.join(output_dir, 'result_index.geojson')
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
                "coordinates": [0, 0]
            }
        }
        features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(geojson_path, 'w', encoding='utf-8') as geojson_file:
        json.dump(geojson_data, geojson_file, ensure_ascii=False, indent=2)
    return geojson_path


