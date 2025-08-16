import numpy as np
from rasterio.transform import Affine
from typing import Tuple


def geo_to_pixel(transform: Affine, x: float, y: float) -> Tuple[int, int]:
    """地理坐标转像素坐标
    
    Args:
        transform:  affine变换矩阵
        x: 地理坐标x
        y: 地理坐标y
    
    Returns:
        像素坐标(col, row)
    """
    col = int((x - transform[0]) / transform[1])
    row = int((y - transform[3]) / transform[5])
    return col, row

def pixel_to_geo(transform: Affine, col: int, row: int) -> Tuple[float, float]:
    """像素坐标转地理坐标
    
    Args:
        transform:  affine变换矩阵
        col: 像素列号
        row: 像素行号
    
    Returns:
        地理坐标(x, y)
    """
    x = transform[0] + col * transform[1]
    y = transform[3] + row * transform[5]
    return x, y

def calculate_homography(src_pts: np.ndarray, dst_pts: np.ndarray) -> np.ndarray:
    """计算单应性变换矩阵
    
    Args:
        src_pts: 源坐标点数组
        dst_pts: 目标坐标点数组
    
    Returns:
        单应性变换矩阵
    """
    A = []
    for (sx, sy), (dx, dy) in zip(src_pts, dst_pts):
        A.append([sx, sy, 1, 0, 0, 0, -sx * dx, -sy * dx])
        A.append([0, 0, 0, sx, sy, 1, -sx * dy, -sy * dy])
    
    A = np.array(A)
    B = np.array(dst_pts).flatten()
    H = np.linalg.lstsq(A, B, rcond=None)[0]
    return np.array([[H[0], H[1], H[2]], [H[3], H[4], H[5]], [H[6], H[7], 1]])
    
def normalize_coordinates(geo_coords: np.ndarray, H: np.ndarray) -> np.ndarray:
    """将地理坐标转换为归一化坐标
    
    Args:
        geo_coords: 地理坐标数组
        H: 单应性变换矩阵
    
    Returns:
        归一化后的坐标数组
    """
    # 将点转换为齐次坐标
    homogeneous_coords = np.column_stack((geo_coords, np.ones(len(geo_coords))))
    
    # 应用单应性变换
    transformed = homogeneous_coords @ H.T
    
    # 归一化齐次坐标
    transformed /= transformed[:, 2].reshape(-1, 1)
    
    # 返回二维坐标
    return transformed[:, :2]

def denormalize_coordinates(normalized_coords: np.ndarray, H: np.ndarray) -> np.ndarray:
    """将归一化坐标转换为地理坐标
    
    Args:
        normalized_coords: 归一化坐标数组
        H: 单应性变换矩阵
    
    Returns:
        地理坐标数组
    """
    # 计算单应性矩阵的逆矩阵
    H_inv = np.linalg.inv(H)
    
    # 将归一化坐标转换为齐次坐标
    homogeneous_coords = np.column_stack((normalized_coords, np.ones(len(normalized_coords))))
    
    # 应用逆变换
    transformed = homogeneous_coords @ H_inv.T
    
    # 归一化齐次坐标
    transformed /= transformed[:, 2].reshape(-1, 1)
    
    # 返回地理坐标
    return transformed[:, :2]

