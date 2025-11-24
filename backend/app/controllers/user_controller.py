from app.models import SimulateRequest, load_ratings, save_ratings
from app.services import RecommendationService
from app.models.item_rating import RatingBatch
import pandas as pd


class UserController:
    def __init__(self):
        self.ratings = load_ratings()

    def simulate_user(self, body: SimulateRequest, service: RecommendationService):
        # NOTA: O FBC não precisa de um novo ID de usuário, mas sim de um perfil temporário.
        # Aqui, apenas retornamos um novo ID (o próximo do ratings) para simulação.

        print(f"[BACKEND - UserController]: ratings: {self.ratings}")
        new_id = self.ratings["user_id"].max() + 1 if not self.ratings.empty else 1

        # Lógica de Cold Start: Retorna livros filtrados pelos atributos iniciais
        recommendations = service.get_initial_recommendations(
            body.categories, body.price_min, body.price_max
        )

        # Para a demonstração, o backend retornará as recomendações iniciais diretamente
        res = {"user_id": int(new_id), "recommendations": recommendations}
        print(f"[BACKEND - UserController]: response: {res}")
        return res

    def rate_item_batch(self, batch: RatingBatch):
        """Persiste um lote de avaliações no ratings.csv."""

        new_ratings = []
        for r in batch.ratings:
            # 1. Verificar duplicidade (opcional, mas bom para garantir)
            # Para simplificar, vamos apenas adicionar, mas em um sistema real faríamos um merge

            new_ratings.append(
                {
                    "user_id": r.user_id,  # Usando o nome correto da coluna
                    "item_id": r.item_id,
                    "rating": r.rating,  # Usando o nome correto da coluna
                }
            )

        if new_ratings:
            new_df = pd.DataFrame(new_ratings)
            ratings = pd.concat([self.ratings, new_df], ignore_index=True)
            save_ratings(ratings)

        return {"status": "success", "count": len(new_ratings)}
