from app.models import load_books


class BookController:
    """Controller para manipulação de dados de livros."""

    def get_all_categories(self):
        books = load_books()
        return sorted(books["category"].dropna().unique().tolist())

    def get_metadata(self):
        books = load_books()
        if books.empty:
            return {"categories": [], "price_range": [0, 100]}

        price_col = books["price"]
        coverage = "$"

        return {
            "categories": self.get_all_categories(),
            "price_range": [float(books["price"].min()), float(books["price"].max())],
        }
