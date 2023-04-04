from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from multidict import CIMultiDictProxy
from pydantic import BaseModel, Field


class IdMixin(BaseModel):
    """
    A Pydantic `BaseModel` subclass with UUID field and `orjson` serialization/deserialization
    configurations for fast JSON serialization.
    """

    id: UUID = Field(
        title='id',
        example='fb58fd7f-7afd-447f-b833-e51e45e2a778',
    )


class PersonDetail(IdMixin):
    """A Pydantic model that represents a person and their roles in a movie."""

    full_name: str = Field(
        title='Full name',
        max_length=255,
        example='Mike Epps',
    )
    roles: Optional[list[str]] = Field(
        title='Roles',
        max_length=50,
        example=['Actor', 'Director'],
        default=[],
    )
    movies_ids: Optional[list[UUID]] = Field(
        title='Movies IDs',
        example=[
            'fb58fd7f-7afd-447f-b833-e51e45e2a778',
            '0e73f787-566f-4b83-816f-7805b32003aa',
        ],
    )


class PersonShort(IdMixin):
    """A Pydantic model that represents a short person instance in a movie."""

    full_name: str = Field(
        title='Full name',
        max_length=255,
        example='Mike Epps',
    )


class MovieList(IdMixin):
    """A Pydantic model that represents a list of movies."""

    title: str = Field(
        title='Movie title',
        max_length=255,
        example='Star Wars: Episode IV - A New Hope',
    )
    imdb_rating: Optional[float] = Field(
        title='Movie IMDb rating',
        ge=0,
        le=10,
        example=6.5,
        default=None,
    )


class GenreDetail(IdMixin):
    """A Pydantic model that represents a movie genre."""

    name: str = Field(
        title='Genre name',
        max_length=255,
        example='Action',
    )
    description: Optional[str] = Field(
        title='Genre description',
        example='Action genre is a media category that features intense physical action and combat, often with a '
        'protagonist facing high-stakes conflicts against enemies.',
        default=None,
    )


class MovieDetail(MovieList):
    """A Pydantic model that represents a movie and its details."""

    description: Optional[str] = Field(
        title='Movie description',
        example='The Imperial Forces, under orders from cruel Darth Vader, hold Princess Leia...',
        default=None,
    )
    genres: Optional[list[GenreDetail]] = Field(
        title='Genres',
        example=[
            GenreDetail(
                id='120a21cf-9097-479e-904a-13dd7198c1dd',
                name='Adventure',
                description='Adventure genre is a media category that features protagonists who embark on a journey',
            ),
            GenreDetail(
                id='0e73f787-566f-4b83-816f-7805b32003aa',
                name='Science fiction',
                description='Science fiction genre is a media category that features futuristic core',
            ),
        ],
        default=[],
    )
    actors: Optional[list[PersonShort]] = Field(
        title='Actors',
        example=[
            PersonShort(
                id='2834aaa1-d11d-4506-966c-0122ac4da0dc',
                full_name='Mike Stoklasa',
            ),
            PersonShort(
                id='7098cdbd-424d-40fa-b7c3-0bf6c81ed283',
                full_name='Mike Epps',
            ),
        ],
        default=[],
    )

    writers: Optional[list[PersonShort]] = Field(
        title='Writers',
        example=[
            PersonShort(
                id='6960e2ca-889f-41f5-b728-1e7313e54d6c',
                full_name='Gene Roddenberry',
            ),
            PersonShort(
                id='82b7dffe-6254-4598-b6ef-5be747193946',
                full_name='Alex Kurtzman',
            ),
        ],
        default=[],
    )
    directors: Optional[list[PersonShort]] = Field(
        title='Directors',
        example=[
            PersonShort(
                id='fda827f8-d261-4c23-9e9c-e42787580c4d',
                full_name='Shaun Robertson',
            ),
        ],
        default=[],
    )


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
