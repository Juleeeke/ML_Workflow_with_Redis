# core/redis_client.py
import redis
from configs import settings

def get_redis_conn():
    """获取 Redis 连接实例"""
    pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True #decode to str
    )
    return redis.Redis(connection_pool=pool)
