import os
import json
import pandas as pd
import geopandas as gpd
from typing import Any, Dict, Optional


def check_file_exists(file_path: str) -> bool:
    """检查文件是否存在
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件是否存在
    """
    return os.path.isfile(file_path)


def check_dir_exists(dir_path: str) -> bool:
    """检查目录是否存在
    
    Args:
        dir_path: 目录路径
    
    Returns:
        目录是否存在
    """
    return os.path.isdir(dir_path)


def create_dir_if_not_exists(dir_path: str) -> bool:
    """如果目录不存在则创建
    
    Args:
        dir_path: 目录路径
    
    Returns:
        是否创建成功
    """
    try:
        if not check_dir_exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            return True
        return False
    except Exception as e:
        raise Exception(f"创建目录时出错: {str(e)}")
