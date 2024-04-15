from typing import Optional

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    page_size: int = 10


settings = Settings()
app = FastAPI()


@app.get("/search/")
async def read_items(user_id: Optional[str], query: str, min_publish_time: int, page: int):
    client = Elasticsearch("http://localhost:9200/")
    resp = client.search(
        index="articles",
        from_=page * settings.page_size,
        size=settings.page_size,
        body={"query": {"match": {"content": query}}},
    )
    result = []
    for hit in resp['hits']['hits']:
        result.append(hit['_source'])
    return result