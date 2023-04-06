from http import HTTPStatus

from tests.functional.utils.helpers import extract_genre, extract_genres

pytest_plugins = "tests.functional.fixtures.genres"


async def test_general_genres_list(
    make_get_request, load_testing_genres_data, redis_client
):
    endpoint = 'genres?page_number=0&page_size=20'

    response = await make_get_request(endpoint)
    genres = await extract_genres(response)
    cache = await redis_client.get('genres:0:20')

    assert response.status == HTTPStatus.OK
    assert len(genres) > 0
    assert cache


async def test_genre_search_via_id(make_get_request, redis_client):
    response_genres = await make_get_request('genres/')
    genres_list = await extract_genres(response_genres)
    genre_id = genres_list[0].id

    response = await make_get_request(f'genres/{genre_id}')
    genre = await extract_genre(response)
    cache = await redis_client.get(f'{genre_id}')

    assert response_genres.status == HTTPStatus.OK
    assert response.status == HTTPStatus.OK
    assert genre.id == genre_id
    assert cache


async def test_genres_search(make_get_request, redis_client):
    response_genres = await make_get_request('genres/')
    genres_list = await extract_genres(response_genres)
    genre_name = genres_list[0].name

    response = await make_get_request(f'genres/search?query={genre_name}')
    search_genre = await extract_genres(response)
    cache = await redis_client.get(f'genres:{genre_name}:name:0:20')

    assert response.status == HTTPStatus.OK
    assert len(search_genre) > 0
    assert cache


async def test_genres_search_with_pagination(make_get_request, redis_client):
    response_genres = await make_get_request('genres?page_number=0&page_size=20')
    genres_list = await extract_genres(response_genres)
    genre_name = genres_list[0].name

    response = await make_get_request(
        f'genres/search?query={genre_name}&page_number=0&page_size=10'
    )
    search_genres = await extract_genres(response)
    cache = await redis_client.get(f'genres:{genre_name}:name:0:10')

    assert response.status == HTTPStatus.OK
    assert len(search_genres) > 0
    assert cache


async def test_genres_list_negative_page_number(make_get_request):
    endpoint = 'genres?page_number=-1&page_size=20'

    response = await make_get_request(endpoint)
    response_body = response.body.get('detail')[0].get('msg')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_body == 'ensure this value is greater than or equal to 0'


async def test_genres_list_negative_page_size(make_get_request):
    endpoint = 'genres?page_number=0&page_size=-20'

    response = await make_get_request(endpoint)
    response_body = response.body.get('detail')[0].get('msg')

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_body == 'ensure this value is greater than 0'


async def test_genres_search_no_results(make_get_request, redis_client):
    non_existent_genre_name = 'NonExistentGenreName1234'
    endpoint = f'genres/search?query={non_existent_genre_name}'

    response = await make_get_request(endpoint)
    response_body = response.body
    cache = await redis_client.get(f'genres:{non_existent_genre_name}:name:0:20')
    decoded_cache = cache.decode('UTF-8').lower()

    assert response.status == HTTPStatus.NOT_FOUND
    assert response_body == {'detail': 'No genres found'}
    assert cache
    assert non_existent_genre_name.lower() not in decoded_cache


async def test_es_genre_uploading(make_get_request, redis_client):
    genre_id = "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07f1"

    response = await make_get_request(f'genres/{genre_id}')
    genre = await extract_genre(response)
    cache = await redis_client.get(genre_id)

    assert str(genre.id) == genre_id
    assert genre.name == "SuperAction"
    assert cache
