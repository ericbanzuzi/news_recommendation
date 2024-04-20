from pydantic import BaseModel


class UserFeedback(BaseModel):
    user_id: str
    article_id: str
    feedback: str
