from app.services import RecommendationService
from .book_controller import BookController
from .recommendation_controller import RecommendationController
from .user_controller import UserController


def get_recommendation_service() -> RecommendationService:
    return RecommendationService()
