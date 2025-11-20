from app.models import load_books


class BookController:
    """Controller para manipulação de dados de livros."""

    def get_all_genres(self):
        books = load_books()
        return sorted(books["genero"].dropna().unique().tolist())

    def get_metadata(self):
        books = load_books()
        if books.empty:
            return {"genres": [], "price_range": [0, 100]}

        return {
            "genres": self.get_all_genres(),
            "price_range": [float(books["price"].min()), float(books["price"].max())],
        }
