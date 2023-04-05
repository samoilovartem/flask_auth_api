import os

from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    flask_debug: bool = Field(False, env='FLASK_DEBUG')
    flask_secret_key: str = Field('secret_key', env='FLASK_SECRET_KEY')

    sqlalchemy_database_uri: str = Field(env='SQLALCHEMY_DATABASE_URI')

    postgres_db: str = Field('postgresql://app:123qwe@localhost/movies_auth', env='POSTGRES_DB')

    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    jwt_secret_key: str = Field(env='FLASK_SECRET_KEY')
    jwt_access: int = Field(15, env='JWT_ACCESS_EXPIRES')
    jwt_refresh: int = Field(32312, env='JWT_REFRESH_EXPIRES')

    class Config:
        env_file = os.path.join(BASE_DIR, '..', '.env')


settings = Settings()
