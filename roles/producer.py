# roles/producer.py
import json
import time
from sklearn.model_selection import ParameterGrid
from core.redis_client import get_redis_conn
from configs import settings

def main():
    r = get_redis_conn()
    
    # 1. 定义超参数网格 (你可以把这个范围调大以产生更多任务)
    param_grid = {
        'n_estimators': [10, 50, 100, 200, 500],
        'max_depth': [None, 3, 5, 10, 20],
        'min_samples_split': [2, 5, 10],
        'criterion': ['squared_error'] 
    }
    
    grid = list(ParameterGrid(param_grid))
    total_tasks = len(grid)
    print(f"📦 准备生成 {total_tasks} 个任务...")

    # 2. 清空旧队列 (可选，视需求而定)
    # r.delete(settings.TASK_QUEUE_KEY)

    # 3. 批量推送任务
    pipe = r.pipeline()
    for i, params in enumerate(grid):
        task_payload = {
            'id': f"task_{i}",
            'params': params,
            'timestamp': time.time()
        }
        pipe.lpush(settings.TASK_QUEUE_KEY, json.dumps(task_payload))
        
        # 每 1000 条执行一次提交，防止内存溢出
        if (i + 1) % 1000 == 0:
            pipe.execute()
            print(f"   已推送 {i + 1}/{total_tasks} ...")
    
    pipe.execute()
    print(f"🚀 所有任务分发完毕！请启动 Worker。")

if __name__ == "__main__":
    main()
