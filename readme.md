# Argus Maximus 

**Um projeto pessoal em desenvolvimento para criar um olheiro com Inteligência Artificial para o Cartola FC, com o objetivo de montar o time ótimo e maximizar a pontuação a cada rodada.**

![Status](https://img.shields.io/badge/status-em_desenvolvimento-yellow)

---

## Sobre o Projeto

O Argus Maximus é um projeto para escalar o melhor time possível no Cartola, um [fantasy game](https://cartolafc.globo.com) desenvolvido pela globo, utilizando IA para prever os Pontos dos jogadores, e programação linear para adequar o time as suas cartoletas.

### 1. Previsão de Pontuação com IA 🤖

O primeiro pilar do projeto é prever a pontuação que cada jogador provavelmente fará na próxima rodada. Para isso, utilizarei um modelo de Random Forest 

-   **Features (Variáveis):** Os modelos levam em conta dezenas de variáveis, como a média de pontos do jogador, o desempenho recente, o mando de campo, a força do adversário, scouts (desarmes, finalizações, faltas), entre outras.
-   **Objetivo:** O resultado final desta etapa será uma pontuação prevista para cada um dos mais de 500 atletas disponíveis no mercado.

### 2. Otimização do Time com Programação Linear 

Com as pontuações previstas em mãos, adequarei o time as cartoletas e as formações válidas.

Para resolver isso, a abordagem é usar Programação Linear:

-   **Função Objetivo:** Maximizar a pontuação total do time.
-   **Restrições:**
    -   O custo total do time não pode exceder o número de cartoletas ($ C_{total} $) disponíveis.
    -   O time deve seguir uma das formações táticas válidas (ex: 4-3-3, 4-4-2).

O resultado esperado é a escalação matematicamente ótima, o time que, segundo as previsões do modelo, tem o maior potencial de pontuação para a rodada.

## 📊 Fonte dos Dados Históricos e Agradecimentos

A qualidade de um modelo de IA depende diretamente da qualidade dos dados utilizados para treiná-lo.

Os dados históricos essenciais para o treinamento dos modelos (rodadas 1 a 12) foram generosamente compilados e disponibilizados por **Henrique P. Gomide** em seu incrível projeto:

👉 **[caRtola - A Consolidated Database of the Brazilian Football League](https://github.com/henriquepgomide/caRtola)**

Deixo aqui meu muito obrigado pela sua contribuição. Recomendo fortemente que visitem o repositório dele e deixem uma estrela ⭐.

Os dados da rodada 12 em diante foram feitos usando o script situado em scripts/update_etl.py

## 🗺️ Roadmap de Desenvolvimento

Este projeto está em andamento. Abaixo estão os próximos passos planejados:
-   [X] **Montagem da Base** Montar uma base consolidada com os dados de rodadas anteriores - e atualizar conforme se passam
-   [ ] **Modelagem:** Treinar e validar diferentes modelos de regressão (XGBoost, LightGBM, Redes Neurais).
-   [ ] **Backtesting:** Implementar um framework de backtesting para validar a eficácia do modelo em rodadas passadas.
-   [ ] **Automação:** Orquestrar o update_etl.py para rodar automaticamente a cada semana.
-   [ ] **Engenharia de Features:** Adicionar mais variáveis aos modelos (ex: dados de casas de aposta, condições climáticas).

Acompanhe as atualizações e commits para ver o progresso!

