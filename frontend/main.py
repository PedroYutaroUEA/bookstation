import streamlit as st

# --------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------
st.set_page_config(
    page_title="BOOKSTATION - Recomendações de Livros",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------
# CORES DO TEMA (Branco + Vermelho)
# --------------------------------------------
BACKGROUND_COLOR = "#ffffff"     # fundo branco
TEXT_COLOR = "#1a1a1a"           # texto quase preto
PRIMARY_RED = "#d90429"          # vermelho forte
SIDEBAR_BG = "#f5f5f5"           # sidebar branco gelo
SIDEBAR_HIGHLIGHT = "#ef233c"    # vermelho mais vivo


# --------------------------------------------
# CSS Global
# --------------------------------------------
st.markdown(
    f"""
    <style>

    /* Fundo geral */
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

    /* Botões */
    .stButton>button {{
        background-color: {PRIMARY_RED} !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }}

    .stButton>button:hover {{
        background-color: {SIDEBAR_HIGHLIGHT} !important;
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {PRIMARY_RED};
    }}

    /* Linhas divisórias */
    hr {{
        border-top: 2px solid {PRIMARY_RED};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------
# LOGO NO TOPO DA PÁGINA
# --------------------------------------------
st.image("logo.png", width=400)

# --------------------------------------------
# CONTEÚDO PRINCIPAL
# --------------------------------------------
st.title("Bem-vindo ao BOOKSTATION 📚")
st.markdown("---")

st.markdown(
    """
O **BookStation** utiliza uma abordagem baseada em *similaridade de conteúdo* para recomendar livros.

Para começar, selecione a página **Simulação e Recomendações** na barra lateral.
"""
)
