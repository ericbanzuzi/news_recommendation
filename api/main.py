import time
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware

from .models import UserFeedback


class Settings(BaseSettings):
    page_size: int = 10


settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(user_id: Optional[str], query: str, days_back: int, page: int):
    tic = time.time()
    if days_back == -1:
        min_publish_datetime = datetime.fromtimestamp(0, tz=timezone.utc)
    else:
        min_publish_datetime = datetime.fromtimestamp(int(time.time()) - days_back * 24 * 60 * 60, tz=timezone.utc)
    client = Elasticsearch("http://localhost:9200/")
    resp = client.search(
        index="articles",
        from_=page * settings.page_size,
        size=settings.page_size,
        body={
            "query": {
                "bool": {
                    "must": [
                        {"match": {"content": query}},
                        {"range": {"date": {"gte": min_publish_datetime.isoformat()}}}
                    ]
                }
            }
        }
    )
    toc = time.time()
    delay_secs = toc - tic
    result = {
        'hits': [],
        'num_results': resp['hits']['total']['value'],
        'delay_secs': delay_secs,
    }
    for hit in resp['hits']['hits']:
        article = {
            'article_id': hit['_id'],
            'liked': True,
            'disliked': False,
        }
        article |= hit['_source']
        result['hits'].append(article)
    return result


@app.post("/provideFeedback")
async def provide_feedback(user_feedback: UserFeedback):
    print(user_feedback.model_dump())
    return True
