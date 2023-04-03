import pytest

from tests.functional.utils.helpers import extract_payload
from tests.functional.utils.schemas import MovieDetail


@pytest.fixture(scope='session')
async def load_testing_movies_data(es_client):
    index = 'movies'
    payload = await extract_payload(f'{index}.json', MovieDetail, index)
    await es_client.bulk(body=payload[0], index=index, refresh=True)
    yield
    await es_client.bulk(body=payload[1], index=index, refresh=True)
