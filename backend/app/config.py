import os


class Config:
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ITEMS_FILE = os.path.join(DATA_DIR, "books.csv")
    RATINGS_FILE = os.path.join(DATA_DIR, "ratings.csv")

    MAX_RECOMMENDATIONS = 30
    MAX_ITEMS_TO_CHECK = 10000
