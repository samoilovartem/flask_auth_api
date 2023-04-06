import json

from uuid import UUID

from pydantic import BaseModel
from tests.functional.settings import BASE_DIR
from tests.functional.utils.schemas import (
    GenreDetail,
    HTTPResponse,
    MovieDetail,
    PersonDetail,
)


async def extract_movies(response: HTTPResponse) -> list[MovieDetail]:
    return [MovieDetail.parse_obj(movies) for movies in response.body]


async def extract_movie(response: HTTPResponse) -> MovieDetail:
    movie = response.body
    return MovieDetail.parse_obj(movie)


async def extract_persons(response: HTTPResponse) -> list[PersonDetail]:
    return [PersonDetail.parse_obj(person) for person in response.body]


async def extract_person(response: HTTPResponse) -> PersonDetail:
    return PersonDetail.parse_obj(response.body)


async def extract_genres(response: HTTPResponse) -> list[GenreDetail]:
    return [GenreDetail.parse_obj(genre) for genre in response.body]


async def extract_genre(response: HTTPResponse) -> GenreDetail:
    return GenreDetail.parse_obj(response.body)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


async def extract_payload(file_name: str, model: BaseModel, es_index: str) -> tuple:
    """Extracts payload from json file for use in elastic bulk uploading"""
    file_path = f'{BASE_DIR}/testdata/{file_name}'
    with open(file_path) as json_file:
        data = json.load(json_file)
    obj_list = [model.parse_obj(some_obj) for some_obj in data]
    add_result = []
    for any_obj in obj_list:
        add_result.append({"index": {"_index": es_index, "_id": any_obj.id}})
        add_result.append(any_obj.dict())
    add_payload = (
        '\n'.join([json.dumps(line, cls=UUIDEncoder) for line in add_result]) + '\n'
    )

    del_result = []
    for some_obj in obj_list:
        del_result.append({"delete": {"_index": es_index, "_id": some_obj.id}})
    del_payload = (
        '\n'.join([json.dumps(line, cls=UUIDEncoder) for line in del_result]) + '\n'
    )

    return add_payload, del_payload
