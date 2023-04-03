from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from core.config import Config
from data_services.cache import Cache, RedisCache
from data_services.database import Database, ElasticSearch
from db.elastic import es_manager
from db.redis import redis_manager
from models.schemas import PersonDetail
from services.common import MovieCommonService


class PersonService(MovieCommonService):
    """
    Class representing the person service that inherits from the MovieCommonService class. It implements methods to
    retrieve persons from the database and cache, such as retrieving persons by id, by search or by list of
    persons.
    """

    def __init__(self, cache: Cache, database: Database):
        super().__init__(cache, database)
        self.es_index = 'persons'
        self.model = PersonDetail

    async def get_person_by_id(self, person_id: UUID) -> Optional[PersonDetail]:
        """
        Retrieve a person detail by its unique id from the database and cache.
        """
        return await self.get_by_id(
            id=person_id,
            model=self.model,
            es_index=self.es_index,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_persons_by_search(
        self, search_string: str, page_number: int, page_size: int
    ) -> list[BaseModel]:
        """
        Retrieve a list of persons by search from the database and cache.
        """
        return await self.get_by_search(
            search_string=search_string,
            search_field='full_name',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_persons_list(
        self, page_number: int, page_size: int
    ) -> Optional[list[PersonDetail]]:
        """
        Retrieve a list of persons from the database and cache.
        """
        return await self.get_list(
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )


@lru_cache()
def get_service(
    redis: Redis = Depends(redis_manager.get_redis),
    elastic: AsyncElasticsearch = Depends(es_manager.get_elastic),
) -> PersonService:
    """
    Retrieve a PersonService object with a RedisCache and an ElasticSearch instance as dependencies.
    """
    redis_cache = RedisCache(redis)
    async_elastic_search = ElasticSearch(elastic)
    return PersonService(cache=redis_cache, database=async_elastic_search)
