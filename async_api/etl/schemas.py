from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, PostgresDsn
from pydantic.env_settings import BaseSettings


class PostgresConfig(BaseSettings):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DB: str

    class Config:
        env_prefix = 'POSTGRES_'

    @property
    def dsn(self) -> str:
        return PostgresDsn.build(
            scheme='postgresql',
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=str(self.PORT),
            path=f'/{self.DB}',
        )

    @property
    def url(self) -> str:
        return str(self.dsn)


class ElasticsearchConfig(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'ES_'

    @property
    def url(self) -> str:
        return f'{self.HOST}:{self.PORT}'


class CustomSettings(BaseSettings):
    CHUNK_SIZE: int = Field(200)
    FREQUENCY: int = Field(60)
    STATE_FILE_NAME: str = Field('movies_state.json')
    INDEX_NAME: str = Field('movies')
    MAX_TRIES = int = Field(5)


class ShortPersonData(BaseModel):
    id: UUID
    full_name: str


class FullPersonData(ShortPersonData):
    roles: list[str] = Field(default_factory=list)
    movies_ids: list[UUID] = Field(default_factory=list)


class GenreData(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None


class MovieData(BaseModel):
    id: UUID
    imdb_rating: Optional[float] = Field(default=None, ge=0, le=10)
    type: str
    creation_date: Optional[date] = None
    genres: list[GenreData]
    title: str
    file_path: Optional[str] = None
    description: Optional[str] = None
    directors_names: list[str] = []
    actors_names: list[str] = []
    writers_names: list[str] = []
    directors: list[ShortPersonData] = []
    actors: list[ShortPersonData] = []
    writers: list[ShortPersonData] = []
