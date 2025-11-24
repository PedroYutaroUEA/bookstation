from app.models import load_books


class BookController:
    """Controller para manipulação de dados de livros."""

    def __init__(self):
        self.books = load_books()

    def get_all_categories(self):
        if self.books.empty or "category" not in self.books.columns:
            return []
        categories_series = self.books["category"].dropna()
        all_categories = categories_series.str.split(",").explode()
        cleaned_categories = all_categories.str.strip().unique()
        return sorted(cleaned_categories[cleaned_categories != ""].tolist())

    def get_metadata(self):
        if self.books.empty or "price" not in self.books.columns:
            return {"categories": self.get_all_categories(), "price_range": [0, 100]}

        return {
            "categories": self.get_all_categories(),
            "price_range": [
                float(self.books["price"].min()),
                float(self.books["price"].max()),
            ],
        }
