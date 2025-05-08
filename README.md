# Modelo Quantitativo e Fundamentalista para Análise de Investimentos

## Visão Geral

Este projeto consiste em um conjunto de scripts Python desenvolvidos para realizar análises quantitativas e fundamentalistas de ativos financeiros, realizar backtests de estratégias, gerar recomendações de investimento e otimizar carteiras. Todos os arquivos de script e dados estão localizados no diretório raiz do projeto para simplificar a implantação, especialmente com o Streamlit Community Cloud.

## Estrutura do Projeto

O projeto está organizado com todos os arquivos na raiz:

```
/modelo_quant_fundamentalista_raiz
|-- app.py              # Estrutura básica para a aplicação Streamlit (inicial)
|-- coleta_dados.py     # Módulo para coleta de dados financeiros e macroeconômicos
|-- analise_quantitativa.py # Módulo para cálculos de indicadores quantitativos
|-- analise_fundamentalista.py # Módulo para processamento de dados fundamentalistas
|-- backtest_module.py  # Módulo para execução de backtests de estratégias
|-- recomendacoes_module.py # Módulo para geração de recomendações
|-- otimizacao_carteira.py # Módulo para otimização de carteira e sugestão de aportes
|
|-- br_PETR4_SA_chart.csv
|-- br_PETR4_SA_insights.json
|-- br_PETR4_SA_quant_analysis.csv
|-- br_PETR4_SA_sma_crossover_backtest.png
|-- br_PETR4_SA_sma_crossover_stats.csv
|-- us_AAPL_chart.csv
|-- us_AAPL_insights.json
|-- us_AAPL_quant_analysis.csv
|-- us_AAPL_sma_crossover_backtest.png
|-- us_AAPL_sma_crossover_stats.csv
|-- optimized_portfolio_max_sharpe.json
|-- optimized_portfolio_min_volatility.json
|-- recomendacoes_geradas.json
|-- fundamental_analysis_summary.json
|-- (outros arquivos de dados macroeconômicos, se a coleta for bem-sucedida)
|
|-- requirements.txt        # Lista de dependências Python
|-- todo.md                 # Checklist do desenvolvimento do projeto
|-- README.md               # Este arquivo
```

## Funcionalidades Implementadas

1.  **Coleta de Dados (`coleta_dados.py`):**
    *   Busca dados históricos de preços e informações de empresas utilizando a API `YahooFinance/get_stock_chart` e `YahooFinance/get_stock_insights`.
    *   Tentativa de coleta de dados macroeconômicos (ex: inflação, PIB) utilizando a API `DataBank` (atualmente com limitações; o código está preparado para usar os dados se disponíveis).
    *   Salva os dados brutos em formato JSON e CSV no diretório raiz.

2.  **Análise Quantitativa (`analise_quantitativa.py`):**
    *   Carrega os dados históricos de preços do diretório raiz.
    *   Calcula indicadores técnicos como Médias Móveis Simples (SMA 50, SMA 200) e Índice de Força Relativa (RSI 14).
    *   Salva os dados enriquecidos com os indicadores em formato CSV no diretório raiz.

3.  **Análise Fundamentalista (`analise_fundamentalista.py`):**
    *   Carrega os dados de insights das empresas (JSON) do diretório raiz.
    *   Extrai e exibe informações relevantes.

4.  **Backtesting (`backtest_module.py`):**
    *   Utiliza a biblioteca `bt`.
    *   Implementa uma estratégia de exemplo baseada no cruzamento de médias móveis.
    *   Gera e salva gráficos de desempenho e estatísticas do backtest no diretório raiz.

5.  **Recomendações (`recomendacoes_module.py`):**
    *   Analisa um cenário macroeconômico simplificado.
    *   Combina informações das análises para gerar recomendações.
    *   Salva as recomendações em formato JSON no diretório raiz.

6.  **Otimização de Carteira (`otimizacao_carteira.py`):**
    *   Utiliza a biblioteca `PyPortfolioOpt`.
    *   Carrega os preços históricos dos ativos recomendados do diretório raiz.
    *   Implementa otimização por Maximização do Índice de Sharpe e Mínima Volatilidade.
    *   Fornece sugestão de alocação de aportes.
    *   Salva os resultados da otimização em formato JSON no diretório raiz.

## Como Configurar e Executar

1.  **Ambiente Virtual e Dependências:**
    *   Recomenda-se criar um ambiente virtual Python.
    *   Instale as dependências listadas no arquivo `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Execução dos Módulos Individuais:**
    *   Cada script Python pode ser executado individualmente. Eles estão configurados para ler e salvar arquivos no diretório atual (raiz).
    *   Exemplo para executar o módulo de coleta de dados (assumindo que o ambiente virtual está ativado e você está no diretório do projeto):
        ```bash
        python3 coleta_dados.py
        ```
    *   Recomenda-se executar os scripts na seguinte ordem para garantir que os dados dependentes estejam disponíveis:
        1.  `coleta_dados.py`
        2.  `analise_quantitativa.py`
        3.  `analise_fundamentalista.py`
        4.  `backtest_module.py`
        5.  `recomendacoes_module.py`
        6.  `otimizacao_carteira.py`

3.  **Integração com Streamlit (`app.py`):**
    *   O arquivo `app.py` contém uma estrutura básica inicial.
    *   **O desenvolvimento da interface Streamlit completa ficou a cargo do usuário.**
    *   Ao desenvolver `app.py`, você importará funções dos outros scripts (ex: `from coleta_dados import fetch_and_save_stock_chart_data`).
    *   Para executar a aplicação Streamlit (após desenvolvê-la):
        ```bash
        streamlit run app.py
        ```

## Limitações e Pontos de Atenção

*   **Dados Macroeconômicos:** A coleta via API `DataBank` pode ter limitações. O módulo `recomendacoes_module.py` usa uma análise simplificada se os dados não estiverem disponíveis.
*   **Dados Fundamentalistas:** A profundidade dos dados da API `YahooFinance/get_stock_insights` pode ser limitada.
*   **Interface Streamlit:** A interface de usuário completa deve ser desenvolvida pelo usuário.
*   **Exemplos de Ativos:** Os scripts usam `PETR4.SA` e `AAPL` como exemplos. Modifique-os ou, idealmente, permita a seleção na interface Streamlit.

## Próximos Passos Sugeridos (para o usuário)

1.  **Desenvolver a Interface Streamlit:** Criar a interface em `app.py`.
2.  **Expandir Fontes de Dados:** Integrar fontes adicionais.
3.  **Desenvolver Novas Estratégias:** Adicionar mais estratégias de backtest.

Este projeto fornece uma base sólida para um sistema de análise de investimentos.
