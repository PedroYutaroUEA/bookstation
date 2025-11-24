from app.models import SimulateRequest, load_ratings, ItemRating
from app.services import RecommendationService


class UserController:
    """Controller para simulação de usuário e lógica de cold start."""

    def simulate_user(self, body: SimulateRequest, service: RecommendationService):
        # NOTA: O FBC não precisa de um novo ID de usuário, mas sim de um perfil temporário.
        # Aqui, apenas retornamos um novo ID (o próximo do ratings) para simulação.
        ratings = load_ratings()
        print(f"[BACKEND - UserController]: ratings: {ratings}")
        new_id = ratings["user_id"].max() + 1 if not ratings.empty else 1

        # Lógica de Cold Start: Retorna livros filtrados pelos atributos iniciais
        recommendations = service.get_initial_recommendations(
            body.categories, body.price_min, body.price_max
        )

        # Para a demonstração, o backend retornará as recomendações iniciais diretamente
        res = {"user_id": int(new_id), "recommendations": recommendations}
        print(f"[BACKEND - UserController]: response: {res}")
        return res

    def rate_item(self, rating_data: ItemRating):
        # NOTA: Em produção, isso iria para o DB. Aqui, apenas salvamos o perfil
        # para que o próximo cálculo FBC use o item como 'liked'
        pass
