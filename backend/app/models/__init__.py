from app.config import Config
from .item_rating import ItemRating
from .simulate_request import SimulateRequest
import csv

# --- Funções de I/O (Data Persistence) ---

def load_books():
    """Carrega o catálogo de livros."""

    books = {}
    with open(Config.DATA_FILE, newline='') as csv_books:
        reader = csv.DictReader(csv_books)
        for row in reader:
            item_id = row['item_id']
            #del row['item_id']
            books[item_id] = row

    return books

def load_ratings():
    """Carrega as avaliações para o cálculo de micas"""

    user_ratings = {}
    with open(Config.RATINGS_FILE, newline='') as csv_ratings:
        reader = csv.reader(csv_ratings)
        for row in reader:
            userId, itemId, rating = row
            user_ratings[int(userId)] = (int(itemId), int(rating))

    return user_ratings

