from backoff import expo, on_exception
from loguru import logger
from redis import ConnectionError, Redis

from tests.functional.settings import test_settings
from tests.functional.utils.loguru_config import loguru_config

logger.add(**loguru_config)


def create_redis_client(host, port):
    return Redis(host=host, port=port)


@on_exception(expo, ConnectionError, max_tries=test_settings.MAX_RETRIES)
def connect_to_redis(redis_client, host, port):
    logger.info(f'Connecting to Redis at {host}:{port}...')
    redis_client.ping()
    logger.success('Redis connected')


if __name__ == '__main__':
    host = test_settings.REDIS_HOST
    port = test_settings.REDIS_PORT
    redis_client = create_redis_client(host, port)
    connect_to_redis(redis_client, host, port)
