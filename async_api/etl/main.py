import time
from datetime import datetime, timezone

from configs import es_config, loguru_config, pg_config, settings_config
from indexes import ALL_INDEXES
from load import ElasticsearchLoader
from loguru import logger
from psql_extractor import PostgresExtractor
from sql_queries import ALL_SQL_QUERIES
from state import JsonFileStorage, State
from transform import DataTransformer

logger.add(**loguru_config)


class ETL:
    """
    A class that performs an ETL process by extracting data from Postgres, transforming it,
    and loading it into Elasticsearch.
    """

    def __init__(self):
        self.psql = PostgresExtractor(dsn=pg_config.dsn, all_queries=ALL_SQL_QUERIES)
        self.es = ElasticsearchLoader(es_url=es_config.url)
        self.transform = DataTransformer()
        self.state = State(JsonFileStorage(settings_config.STATE_FILE_NAME))

    def load_all_data(self, index_name: str) -> None:
        """
        Load data from Postgres to Elasticsearch
        """

        last_state = self.state.get_state(f'{index_name}_updated_at') or datetime.min
        count = 0
        try:
            for movies_data in self.psql.get_movies_data(last_state, index_name):
                self.state.set_state(
                    f'{index_name}_updated_at', datetime.now(timezone.utc).isoformat()
                )
                es_movies = self.transform.transform_movies_data(
                    movies_data, index_name
                )
                self.es.load_movies_data(es_movies, index_name),
                count += len(es_movies)
            logger.info(
                'Successfully transferred {} documents to Elasticsearch.', count
            )
        except Exception as e:
            logger.error('An error occurred while transferring data. Error: {}.', e)
            raise

    def run(self):
        while True:
            try:
                self.psql.connect_to_postgres()
                self.es.connect_to_elastic()
                for index_name in ALL_INDEXES:
                    self.es.create_index(index_name)
                    self.load_all_data(index_name)
            except Exception as e:
                logger.error('An error occurred during ETL process. Error: {}.', e)
            finally:
                self.psql.cursor.close()
                self.psql.connection.close()
                time.sleep(settings_config.FREQUENCY)


if __name__ == "__main__":
    etl = ETL()
    etl.run()
