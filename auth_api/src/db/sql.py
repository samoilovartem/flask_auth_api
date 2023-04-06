from core.settings import settings
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DDL, MetaData, create_engine

db = SQLAlchemy(metadata=MetaData(schema=settings.postgres_schema))
migration = Migrate()


def create_schema_if_not_exists(database_uri, schema_name):
    engine = create_engine(database_uri)
    create_schema = DDL(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    with engine.begin() as connection:
        connection.execute(create_schema)
