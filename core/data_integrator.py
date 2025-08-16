import pandas as pd
import geopandas as gpd
import pandas as pd
from utils.file_utils import check_file_exists


class DataIntegrator:
    def __init__(self, tile_id_field: str = 'FID'):
        """初始化，设置区块ID字段名
        
        Args:
            tile_id_field: 区块ID字段名
        """
        self.tile_id_field = tile_id_field
        self.dataframes = []
        self.merged_df = pd.DataFrame()

    def add_data(self, file_path: str, file_type: str) -> bool:
        """添加数据文件(shp/geojson/csv/excel)
        
        Args:
            file_path: 数据文件路径
            file_type: 文件类型 ('shp', 'geojson', 'csv', 'excel')
        
        Returns:
            是否添加成功
        """
        if not check_file_exists(file_path):
            return False
        
        try:
            if file_type.lower() == 'shp':
                df = gpd.read_file(file_path)
                if df is None:
                    return False
            elif file_type.lower() == 'geojson':
                df = gpd.read_file(file_path)
            elif file_type.lower() == 'csv':
                df = pd.read_csv(file_path)
                if df is None:
                    return False
            elif file_type.lower() == 'excel':
                df = pd.read_excel(file_path)
            else:
                raise Exception(f"不支持的文件类型: {file_type}")
            
            # 检查区块ID字段是否存在
            if self.tile_id_field not in df.columns:
                raise Exception(f"文件{file_path}中缺少{self.tile_id_field}字段")
            
            # 添加到数据框列表
            self.dataframes.append(df)
            return True
        except Exception as e:
            raise Exception(f"添加数据文件时出错: {str(e)}")

    def merge_data(self) -> pd.DataFrame:
        """合并所有数据，处理字段冲突
        
        Returns:
            合并后的数据框
        """
        if not self.dataframes:
            return pd.DataFrame()
        
        # 从第一个数据框开始合并
        merged_df = self.dataframes[0].copy()
        
        # 合并剩余的数据框
        for df in self.dataframes[1:]:
            merged_df = self._resolve_column_conflicts(merged_df, df)

        self.merged_df = merged_df
        
        return merged_df

    def _resolve_column_conflicts(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """处理字段冲突
        
        Args:
            df1: 第一个数据框
            df2: 第二个数据框
        
        Returns:
            合并后的数据框
        """
        common_cols = set(df1.columns) & set(df2.columns)
        common_cols.discard(self.tile_id_field)
        
        for col in common_cols:
            # 简单策略：保留第一个数据源的字段
            df2 = df2.drop(columns=[col])
            # print(f"检测到重复列{col}，已从第二个数据集中移除")
        
        return pd.merge(df1, df2, on=self.tile_id_field)

    def export_data(self, output_path: str, output_type: str) -> bool:
        """导出数据到指定格式
        
        Args:
            output_path: 输出文件路径
            output_type: 输出类型 ('csv', 'json', 'excel', 'shp)
        
        Returns:
            是否导出成功
        """
        if self.merged_df is None:
            raise Exception("请先合并数据")
        
        merged_df = self.merged_df
        try:
            if merged_df.empty:
                raise Exception("没有数据可导出")
                return False
            
            # 导出数据
            if output_type.lower() == 'csv':
                merged_df.to_csv(output_path, index=False)
            elif output_type.lower() == 'geojson':
                # 转换为GeoDataFrame后导出
                gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')
                gdf.to_file(output_path, driver='GeoJSON')
            elif output_type.lower() == 'excel':
                merged_df.to_excel(output_path, index=False)
            elif output_type.lower() == 'shp':
                gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')
                gdf.to_file(output_path, driver='ESRI Shapefile')
            else:
                raise Exception(f"不支持的输出类型: {output_type}")
            
            return True
        except Exception as e:
            raise Exception(f"导出数据时出错: {str(e)}")
