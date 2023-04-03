from backoff import expo, on_exception
from configs import loguru_config, settings_config
from elasticsearch import (
    ConnectionTimeout,
    Elasticsearch,
    RequestError,
    SerializationError,
    TransportError,
)
from elasticsearch.helpers import bulk
from indexes import ALL_INDEXES
from loguru import logger
from schemas import MovieData

logger.add(**loguru_config)


class ElasticsearchLoader:
    """
    A class to load data into Elasticsearch.
    """

    def __init__(self, es_url: str):
        self.connection = None
        self.es_url = es_url

    @on_exception(
        expo,
        (ConnectionError, TransportError, ConnectionTimeout),
        max_tries=settings_config.MAX_TRIES,
        logger=logger,
    )
    def connect_to_elastic(self) -> None:
        """
        Connects to Elasticsearch.
        """

        logger.info('Attempting to connect to Elasticsearch')
        self.connection = Elasticsearch(hosts=[self.es_url])
        logger.info('The connection with Elasticsearch has been established')

    @on_exception(
        expo, RequestError, max_tries=settings_config.MAX_TRIES, logger=logger
    )
    def create_index(self, index_name: str) -> None:
        """
        Creates the Elasticsearch index if it doesn't exist.
        """

        if not self.connection.indices.exists(index=index_name):
            response = self.connection.indices.create(
                index=index_name, body=ALL_INDEXES[index_name], ignore=400
            )
            logger.info(
                'Created index "{}". Response from Elasticsearch: {}',
                index_name,
                response,
            )

    @on_exception(
        expo, SerializationError, max_tries=settings_config.MAX_TRIES, logger=logger
    )
    def load_movies_data(self, data: list[MovieData], index_name: str) -> None:
        """
        Loads data into Elasticsearch.
        """

        actions = [
            {'_index': index_name, '_id': row.id, '_source': row.dict()} for row in data
        ]
        bulk(self.connection, actions=actions)
        logger.info('Loaded {} documents to Elasticsearch.', len(data))
