import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router
from core.config import Config
from core.custom_logger import CustomLogger
from databases.elastic import es_manager
from databases.redis import redis_manager

logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.PROJECT_NAME,
    description=Config.PROJECT_DESCRIPTION,
    version=Config.PROJECT_VERSION,
    license_info=Config.PROJECT_LICENSE,
    docs_url=Config.PROJECT_DOCS_URL,
    openapi_url=Config.PROJECT_OPENAPI_URL,
    openapi_tags=Config.PROJECT_OPENAPI_TAGS,
    default_response_class=ORJSONResponse,
    logger=CustomLogger.make_logger(),
)


@app.on_event('startup')
async def startup():
    await asyncio.gather(
        redis_manager.redis_connect(),
        es_manager.elastic_connect(),
    )


@app.on_event('shutdown')
async def shutdown():
    await asyncio.gather(
        redis_manager.redis_disconnect(),
        es_manager.elastic_disconnect(),
    )


app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
    )
