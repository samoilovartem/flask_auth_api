from contextlib import contextmanager

from core.settings import settings
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DDL, MetaData, create_engine


class DatabaseManager:
    def __init__(self):
        self.db = SQLAlchemy(metadata=MetaData(schema=settings.postgres_schema))
        self.migration = Migrate()

    @staticmethod
    def create_schema_if_not_exists(database_uri, schema_name):
        engine = create_engine(database_uri)
        create_schema = DDL(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')
        with engine.begin() as connection:
            connection.execute(create_schema)

    @contextmanager
    def transaction(self):
        """
        Provide a transactional scope for database operations.
        Commits the transaction if no exceptions occur, otherwise rolls back.

        Usage:

        with database_manager.transaction():
            # Perform database operations here
        """
        try:
            yield self.db.session
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            raise


db_manager = DatabaseManager()
