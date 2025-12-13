import pandas as pd
import numpy as np
import os

def load_boston_data_local(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ 找不到本地文件: {file_path}")

    print(f"📂 正在读取文件: {file_path}")
    
    try:
        # 尝试 1: 假设是标准 CSV (逗号分隔)，且有表头
        # 这是最常见的情况
        df = pd.read_csv(file_path)
        
        # 检查是否读取失败（比如所有数据挤在一列里）
        if df.shape[1] < 2:
            print("⚠️ 逗号分隔读取似乎不对 (列数<2)，尝试使用空格分隔...")
            # 尝试 2: 假设是空格分隔 (sep=r"\s+")
            df = pd.read_csv(file_path, sep=r"\s+")

        # 再次检查
        if df.shape[1] < 2:
             # 尝试 3: 有可能前面有几十行说明文字？尝试跳过一些行
             print("⚠️ 还是不对，尝试跳过前22行...")
             df = pd.read_csv(file_path, sep=r"\s+", skiprows=22, header=None)

        print(f"✅ 读取成功，原始形状: {df.shape}")

        # 数据清洗：确保数据都是数值型
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna() # 丢弃解析失败的行

        # 按照标准波士顿数据集格式：最后一列是 Label (房价)，前面是 Features
        X = df.iloc[:, :-1].values.astype(np.float32)
        y = df.iloc[:, -1].values.astype(np.float32)

        print(f"✅ 数据集加载完毕! 特征: {X.shape}, 标签: {y.shape}")
        return X, y

    except Exception as e:
        print(f"❌ 数据加载彻底失败: {e}")
        # 打印文件的前几行，帮你调试
        print("--- 文件前5行内容 ---")
        with open(file_path, 'r') as f:
            for _ in range(5):
                print(f.readline().strip())
        print("--------------------")
        raise e
