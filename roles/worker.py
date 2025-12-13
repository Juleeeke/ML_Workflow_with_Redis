# roles/worker.py
import json
import time
import socket
import sys
from core.redis_client import get_redis_conn
from core.data_loader import load_boston_data_local
from core.model_trainer import train_and_evaluate
from configs import settings

def main():
    # 获取本机名称，用于标识是谁跑的任务
    worker_id = socket.gethostname()
    r = get_redis_conn()
    
    print(f"🐜 Worker [{worker_id}] 正在启动...")
    
    # 1. 预加载数据 (内存常驻)
    try:
        X, y = load_boston_data_local('/Users/juleyau/code/redis/cluster/BostonHousing.csv')
    except Exception:
        print("❌ 无法加载数据，Worker 退出。")
        sys.exit(1)

    print(f"👂 监听队列: {settings.TASK_QUEUE_KEY}")

    while True:
        # 2. 阻塞式拉取任务
        try:
            # brpop 返回元组 (queue_name, data)
            task_data = r.brpop(settings.TASK_QUEUE_KEY, timeout=settings.WORKER_TIMEOUT)
            
            if not task_data:
                # 超时无任务，打印心跳或直接 continue
                continue
                
            _, task_json = task_data
            task = json.loads(task_json)
            
            # 3. 执行计算
            print(f"   [{worker_id}] 处理任务 {task['id']} ...", end="", flush=True)
            start_t = time.time()
            
            mse = train_and_evaluate(X, y, task['params'])
            
            cost_t = time.time() - start_t
            
            # 4. 封装结果
            result_payload = {
                'task_id': task['id'],
                'params': task['params'],
                'mse': mse,
                'worker': worker_id,
                'compute_time': round(cost_t, 4),
                'finished_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 5. 推送回结果队列
            r.lpush(settings.RESULT_QUEUE_KEY, json.dumps(result_payload))
            print(f" 完成 (MSE={mse:.4f}, {cost_t:.2f}s)")
            
        except KeyboardInterrupt:
            print("\n🛑 Worker 停止运行。")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            # 实际生产中可能需要把失败任务重新塞回队列
            import traceback
            print(f"\n❌ 任务 {task['id']} 炸了！")
            print(traceback.format_exc()) # 打印完整堆栈
            
            # 【重要】把失败的任务记录下来，或者塞入一个 'failed_queue'
            # 否则这个任务就凭空消失了
            r.lpush('boston:failed_tasks', json.dumps(task))

if __name__ == "__main__":
    main()
