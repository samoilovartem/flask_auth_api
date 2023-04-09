import redis

from core.settings import settings

host = settings.redis_host
port = settings.redis_port
redis = redis.Redis(host=host, port=port)
