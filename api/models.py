from enum import Enum
from typing import List

from pydantic import BaseModel


class UserFeedbackAction(Enum):
    ADD_LIKE = 'add_like'
    DELETE_LIKE = 'delete_like'
    ADD_DISLIKE = 'add_dislike'
    DELETE_DISLIKE = 'delete_dislike'


class UserFeedback(BaseModel):
    user_id: str
    article_id: str
    action: UserFeedbackAction


class UserPreferences(BaseModel):
    liked_articles_ids: List[str]
    disliked_articles_ids: List[str]
