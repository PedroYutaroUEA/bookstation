import streamlit as st

from api_service import ApiService

COL_W, COL_H = (3,20)

service = ApiService()

def books_grid(books):
    book_rows = [[None, None, None] for _ in range(COL_H)] 
    for i, book in enumerate(books):
        if i >= (COL_W*COL_H):
            break
        book_rows[i//COL_W][i%COL_W] = book

    for c, col in enumerate(st.columns(COL_W)):
        with col:
            for l in range(COL_H):
                book = book_rows[l][c]

                if book == None:
                    break

                _book_card(book)

_SELECT_OPTIONS = ["👍 Gosto","👎 Não Gosto"]
@st.fragment
def _book_card(book):
    st.image(book['image_url'], width="stretch")
    st.markdown(f"**{book['title']}**")

    categories = eval(book['category'])
    st.caption(' | '.join(categories))

    # Botões de Avaliação Binária
    col_like, col_dislike = st.columns(2)

    book_id = int(book['item_id'])
    rating = st.session_state.ratings.get(book_id) or st.session_state.rating_queue.get(book_id)

    selected = st.pills(None, _SELECT_OPTIONS, selection_mode="single", key=f"like_{book_id}", default=None if rating == None else _SELECT_OPTIONS[rating])
    if selected != None:
        _handle_rate_in_queue(book_id, 1 if selected == "👍 Gosto" else 0)
    else:
        st.session_state.rating_queue.pop(book_id, None)

#    if col_like.button("👍 Gosto", key=f"like_{book_id}", type="primary" if rating == 1 else "secondary"):
#        _handle_rate_in_queue(book_id, 1)
#
#    if col_dislike.button("👎 Não Gosto", key=f"dislike_{book_id}", type="primary" if rating == 0 else "secondary"):
#        _handle_rate_in_queue(book_id, 0)



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


