import streamlit as st

from api_service import ApiService

COL_W, COL_H = (3, 20)

service = ApiService()


def books_grid(books):
    book_rows = [[None, None, None] for _ in range(COL_H)]
    for i, book in enumerate(books):
        if i >= (COL_W * COL_H):
            break
        book_rows[i // COL_W][i % COL_W] = book

    for c, col in enumerate(st.columns(COL_W)):
        with col:
            for l in range(COL_H):
                book = book_rows[l][c]

                if book is None:
                    break

                _book_card(book)


RATE_LABEL = {"👍 Like": 1, "👎 Dislike": 0}
_SELECT_OPTIONS = list(RATE_LABEL.keys())


@st.fragment
def _book_card(book):
    # Definindo as cores do tema para uso no CSS
    PRIMARY_RED = "#d90429"  # Vermelho Principal
    SECONDARY_BACKGROUND = "#9e9e9e"  # Cinza de fundo do card (do seu tema)

    book_id = int(book["item_id"])
    rating = st.session_state.ratings.get(book_id) or st.session_state.rating_queue.get(
        book_id
    )
    categories = eval(book.get("category", "[]"))
    categories_str = " | ".join(categories)

    st.html(
        f"""
        <div style='
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 8px; 
            background-color: {SECONDARY_BACKGROUND};
            color: {PRIMARY_RED}; /* Cor principal do título/autor */
            min-height: 350px; /* Altura garantida */
            overflow: hidden;
        '>
            <h4 style='color: white; margin-top: 0; font-size: 16px; min-height: 40px;'>{book.get('title', 'N/A')}</h4>
            <p style='color: {PRIMARY_RED}; font-size: 12px; margin-bottom: 5px;'>Autor: {book.get('authors', 'N/A')}</p>
            <p style='color: white; font-size: 12px;'>Categoria: {categories_str}</p>
            
            <hr style='border-top: 1px solid #777; margin: 5px 0;'>

            <!-- ESTRUTURA HORIZONTAL: IMAGEM + DESCRIÇÃO -->
            <div style='display: flex; gap: 10px; margin-bottom: 10px;'>
                
                <!-- Coluna 1: Imagem (Largura Fixa) -->
                <div style='flex-shrink: 0; width: 80px; text-align: center;'>
                    <img src="{book.get('image_url', 'https://placehold.co/80x120/9e9e9e/FFFFFF?text=BOOK')}" 
                         alt="Book Cover" style='width: 80px; height: 120px; object-fit: cover; border-radius: 4px;'>
                </div>
                
                <!-- Coluna 2: Descrição (Com Scroll) -->
                <div style='
                    flex-grow: 1; 
                    height: 120px; /* ALTURA FIXA PARA O SCROLL */
                    overflow-y: scroll; 
                    font-size: 14px; 
                    color: #fff;
                    padding-right: 5px; 
                    font-weight: semibold; 
                '>
                    <span style='font-weight: bold; color: white;'>Descrição:</span><br>
                    {book.get('description', 'Descrição não disponível.')}
                </div>
            </div>
            
        </div>
        """
    )

    selected = st.pills(
        None,
        _SELECT_OPTIONS,
        selection_mode="single",
        key=f"like_{book_id}",
        default=None if rating is None else _SELECT_OPTIONS[rating],
    )
    if selected is not None:
        _handle_rate_in_queue(book_id, RATE_LABEL[selected])
    else:
        st.session_state.rating_queue.pop(book_id, None)


def _handle_rate_in_queue(item_id: int, rating: int | None):
    """Adiciona/Atualiza o rating na fila local."""
    st.session_state.rating_queue[item_id] = rating
    st.toast(f"Avaliação {rating} para o item {item_id} registrada localmente.")


def process_ratings_and_update(user_id: int, n: int):
    """Função chamada pelo botão 'Atualizar Recomendações'."""
    queue = st.session_state.rating_queue

    if not queue:
        st.warning("Nenhuma nova avaliação para processar.")
        return

    # 1. Enviar o lote para o Backend
    if service.send_rating_batch(user_id, queue):

        # 2. Atualiza o dicionário de avaliações atuais do usuário com a da fila
        st.session_state.ratings |= st.session_state.rating_queue

        # 3. Limpar a fila local
        st.session_state.rating_queue = {}

        # 4. Chamar o FBC principal para atualizar
        st.session_state.recommendations = service.fetch_recommendations(user_id, n)

        st.success(f"{len(queue)} avaliações processadas. Perfil atualizado!")
    else:
        st.error("Falha ao atualizar o perfil no backend.")

    st.rerun()
