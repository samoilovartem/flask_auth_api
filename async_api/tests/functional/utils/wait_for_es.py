from backoff import expo, on_exception
from elasticsearch import Elasticsearch
from loguru import logger
from tests.functional.settings import test_settings
from tests.functional.utils.loguru_config import loguru_config

logger.add(**loguru_config)


def create_es_client(hosts, validate_cert=False, use_ssl=False):
    return Elasticsearch(hosts=hosts, validate_cert=validate_cert, use_ssl=use_ssl)


@on_exception(expo, ConnectionError, max_tries=test_settings.MAX_RETRIES)
def connect_to_es(es_client, hosts):
    logger.info('Connecting to Elasticsearch at {}...', hosts)
    es_client.ping()
    logger.success('Elasticsearch connected')


if __name__ == '__main__':
    hosts = f'{test_settings.ES_HOST}:{test_settings.ES_PORT}'
    es_client = create_es_client(hosts)
    connect_to_es(es_client, hosts)
