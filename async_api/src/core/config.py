import os

from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DESCRIPTION = (
    'A powerful API for online cinema platforms, powered by FastAPI, PostgreSQL, and Elasticsearch. '
    'CinemaHub API provides rich search, filtering, and exploration features for movies, actors, '
    'directors, writers, and genres, enabling an immersive and interactive experience for users.'
)

LICENSE_INFO = {
    'name': 'MIT',
    'url': 'https://opensource.org/licenses/MIT',
}

PROJECT_TAGS_METADATA = [
    {
        'name': 'Movies',
        'description': 'Discover **movies** with **search**, **sorting**, **filtering**, and access **detailed '
        'information** about each movie.',
    },
    {
        'name': 'Persons',
        'description': 'Explore **actors**, **writers**, and **directors** in the movie library with **search** '
        'and access **detailed information**.',
    },
    {
        'name': 'Genres',
        'description': 'Browse a **list** of movie genres and access **detailed information** about each genre in the '
        'movie library.',
    },
]


class Config(BaseSettings):
    PROJECT_NAME: str = Field('CinemaHub API', env='PROJECT_NAME')
    PROJECT_DESCRIPTION: str = Field(PROJECT_DESCRIPTION, env='PROJECT_DESCRIPTION')
    PROJECT_VERSION: str = Field('1.0.0', env='PROJECT_VERSION')
    PROJECT_LICENSE: dict = Field(LICENSE_INFO)
    PROJECT_OPENAPI_TAGS: list[dict[str, str]] = Field(PROJECT_TAGS_METADATA)
    PROJECT_DOCS_URL: str = Field('/api/openapi', env='PROJECT_DOCS_URL')
    PROJECT_OPENAPI_URL: str = Field('/api/openapi.json', env='PROJECT_OPENAPI_URL')
    PROJECT_GLOBAL_PAGE_SIZE: int = Field(20, env='PROJECT_GLOBAL_PAGE_SIZE')

    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    REDIS_CACHE_TIMEOUT: int = Field(60 * 10, env='REDIS_CACHE_TIMEOUT')

    ES_HOST: str = Field('127.0.0.1', env='ES_HOST')
    ES_PORT: int = Field(9200, env='ES_PORT')

    POSTGRES_HOST: str = Field('db', env='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(5432, env='POSTGRES_PORT')
    POSTGRES_USER: str = Field('app', env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field('123qwe', env='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field('movies_database', env='POSTGRES_DB')

    FASTAPI_HOST: str = Field('0.0.0.0', env='FASTAPI_HOST')
    FASTAPI_PORT: int = Field(8000, env='FASTAPI_PORT')

    LOG_LEVEL: str = Field('INFO', env='LOGLEVEL')
    LOG_PATH: str = Field(os.path.join(BASE_DIR, './logs/fastapi.log'), env='LOG_PATH')
    LOG_RETENTION: str = Field('10 days', env='LOG_RETENTION')
    LOG_ROTATION: str = Field('1 day', env='LOG_ROTATION')

    MAX_RETRIES: int = Field(10, env='MAX_RETRIES')
    MIN_SIZE: int = Field(10, env='MIN_SIZE')
    MAX_SIZE: int = Field(20, env='MAX_SIZE')

    JWT_SECRET: str = Field('secret', env='JWT_SECRET')
    JWT_ALGORITHM: str = Field('HS256', env='JWT_ALGORITHM')

    AUTH_API_URL: str = Field(
        'http://localhost:80/api/v1/user/roles', env='AUTH_API_URL'
    )
    NOT_SUBSCRIBER_MAX_RATING: int = Field(6, env='NOT_SUBSCRIBER_MAX_RATING')

    class Config:
        env_file = os.path.join(BASE_DIR, '..', '.env')


Config = Config()
