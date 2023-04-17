import os

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(find_dotenv())


class Settings(BaseSettings):
    flask_host: str = Field('0.0.0.0', env='FLASK_HOST')
    flask_port: int = Field(5000, env='FLASK_PORT')
    flask_debug: bool = Field(False, env='FLASK_DEBUG')
    flask_secret_key: str = Field('secret_key', env='FLASK_SECRET_KEY')

    sqlalchemy_database_uri: str = Field(env='SQLALCHEMY_DATABASE_URI')
    sqlalchemy_track_modifications: bool = Field(
        False, env='SQLALCHEMY_TRACK_MODIFICATIONS'
    )

    postgres_db: str = Field(
        'postgresql://app:123qwe@localhost/movies_auth', env='POSTGRES_DB'
    )
    postgres_schema: str = Field('content', env='POSTGRES_SCHEMA')

    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    jwt_secret_key: str = Field(env='FLASK_SECRET_KEY')
    jwt_access: int = Field(15, env='JWT_ACCESS_EXPIRES')
    jwt_refresh: int = Field(32312, env='JWT_REFRESH_EXPIRES')

    security_password_salt: str = Field(env='SECURITY_PASSWORD_SALT')
    security_password_hash: str = Field(env='SECURITY_PASSWORD_HASH')

    google_auth_client_id: str = Field(env='GOOGLE_AUTH_CLIENT_ID')
    google_auth_secret: str = Field(env='GOOGLE_AUTH_SECRET')

    admin_default_username: str = Field(env='ADMIN_DEFAULT_USERNAME')
    admin_default_password: str = Field(env='ADMIN_DEFAULT_PASSWORD')

    jaeger_host: str = Field('localhost', env='JAEGER_HOST')
    jaeger_port: int = Field(6831, env='JAEGER_PORT')

    documentation_path: str = os.path.join(BASE_DIR, 'design', 'openapi.yaml')

    class Config:
        env_file = os.path.join(BASE_DIR, '..', '.env')


settings = Settings()
