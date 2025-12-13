# configs/settings.py
import os

#主机的IP：
#单设备模拟，以'localhost'
#多设备，指向主机的IP
REDIS_HOST = os.getenv('REDIS_HOST', '172.19.123.33')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_DB = 0

#Queue keys
TASK_QUEUE_KEY = 'boston:tasks'
RESULT_QUEUE_KEY = 'boston:results'

#工作设置
WORKER_TIMEOUT = 5 
