import time
import string
import textdistance
from typing import Tuple, List, Set, Optional
from datetime import datetime, timezone

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware

from .models import UserFeedback, UserPreferences  # type: ignore
from .users_preferences_handling import (  # type: ignore
    load_user_preferences, get_updated_user_preferences, save_user_preferences
)


AUTHENTICATION = False

# configure elastic correctly
if AUTHENTICATION:
    ELASTIC_PASSWORD = 'password'  # when using authentication, paste your password for elastic search here

    client = Elasticsearch(hosts=['https://localhost:9200'],
                           ca_certs='../http_ca.crt',
                           basic_auth=("elastic", ELASTIC_PASSWORD),
                           verify_certs=False)
else:
    client = Elasticsearch("http://localhost:9200/")


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
index_name = "articles"


def get_result_from_elasticsearch_response(
        elasticsearch_response,
        user_preferences: UserPreferences,
        query: Optional[str],
        tic: float,
        include_spelling_suggestions: bool,
        ) -> dict:
    result = {
        'hits': [],
        'num_results': elasticsearch_response['hits']['total']['value'],
    }
    for hit in elasticsearch_response['hits']['hits']:
        article_id = hit['_id']
        article = {
            'article_id': article_id,
            'liked': (article_id in user_preferences.liked_articles_ids),
            'disliked': (article_id in user_preferences.disliked_articles_ids),
        }
        article |= hit['_source']
        result['hits'].append(article)
    if include_spelling_suggestions:
        if query is None:
            raise RuntimeError
        result["spelling_suggestions"] = get_spelling_suggestions(
            query_word=query, suggested_articles=elasticsearch_response['hits']['hits']
        )
    result["delay_secs"] = time.time() - tic
    return result


def get_elasticsearch_search_body(
        query: Optional[str],
        days_back: Optional[int],
        user_preferences: UserPreferences,
        ) -> dict:
    must_queries: List[dict] = []
    if query is not None:
        must_queries.append({"match": {"content": query}})
    if days_back is not None:
        min_publish_datetime = datetime.fromtimestamp(int(time.time()) - days_back * 24 * 60 * 60, tz=timezone.utc)
        must_queries.append({"range": {"date": {"gte": min_publish_datetime.isoformat()}}})
    if user_preferences.liked_articles_ids:
        must_queries.append({
            "more_like_this": {
                "fields": ["content"],
                "like": [
                    {
                        "_index": index_name,
                        "_id": article_id
                    }
                    for article_id in user_preferences.liked_articles_ids
                ],
                "min_term_freq": 1,
                "min_doc_freq": 1,
                "include": True
            }
        })
    bool_query: dict = {}
    if must_queries:
        bool_query["must"] = must_queries
    if user_preferences.disliked_articles_ids:
        bool_query["must_not"] = {
            "ids": {
                "values": [
                    article_id
                    for article_id in user_preferences.disliked_articles_ids
                ]
            }
        }
    if bool_query:
        body: dict = {
            "query": {
                "bool": bool_query
            }
        }
    else:
        body = {}
    return body


@app.get("/search")
async def search(user_id: str, page: int, query: Optional[str] = None, days_back: Optional[int] = None):
    tic = time.time()
    user_preferences = load_user_preferences(user_id)
    elasticsearch_response = client.search(
        index=index_name,
        from_=page * settings.page_size,
        size=settings.page_size,
        body=get_elasticsearch_search_body(query, days_back, user_preferences),
    )
    result = get_result_from_elasticsearch_response(
        elasticsearch_response,
        user_preferences,
        query,
        tic,
        include_spelling_suggestions=False,
    )
    if query is not None and not result['hits']:
        return fuzzy_search(query, user_preferences, tic)
    return result


@app.post("/provideFeedback")
async def provide_feedback(user_feedback: UserFeedback):
    user_preferences = load_user_preferences(user_feedback.user_id)
    updated_user_preferences = get_updated_user_preferences(user_preferences, user_feedback)
    save_user_preferences(user_feedback.user_id, updated_user_preferences)
    return True


def tokenize_text(text: str) -> List[str]:
    exclude = set(string.punctuation)
    text = ''.join(ch for ch in text if (ch not in exclude and not ch.isdigit()))
    return text.split()


def get_most_similar_words(word: str, candidate_similar_words: Set[str], top_n: int) -> List[Tuple[str, float]]:
    similarities = [(w, textdistance.levenshtein.normalized_similarity(word, w)) for w in candidate_similar_words]
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return sorted_similarities[:top_n]


def get_spelling_suggestions(query_word: str, suggested_articles: List[dict]) -> List[str]:
    candidate_spelling_suggestions: Set[str] = set()
    for suggested_article in suggested_articles:
        suggested_article_tokens = tokenize_text(suggested_article['_source']['content'])
        candidate_spelling_suggestions.update(suggested_article_tokens)
    candidate_spelling_suggestions = {word for word in candidate_spelling_suggestions if word}
    most_similar_words = get_most_similar_words(query_word, candidate_spelling_suggestions, top_n=5)
    return [
        word
        for word, _ in most_similar_words
    ]


def fuzzy_search(query: str, user_preferences: UserPreferences, tic: float):
    elasticsearch_response = client.search(
        index=index_name,
        body={
            "query": {
                "fuzzy": {
                    "content": {
                        "value": query,
                        "fuzziness": "AUTO",
                    }
                }
            },
        }
    )
    return get_result_from_elasticsearch_response(
        elasticsearch_response,
        user_preferences,
        query,
        tic,
        include_spelling_suggestions=True,
    )
