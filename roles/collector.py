# roles/collector.py
import json
import csv
import os
import time
from core.redis_client import get_redis_conn
from configs import settings

OUTPUT_FILE = 'results/tuning_results.csv'

def main():
    r = get_redis_conn()
    
    # 确保结果目录存在
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    print(f"💾 Collector 启动，等待结果写入 {OUTPUT_FILE} ...")
    
    # 简单的文件头处理逻辑
    file_exists = os.path.exists(OUTPUT_FILE)
    
    while True:
        try:
            # 阻塞获取结果
            BATCH_SIZE = 1
            res_data = r.brpop(settings.RESULT_QUEUE_KEY, timeout=1)
            
            if not res_data:
                continue
                
            _, res_json = res_data
            result = json.loads(res_json)
            
            # 展平数据结构 (params 里的字典解包出来放到最外层)
            row = result['params'].copy()
            row.update({
                'task_id': result['task_id'],
                'mse': result['mse'],
                'worker': result['worker'],
                'compute_time': result['compute_time'],
                'finished_at': result['finished_at']
            })
            
            # 实时写入 (追加模式)
            # 注意：高并发下可能需要批量写入优化，这里为了实时演示逐条写入
            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                
                # 如果是新文件，先写表头
                if not file_exists:
                    writer.writeheader()
                    file_exists = True
                
                writer.writerow(row)
                
            print(f"   [已落盘] {result['task_id']} 来自 {result['worker']}")
            
        except KeyboardInterrupt:
            print("\n🛑 Collector 停止。")
            break
        except Exception as e:
            print(f"❌ 写入错误: {e}")

if __name__ == "__main__":
    main()
