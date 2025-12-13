# core/model_trainer.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

def train_and_evaluate(X, y, params):
    """
    根据给定的超参数训练模型并返回 CV 均分。
    """
    # 提取参数
    n_estimators = params.get('n_estimators', 100)
    max_depth = params.get('max_depth', None)
    min_samples_split = params.get('min_samples_split', 2)
    
    # 初始化模型
    # 注意：在微机上 n_jobs=1，避免单个任务占满所有核，导致无法并发处理多个任务
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        n_jobs=1, 
        random_state=42
    )
    
    # 5折交叉验证，使用负均方误差 (Negative MSE)
    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    
    # 返回正的 MSE 均值
    return -scores.mean()
