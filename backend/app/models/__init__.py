import pandas as pd
from app.config import Config
from .item_rating import ItemRating
from .simulate_request import SimulateRequest

# --- Funções de I/O (Data Persistence) ---


def load_books():
    """Carrega o catálogo de livros."""
    try:
        return pd.read_csv(Config.ITEMS_FILE)
    except FileNotFoundError:
        print(f"Erro: Arquivo {Config.ITEMS_FILE} não encontrado.")
        return pd.DataFrame()


def load_ratings():
    """Carrega as avaliações para o cálculo de métricas."""
    try:
        return pd.read_csv(Config.RATINGS_FILE)
    except FileNotFoundError:
        print(f"Erro: Arquivo {Config.RATINGS_FILE} não encontrado.")
        return pd.DataFrame()
