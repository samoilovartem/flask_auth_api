from typing import Optional

import aioredis

from aioredis import Redis
from backoff import expo, on_exception
from core.config import Config
from core.custom_logger import CustomLogger
from redis import ConnectionError

logger = CustomLogger.make_logger()


class RedisManager:
    _instance: Optional['RedisManager'] = None

    def __new__(cls) -> 'RedisManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._redis: Optional[Redis] = None

    async def get_redis(self) -> Redis:
        if self._redis is None:
            await self.redis_connect()
        return self._redis

    @on_exception(expo, ConnectionError, max_tries=Config.MAX_RETRIES, logger=logger)
    async def redis_ping(self):
        ping = await self._redis.ping()
        if ping != b'PONG':
            raise ConnectionError('Redis is not responding.')
        logger.info('Successfully connected to redis.')

    async def redis_connect(self):
        if self._redis is None:
            logger.info('Checking connection to redis.')
            self._redis = await aioredis.create_redis_pool(
                (Config.REDIS_HOST, Config.REDIS_PORT),
                minsize=Config.MIN_SIZE,
                maxsize=Config.MAX_SIZE,
            )
            await self.redis_ping()
            logger.info('Successfully connected to redis.')

    async def redis_disconnect(self):
        if self._redis is not None:
            self._redis.close()
            await self._redis.wait_closed()
            self._redis = None
            logger.info('Successfully disconnected from redis.')


redis_manager = RedisManager()
