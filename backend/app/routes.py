from fastapi import APIRouter, Depends
from .controllers import (
    BookController,
    UserController,
    RecommendationController,
    get_recommendation_service,
)
from .models import SimulateRequest, ItemRating
from .services import RecommendationService

router = APIRouter()

# Instâncias dos Controllers (sem estado)
book_controller = BookController()
user_controller = UserController()
rec_controller = RecommendationController()

# --- Rotas de Consulta ---


@router.get("/metadata")
def get_metadata():
    return book_controller.get_metadata()


@router.get("/categories")
def get_categories():
    return book_controller.get_all_categories()


# --- Rotas de Ação/Recomendação ---


@router.post("/simulate")
def simulate_user(
    body: SimulateRequest,
    service: RecommendationService = Depends(get_recommendation_service),
):
    # Retorna o ID de usuário simulado e as recomendações iniciais do Cold Start
    return user_controller.simulate_user(body, service)


@router.post("/rate")
def rate_item(rating_data: ItemRating):
    # NOTA: Em um sistema FBC puro, isso apenas atualizaria o perfil do usuário na sessão/DB,
    # mas aqui, faremos a FBC usar a avaliação na próxima rodada.
    return user_controller.rate_item(rating_data)


@router.get("/recomendar")
def get_recommendations(
    user_id: int,
    n: int,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return rec_controller.get_recommendations(user_id, n, service)


# --- Rotas de Avaliação ---


@router.get("/metrics")
def get_metrics(
    user_id: int,
    n: int,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return rec_controller.get_metrics(user_id, n, service)
