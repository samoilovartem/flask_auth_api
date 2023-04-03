from dotenv import find_dotenv, load_dotenv
from schemas import CustomSettings, ElasticsearchConfig, PostgresConfig

load_dotenv(find_dotenv())

pg_config = PostgresConfig()

es_config = ElasticsearchConfig()

settings_config = CustomSettings()

loguru_config = {
    'sink': './logs/etl.log',
    'format': '{time:MMMM D, YYYY > HH:mm:ss} | {message} | {level}',
    'level': 'INFO',
    'rotation': '00:00',
}
