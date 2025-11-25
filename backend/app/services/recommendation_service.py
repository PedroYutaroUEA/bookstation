import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score

from app.models import load_books, load_ratings
from app.config import Config


class RecommendationService:
    def __init__(self):
        self.books = load_books()
        self.ratings = load_ratings()
        self._vectorizer = None
        self._item_vectors = None
        self._initialize_fbc()

    def _initialize_fbc(self):
        """Inicializa o TF-IDF e vetoriza todos os livros."""
        if self.books.empty:
            return

        # 1. Pré-processamento: Cria uma string de conteúdo para vetorização
        # Usamos descrição e gênero
        self.books["content"] = self.books.apply(
            lambda row: f"{row['description']} {row['category']} {row['authors']}",
            axis=1,
        ).fillna("")

        # 2. Vetorização TF-IDF
        self._vectorizer = TfidfVectorizer(stop_words="english", min_df=1, max_df=0.8)
        self._item_vectors = self._vectorizer.fit_transform(self.books["content"])

        print(f"FBC Inicializado. Vetores de itens shape: {self._item_vectors.shape}")

    def build_user_profile(self, user_id: int):
        """
        Constrói o vetor de perfil do usuário a partir da média dos vetores dos itens que ele gostou.
        Se o usuário for novo, retorna um vetor vazio (zero).
        """
        # Assumimos que 'rating' 1 = Gosto
        liked_items_ids = self.ratings[
            (self.ratings["user_id"] == user_id) & (self.ratings["rating"] == 1)
        ]["item_id"].unique()

        if len(liked_items_ids) == 0:
            zeros = np.zeros(
                self._item_vectors.shape[1]
            )  # Retorna vetor zero para Cold Start
            print(
                f"[BACKEND - RecommendationService]: Usuario n gosstou de nenhum item: {zeros}"
            )
            return zeros

        # 1. Encontrar índices dos livros que o usuário gostou no vetor de itens
        item_indices = self.books[self.books["item_id"].isin(liked_items_ids)].index

        if len(item_indices) == 0:
            return np.zeros(self._item_vectors.shape[1])

        # 2. Extrair os vetores desses itens
        liked_vectors = self._item_vectors[item_indices]

        # 3. Calcular o perfil: Média dos vetores
        user_profile_vector = np.mean(liked_vectors, axis=0)
        result = np.asarray(user_profile_vector).flatten()
        return result

    def get_initial_recommendations(self, categories: list) -> list:
        """Gera recomendações baseadas nos atributos iniciais do Cold Start."""

        # Filtro de conteúdo baseado em metadados puros
        category_regex = "|".join([f"({c})" for c in categories])

        filtered_books = self.books[
            self.books["category"].str.contains(category_regex, case=False, na=False)
        ]

        print(f"[BACKEND - RecommendationService]: filtered_books: {filtered_books}")

        # Amostra aleatória dos melhores itens filtrados (Content-Based puro)
        sample_size = min(Config.MAX_RECOMMENDATIONS, len(filtered_books))
        if filtered_books.empty or sample_size == 0:
            return []

        sample = filtered_books.sample(n=sample_size).to_dict(orient="records")
        print(f"[BACKEND - RecommendationService]: sample: {sample}")
        return sample

    def recommend_items(self, user_id: int) -> list:
        """Gera recomendações com base no perfil vetorizado do usuário (FBC principal)."""

        user_profile = self.build_user_profile(user_id)
        print(f"[BACKEND - RecommendationService]: profile: {user_profile}")

        # Se o perfil é zero (usuário novo, sem likes)
        if np.all(user_profile == 0):
            # Não temos como gerar FBC, precisa do Cold Start ou likes
            print(f"[BACKEND - RecommendationService]: Retornando array vazio...")
            return []

        # 1. Calcular Similaridade: Cosseno entre o Perfil do Usuário e TODOS os itens
        # user_profile é (1, N_features), item_vectors é (N_items, N_features)

        # Otimização: Sample items para evitar calcular similaridade em todos 65k itens
        items_to_check = self.books.sample(
            n=min(Config.MAX_ITEMS_TO_CHECK, len(self.books))
        ).index

        # Calcula similaridade para os itens selecionados (mais rápido)
        item_vectors_sample = self._item_vectors[items_to_check]

        # Calcular similaridade do cosseno
        # Reshape do vetor de perfil para (1, N)
        similarity_scores = cosine_similarity(
            user_profile.reshape(1, -1), item_vectors_sample
        )

        # 2. Ranqueamento
        # Achatando o array de scores para 1D e combinando com os índices originais
        scores_df = pd.DataFrame(
            {"score": similarity_scores.flatten(), "original_index": items_to_check}
        )

        # Filtrar itens já avaliados (para não recomendar o que o usuário já viu)
        liked_ids = self.ratings[self.ratings["user_id"] == user_id]["item_id"].unique()

        # Mapeia de volta para o catálogo original e ranqueia
        recommended_indices = scores_df.sort_values(by="score", ascending=False)[
            "original_index"
        ]

        # 3. Filtragem e Seleção do Top N
        recommended_books = self.books.loc[recommended_indices]

        final_recs = recommended_books[
            ~recommended_books["item_id"].isin(liked_ids)
        ].head(Config.MAX_RECOMMENDATIONS)

        return final_recs.to_dict(orient="records")

    # --- Cálculo de Métricas ---

    def calculate_metrics(self, user_id: int, n: int) -> dict:
        """
        Calcula Precision, Recall e F1-score para o usuário-alvo.
        Usa o dataset de avaliações como Gabarito.
        """

        # 1. GABARITO (True Positives): O que o usuário realmente gostou
        # Baseado em todas as avaliações positivas (rating=1) no dataset de avaliação
        actual_likes_df = self.ratings[
            (self.ratings["user_id"] == user_id) & (self.ratings["rating"] == 1)
        ]
        actual_likes_ids = actual_likes_df["item_id"].unique()

        # Requisito Mínimo: Deve ter pelo menos 5 likes no gabarito para ter sentido
        if len(actual_likes_ids) < 5:
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
