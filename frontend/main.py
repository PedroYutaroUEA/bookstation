import streamlit as st

# --- Configuração do Tema Global (SOUNDFOREST) ---
# O mesmo CSS que você injetou em outras páginas pode ser colocado aqui
# para garantir que o tema seja aplicado universalmente.

st.set_page_config(
    page_title="BOOKSTATION - Recomendações de Livros",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cores do tema (Marrom Escuro e Verde Floresta)

BACKGROUND_COLOR = "#a2a29d"
HEADER_COLOR = "#e8e8e8"
ASIDE = "#828693"
TEXT_COLOR = "#050608"
ASIDE_BUTTON_HOVER = "#495464"
ASIDE_BUTTON_COLOR = "#495464AC"
PRIMARY_COLOR = "#38761d"
SECONDARY_BACKGROUND = "#4d2800"

st.markdown(
    f"""
    <style>
    /* ---------------------- CORES DE FUNDO GERAIS ---------------------- */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    [data-testid="stSidebar"] {{
        background-color: {ASIDE};
    }}
    [data-testid="stSidebarNavItems"] * {{
        color: {HEADER_COLOR};
    }}
    [data-testid="stSidebarNavLink"] {{
        background-color: {ASIDE_BUTTON_COLOR};
    }}
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {ASIDE_BUTTON_HOVER};
    }}
    /* Cor dos botões e sliders (Verde Floresta) */
    .stButton>button {{
        background-color: {PRIMARY_COLOR} !important;
        border-color: {PRIMARY_COLOR} !important;
        color: white !important;
    }}
    /*app header*/
    .stAppToolbar {{
      background-color: {HEADER_COLOR};
    }}
    /* Fundo dos widgets de entrada */
    [data-testid="stForm"], 
    [data-testid^="stWidget"] > div {{
        background-color: {SECONDARY_BACKGROUND};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Conteúdo da Página Principal ---

st.title("Bem-vindo ao BOOKSTATION 📚")
st.markdown("---")
st.markdown(
    """
Este sistema utiliza uma abordagem baeada em similaridade de conteúdo para recomendar livros.

Para começar, selecione a página **Simulação e Recomendações** na barra lateral.
"""
)

# Se você quiser, pode exibir o logo aqui também.
