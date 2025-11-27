from pages import PAGE_2
import streamlit as st
from api_service import fetch_catalog_metadata, ApiService
from PIL import Image

from common import books_grid, process_ratings_and_update

service = ApiService()


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
WARNING = "#d68d26ca"

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
        background-color: {SIDEBAR_HIGHLIGHT};
    }}
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {SIDEBAR_HIGHLIGHT};
    }}

    .stButton > button {{
        background-color: {PRIMARY_RED} !important;
        color: white !important;
        border-radius: 6px !important;
    }}

    .stFormSubmitButton button {{
        background-color: {PRIMARY_RED} !important;
        color: white !important;
        border-radius: 6px !important;
    }}

    .stFormSubmitButton button:hover, .stButton > button:hover {{
        background-color: {SIDEBAR_HIGHLIGHT} !important;
    }}

    h1, h2, h3, h4 {{
        color: {PRIMARY_RED};
    }}
    hr {{
        border-top: 2px solid {PRIMARY_RED};
    }}

    [data-testid="stButtonGroup"] button {{
        background-color: {SIDEBAR_BG} !important;
    }}

    .stAlert div[data-testid="stAlertContainer"] {{
        background-color: {WARNING} !important;
        color: {TEXT_COLOR} !important; 
        border-left: 5px solid {TEXT_COLOR} !important; 
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

N_RECOMMEND = 30

# Título
st.title("📚 Bookstation: Encontre sua Próxima Leitura")
st.markdown("---")

catalog_metadata = fetch_catalog_metadata()
available_categories = catalog_metadata.get("categories", [])

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

        submitted = st.form_submit_button("Gerar Perfil e Recomendações")

        if submitted:
            if not selected_categories:
                st.warning("Selecione ao menos um gênero.")
            else:
                with st.spinner("Criando perfil..."):
                    result = service.simulate_user_api(selected_categories)

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


# --- 2. Recomendações ---
if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Usuário Ativo: **{current_user}**")

    recs = st.session_state.recommendations
    st.header(
        f"Livros sugeridos ({len(recs)}/{N_RECOMMEND} dos livros combinam com o seu perfil)"
    )
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

    if recs:
        books_grid(recs)
    else:
        st.warning("Nenhum livro recomendado. Tente atualizar seu perfil.")

# --- Barra Lateral e Limpeza ---
st.sidebar.divider()
if st.sidebar.button("Limpar Perfil e Iniciar Novo"):
    service.clear_session()

if st.sidebar.button("Ir para Avaliação de Métricas"):
    st.switch_page(f"pages/{PAGE_2}")
