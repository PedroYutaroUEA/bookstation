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
(TODO)

## Recall
(TODO)

## F1-score
(TODO)

# Interpretação dos resultados
(TODO)
