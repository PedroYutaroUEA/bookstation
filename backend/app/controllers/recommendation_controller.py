from app.services import RecommendationService


class RecommendationController:
    """Controller para gerar e retornar recomendações FBC."""

    def get_recommendations(self, user_id: int, n: int, service: RecommendationService):
        # Verifica se o usuário existe, se não, cria um perfil zero
        return service.recommend_items(user_id)

    def get_metrics(self, user_id: int, n: int, service: RecommendationService):
        # Lógica de controle: Chama o Service para o cálculo de métricas
        return service.calculate_metrics(user_id, n)
