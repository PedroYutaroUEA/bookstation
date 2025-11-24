from app.models import load_books

class BookController:
    """Controller para manipulação de dados de livros."""
    books = load_books()

    #armazene todas as cartegorias de livros
    categories = set()
    for book in books.values():
        categories.update(map(lambda x: x.strip(), book['category'].split(',')))

    price_min = min(map(lambda book: float(book['price']), books.values()))
    price_max = max(map(lambda book: float(book['price']), books.values()))

    def get_metadata(self):
        assert len(self.books) > 0, "O dataset books está vazio"

        return {
            "categories": self.categories,
            "price_range": [self.price_min, self.price_max]
        }
