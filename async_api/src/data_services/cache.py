import json

from abc import ABC, abstractmethod
from uuid import UUID

from aioredis import Redis
from pydantic import BaseModel, parse_raw_as
from pydantic.json import pydantic_encoder


class Cache(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID, model: BaseModel) -> BaseModel | None:
        pass

    @abstractmethod
    async def put_by_id(self, id: UUID, model: BaseModel, cache_timeout: int) -> None:
        pass

    @abstractmethod
    async def get_list(self, key: str, model: BaseModel) -> list[BaseModel] | None:
        pass

    @abstractmethod
    async def put_list(
        self, key: str, data_list: list[BaseModel], cache_timeout: int
    ) -> None:
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_by_id(self, id: UUID, model: BaseModel) -> BaseModel | None:
        data = await self.redis.get(key=str(id))
        if not data or data == b'{}':
            return None
        return model.parse_raw(data)

    async def put_by_id(self, id: UUID, model: BaseModel, cache_timeout: int) -> None:
        await self.redis.set(
            key=str(id), value=model.json() if model else '{}', expire=cache_timeout
        )

    async def get_list(self, key: str, model: BaseModel) -> list[BaseModel] | None:
        data = await self.redis.get(key)
        if not data:
            return None
        return parse_raw_as(list[model], data)

    async def put_list(
        self, key: str, data_list: list[BaseModel], cache_timeout: int
    ) -> None:
        list_json = json.dumps(data_list, default=pydantic_encoder)
        await self.redis.set(key=str(key), value=list_json, expire=cache_timeout)
