import time
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware

from .models import UserFeedback
from .users_preferences_handling import load_user_preferences, get_updated_user_preferences, save_user_preferences


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

@app.get("/recomend")
async def search(user_id: Optional[str], page: int):
    tic = time.time()
    client = Elasticsearch("http://localhost:9200/")
    print("_________________!22222222222222222222222222222222222")

    user_preferences = load_user_preferences(user_id)

    print("_________________!11111111111111111111111111111111111111")
    query = {
        "query": {
            "more_like_this": {
                "fields": [ "content"],  # Fields to consider
                "like": [
                    {
                        "_index": "articles",
                        "_id": doc_id
                    }
                    for doc_id in user_preferences.liked_articles_ids
                ],
                "unlike": [
                    {
                        "_index": "articles",
                        "_id": doc_id
                    }
                    for doc_id in user_preferences.disliked_articles_ids
                ],
                "min_term_freq": 1,  # Minimum term frequency
                "min_doc_freq": 1,  # Minimum document frequency
                "include": True  # Include the liked document in the results
            }
        }
    }
    print("here1")

    # Execute the query
    resp = client.search(index="articles", body=query)
    print("here2")

    toc = time.time()
    delay_secs = toc - tic
    # Process the result
    result = {
        'hits': [],
        'num_results': resp['hits']['total']['value'],
        'delay_secs': delay_secs,
    }
    print( len(resp['hits']['hits']))
    for hit in resp['hits']['hits']:
        article_id = hit['_id']
        if article_id not in user_preferences.disliked_articles_ids:
            article = {
                'article_id': article_id,
                'liked': (article_id in user_preferences.liked_articles_ids),
                'disliked': (article_id in user_preferences.disliked_articles_ids),
            }
            article |= hit['_source']
            result['hits'].append(article)
    return result


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
    user_preferences = load_user_preferences(user_id)
    for hit in resp['hits']['hits']:
        article_id = hit['_id']
        if article_id in user_preferences.liked_articles_ids:
            print(article_id)
        article = {
            'article_id': article_id,
            'liked': (article_id in user_preferences.liked_articles_ids),
            'disliked': (article_id in user_preferences.disliked_articles_ids),
        }
        article |= hit['_source']
        result['hits'].append(article)
    return result


@app.post("/provideFeedback")
async def provide_feedback(user_feedback: UserFeedback):
    user_preferences = load_user_preferences(user_feedback.user_id)
    updated_user_preferences = get_updated_user_preferences(user_preferences, user_feedback)
    save_user_preferences(user_feedback.user_id, updated_user_preferences)
    return True
