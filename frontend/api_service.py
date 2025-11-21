import requests
import streamlit as st

# Mantenha a URL base configurável
BASE_URL = "http://127.0.0.1:8000"


def fetch_catalog_metadata():
    """Busca gêneros e faixas de preço (simuladas) do backend."""
    # Supondo que o backend tenha um endpoint /metadata
    try:
        response = requests.get(f"{BASE_URL}/metadata", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Fallback para o caso de o backend não estar rodando
        st.error(f"Erro ao buscar metadados do catálogo: {e}. Usando dados simulados.")
        return {
            "categories": [
                "Fiction",
                "Fantasy",
                "Science Fiction",
                "Biography",
                "Thriller",
                "Poetry",
            ],
            "price_range": [10.0, 100.0],
        }


class ApiService:
    """Gerencia a comunicação com o Backend e o estado da aplicação."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Inicializa as variáveis de estado do Streamlit na primeira execução."""
        if "initialized" not in st.session_state:
            st.session_state.user_id = None
            st.session_state.recommendations = []
            st.session_state.metrics_result = None

            # Carrega dados do catálogo (gêneros e faixas de preço)
            st.session_state.catalog_data = fetch_catalog_metadata()
            st.session_state.initialized = True

    def simulate_user_api(self, categories, price_range):
        """Cria/Simula um novo usuário para o cold start."""
        try:
            response = requests.post(
                f"{self.base_url}/simulate",
                json={
                    "categories": categories,
                    "price_min": price_range[0],
                    "price_max": price_range[1],
                },
                timeout=90,
            )
            response.raise_for_status()
            return response.json().get("user_id")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao simular usuário: {e}")
            return None

    def fetch_recommendations(self, user_id, n):
        """Busca recomendações personalizadas com base no perfil."""
        try:
            response = requests.get(
                f"{self.base_url}/recomendar",
                params={"user_id": user_id, "n": n},
                timeout=90,
            )
            response.raise_for_status()
            return response.json().get("recommendations", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao buscar recomendações: {e}")
            return []

    def fetch_metrics(self, user_id, n):
        """Busca Precision, Recall e F1-score do backend."""
        try:
            response = requests.get(
                f"{self.base_url}/metrics",
                params={"user_id": user_id, "n": n},
                timeout=90,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao calcular métricas: {e}")
            return None

    def rate_item(self, user_id, item_id, rating: int):
        """Envia o rating (1=like, 0=dislike) e força a atualização do perfil."""
        try:
            response = requests.post(
                f"{self.base_url}/rate",
                json={"user_id": user_id, "item_id": item_id, "rating": rating},
                timeout=90,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao enviar avaliação: {e}")
            return False

    def clear_session(self):
        """Limpa todo o estado da sessão."""
        st.session_state.clear()
        st.rerun()
