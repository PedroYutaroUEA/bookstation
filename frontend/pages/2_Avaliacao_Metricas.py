import streamlit as st
import numpy as np
from api_service import ApiService
import pandas as pd

# -------------------------------------------------------------
# INJEÇÃO DE TEMA E CONFIGURAÇÃO
# -------------------------------------------------------------
# Replicar o tema
BACKGROUND_COLOR = "#f4f4f2"
HEADER_COLOR = "#e8e8e8"
ASIDE = "#bbbfca"
TEXT_COLOR = "#050608"
PRIMARY_COLOR = "#38761d"
SECONDARY_BACKGROUND = "#4d2800"

st.set_page_config(
    page_title="Bookstation - Métricas",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {ASIDE}; }}
    .stButton>button {{ background-color: {PRIMARY_COLOR} !important; border-color: {PRIMARY_COLOR} !important; color: white !important; }}
    .stAppToolbar {{ background-color: {HEADER_COLOR}; }}
    /* Títulos e texto principal */
    h1, h2, h3, h4, .stMarkdown, .stText {{ color: {TEXT_COLOR} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)
# -------------------------------------------------------------

service = ApiService()

st.title("📊 Avaliação de Desempenho (Precision, Recall, F1-Score)")
st.info(
    "As métricas são calculadas comparando as recomendações com o 'gabarito' do dataset de avaliações, conforme o guia de trabalho."
)

if st.session_state.user_id is None:
    st.warning(
        "Por favor, inicie um perfil de usuário na página 'Simulação e Recomendação' primeiro."
    )
else:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Usuário Ativo: ID **{current_user}**")

    st.header("Cálculo das Métricas")

    # Controles de Parâmetros
    n_recommend = st.slider("Número de Recomendações (N):", 5, 50, 15, step=5)

    st.markdown("---")
    st.markdown("### Explicando o Gabarito")
    st.write(
        f"O sistema usará as avaliações binárias do **Usuário {current_user}** no `avaliacoes.csv` como gabarito (Likert: 1=Gostou, 0=Não Gostou)."
    )

    if st.button("Calcular Precision, Recall e F1-Score", type="primary"):
        with st.spinner(
            f"Calculando métricas para N={n_recommend} e Usuário {current_user}..."
        ):

            # Chama o Service para obter os resultados
            metrics = service.fetch_metrics(current_user, n_recommend)

            if metrics and metrics.get("f1_score") is not None:

                # Exibir Métricas em Colunas
                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Precision (Precisão)", f"{metrics['precision']:.3f}")
                col2.metric("Recall (Sensibilidade)", f"{metrics['recall']:.3f}")
                col3.metric("F1-Score (Média Harmônica)", f"{metrics['f1_score']:.3f}")

                st.success("Cálculo finalizado.")

                st.markdown("---")
                st.subheader("Interpretação")
                st.markdown(
                    f"**Recomendados (N):** {metrics.get('recommended_count', 'N/A')} | **Gabarito (Total de Likes):** {metrics.get('actual_likes', 'N/A')}"
                )

                st.markdown(
                    """
                - **Precision:** De todos os itens recomendados, quantos o usuário realmente gostou? (Acertos/Recomendados).
                - **Recall:** De todos os itens que o usuário gostou, quantos o sistema conseguiu recomendar? (Acertos/Total de Likes).
                - **F1-Score:** Média ponderada de Precision e Recall. É a métrica principal para o desempenho geral.
                """
                )
            else:
                st.warning(
                    metrics.get(
                        "reason",
                        "Não foi possível calcular. O usuário precisa de pelo menos 10 likes no dataset de avaliações.",
                    )
                )

# --- Navegação ---
st.sidebar.divider()
if st.sidebar.button("Voltar para Recomendações"):
    st.switch_page("pages/1_Simulacao_Recomendacao.py")
