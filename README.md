# 智慧育种算法框架

## 项目介绍

本项目是一个基于Python的智慧育种算法框架, 提供基于多维平面转换的育种小区分割 -> 区块切面的多维度像元统计计算 -> 多源数据融合的全链路育种算法支持

## 项目结构

```text
smart-breeding-algorithms/
├── core/ # 核心算法模块
├── utils/ # 工具函数模块
├── requirements.txt # 项目依赖
├── README.md # 项目介绍
├── 若干示例代码
```

## 安装依赖

```bash
conda create -n smart-breeding-algorithms python=3.12 # 创建conda环境
conda activate smart-breeding-algorithms # 激活conda环境
conda install --file requirements.txt # 安装依赖
```

## 运行示例

```bash
# 运行之前确保激活conda环境
# conda activate smart-breeding-algorithms # 激活conda环境
# 运行前确保根据注释修改示例代码

python examples.py # 修改为实际的示例文件名
```

## 使用说明

- 惯用流程: 
  - 分割小区, 产出 shape.shp 文件
  - 根据 shape.shp 文件
    - 分割小区 rgb 图像
    - 计算小区数据, 产出 result_index.shp 文件
  - 将其它来源数据 (支持 shp, xlsx, csv, geojson 格式) 与 result_index.shp 中的数据多源融合
  - 导出 shp, xlsx, csv, geojson 格式 result 文件
- 示例演示:
  - `python 小区分割.py`
  - `python 切割图像.py`
  - `python 技术大全.py`
  - `python 生成示例多源数据文件.py`
  - `python 多源数据融合.py`
- 运行示例见示例文件中的注释
