import streamlit as st
import pandas as pd
from api_service import ApiService, fetch_catalog_metadata
import os

# -------------------------------------------------------------
# INJEÇÃO DE TEMA E CONFIGURAÇÃO
# -------------------------------------------------------------
# Replicar as cores do projeto anterior para consistência
BACKGROUND_COLOR = "#f4f4f2"
HEADER_COLOR = "#e8e8e8"
ASIDE = "#bbbfca"
TEXT_COLOR = "#050608"
PRIMARY_COLOR = "#38761d"
SECONDARY_BACKGROUND = "#4d2800"

st.set_page_config(
    page_title="Bookstation - Recomendação",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {ASIDE}; }}
    .stButton>button {{ background-color: {PRIMARY_COLOR} !important; border-color: {PRIMARY_COLOR} !important; color: white !important; }}
    .stAppToolbar {{ background-color: {HEADER_COLOR}; }}
    
    /* Fundo dos widgets de entrada */
    [data-testid="stForm"], 
    [data-testid^="stWidget"] > div {{
        background-color: {SECONDARY_BACKGROUND};
    }}
    /* Cor do texto nos widgets */
    .stMultiSelect, .stSlider > div {{
        color: white !important;
    }}
    /* Títulos e texto principal */
    h1, h2, h3, h4, .stMarkdown, .stText {{ color: {TEXT_COLOR} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)
# -------------------------------------------------------------

service = ApiService()
N_RECOMMEND = 30  # Número fixo de recomendações, conforme o requisito

st.title("📚 Bookstation: Encontre sua Próxima Leitura")

catalog_metadata = fetch_catalog_metadata()
available_genres = catalog_metadata.get("genres", [])
price_min, price_max = catalog_metadata.get("price_range", [10, 100])

# --- 1. Cold Start: Simulação Inicial ---

if st.session_state.user_id is None:
    st.header("1. Simulação Inicial (Cold Start)")
    st.info(
        "Para gerar seu perfil inicial, selecione seus gostos. Nenhuma avaliação de usuário é usada neste cálculo."
    )

    with st.form("cold_start_form"):
        st.subheader("Seus Interesses")

        # Seleção de Gêneros
        selected_genres = st.multiselect(
            "Quais categorias de livros você costuma ler?",
            options=available_genres,
            default=available_genres[:2] if available_genres else [],
        )

        # Faixa de Preço
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
                st.warning("Por favor, selecione pelo menos um gênero.")
            else:
                with st.spinner("Criando perfil de conteúdo..."):
                    new_user_id = service.simulate_user_api(
                        selected_genres, selected_price_range
                    )
                    if new_user_id is not None:
                        st.session_state.user_id = new_user_id
                        st.session_state.recommendations = (
                            service.fetch_recommendations(new_user_id, N_RECOMMEND)
                        )
                        st.success(
                            f"Perfil criado com sucesso (User ID: {new_user_id})."
                        )
                        st.rerun()

# --- 2. Interação e Catálogo ---

if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Perfil Ativo: Usuário ID **{current_user}**")

    st.header(f"2. Recomendações de Livros ({N_RECOMMEND} itens)")
    st.info(
        "As recomendações são baseadas no seu perfil de conteúdo. Avalie os livros para refinar seu perfil."
    )

    # Botão de atualização
    if st.button("🔄 Atualizar Recomendações (Com novo perfil)"):
        st.session_state.recommendations = service.fetch_recommendations(
            current_user, N_RECOMMEND
        )
        st.experimental_rerun()

    # Exibição do Catálogo em Grid
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
                            min-height: 250px;
                        '>
                            <h4 style='color: white; margin-top: 0; font-size: 16px;'>{rec['title']}</h4>
                            <p style='color: #ccc; font-size: 12px;'>**Autor:** {rec['author']}</p>
                            <p style='color: {PRIMARY_COLOR}; font-size: 12px;'>**Categoria:** {rec['category']}</p>
                            <p style='color: #ddd; font-size: 14px;'>Score: {rec.get('score', 'N/A'):.4f}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Botões de Avaliação Binária
                    col_like, col_dislike = st.columns(2)

                    if col_like.button("👍 Gosto (1)", key=f"like_{rec['item_id']}"):
                        if service.rate_item(current_user, rec["item_id"], 1):
                            st.toast(f"Like em '{rec['title']}'! Perfil atualizado.")
                            st.session_state.recommendations.remove(
                                rec
                            )  # Remove da lista para não poluir
                            st.rerun()

                    if col_dislike.button(
                        "👎 Não Gosto (0)", key=f"dislike_{rec['item_id']}"
                    ):
                        if service.rate_item(current_user, rec["item_id"], 0):
                            st.toast(f"Dislike em '{rec['title']}'. Perfil atualizado.")
                            st.session_state.recommendations.remove(rec)
                            st.rerun()
    else:
        st.warning("Nenhum livro recomendado. Tente atualizar seu perfil.")

# --- Barra Lateral e Limpeza ---
st.sidebar.divider()
if st.sidebar.button("Limpar Perfil e Iniciar Novo"):
    service.clear_session()

if st.sidebar.button("Ir para Avaliação de Métricas"):
    st.switch_page("pages/2_Avaliacao_Metricas.py")
