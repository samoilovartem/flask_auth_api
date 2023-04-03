from datetime import datetime
from typing import Generator

import psycopg2
from backoff import expo, on_exception
from configs import loguru_config, settings_config
from loguru import logger
from psycopg2 import DatabaseError, OperationalError, ProgrammingError
from psycopg2.extras import RealDictCursor

logger.add(**loguru_config)


class PostgresExtractor:
    """
    A class that extracts data from a Postgres database using a provided SQL query.
    """

    def __init__(self, dsn: str, all_queries: dict[str]):
        self.cursor = None
        self.connection = None
        self.dsn = dsn
        self.all_queries = all_queries

    @on_exception(
        expo, OperationalError, max_tries=settings_config.MAX_TRIES, logger=logger
    )
    def connect_to_postgres(self) -> None:
        """
        Connects to PostgreSQL using the provided DSN.
        """

        logger.info('Attempting to connect to PostgreSQL')
        self.connection = psycopg2.connect(dsn=self.dsn, cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()
        logger.info('The connection with PostgreSQL has been established')

    @on_exception(
        expo,
        (DatabaseError, ProgrammingError),
        max_tries=settings_config.MAX_TRIES,
        logger=logger,
    )
    def get_movies_data(
        self,
        latest_updated_at: datetime,
        index_name: str,
        chunk_size: int = settings_config.CHUNK_SIZE,
    ) -> Generator:
        """
        Retrieves movies data from PostgreSQL using the provided SQL query.
        """

        self.cursor.execute(
            query=self.all_queries[index_name], vars=(latest_updated_at,)
        )
        while True:
            rows = self.cursor.fetchmany(chunk_size)
            logger.info(
                'Fetched {} rows of index "{}" from PostgreSQL', len(rows), index_name
            )
            if not rows:
                break
            yield rows
