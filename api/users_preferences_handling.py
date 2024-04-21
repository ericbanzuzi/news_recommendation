import os

from .models import UserFeedbackAction, UserFeedback, UserPreferences


USERS_PREFERENCES_DIR_PATH = 'users_preferences'


def load_user_preferences(user_id: str) -> UserPreferences:
    user_preferences_file_path = os.path.join(USERS_PREFERENCES_DIR_PATH, f'{user_id}.json')
    if os.path.isfile(user_preferences_file_path):
        with open(user_preferences_file_path, encoding='utf-8') as f:
            user_preferences = UserPreferences.model_validate_json(f.read())
    else:
        user_preferences = UserPreferences(liked_articles_ids=[], disliked_articles_ids=[])
    return user_preferences


def get_updated_user_preferences(user_preferences: UserPreferences, user_feedback: UserFeedback) -> UserPreferences:
    liked_articles_ids_set = set(user_preferences.liked_articles_ids)
    disliked_articles_ids_set = set(user_preferences.disliked_articles_ids)
    if user_feedback.action == UserFeedbackAction.ADD_LIKE:
        liked_articles_ids_set.add(user_feedback.article_id)
        disliked_articles_ids_set.discard(user_feedback.article_id)
    elif user_feedback.action == UserFeedbackAction.DELETE_LIKE:
        liked_articles_ids_set.discard(user_feedback.article_id)
    elif user_feedback.action == UserFeedbackAction.ADD_DISLIKE:
        disliked_articles_ids_set.add(user_feedback.article_id)
        liked_articles_ids_set.discard(user_feedback.article_id)
    elif user_feedback.action == UserFeedbackAction.DELETE_DISLIKE:
        disliked_articles_ids_set.discard(user_feedback.article_id)
    return UserPreferences(
        liked_articles_ids=list(liked_articles_ids_set),
        disliked_articles_ids=list(disliked_articles_ids_set),
    )


def save_user_preferences(user_id: str, user_preferences: UserPreferences) -> None:
    user_preferences_file_path = os.path.join(USERS_PREFERENCES_DIR_PATH, f'{user_id}.json')
    with open(user_preferences_file_path, 'w', encoding='utf-8') as f:
        f.write(user_preferences.model_dump_json(indent=2))
