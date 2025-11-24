import numpy as np
import math
from app.models import load_books, load_ratings
from app.config import Config


def calculate_tf_idf(term, words):
    return words.count(term) / len(words)


def cosine_similarity(vec1, vec2):
    print("oiiii")
    assert len(vec1) == len(vec2), "Ambos vetores devem ter mesma dimensão"

    dot = sum(vec1[i] * vec2[i] for i in range(len(vec1)))
    norm_1 = math.sqrt(sum(x**2 for x in vec1))
    norm_2 = math.sqrt(sum(x**2 for x in vec2))

    if norm_1 == 0 or norm_2 == 0:
        return 0.0

    return dot / (norm_1 * norm_2)


class RecommendationService:
    def __init__(self):
        self.books = load_books()
        self.ratings = load_ratings()
        self.vectors = {}
        self._initialize_fbc()

    def _initialize_fbc(self):
        """Inicializa o TF-IDF e vetoriza todos os livros."""
        if len(self.books) == 0:
            return

        # 1. Pré-processamento: Cria uma string de conteúdo para vetorização
        # Primeiramente defina as colunas de todos os termos no dataset
        todos_termos = set()
        termos_books = {}
        for item_id, book in self.books.items():
            termos = book["description"]
            termos += " " + book["category"].replace(",", " ")
            termos += " " + book["authors"].replace(",", " ").lower().replace(
                "and", " "
            )
            termos = termos.split()

            todos_termos.update(termos)
            termos_books[item_id] = termos

        # Agora transformemos em uma lista ordenada
        todos_termos = list(todos_termos)

        # 2. Vetorização TF-I
        for item_id, book in self.books.items():
            vetor = [0] * len(todos_termos)
            for termo in termos_books[item_id]:
                vetor[todos_termos.index(termo)] = calculate_tf_idf(termo, todos_termos)
            self.vectors[item_id] = vetor

        print(
            f"FBC Inicializado. Vetores de itens dimens?o: {(len(todos_termos), len(self.vectors))}"
        )

    def build_user_profile(self, user_id: int):
        """
        Constrói o vetor de perfil do usuário a partir da média dos vetores dos itens que ele gostou.
        Se o usuário for novo, retorna um vetor vazio (zero).
        """
        # 1. Extrair os vetores desses itens
        liked_vectors = []
        for item_id, rating in self.ratings[user_id]:
            # Só queremos os items avaliado positivamente
            if rating != 1:
                continue
            liked_vectors += self.vectors[item_id]

        if len(liked_vectors) == 0:
            return []

        # 2. Calcular o perfil: Média dos vetores
        user_profile_vector = np.mean(liked_vectors, axis=0)
        return user_profile_vector

    def get_initial_recommendations(
        self, categories: list, price_min: float, price_max: float
    ) -> list:
        """Gera recomendações baseadas nos atributos iniciais do Cold Start."""

        # Filtro de conteúdo baseado em metadados puros
        filtered_books = filter(
            lambda book: book["category"].split(",") in categories
            and price_min <= float(book["price"]) <= price_max,
            self.books.values(),
        )

        # Amostra aleatória dos melhores itens filtrados (Content-Based puro)
        sample_size = min(Config.MAX_RECOMMENDATIONS, len(filtered_books))
        if len(filtered_books) == 0 or sample_size == 0:
            return []

        return list(filtered_books)[: Config.MAX_RECOMMENDATIONS]

    def recommend_items(self, user_id: int) -> list:
        """Gera recomendações com base no perfil vetorizado do usuário (FBC principal)."""
        user_profile = self.build_user_profile(user_id)
        # Se o perfil é zero (usuário novo, sem likes)
        if len(user_profile) == 0:
            # Não temos como gerar FBC, precisa do Cold Start ou likes
            return []
        # Só calcule as recomendações com os vetores(items) que não foram avaliados pelo usuários para que ele não seja recomendado novamente eles
        vectors_filtered = self.vectors[:]
        for item_id, _ in self.ratings[user_id]:
            del vectors_filtered[item_id]

        # 1. Calcular Similaridade: Cosseno entre o Perfil do Usuário e TODOS os items
        sims = [
            (item_id, cosine_similarity(user_profile, vetor))
            for item_id, vetor in vectors_filtered.items()
        ]
        sims.sort(lambda x: x[1])  # Ordernar com base na similaridade

        # 2. Retornar somente os top N items
        return map(lambda x: self.books[x[0]], sims[: Config.MAX_RECOMMENDATIONS])

    # --- Cálculo de Métricas ---

    def calculate_metrics(self, user_id: int, n: int) -> dict:
        """
        Calcula Precision, Recall e F1-score para o usuário-alvo.
        Usa o dataset de avaliações como Gabarito.
        """

        # 1. GABARITO (True Positives): O que o usuário realmente gostou
        # Baseado em todas as avaliações positivas (rating=1) no dataset de avaliação
        user_likes = filter(lambda x: x[1] == 1, self.ratings[user_id])
        actual_likes_ids = map(lambda x: x[0], user_likes)

        # Requisito Mínimo: Deve ter pelo menos 5 likes no gabarito para ter sentido
        if len(user_likes) < 5:
            return {
                "f1_score": None,
                "reason": "Usuário precisa de pelo menos 5 likes no dataset de avaliações para métricas.",
            }

        # 2. PREDIÇÃO (Recomendados): O que o sistema sugere
        recommended_items = self.recommend_items(user_id)
        recommended_ids = [item["item_id"] for item in recommended_items]

        # Truncar o N para o valor exigido
        recommended_ids = recommended_ids[:n]

        # 3. CÁLCULO DAS MÉTRICAS

        # True Positives: Acertos - Itens que foram recomendados E que o usuário gostou
        true_positives = len(set(recommended_ids) & set(actual_likes_ids))

        # False Positives: Erros de Recomendação - Itens recomendados que o usuário NÃO gostou
        false_positives = len(recommended_ids) - true_positives

        # False Negatives: Oportunidades Perdidas - Itens que o usuário gostou, mas NÃO foram recomendados
        false_negatives = len(actual_likes_ids) - true_positives

        # Precision: (Acertos) / (Total de Recomendados)
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0
        )

        # Recall: (Acertos) / (Total que o usuário gostou)
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0
        )

        # F1-Score: Média Harmônica de Precision e Recall
        f1_score_val = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score_val,
            "recommended_count": len(recommended_ids),
            "actual_likes": len(actual_likes_ids),
        }
