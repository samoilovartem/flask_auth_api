import os

from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestSettings(BaseSettings):
    REDIS_HOST: str = Field('localhost', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    ES_HOST: str = Field('localhost', env='ES_HOST')
    ES_PORT: int = Field(9200, env='ES_PORT')
    ES_INDEX: str = Field('movies', env='ES_INDEX')
    ES_ID_FIELD: str = Field('id', env='ES_ID_FIELD')
    ES_INDEX_MAPPING: dict = Field({}, env='ES_INDEX_MAPPING')

    SERVICE_HOST: str = Field('localhost', env='NGINX_HOST')
    SERVICE_PORT: int = Field(80, env='NGINX_PORT')

    MAX_RETRIES: int = Field(5, env='MAX_RETRIES')

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')


test_settings = TestSettings()
