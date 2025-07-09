# 🍰 Doce Controle - Sistema de Gestão para Confeitaria

Um sistema de gestão completo desenvolvido em Python com Flask, criado especialmente para a confeitaria "Confeitando com Artes" da minha sogra, Edneuza Pereira. O objetivo é profissionalizar e simplificar o controle financeiro e de produção, desde o custo dos ingredientes até a geração de orçamentos para clientes.

O projeto está online e funcionando, hospedado na plataforma Render.

## ✨ Funcionalidades Implementadas

O "Doce Controle" é uma ferramenta robusta que oferece um conjunto completo de funcionalidades para gerenciar uma confeitaria artesanal de forma eficiente:

#### Gestão Financeira e de Custos
* **Custo da Hora de Trabalho:** Uma calculadora de custos que leva em conta despesas fixas (gás, luz, água) e o pró-labore desejado para definir um custo/hora preciso para a mão de obra.
* **Custo por Ficha Técnica:** Cálculo automático do custo total de produção de cada receita, somando o custo dos ingredientes e, opcionalmente, o custo da mão de obra com base no tempo de produção.
* **Módulo de Vendas:** Registro de todas as vendas, com cálculo automático de faturamento, custo total e lucro líquido, tanto por venda quanto no geral.

#### Gestão de Produção e Estoque
* **Controle de Estoque Inteligente:** Cadastro de ingredientes e materiais (incluindo embalagens) com controle de quantidade.
* **Custo Médio Ponderado:** O custo dos ingredientes é recalculado automaticamente a cada nova compra com preço diferente, garantindo uma precificação sempre justa e atualizada.
* **Histórico de Compras:** Cada compra de ingrediente fica registrada, permitindo analisar a variação de preços dos fornecedores ao longo do tempo.
* **Baixa Automática de Estoque:** Funcionalidade para "Produzir" uma ficha técnica, que valida se há estoque suficiente e subtrai as quantidades usadas automaticamente.
* **Alertas Visuais:** O sistema usa cores (amarelo para alerta, vermelho para crítico) para indicar visualmente quais ingredientes estão com estoque baixo.

#### Ferramentas de Apoio
* **Fichas Técnicas Detalhadas:** Criação de receitas completas com modo de preparo, rendimento, peso final, tempo de produção e associação com formas de bolo cadastradas.
* **Gerador de Orçamento em PDF:** Uma ferramenta que permite criar um orçamento personalizado para clientes, adicionando múltiplos itens, e gera um arquivo `.pdf` com design profissional, pronto para ser enviado.
* **Busca e Paginação:** As listas de ingredientes e fichas técnicas possuem sistemas de busca e paginação para facilitar a navegação.
* **Sistema de Login:** Acesso seguro à plataforma com um sistema de autenticação de usuários.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
* **Banco de Dados:** SQLite (para desenvolvimento local) e PostgreSQL (em produção)
* **Geração de PDF:** xhtml2pdf e Pillow
* **Frontend:** HTML5, CSS3, JavaScript
* **Framework CSS:** Bootstrap 5
* **Gráficos:** Chart.js
* **Deploy:** Render, Gunicorn

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para executar o projeto em um ambiente local.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/biinahc/gestao-confeitaria-flask.git](https://github.com/biinahc/gestao-confeitaria-flask.git)
    cd gestao-confeitaria-flask
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie o banco de dados:**
    ```bash
    flask init-db
    ```

5.  **Crie o primeiro usuário (interativo):**
    ```bash
    flask create-user
    ```

6.  **Execute a aplicação:**
    ```bash
    flask run --debug
    ```
    O sistema estará disponível em `http://127.0.0.1:5000`.

---
Feito com ❤️ para a melhor sogra e confeiteira!