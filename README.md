# 🍰 Doce Controle - Sistema de Gestão para Confeitaria

Um sistema de gestão completo desenvolvido em Python com Flask, criado especialmente para a confeitaria "Confeitando com Artes" da minha sogra, Edneuza Pereira. O objetivo é simplificar o controle financeiro e de produção, desde o custo dos ingredientes até o preço final de venda.

## ✨ Funcionalidades

O "Doce Controle" oferece um conjunto de ferramentas para gerenciar uma confeitaria artesanal de forma eficiente:

* **Gestão de Ingredientes:** Cadastro de ingredientes e controle de estoque com cálculo de **Custo Médio Ponderado**, garantindo que o preço seja sempre atualizado conforme novas compras são feitas.
* **Fichas Técnicas Detalhadas:** Criação de receitas (fichas técnicas) com lista de ingredientes, modo de preparo, rendimento e associação com formas de bolo.
* **Cálculo de Custos Profissional:**
    * Cálculo automático do custo total dos ingredientes por ficha.
    * Calculadora de **Custo da Hora de Trabalho** baseada em custos fixos (gás, luz, água) e pró-labore.
    * Opção de incluir ou não o custo da mão de obra em cada ficha técnica.
* **Controle de Produção:** Funcionalidade para "Produzir" uma ficha técnica, com validação de estoque e baixa automática dos ingredientes utilizados.
* **Precificação Inteligente:** Calculadora interativa de preço de venda baseada no custo total de produção e na margem de lucro desejada.
* **Relatórios e Exportação:** Exportação de Fichas Técnicas detalhadas para planilhas Excel (`.xlsx`).
* **Interface Amigável:** Busca instantânea na lista de ingredientes e interface limpa e organizada.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3, Flask
* **Banco de Dados:** SQLite com SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript
* **Framework CSS:** Bootstrap 5
* **Geração de Excel:** Pandas e Openpyxl
* **Gráficos:** Chart.js

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para executar o projeto em um ambiente local.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/doce-controle.git](https://github.com/SEU_USUARIO/doce-controle.git)
    cd doce-controle
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

5.  **Execute a aplicação:**
    ```bash
    flask run --debug
    ```
    O sistema estará disponível em `http://127.0.0.1:5000`.

---
Feito com ❤️ para a melhor sogra e confeiteira!