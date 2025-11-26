# 📚 Bookstation: Sistema de Recomendação por Conteúdo

## Equipe:
- Pedro Yutaro Mont Morency Nakamura
- Renato Barbosa de Carvalho
- Ryan Da Silva Marinho
- Filipe Araújo Paulino

# 🎯 1. Objetivo do Sistema

Desenvolver um motor de recomendação para o catálogo de livros ($\approx 17.400$ títulos) baseado exclusivamente nos atributos de conteúdo dos livros. O objetivo é criar um perfil de gosto para o usuário e sugerir novos livros que sejam vetorialmente similares a esse perfil.

- Cenário de Uso: Descoberta de livros (Bookstation). A FBC é relevante porque os livros possuem metadados ricos (descrição, autor, categoria) que definem intrinsecamente seu conteúdo, independentemente de quantas pessoas os avaliaram.

- Avaliação: O sistema é validado utilizando as métricas Precision, Recall e F1-score, calculadas sobre um dataset binário de avaliações.

# 🏗️ 2. Arquitetura e Organização (MVC)

O backend utiliza o framework FastAPI e segue rigorosamente a arquitetura Model-View-Controller (MVC), com a camada de Service contendo a lógica de negócio.

## 2.1. Separação de Responsabilidades

├── config.py
├── controllers
│   ├── book_controller.py
│   ├── __init__.py
│   ├── recommendation_controller.py
│   └── user_controller.py
├── __init__.py
├── models
│   ├── __init__.py    /* Lidar com a persistência de dados (I/O de CSVs) e definir os schemas Pydantic. */
│   ├── item_rating.py
│   └── simulate_request.py
├── routes.py /* Camada de orquestração (Endpoints HTTP). Recebe requisições e chama os métodos do Service. */
├── services
│   ├── __init__.py
│   └── recommendation_service.py /* Motor de Recomendação: Contém a lógica FBC (TF-IDF, Similaridade de Cossenos e Cálculo de Métricas). */
└── utils
    └── __init__.py


## 2.2. Datasets

Arquivo | Tamanho | Colunas-Chave | Uso
|---|---|---|---|
books.csv | $\approx 17.000$ itens | title, author, description, category | Base para a vetorização de conteúdo.
ratings.csv | $\approx 200$ avaliações | user_id, item_id, rating (0 ou 1) | Exclusivamente para avaliação de métricas.

# 🧠 3. Implementação da Filtragem Baseada em Conteúdo (FBC)

## 3.1. Vetorização dos Itens (TF-IDF)

A vetorização transforma as características textuais de cada livro em um vetor numérico, permitindo o cálculo da similaridade.

Conteúdo Vetorizado: Uma string unificada é criada a partir das colunas description, category e author.

Algoritmo: Utiliza-se o TF-IDF (Term Frequency-Inverse Document Frequency) do scikit-learn. O TF-IDF atribui pesos maiores a palavras que são frequentes em um livro específico (TF), mas raras em todo o catálogo (IDF), destacando termos únicos como "magia antiga" ou "distopia".

## 3.2. Construção do Perfil do Usuário

O perfil não é baseado em vizinhos, mas sim no histórico de likes do próprio usuário:

$$\text{Perfil}_{\text{Usuário}} = \frac{1}{N} \sum_{i=1}^{N} \text{Vetor}_{\text{Livro } i}$$

Mecanismo: O Perfil do Usuário é o vetor médio dos vetores TF-IDF de todos os livros que o usuário avaliou como Gostou ($\text{rating} = 1$).

Resultados: Este perfil final representa matematicamente os interesses centrais do usuário.

## 3.3. Métrica de Similaridade

Métrica Escolhida: Similaridade de Cossenos (Cosine Similarity).

### Justificativa: A Similaridade de Cossenos é ideal para vetores TF-IDF (FBC), pois mede o ângulo entre o $\text{Perfil}_{\text{Usuário}}$ e o vetor de cada livro não lido no catálogo. O resultado indica o quão similar é o conteúdo de um novo livro ao gosto consolidado do usuário, ignorando o comprimento dos vetores.

# 📊 4. Avaliação do Sistema (Precision, Recall, F1-Score)

As métricas são calculadas comparando a lista de $N$ recomendações com o gabarito ($\text{rating}=1$) no ratings.csv.

Métrica

Definição

Fórmula

Interpretação

Precision

A proporção de recomendações que foram acertos.

$TP / (TP + FP)$

Quão preciso é o sistema em evitar erros (FP).

Recall

A proporção de todos os itens gostados que foram recuperados.

$TP / (TP + FN)$

Quão abrangente é o sistema em encontrar todos os itens relevantes (FN).

F1-Score

Média Harmônica de Precision e Recall.

$2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$

Métrica principal que avalia o equilíbrio entre acerto e cobertura.

(O cálculo de Precision, Recall e F1-score é implementado no RecommenderService.)

# 5. Como Executar o Sistema

Ambos os serviços (Backend e Frontend) devem ser executados em terminais separados.

5.1. Frontend (Interface)

Navegue até o diretório frontend/.

Instale as dependências: pip install -r requirements.txt

Execute o aplicativo principal:

streamlit run main.py
