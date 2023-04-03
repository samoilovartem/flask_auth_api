from abc import ABC, abstractmethod
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel


class Database(ABC):
    @abstractmethod
    async def get_by_id(
        self, id: UUID, model: BaseModel, es_index: str
    ) -> BaseModel | None:
        pass

    @abstractmethod
    async def search(
        self,
        search_string: str,
        search_field: str,
        page_number: int,
        page_size: int,
        es_index: str,
        model: BaseModel,
    ) -> list[BaseModel]:
        pass

    @abstractmethod
    async def get_list(
        self,
        page_number: int,
        page_size: int,
        es_index: str,
        model: BaseModel,
        query: dict = None,
    ) -> list[BaseModel]:
        pass


class ElasticSearch(Database):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(
        self, id: UUID, model: BaseModel, es_index: str
    ) -> BaseModel | None:
        try:
            doc = await self.elastic.get(index=es_index, id=id)
        except NotFoundError:
            return None
        return model(**doc['_source'])

    async def search(
        self,
        search_string: str,
        search_field: str,
        page_number: int,
        page_size: int,
        es_index: str,
        model: BaseModel,
    ) -> list[BaseModel]:
        body = {"from": page_number * page_size, "size": page_size}
        query = {
            "query": {
                "match": {search_field: {"query": search_string, "fuzziness": "auto"}}
            }
        }
        doc = await self.elastic.search(index=es_index, body=body | query)
        return [model(**d['_source']) for d in doc['hits']['hits']]

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        es_index: str,
        model: BaseModel,
        query: dict = None,
    ) -> list[BaseModel]:
        body = {"from": page_number * page_size, "size": page_size}
        if query:
            body = body | query
        docs = await self.elastic.search(index=es_index, body=body)
        return [model(**d['_source']) for d in docs['hits']['hits']]
