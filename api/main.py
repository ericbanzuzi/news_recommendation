import time
import string
import textdistance
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware

from .models import UserFeedback
from .users_preferences_handling import load_user_preferences, get_updated_user_preferences, save_user_preferences


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


def clean_text(line):
    exclude = set(string.punctuation)
    line = ''.join(ch for ch in line if (ch not in exclude and not ch.isdigit()))
    return line.split()


@app.get("/search")
async def search(user_id: str, page: int, query: Optional[str] = None, days_back: Optional[int] = None):
    tic = time.time()
    must_queries: List[dict] = []
    if query is not None:
        must_queries.append({"match": {"content": query}})
    if days_back is not None:
        min_publish_datetime = datetime.fromtimestamp(int(time.time()) - days_back * 24 * 60 * 60, tz=timezone.utc)
        must_queries.append({"range": {"date": {"gte": min_publish_datetime.isoformat()}}})
    user_preferences = load_user_preferences(user_id)
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
    resp = client.search(
        index=index_name,
        from_=page * settings.page_size,
        size=settings.page_size,
        body=body,
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
        article = {
            'article_id': article_id,
            'liked': (article_id in user_preferences.liked_articles_ids),
            'disliked': (article_id in user_preferences.disliked_articles_ids),
        }
        article |= hit['_source']
        result['hits'].append(article)
    if query is not None and not result['hits']:
        return correct_spelling(query, client, user_id, tic)
    return result


@app.post("/provideFeedback")
async def provide_feedback(user_feedback: UserFeedback):
    user_preferences = load_user_preferences(user_feedback.user_id)
    updated_user_preferences = get_updated_user_preferences(user_preferences, user_feedback)
    save_user_preferences(user_feedback.user_id, updated_user_preferences)
    return True


def most_similar_words(word, word_list, top_n=5):
    similarities = [(w, textdistance.levenshtein.normalized_similarity(word, w)) for w in word_list]
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return sorted_similarities[:top_n]


def correct_spelling(query, client, user_id, tic):
    # Search for similar terms using a fuzzy query
    #
    res = client.search(
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

    toc = time.time()
    delay_secs = toc - tic
    if res['hits']['total']['value'] > 0:
        recommendations = []
        recommendations = {
            'hits': [],
            'num_results': res['hits']['total']['value'],
            'delay_secs': delay_secs,
            'spelling_suggestions': []
        }
        user_preferences = load_user_preferences(user_id)
        for hit in res['hits']['hits']:
            article_id = hit['_id']
            article = {
                'article_id': article_id,
                'liked': (article_id in user_preferences.liked_articles_ids),
                'disliked': (article_id in user_preferences.disliked_articles_ids),
            }
            article |= hit['_source']
            recommendations['hits'].append(article)
        spelling_suggestions = []
        for suggestion in res['hits']['hits']:
            spelling_suggestions.extend(clean_text(suggestion['_source']['content']))
        # spelling_suggestions = clean_text(res['hits']['hits'][0]['_source']['content'])
        # #recommendations, spelling_suggestions = correct_spelling(query, client, user_id)
        suggestions = set(spelling_suggestions)

        word_list = [word for word in suggestions if word]
        word_list = set(word_list)
        similar_words = most_similar_words(query, word_list)

        suggestions = []
        for word, score in similar_words[:max(len(similar_words), 3)]:
            suggestions.append(word)
        recommendations['spelling_suggestions'] = suggestions
        return recommendations
        # return recommendations, res['hits']['hits'][0]['_source']['content'].split()
    else:
        return None
