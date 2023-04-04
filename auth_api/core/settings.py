import os

from pydantic import BaseModel, BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FlaskSettings(BaseModel):
    debug: bool = Field(False, env='FLASK_DEBUG')
    secret_key: str = Field(env='FLASK_SECRET_KEY')


class SQLAlchemySettings(BaseModel):
    database_uri: str = Field(env='SQLALCHEMY_DATABASE_URI')


class RedisSettings(BaseModel):
    host: str = Field('localhost', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')


class JWTSettings(BaseModel):
    secret_key: str = Field(env='FLASK_SECRET_KEY')
    access: int = Field(15, env='JWT_ACCESS_EXPIRES')
    refresh: int = Field(32312, env='JWT_REFRESH_EXPIRES')


class OAuthProviderSettings(BaseModel):
    pass


class OAuthSettings(BaseModel):
    yandex: OAuthProviderSettings
    google: OAuthProviderSettings
    vk: OAuthProviderSettings


class Settings(BaseSettings):
    flask: FlaskSettings
    sqlalchemy: SQLAlchemySettings
    redis: RedisSettings
    jwt: JWTSettings
    oauth: OAuthSettings

    class Config:
        env_file = os.path.join(BASE_DIR, '..', '.env')


settings = Settings()
