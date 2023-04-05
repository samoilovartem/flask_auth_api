import asyncio

import aiohttp
import aioredis
import pytest

from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings
from tests.functional.utils.schemas import HTTPResponse


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def redis_client():
    redis = await aioredis.create_redis_pool(
        (f'{test_settings.REDIS_HOST}', test_settings.REDIS_PORT)
    )
    await redis.flushall()
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{test_settings.ES_HOST}:{test_settings.ES_PORT}'
    )
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = 'http://{host}:{port}/api/v1/{method}'.format(
            host=test_settings.SERVICE_HOST,
            port=test_settings.SERVICE_PORT,
            method=method,
        )
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
