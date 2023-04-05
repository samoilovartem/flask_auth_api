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
from models.schemas import MovieDetail
from services.common import MovieCommonService


class MovieService(MovieCommonService):
    """
    Class representing the movie service that inherits from the MovieCommonService class. It implements methods to
    retrieve movies from the database and cache, such as retrieving movies by id or by search, retrieving a list of
    sorted movies, retrieving a list of similar movies, and retrieving a list of popular movies by genre.
    """

    def __init__(self, cache: Cache, database: Database):
        super().__init__(cache, database)
        self.es_index = 'movies'
        self.model = MovieDetail

    async def get_movie_by_id(self, movie_id: UUID) -> Optional[MovieDetail]:
        """
        Retrieve a movie detail by its unique id from the database and cache.
        """
        return await self.get_by_id(
            id=movie_id,
            model=self.model,
            es_index=self.es_index,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_movies_by_search(
        self, search_string: str, page_number: int, page_size: int
    ) -> list[BaseModel]:
        """
        Retrieve a list of movies by search from the database and cache.
        """
        return await self.get_by_search(
            search_string=search_string,
            search_field='title',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_sorted_movies(
        self,
        page_number: int,
        page_size: int,
        sort_field: str,
        sort_type: str,
        genre_id: UUID,
    ) -> list[BaseModel] | None:
        """
        Retrieve a list of sorted movies from the database and cache.
        """
        return await self.get_sorted_list(
            sort_type=sort_type,
            sort_field=sort_field,
            page_number=page_number,
            page_size=page_size,
            genre_id=genre_id,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_similar_movies(
        self,
        movie_id: UUID,
    ) -> Optional[list[MovieDetail]]:
        """
        Retrieve a list of similar movies from the database and cache.
        """
        return await self.get_similar_list(
            movie_id=movie_id,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_popular_movies_by_genre(self, genre_id: UUID) -> list[BaseModel]:
        """
        Retrieve a list of popular movies by genre from the database and cache.
        """
        return await super().get_list_of_popular_movies_by_genre(
            genre_id=genre_id,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )


@lru_cache()
def get_service(
    redis: Redis = Depends(redis_manager.get_redis),
    elastic: AsyncElasticsearch = Depends(es_manager.get_elastic),
) -> MovieService:
    """
    Retrieve a MovieService object with a RedisCache and an ElasticSearch instance as dependencies.
    """
    redis_cache = RedisCache(redis)
    async_elastic_search = ElasticSearch(elastic)
    return MovieService(cache=redis_cache, database=async_elastic_search)
