# Equipe:
- Pedro Yutaro Mont Morency Nakamura
- Renato Barbosa de Carvalho
- Ryan Da Silva Marinho

# Objetivo do Sistema
Recomendar diversos livros ao usuário, de diferentes gêneros, publicadoras e épocas, mas que se assemelham pelo seu descritivo.

# Como executar o sistema
## Frontend
1. cd frontend
2. python -m venv venv
3. Ativar venv:
   - Windows: .\venv\Scripts\activate.bat
   - Linux: source ./venv/bin/activate
4. pip install -r requirements.txt
5. streamlit run main.py --server.port 8501

## Backend
1. cd backend
2. python -m venv venv
3. Ativar venv:
   - Windows: .\venv\Scripts\activate.bat
   - Linux: source ./venv/bin/activate
4. pip install -r requirements.txt
5. uvicorn main:app --reload --port 8000

# Como foi feita a vetorização
Usando o Vetorizador TF-IDF do Próprio sklearn, no qual é otimizado (parcialmente feito com C++).

# Como o perfil do usuário é construído
É construído a partir da média dos embeddings das descrições dos livros que o usuário gostou (deu like).

# Métrica de similaridade escolhida
Semelhança de cossenos, pois a avaliação, além de ser binária, ela é feita em um dataset relativamente esparsoso.

# Avaliação do sistema
## Precision
O quanto das recomendações foram realmente relevantes.
Fórmula usada: **Precision = TP/TP + FP **
TP = Qtd de livros que o usuário gostou
FP = Qtd de livros que o usuário não gostou

## Recall
O quanto o sistema conseguiu recuperar dos livros que o usuário realmente gostou.
Recall = TP/TP + FN
FN = livros que o usuário gostou, mas o sistema não recomendou

## F1-score
Equilíbrio entre precisão e abrangência.
F1 = 2 ( Precision x Recall/ Precision + Recall
É usado como medida final de quão bom é o sistema em:
- acerto
- cobertura
- Simultaneamente.

# Interpretação dos resultados
O sistema apresenta resultados que dependem diretamente da quantidade de likes fornecidos pelo usuário:
- Precision alto: O sistema consegue identificar com precisão livros alinhados ao gosto do usuário, cometendo poucos erros.
- Recall alto: O sistema consegue recuperar uma grande parte dos livros que o usuário efetivamente teria gostado.
- F1-score: Valores mais altos indicam que o modelo está sendo eficaz tanto em sugerir livros adequados quanto em não desperdiçar boas oportunidades.
