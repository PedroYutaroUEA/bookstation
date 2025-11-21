import streamlit as st
import pandas as pd
from api_service import ApiService, fetch_catalog_metadata
from PIL import Image
import os

# -------------------------------------------------------------
# TEMA PADRÃO (BRANCO + VERMELHO)
# -------------------------------------------------------------

BACKGROUND_COLOR = "#ffffff"       # branco
TEXT_COLOR = "#1a1a1a"             # quase preto
PRIMARY_RED = "#d90429"            # vermelho principal
SIDEBAR_BG = "#f5f5f5"             # sidebar branca
SIDEBAR_HIGHLIGHT = "#ef233c"      # vermelho hover

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
available_genres = catalog_metadata.get("genres", [])
price_min, price_max = catalog_metadata.get("price_range", [10, 100])

# --- 1. Simulação Inicial (Cold Start) ---
if st.session_state.user_id is None:
    st.header("1. Simulação Inicial (Cold Start)")
    st.info("Selecione características iniciais do seu gosto para gerarmos seu perfil.")

    with st.form("cold_start_form"):
        st.subheader("Seus Interesses")

        selected_genres = st.multiselect(
            "Categorias preferidas:",
            options=available_genres,
            default=available_genres[:2]
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
            if not selected_genres:
                st.warning("Selecione ao menos um gênero.")
            else:
                with st.spinner("Criando perfil..."):
                    new_user_id = service.simulate_user_api(
                        selected_genres, selected_price_range
                    )
                    if new_user_id is not None:
                        st.session_state.user_id = new_user_id
                        st.session_state.recommendations = (
                            service.fetch_recommendations(new_user_id, N_RECOMMEND)
                        )
                        st.success(f"Perfil criado! ID: {new_user_id}")
                        st.rerun()

# --- 2. Recomendações ---
if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Usuário Ativo: **{current_user}**")

    st.header(f"2. Recomendações de Livros ({N_RECOMMEND} itens)")
    st.info("Avalie os livros para melhorar suas recomendações!")

    if st.button("🔄 Atualizar Recomendações"):
        st.session_state.recommendations = service.fetch_recommendations(
            current_user, N_RECOMMEND
        )
        st.rerun()

    recs = st.session_state.recommendations

    if recs:
        COLS = 3
        for i in range(0, len(recs), COLS):
            cols = st.columns(COLS)
            for col, rec in zip(cols, recs[i:i+COLS]):
                with col:
                    st.markdown(
                        f"""
                        <div style='
                            padding: 10px;
                            margin: 10px 0;
                            border-radius: 8px;
                            background-color: #f9f9f9;
                            border: 1px solid {PRIMARY_RED};
                            min-height: 250px;
                            color: {TEXT_COLOR};
                        '>
                            <h4 style='color:{PRIMARY_RED}; margin-top:0;'>{rec['title']}</h4>
                            <p><b>Autor:</b> {rec['author']}</p>
                            <p><b>Categoria:</b> {rec['category']}</p>
                            <p><b>Score:</b> {rec.get('score', 'N/A'):.4f}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col_like, col_dislike = st.columns(2)

                    if col_like.button("👍 Gostei", key=f"like_{rec['item_id']}"):
                        service.rate_item(current_user, rec["item_id"], 1)
                        st.session_state.recommendations.remove(rec)
                        st.rerun()

                    if col_dislike.button("👎 Não Gostei", key=f"dislike_{rec['item_id']}"):
                        service.rate_item(current_user, rec["item_id"], 0)
                        st.session_state.recommendations.remove(rec)
                        st.rerun()
    else:
        st.warning("Nenhuma recomendação disponível.")

# --- Navegação ---
st.sidebar.divider()
if st.sidebar.button("Ir para Avaliação de Métricas"):
    st.switch_page("pages/2_Avaliacao_Metricas.py")

if st.sidebar.button("Limpar Perfil e Recomeçar"):
    service.clear_session()
