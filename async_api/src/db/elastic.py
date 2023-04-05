from typing import Optional

from backoff import expo, on_exception
from core.config import Config
from core.custom_logger import CustomLogger
from elasticsearch import AsyncElasticsearch, ConnectionError

logger = CustomLogger.make_logger()


class ElasticsearchManager:
    _instance: Optional['ElasticsearchManager'] = None

    def __new__(cls) -> 'ElasticsearchManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._es: Optional[AsyncElasticsearch] = None

    async def get_elastic(self) -> AsyncElasticsearch:
        if self._es is None:
            await self.elastic_connect()
        return self._es

    @on_exception(expo, ConnectionError, max_tries=Config.MAX_RETRIES)
    async def elastic_ping(self):
        result = await self._es.ping()
        if not result:
            raise ConnectionError('Elasticsearch is not responding.')

    async def elastic_connect(self):
        if self._es is None:
            logger.info('Check connection to elasticsearch server.')
            self._es = AsyncElasticsearch(hosts=[f'{Config.ES_HOST}:{Config.ES_PORT}'])
            await self.elastic_ping()
            logger.info('Successfully connected to elasticsearch.')

    async def elastic_disconnect(self):
        if self._es is not None:
            await self._es.close()
            self._es = None
            logger.info('Successfully disconnected from elasticsearch.')


es_manager = ElasticsearchManager()
