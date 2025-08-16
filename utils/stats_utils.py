import numpy as np
from scipy.stats import skew, kurtosis

def calculate_mean(indexs):
    """计算指数平均值"""
    return {f"avg_{name}": np.nanmean(index) for name, index in indexs.items()}

def calculate_std(indexs):
    """计算指数标准差"""
    return {f"std_ff{name}": np.nanstd(index) for name, index in indexs.items()}

def calculate_mode(indexs):
    """计算指数众数"""
    mode_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) == 0:
                mode_index[f"mode_{name}"] = np.nan
            else:
                hist, bins = np.histogram(clean_index, bins='auto')
                mode_index[f"mode_{name}"] = bins[np.argmax(hist)]
        except:
            mode_index[f"mode_{name}"] = np.nan
    return mode_index

def calculate_variance(indexs):
    """计算指数方差"""
    return {f"var_{name}": np.nanvar(index) for name, index in indexs.items()}

def calculate_median(indexs):
    """计算指数中位数"""
    median_index = {}
    for name, index in indexs.items():
        try:
            median_index[f"medi_{name}"] = np.nanmedian(index)
        except:
            median_index[f"medi_{name}"] = np.nan
    return median_index

def calculate_iqr(indexs):
    """计算指数四分位距"""
    iqr_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) == 0:
                iqr_index[f"iqr_{name}"] = np.nan
            else:
                iqr_index[f"iqr_{name}"] = np.percentile(clean_index, 75) - np.percentile(clean_index, 25)
        except:
            iqr_index[f"iqr_{name}"] = np.nan
    return iqr_index

def calculate_range(indexs):
    """计算指数范围"""
    range_index = {}
    for name, index in indexs.items():
        try:
            range_index[f"rng_{name}"] = np.nanmax(index) - np.nanmin(index)
        except:
            range_index[f"rng_{name}"] = np.nan
    return range_index

def calculate_skewness(indexs):
    """计算指数偏度"""
    skew_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) < 3:
                skew_index[f"skew_{name}"] = np.nan
            else:
                skew_index[f"skew_{name}"] = skew(clean_index)
        except:
            skew_index[f"skew_{name}"] = np.nan
    return skew_index

def calculate_kurtosis(indexs):
    """计算指数峰度"""
    kurt_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) < 4:
                kurt_index[f"kurt_{name}"] = np.nan
            else:
                kurt_index[f"kurt_{name}"] = kurtosis(clean_index)
        except:
            kurt_index[f"kurt_{name}"] = np.nan
    return kurt_index

def calculate_coefficient_of_variation(indexs):
    """计算指数变异系数"""
    cov_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) == 0:
                cov_index[f"var_{name}"] = np.nan
            else:
                mean_val = np.mean(clean_index)
                if mean_val == 0:
                    cov_index[f"var_{name}"] = 0
                else:
                    cov_index[f"var_{name}"] = np.std(clean_index) / mean_val
        except:
            cov_index[f"var_{name}"] = np.nan
    return cov_index

def calculate_uniformity(indexs):
    """计算指数均匀度"""
    uniform_index = {}
    for name, index in indexs.items():
        try:
            clean_index = index[~np.isnan(index)]
            if len(clean_index) == 0:
                uniform_index[f"uni_{name}"] = np.nan
            else:
                mean_val = np.mean(clean_index)
                if mean_val == 0:
                    uniform_index[f"uni_{name}"] = 1
                else:
                    uniformity = 1 - (np.std(clean_index) / mean_val)
                    uniform_index[f"uni_{name}"] = np.clip(uniformity, 0, 1)
        except:
            uniform_index[f"uni_{name}"] = np.nan
    return uniform_index
    
