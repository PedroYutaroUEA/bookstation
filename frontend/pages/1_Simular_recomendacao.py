from pages import PAGE_2
import streamlit as st
from api_service import ApiService, fetch_catalog_metadata
from PIL import Image

# -------------------------------------------------------------
# TEMA PADRÃO (BRANCO + VERMELHO)
# -------------------------------------------------------------

BACKGROUND_COLOR = "#ffffff"  # branco
SECONDARY_BACKGROUND = "#9e9e9e"  # branco
TEXT_COLOR = "#1a1a1a"  # quase preto
PRIMARY_RED = "#d90429"  # vermelho principal
PRIMARY_COLOR = "#6e04d9"
SIDEBAR_BG = "#f5f5f5"  # sidebar branca
SIDEBAR_HIGHLIGHT = "#ef233c"  # vermelho hover

st.set_page_config(
    page_title="Bookstation - Recomendações",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}

    [data-testid="stSidebarNavItems"] * {{
        color: {TEXT_COLOR};
    }}

    [data-testid="stSidebarNavLink"] {{
        background-color: transparent;
        border-radius: 6px;
        padding: 6px;
    }}

    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {SIDEBAR_HIGHLIGHT}33;
    }}
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {SIDEBAR_HIGHLIGHT}33;
    }}
    .stButton>button {{
        background-color: {PRIMARY_RED} !important;
        color: white !important;
        border-radius: 6px !important;
    }}
    h1, h2, h3, h4 {{
        color: {PRIMARY_RED};
    }}
    hr {{
        border-top: 2px solid {PRIMARY_RED};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# LOGO
# -------------------------------------------------------------
logo_path = "logo.png"
try:
    st.image(Image.open(logo_path), width=400)
except:
    st.warning("⚠️ Não foi possível carregar a logo. Verifique o caminho.")

# -------------------------------------------------------------
# LÓGICA DA PÁGINA
# -------------------------------------------------------------

service = ApiService()
N_RECOMMEND = 30

# Título
st.title("📚 Bookstation: Encontre sua Próxima Leitura")
st.markdown("---")

catalog_metadata = fetch_catalog_metadata()
available_categories = catalog_metadata.get("categories", [])
price_min, price_max = catalog_metadata.get("price_range", [10, 100])

# --- 1. Simulação Inicial (Cold Start) ---
if st.session_state.user_id is None:
    st.header("1. Simulação Inicial (Cold Start)")
    st.info("Selecione características iniciais do seu gosto para gerarmos seu perfil.")

    with st.form("cold_start_form"):
        st.subheader("Seus Interesses")

        selected_categories = st.multiselect(
            "Categorias preferidas:",
            options=available_categories,
            default=available_categories[:2],
        )

        selected_price_range = st.slider(
            "Faixa de Preço (R$):",
            min_value=float(price_min),
            max_value=float(price_max),
            value=(float(price_min), float(price_max)),
            step=5.0,
        )

        submitted = st.form_submit_button("Gerar Perfil e Recomendações")

        if submitted:
            if not selected_categories:
                st.warning("Selecione ao menos um gênero.")
            else:
                with st.spinner("Criando perfil..."):
                    result = service.simulate_user_api(
                        selected_categories, selected_price_range
                    )
                    # CORREÇÃO: O simulate_user_api agora retorna as recomendações iniciais
                    # do Cold Start (Content-Based puro)
                    new_user_id = result.get("user_id") if result else None
                    if result and result.get("user_id") is not None:
                        print(f"[FRONTEND] NEW USER ID: {new_user_id}")
                        st.session_state.recommendations = result.get(
                            "recommendations", []
                        )
                        st.session_state.user_id = new_user_id
                        st.success(f"Perfil criado! ID: {new_user_id}")
                        st.rerun()
                    else:
                        print(f"[FRONTEND] USER ID IS NONE IDK WHY")


def handle_rate_in_queue(item_id: int, rating: int):
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

        # 2. Limpar a fila local
        st.session_state.rating_queue = {}

        # 3. Chamar o FBC principal para atualizar
        st.session_state.recommendations = service.fetch_recommendations(user_id, n)

        st.success(f"{len(queue)} avaliações processadas. Perfil atualizado!")
    else:
        st.error("Falha ao atualizar o perfil no backend.")

    st.rerun()


# --- 2. Recomendações ---
if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Usuário Ativo: **{current_user}**")

    st.header(f"2. Recomendações de Livros ({N_RECOMMEND} itens)")
    if st.session_state.rating_queue:
        st.error(
            f"⚠️ {len(st.session_state.rating_queue)} avaliações pendentes. Clique em Atualizar!"
        )
    else:
        st.info(
            "Avalie os livros (Gosto/Não Gosto) e clique em Atualizar para refinar seu perfil!"
        )

    if st.button(
        "🔄 Atualizar Recomendações", type="primary"
    ):  # Agora este botão processa o batch
        process_ratings_and_update(current_user, N_RECOMMEND)

    recs = st.session_state.recommendations

    if recs:
        # Usando 3 colunas para um layout melhor de livro
        COLS_PER_ROW = 3

        for row_start in range(0, len(recs), COLS_PER_ROW):
            cols = st.columns(COLS_PER_ROW)
            for col, rec in zip(cols, recs[row_start : row_start + COLS_PER_ROW]):
                with col:
                    # Cartão de Livro
                    st.markdown(
                        f"""
                        <div style='
                            padding: 10px; 
                            margin: 10px 0; 
                            border-radius: 8px; 
                            background-color: {SECONDARY_BACKGROUND};
                            border: 1px solid {PRIMARY_COLOR};
                            color: white;
                            overflow: hidden;
                            height: 300px;
                        '>
                            <h4 style='color: white; margin-top: 0; font-size: 16px;'>{rec.get('title', 'N/A')}</h4>
                            <p style='color: #ccc; font-size: 12px;'>Autor: {rec.get('authors', 'N/A')}</p>
                            <p style='color: {PRIMARY_COLOR}; font-size: 12px;'>Categoria: {rec.get('category', 'N/A')}</p>
                            <p style='color: #ddd; font-size: 14px;'>Score: {rec.get('score', 'N/A')}</p>
                            <hr style='border-top: 1px solid #555; margin: 5px 0;'>
                            <div style='
                                height: 80px; 
                                overflow-y: scroll; 
                                text-overflow: ellipsis; 
                                display: -webkit-box;
                                -webkit-line-clamp: 4; 
                                -webkit-box-orient: vertical;
                                font-size: 12px; 
                                color: #ddd;
                            '>
                                <span style='color: #fff; font-size: 14px;'>Descrição: </span>
                                <p style='color: {TEXT_COLOR}; font-size: 14px;'>{rec.get('description', 'N/A')}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Botões de Avaliação Binária
                    col_like, col_dislike = st.columns(2)

                    if col_like.button("👍 Gosto (1)", key=f"like_{rec['item_id']}"):
                        handle_rate_in_queue(rec["item_id"], 1)
                        st.rerun()

                    if col_dislike.button(
                        "👎 Não Gosto (0)", key=f"dislike_{rec['item_id']}"
                    ):
                        handle_rate_in_queue(rec["item_id"], 0)
                        st.rerun()
    else:
        st.warning("Nenhum livro recomendado. Tente atualizar seu perfil.")

# --- Barra Lateral e Limpeza ---
st.sidebar.divider()
if st.sidebar.button("Limpar Perfil e Iniciar Novo"):
    service.clear_session()

if st.sidebar.button("Ir para Avaliação de Métricas"):
    st.switch_page(f"pages/{PAGE_2}")
