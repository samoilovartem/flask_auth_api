from http import HTTPStatus

from tests.functional.utils.helpers import (
    extract_person,
    extract_persons,
)

pytest_plugins = "tests.functional.fixtures.persons"


async def test_general_persons_list(
    make_get_request, load_testing_persons_data, redis_client
):
    response = await make_get_request('persons/')
    persons = await extract_persons(response)
    cache = await redis_client.get('persons:0:20')

    assert response.status == HTTPStatus.OK
    assert len(persons) > 0
    assert cache


async def test_person_search_via_id(make_get_request, redis_client):
    response_persons = await make_get_request('persons/')
    persons_list = await extract_persons(response_persons)
    person_id = persons_list[0].id

    response = await make_get_request(f'persons/{person_id}')
    person = await extract_person(response)
    cache = await redis_client.get(f'{person_id}')

    assert response_persons.status == HTTPStatus.OK
    assert response.status == HTTPStatus.OK
    assert person.id == person_id
    assert cache


async def test_persons_list_page_number(make_get_request, redis_client):
    response = await make_get_request('persons?page_number=0')
    persons = await extract_persons(response)
    cache = await redis_client.get('persons:0:20')

    assert response.status == HTTPStatus.OK
    assert len(persons) > 0
    assert cache


async def test_persons_list_page_size(make_get_request, redis_client):
    response = await make_get_request('persons?page_size=15')
    persons = await extract_persons(response)
    cache = await redis_client.get('persons:0:15')

    assert response.status == HTTPStatus.OK
    assert (len(persons) > 0) and (len(persons) <= 15)
    assert cache


async def test_persons_list_page_number_and_size(make_get_request, redis_client):
    response = await make_get_request('persons?page_size=18&page_number=0')
    persons = await extract_persons(response)
    cache = await redis_client.get('persons:0:18')

    assert response.status == HTTPStatus.OK
    assert (len(persons) > 0) and (len(persons) <= 18)
    assert cache


async def test_persons_search(make_get_request, redis_client):
    response_persons = await make_get_request('persons/')
    persons_list = await extract_persons(response_persons)
    person_name = persons_list[0].full_name

    response = await make_get_request(f'persons/search?query={person_name}')
    search_people = await extract_persons(response)
    cache = await redis_client.get(f'persons:{person_name}:full_name:0:20')

    assert response.status == HTTPStatus.OK
    assert len(search_people) > 0
    assert cache


async def test_persons_search_with_pagination(make_get_request, redis_client):
    response_persons = await make_get_request('persons/')
    persons_list = await extract_persons(response_persons)
    person_name = persons_list[0].full_name

    response = await make_get_request(
        f'persons/search?query={person_name}&page_number=0&page_size=10'
    )
    search_persons = await extract_persons(response)
    cache = await redis_client.get(f'persons:{person_name}:full_name:0:10')

    assert response.status == HTTPStatus.OK
    assert len(search_persons) > 0
    assert cache


async def test_persons_list_negative_page_number(make_get_request):
    response = await make_get_request('persons?page_number=-1&page_size=20')
    response_body = response.body.get('detail')[0].get('msg')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_body == 'ensure this value is greater than or equal to 0'


async def test_persons_list_negative_page_size(make_get_request):
    response = await make_get_request('persons?page_number=0&page_size=-20')
    response_body = response.body.get('detail')[0].get('msg')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_body == 'ensure this value is greater than 0'


async def test_persons_search_no_results(make_get_request, redis_client):
    non_existent_person_name = 'NonExistentPersonName1234'

    response = await make_get_request(
        f'persons/search?query={non_existent_person_name}'
    )
    response_body = response.body
    cache = await redis_client.get(f'persons:{non_existent_person_name}:full_name:0:20')
    decoded_cache = cache.decode('UTF-8').lower()

    assert response.status == HTTPStatus.NOT_FOUND
    assert response_body == {'detail': 'No persons found'}
    assert cache
    assert non_existent_person_name.lower() not in decoded_cache


async def test_es_person_uploading(make_get_request, redis_client):
    response = await make_get_request('persons/00e1b6fd-cc86-4841-a983-5a3d34e4da98')
    person = await extract_person(response)
    cache = await redis_client.get('00e1b6fd-cc86-4841-a983-5a3d34e4da98')

    assert str(person.id) == "00e1b6fd-cc86-4841-a983-5a3d34e4da98"
    assert person.full_name == "Lars Alexanderson"
    assert cache
