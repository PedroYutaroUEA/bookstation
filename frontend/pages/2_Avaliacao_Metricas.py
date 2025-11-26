from pages import PAGE_1
import streamlit as st
from api_service import ApiService
from PIL import Image

# -------------------------------------------------------------
# TEMA PADRÃO (BRANCO + VERMELHO)
# -------------------------------------------------------------

BACKGROUND_COLOR = "#ffffff"
TEXT_COLOR = "#1a1a1a"
PRIMARY_RED = "#d90429"
SIDEBAR_BG = "#f5f5f5"
SIDEBAR_HIGHLIGHT = "#ef233c"
WARNING = "#d68d26ca"

st.set_page_config(
    page_title="Bookstation - Métricas",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT_COLOR} !important;
    }}

    .stButton>button {{
        background-color: {PRIMARY_RED} !important;
        color: white !important;
    }}

    h1, h2, h3, h4 {{
        color: {PRIMARY_RED};
    }}

    hr {{
        border-top: 2px solid {PRIMARY_RED};
    }}

    .stAlert div[data-testid="stAlertContainer"] {{
        background-color: {WARNING} !important;
        color: {TEXT_COLOR} !important; 
        border-left: 5px solid {TEXT_COLOR} !important; 
    }}

    /* ----------st.metric---------- */
    [data-testid="stMetricValue"], 
    [data-testid="stMetricLabel"],
    [data-testid="stMetricDelta"] {{
        color: #000000 !important;   /* preto */
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# LOGO
# -------------------------------------------------------------
try:
    st.image(Image.open("logo.png"), width=400)
except:
    st.warning("Logo não encontrada.")

# -------------------------------------------------------------
# CONTEÚDO
# -------------------------------------------------------------

service = ApiService()

st.title("📊 Avaliação de Desempenho (Precision, Recall, F1-Score)")
st.markdown("---")

if st.session_state.user_id is None:
    st.warning("⚠️ Você deve iniciar um perfil antes de calcular métricas!")
else:
    user = st.session_state.user_id
    st.sidebar.success(f"Usuário Ativo: {user}")

    st.subheader("Cálculo das Métricas")
    st.markdown(
        "Escolha o **número de recomendações** que deseja avaliar (de 5 a 50) com base no perfil do usuário ativo."
    )

    n_recommend = st.slider("**N Recomendações:**", 5, 50, 15, step=5)

    if st.button("Calcular Métricas"):
        with st.spinner("Calculando..."):
            metrics = service.fetch_metrics(user, n_recommend)

        if metrics and metrics.get("f1_score") is not None:
            col1, col2, col3 = st.columns(3)

            col1.metric("Precision", f"{metrics['precision'] * 100:.1f}%")
            col2.metric("Recall", f"{metrics['recall'] * 100:.1f}%")
            col3.metric("F1-Score", f"{metrics['f1_score'] * 100:.1f}%")

            st.success("Cálculo concluído.")
        else:
            st.warning(metrics.get("reason", "Erro desconhecido."))

st.sidebar.divider()
if st.sidebar.button("Voltar para Recomendações"):
    st.switch_page(f"pages/{PAGE_1}")
