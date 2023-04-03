import pytest

from tests.functional.utils.helpers import extract_payload
from tests.functional.utils.schemas import PersonDetail


@pytest.fixture(scope='session')
async def load_testing_persons_data(es_client):
    index = 'persons'
    payload = await extract_payload(f'{index}.json', PersonDetail, index)
    await es_client.bulk(body=payload[0], index=index, refresh=True)
    yield
    await es_client.bulk(body=payload[1], index=index, refresh=True)
