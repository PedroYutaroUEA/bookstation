from app.models import load_books

class BookController:
    """Controller para manipulação de dados de livros."""
    books = load_books()

    categories = set()
    for cat in books['category']:
        categories.update(eval(cat))

    def get_metadata(self):
        return { "categories": self.categories }
