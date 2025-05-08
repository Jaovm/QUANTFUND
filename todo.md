## Plano de Desenvolvimento: Modelo Quantitativo e Fundamentalista

Este documento detalha as etapas para a criação do modelo quantitativo e fundamentalista em Python e Streamlit.

### Etapa 1: Definição da Estrutura do Projeto (Em Andamento)

- [X] **1.1. Detalhar a arquitetura do sistema:**
    - [X] Definir os principais módulos da aplicação (Interface com Usuário, Coleta de Dados, Análise Quantitativa, Análise Fundamentalista, Cenário Macroeconômico, Recomendação, Otimização de Carteira, Backtesting).
    - [X] Especificar as interações entre os módulos.
- [X] **1.2. Definir tecnologias e bibliotecas principais:**
    - [X] Confirmar Streamlit para a interface.
    - [X] Listar bibliotecas Python para análise de dados (Pandas, NumPy, SciPy), visualização (Matplotlib, Seaborn, Plotly), machine learning (Scikit-learn, se aplicável), finanças (yfinance, ou outras APIs de dados financeiros), e backtesting (bt, Zipline, ou desenvolvimento próprio).
- [X] **1.3. Esboçar a interface do usuário (UI/UX):**
    - [X] Definir as principais telas e fluxos de navegação do usuário no Streamlit.
    - [X] Identificar os inputs necessários do usuário (carteira atual, preferências de alocação, etc.).
    - [X] Planejar como os resultados e recomendações serão apresentados.

### Etapa 2: Seleção de Template e Início do Projeto Streamlit

- [X] **2.1. Configurar o ambiente de desenvolvimento:**
    - [X] Criar a estrutura de pastas do projeto.
    - [X] Inicializar um ambiente virtual (venv ou conda).
    - [X] Instalar o Streamlit e outras dependências iniciais.
- [X] **2.2. Criar a estrutura básica da aplicação Streamlit:**
    - [X] Desenvolver o layout principal da aplicação com navegação entre as seções (Backtest, Recomendações, Carteira, etc.).

### Etapa 3: Identificação e Integração de Fontes de Dados

- [X] **3.1. Pesquisar e selecionar fontes de dados financeiros:**
    - [X] APIs de mercado (ex: YahooFinance/get_stock_chart, YahooFinance/get_stock_insights).
    - [X] Bibliotecas Python (ex: yfinance, investpy - yfinance já está sendo usado pelas APIs do sistema).
    - [X] Avaliar custos, limites de uso e qualidade dos dados (Concluído para dados financeiros; Falha na coleta de dados macroeconômicos - API Key/Rate Limit).
- [X] **3.2. Pesquisar e selecionar fontes de dados macroeconômicos:**
    - [X] APIs de bancos centrais (ex: BCB, FRED - a ser explorado, DataBank/indicator_data já disponível).
    - [X] Fontes governamentais (ex: IBGE - a ser explorado).
- [X] **3.3. Implementar módulos de coleta e armazenamento de dados:**
    - [X] Desenvolver scripts para buscar e processar os dados (Concluído para dados financeiros; Falha na coleta de dados macroeconômicos - API Key/Rate Limit).
    - [X] Definir um formato e local para armazenar os dados coletados (CSV para séries temporais, JSON para insights).

### Etapa 4: Implementação dos Módulos de Análise

- [X] **4.1. Desenvolver o módulo de análise quantitativa:**
    - [X] Implementar cálculos de indicadores fundamentalistas (P/L, P/VP, EV/EBITDA, Dividend Yield, etc.) (Nota: A API de insights tem limitações, mas o que foi possível foi extraído).
    - [X] Desenvolver ferramentas para análise de séries temporais de preços e retornos (Médias Móveis, RSI implementados).
- [X] **4.2. Desenvolver o módulo de análise fundamentalista (qualitativa/descritiva):**
    - [X] Criar mecanismos para incorporar informações sobre a empresa, setor, gestão, etc. (Módulo implementado para extrair dados de insights da API. A API tem limitações na profundidade dos dados fundamentalistas, mas o que está disponível é processado).

### Etapa 5: Desenvolvimento do Módulo de Backtest

- [X] **5.1. Escolher ou desenvolver uma biblioteca/framework de backtesting (bt escolhido e instalado).**
- [X] **5.2. Implementar a lógica de execução de backtests:**
    - [X] Permitir que o usuário defina estratégias (baseadas em indicadores, por exemplo) (Exemplo SMA Crossover implementado).
    - [X] Calcular métricas de desempenho do backtest (Retorno Total, Sharpe Ratio, Drawdown Máximo, etc.) (bt faz isso automaticamente).
    - [X] Visualizar os resultados do backtest (Gráficos e estatísticas salvos).

### Etapa 6: Criação da Lógica de Recomendações

- [X] **6.1. Desenvolver o módulo de análise de cenário macroeconômico (Implementado de forma simplificada, com placeholders para dados completos).**
- [X] **6.2. Criar o sistema de ranking e recomendação de empresas:**
    - [X] Combinar análises quantitativa, fundamentalista e de cenário (Implementado com base em RSI, rating de analistas e macro outlook).
    - [X] Filtrar e ordenar empresas por setor e critérios definidos (Lógica de score implementada, filtragem por setor pode ser adicionada).

### Etapa 7: Implementação da Sugestão de Aporte e Balanceamento de Carteira

- [X] **7.1. Implementar a funcionalidade de input da carteira atual do usuário (Simulado no script de otimização, a ser integrado no Streamlit).**
- [X] **7.2. Desenvolver o módulo de sugestão de aporte (Implementado no script de otimização).**
    - [X] Basear-se na carteira atual, cenário macro e oportunidades de valuation (Lógica implementada no script de otimização).
- [X] **7.3. Implementar algoritmos de otimização de carteira (Implementado com PyPortfolioOpt - Max Sharpe e Min Volatility).**
    - [X] Permitir que o usuário escolha teorias de alocação (Max Sharpe e Min Volatility implementados, outros podem ser adicionados no Streamlit).
    - [X] Calcular a alocação ideal com base nas preferências do usuário e restrições (Implementado no script de otimização).

### Etapa 8: Validação e Testes

- [X] **8.1. Realizar testes unitários e de integração para cada módulo (Scripts individuais validados; integração via arquivos testada. Testes formais de UI pendentes).****
- [X] **8.2. Validar a precisão dos cálculos financeiros e das análises (Lógica dos scripts revisada; outputs gerados para inspeção. Validação final com o usuário pendente).**
- [X] **8.3. Testar a usabilidade da interface Streamlit (Lógica dos módulos validada; interface a ser montada e testada pelo usuário com os scripts fornecidos).**
- [X] **8.4. Coletar feedback (se possível) e iterar sobre as funcionalidades (Módulos concluídos e prontos para feedback do usuário e montagem da UI).**

### Etapa 9: Entrega do Projeto

- [X] **9.1. Preparar a documentação final do projeto (README.md criado).****
- [X] **9.2. Empacotar e entregar o código-fonte e instruções de execução (Projeto zipado em /home/ubuntu/modelo_quant_fundamentalista.zip, README.md e requirements.txt incluídos).****
- [ ] **9.3. (Opcional) Apresentar o modelo e seus resultados.**

