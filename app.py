import streamlit as st
import pandas as pd
import os
import json
import matplotlib.pyplot as plt

# Importar módulos do projeto
import coleta_dados
import analise_fundamentalista
import analise_quantitativa
import backtest_module
import otimizacao_carteira
import recomendacoes_module

# Configuração da página
st.set_page_config(layout="wide", page_title="Painel Quant-Fundamentalista Interativo")

# Define o diretório de dados (consistente com os módulos)
DATA_DIR = "."
coleta_dados.DATA_DIR = DATA_DIR
analise_fundamentalista.DATA_DIR = DATA_DIR
analise_quantitativa.DATA_DIR = DATA_DIR
backtest_module.DATA_DIR = DATA_DIR
otimizacao_carteira.DATA_DIR = DATA_DIR
recomendacoes_module.DATA_DIR = DATA_DIR

# Inicializar st.session_state para armazenar dados coletados
if 'dados_coletados_info' not in st.session_state:
    st.session_state.dados_coletados_info = {} 
if 'ativos_analisados_quant' not in st.session_state:
    st.session_state.ativos_analisados_quant = {} 
if 'backtests_executados' not in st.session_state:
    st.session_state.backtests_executados = {} 
if 'otimizacoes_realizadas' not in st.session_state:
    st.session_state.otimizacoes_realizadas = {} 
if 'recomendacoes_geradas_data' not in st.session_state: 
    st.session_state.recomendacoes_geradas_data = None
if 'dados_macro_coletados' not in st.session_state:
    st.session_state.dados_macro_coletados = {} 
if 'last_ticker_input' not in st.session_state:
    st.session_state.last_ticker_input = "PETR4.SA"
if 'last_region_input' not in st.session_state:
    st.session_state.last_region_input = "BR"
if 'macro_scenario_data' not in st.session_state:
    st.session_state.macro_scenario_data = None

# Barra lateral para navegação
st.sidebar.title("Navegação")
app_mode = st.sidebar.selectbox("Escolha o Módulo:",
    ["Página Inicial", "Análise de Ativos", "Backtesting", "Recomendações", "Otimização de Carteira", "Cenário Macroeconômico"])

# --- Módulo: Página Inicial ---
if app_mode == "Página Inicial":
    st.title("Bem-vindo ao Painel Quantitativo e Fundamentalista Interativo")
    st.markdown("""
    Este é um sistema interativo para análise de investimentos, combinando abordagens quantitativas e fundamentalistas.
    Utilize o menu na barra lateral para navegar entre os diferentes módulos.
    
    **Funcionalidades Principais:**
    - **Análise de Ativos:** Colete dados, visualize gráficos históricos, indicadores fundamentalistas e quantitativos de empresas. Para empresas da B3, utilize o sufixo `.SA` (ex: `PETR4.SA`).
    - **Backtesting:** Teste estratégias de investimento (ex: Cruzamento de Médias Móveis) com dados históricos.
    - **Recomendações:** Receba sugestões de ativos com base em múltiplos critérios e no cenário macroeconômico.
    - **Otimização de Carteira:** Construa e balanceie sua carteira de investimentos (ex: Max Sharpe, Mínima Volatilidade), incluindo uma projeção de ganhos/perdas em 12 meses com 95% de confiança.
    - **Cenário Macroeconômico:** Colete e visualize dados macroeconômicos relevantes (funcionalidade placeholder).
    
    **Como usar:**
    1. Comece pelo módulo "Análise de Ativos" para coletar dados de um ou mais tickers. Lembre-se do sufixo `.SA` para ativos da B3.
    2. Explore as análises fundamentalista e quantitativa para os ativos coletados.
    3. Utilize o módulo "Backtesting" para testar estratégias nos ativos com análise quantitativa.
    4. Gere "Recomendações" com base nas análises e no cenário macro.
    5. Otimize uma "Carteira" com os ativos desejados e veja a projeção de risco/retorno.
    6. Consulte o "Cenário Macroeconômico" para dados específicos (atualmente placeholder).
    """)
    st.info("Lembre-se que os dados são obtidos de fontes públicas (yfinance) e podem ter limitações. Este painel é para fins educacionais e de demonstração.")

# --- Módulo: Análise de Ativos ---
elif app_mode == "Análise de Ativos":
    st.title("Módulo: Análise de Ativos")

    st.subheader("1. Coleta de Dados de Ativos")
    st.markdown("Para ativos da B3, use o formato `TICKER.SA` (ex: `PETR4.SA`, `VALE3.SA`). Para outros mercados, use o ticker padrão (ex: `AAPL` para Apple nos EUA). A região (`BR`, `US`, etc.) é usada para organizar os arquivos.")
    
    col1_coleta, col2_coleta = st.columns(2)
    with col1_coleta:
        ticker_input = st.text_input("Ticker do Ativo (ex: PETR4.SA, AAPL)", key="ticker_coleta", value=st.session_state.last_ticker_input)
    with col2_coleta:
        region_input = st.text_input("Região/País (ex: BR, US)", key="region_coleta", value=st.session_state.last_region_input)

    if st.button("Buscar Dados Históricos e Insights", key="buscar_dados_btn"):
        if ticker_input and region_input:
            ticker_clean = ticker_input.strip().upper()
            region_clean = region_input.strip().upper()
            st.session_state.last_ticker_input = ticker_clean
            st.session_state.last_region_input = region_clean

            if region_clean == "BR" and not ticker_clean.endswith(".SA"):
                st.warning("Para ativos da B3 (região BR), o ticker deve terminar com ".SA". Exemplo: {ticker_clean}.SA")
            else:
                stem_key = f"{region_clean.lower()}_{ticker_clean.replace(".", "_")}"
                coleta_dados_filename_prefix = region_clean.lower()
                
                with st.spinner(f"Buscando dados para {ticker_clean}..."):
                    try:
                        success_chart = coleta_dados.fetch_and_save_stock_chart(symbol=ticker_clean, region=region_clean, filename_prefix=coleta_dados_filename_prefix)
                        success_insights = coleta_dados.fetch_and_save_stock_insights(symbol=ticker_clean, region=region_clean, filename_prefix=coleta_dados_filename_prefix)
                        
                        if success_chart and success_insights:
                            symbol_part_for_filename = ticker_clean.replace(".", "_")
                            chart_file_path = os.path.join(DATA_DIR, f"{coleta_dados_filename_prefix}_{symbol_part_for_filename}_chart.csv")
                            insights_file_path = os.path.join(DATA_DIR, f"{coleta_dados_filename_prefix}_{symbol_part_for_filename}_insights.json")
                            
                            st.session_state.dados_coletados_info[stem_key] = {
                                'ticker': ticker_clean,
                                'region': region_clean,
                                'chart_file': chart_file_path,
                                'insights_file': insights_file_path,
                                'stem': stem_key 
                            }
                            st.success(f"Dados históricos e insights para {ticker_clean} coletados e salvos!")
                            st.experimental_rerun()
                        else:
                            error_messages = []
                            if not success_chart: error_messages.append("Falha ao buscar/salvar dados históricos (gráfico).")
                            if not success_insights: error_messages.append("Falha ao buscar/salvar insights.")
                            st.error(f"Erro ao coletar dados para {ticker_clean}: {"; ".join(error_messages)}. Verifique o console para mais detalhes e se o ticker é válido no Yahoo Finance.")
                    
                    except Exception as e:
                        st.error(f"Erro inesperado ao coletar dados para {ticker_clean}: {str(e)}")
        else:
            st.warning("Por favor, preencha o ticker e a região do ativo.")

    available_stems_display = {info['stem']: f"{info['ticker']} ({info['region']})" for stem, info in st.session_state.dados_coletados_info.items()}
    options_for_select_asset = {"": "Selecione um ativo"} 
    options_for_select_asset.update(available_stems_display)

    selected_stem_key_for_display = st.selectbox(
        "Selecione um ativo para visualizar/analisar:", 
        options=list(options_for_select_asset.keys()), 
        format_func=lambda x: options_for_select_asset[x],
        key="select_ativo_analise"
    )
    
    st.markdown("---")
    st.subheader("2. Visualização de Dados Históricos")
    if selected_stem_key_for_display and selected_stem_key_for_display in st.session_state.dados_coletados_info:
        ativo_info = st.session_state.dados_coletados_info[selected_stem_key_for_display]
        st.write(f"**Exibindo dados para: {ativo_info['ticker']} ({ativo_info['region']})**")
        chart_file = ativo_info['chart_file']
        if os.path.exists(chart_file):
            try:
                df_chart = pd.read_csv(chart_file, index_col='Timestamp', parse_dates=True)
                st.write("**Gráfico de Preço de Fechamento Ajustado (Adj Close):**")
                if 'Adj Close' in df_chart.columns:
                    st.line_chart(df_chart['Adj Close'])
                else:
                    st.warning("Coluna 'Adj Close' não encontrada nos dados do gráfico.")
                
                st.write("**Dados Históricos (Últimos 10 registros):**")
                st.dataframe(df_chart.tail(10))
                
                if st.checkbox("Mostrar todos os dados históricos", key=f"show_all_hist_{selected_stem_key_for_display}"):
                    st.dataframe(df_chart)
            except Exception as e:
                st.error(f"Erro ao carregar ou exibir dados históricos de {chart_file}: {str(e)}")
        else:
            st.warning(f"Arquivo de dados históricos ({chart_file}) não encontrado para {ativo_info['ticker']}. Tente coletar os dados novamente.")
    elif not selected_stem_key_for_display:
        st.info("Selecione um ativo na lista acima (após a coleta) para visualizar seus dados históricos.")

    st.markdown("---")
    st.subheader("3. Análise Fundamentalista")
    if selected_stem_key_for_display and selected_stem_key_for_display in st.session_state.dados_coletados_info:
        ativo_info = st.session_state.dados_coletados_info[selected_stem_key_for_display]
        st.write(f"**Análise Fundamentalista para: {ativo_info['ticker']} ({ativo_info['region']})**")
        insights_file = ativo_info['insights_file']
        if os.path.exists(insights_file):
            try:
                insights_data_loaded = analise_fundamentalista.load_stock_insights_data(ativo_info['stem'])
                if insights_data_loaded:
                    st.write("**Indicadores Fundamentalistas Chave (Extraídos do yfinance):**")
                    fundamental_metrics = analise_fundamentalista.extract_fundamental_indicators(insights_data_loaded, ativo_info['ticker'])
                    if fundamental_metrics:
                        df_fund = pd.DataFrame(list(fundamental_metrics.items()), columns=["Métrica", "Valor"])
                        st.table(df_fund)
                    else:
                        st.info("Não foram extraídos indicadores fundamentalistas chave ou o yfinance não os forneceu para este ativo.")

                    if st.checkbox("Mostrar JSON completo de Insights (yfinance)", key=f"show_json_insights_{selected_stem_key_for_display}"):
                        st.json(insights_data_loaded, expanded=False)
                else:
                    st.warning(f"Não foi possível carregar os dados de insights (yfinance) para {ativo_info['ticker']}.")
            except Exception as e:
                st.error(f"Erro ao carregar ou exibir dados fundamentalistas de {insights_file}: {str(e)}")
        else:
            st.warning(f"Arquivo de insights ({insights_file}) não encontrado para {ativo_info['ticker']}. Tente coletar os dados novamente.")
    elif not selected_stem_key_for_display:
        st.info("Selecione um ativo na lista acima (após a coleta) para visualizar sua análise fundamentalista.")

    st.markdown("---")
    st.subheader("4. Análise Quantitativa")
    if selected_stem_key_for_display and selected_stem_key_for_display in st.session_state.dados_coletados_info:
        ativo_info = st.session_state.dados_coletados_info[selected_stem_key_for_display]
        st.write(f"**Análise Quantitativa para: {ativo_info['ticker']} ({ativo_info['region']})**")
        
        col_aq1, col_aq2, col_aq3 = st.columns(3)
        with col_aq1:
            sma_short_window_quant = st.number_input("Janela Média Móvel Curta (SMA)", min_value=5, max_value=100, value=20, step=1, key=f"sma_short_quant_{selected_stem_key_for_display}")
        with col_aq2:
            sma_long_window_quant = st.number_input("Janela Média Móvel Longa (SMA)", min_value=20, max_value=250, value=50, step=1, key=f"sma_long_quant_{selected_stem_key_for_display}")
        with col_aq3:
            rsi_window_quant = st.number_input("Janela RSI", min_value=5, max_value=50, value=14, step=1, key=f"rsi_win_quant_{selected_stem_key_for_display}")

        if st.button("Calcular Indicadores Quantitativos", key=f"calc_quant_{selected_stem_key_for_display}"):
            chart_file = ativo_info['chart_file']
            if os.path.exists(chart_file):
                try:
                    df_hist = analise_quantitativa.load_stock_chart_data(ativo_info['stem'])
                    if df_hist is not None and not df_hist.empty:
                        with st.spinner("Calculando indicadores..."):
                            df_hist[f'SMA_{sma_short_window_quant}'] = analise_quantitativa.calculate_moving_average(df_hist, sma_short_window_quant)
                            df_hist[f'SMA_{sma_long_window_quant}'] = analise_quantitativa.calculate_moving_average(df_hist, sma_long_window_quant)
                            df_hist['RSI'] = analise_quantitativa.calculate_rsi(df_hist, rsi_window_quant)
                            
                            quant_output_filename = f"{ativo_info['stem']}_quant_analysis.csv"
                            quant_output_filepath = os.path.join(DATA_DIR, quant_output_filename)
                            df_hist.to_csv(quant_output_filepath)
                            st.session_state.ativos_analisados_quant[selected_stem_key_for_display] = quant_output_filepath
                            st.success(f"Indicadores quantitativos calculados e salvos em {quant_output_filepath}")
                            st.experimental_rerun()
                    else:
                        st.error("Não foi possível carregar os dados históricos (ou estão vazios) para cálculo quantitativo.")
                except Exception as e:
                    st.error(f"Erro ao calcular indicadores quantitativos: {str(e)}")
            else:
                st.warning(f"Arquivo de dados históricos ({chart_file}) não encontrado. Colete os dados primeiro.")

        if selected_stem_key_for_display in st.session_state.ativos_analisados_quant:
            quant_file_path = st.session_state.ativos_analisados_quant[selected_stem_key_for_display]
            if os.path.exists(quant_file_path):
                df_quant_results = pd.read_csv(quant_file_path, index_col='Timestamp', parse_dates=True)
                st.write("**Gráfico de Preços com Médias Móveis:**")
                cols_to_plot_sma = ['Adj Close']
                sma_short_col_name_q = f'SMA_{sma_short_window_quant}' 
                sma_long_col_name_q = f'SMA_{sma_long_window_quant}' 
                if sma_short_col_name_q in df_quant_results.columns: cols_to_plot_sma.append(sma_short_col_name_q)
                if sma_long_col_name_q in df_quant_results.columns: cols_to_plot_sma.append(sma_long_col_name_q)
                st.line_chart(df_quant_results[cols_to_plot_sma])

                st.write("**Gráfico RSI:**")
                if 'RSI' in df_quant_results.columns:
                    st.line_chart(df_quant_results['RSI'])
                
                st.write("**Últimos Dados Quantitativos Calculados:**")
                st.dataframe(df_quant_results.tail())
            else:
                st.info("Arquivo de análise quantitativa não encontrado. Clique em 'Calcular Indicadores Quantitativos'.")
        else:
            st.info("Nenhum indicador quantitativo calculado para este ativo nesta sessão. Use o botão acima.")

    elif not selected_stem_key_for_display:
        st.info("Selecione um ativo na lista acima (após a coleta) para realizar a análise quantitativa.")

# --- Módulo: Backtesting ---
elif app_mode == "Backtesting":
    st.title("Módulo: Backtesting de Estratégias")

    if not st.session_state.ativos_analisados_quant:
        st.warning("Nenhum ativo com análise quantitativa realizada nesta sessão. Por favor, realize a Análise Quantitativa no módulo 'Análise de Ativos' primeiro.")
    else:
        available_stems_for_backtest_display = {stem: f"{st.session_state.dados_coletados_info[stem]['ticker']} ({st.session_state.dados_coletados_info[stem]['region']})" 
                                                for stem in st.session_state.ativos_analisados_quant.keys()}
        options_for_select_backtest_asset = {"": "Selecione um ativo analisado"}
        options_for_select_backtest_asset.update(available_stems_for_backtest_display)

        selected_stem_key_for_backtest = st.selectbox(
            "Selecione um Ativo com Análise Quantitativa para Backtest:",
            options=list(options_for_select_backtest_asset.keys()),
            format_func=lambda x: options_for_select_backtest_asset[x],
            key="select_ativo_backtest"
        )

        if selected_stem_key_for_backtest:
            ativo_info_backtest = st.session_state.dados_coletados_info[selected_stem_key_for_backtest]
            st.write(f"**Backtest para: {ativo_info_backtest['ticker']} ({ativo_info_backtest['region']})**")

            col_bt1, col_bt2 = st.columns(2)
            with col_bt1:
                bt_sma_short = st.number_input("Janela Curta SMA (Estratégia)", min_value=5, max_value=100, value=20, step=1, key=f"bt_sma_short_{selected_stem_key_for_backtest}")
            with col_bt2:
                bt_sma_long = st.number_input("Janela Longa SMA (Estratégia)", min_value=20, max_value=250, value=50, step=1, key=f"bt_sma_long_{selected_stem_key_for_backtest}")
            
            run_backtest_button_disabled = False
            if bt_sma_short >= bt_sma_long:
                st.warning("A janela curta da SMA deve ser menor que a janela longa.")
                run_backtest_button_disabled = True

            if st.button("Executar Backtest SMA Crossover", key=f"run_bt_{selected_stem_key_for_backtest}", disabled=run_backtest_button_disabled):
                quant_analysis_file_path = st.session_state.ativos_analisados_quant.get(selected_stem_key_for_backtest)
                if quant_analysis_file_path and os.path.exists(quant_analysis_file_path):
                    try:
                        with st.spinner("Executando backtest..."):
                            price_data, full_data_df = backtest_module.load_quant_analysis_data(selected_stem_key_for_backtest)
                            
                            if price_data is not None and not price_data.empty and full_data_df is not None and not full_data_df.empty:
                                results = backtest_module.run_sma_crossover_backtest(price_data, full_data_df, ativo_info_backtest['ticker'], short_window=bt_sma_short, long_window=bt_sma_long)

                                if results:
                                    strategy_name_key = f"{selected_stem_key_for_backtest}_sma_{bt_sma_short}_{bt_sma_long}"
                                    plot_filepath = os.path.join(DATA_DIR, f"{strategy_name_key}_backtest.png")
                                    stats_filepath = os.path.join(DATA_DIR, f"{strategy_name_key}_stats.csv")

                                    fig = results.plot(title=f"Desempenho Backtest SMA Crossover {ativo_info_backtest['ticker']} ({bt_sma_short}x{bt_sma_long})")
                                    fig.savefig(plot_filepath)
                                    plt.close(fig) 
                                    
                                    results.stats.to_csv(stats_filepath)
                                    
                                    st.session_state.backtests_executados[strategy_name_key] = {
                                        'plot': plot_filepath,
                                        'stats': stats_filepath
                                    }
                                    st.success(f"Backtest para {ativo_info_backtest['ticker']} concluído!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Falha ao executar o backtest (run_sma_crossover_backtest não retornou resultados). Verifique os logs ou dados de entrada.")
                            else:
                                st.error("Dados de preço ou DataFrame completo não puderam ser carregados para o backtest.")
                    except Exception as e:
                        st.error(f"Erro durante o backtest: {str(e)}")
                else:
                    st.warning("Arquivo de análise quantitativa não encontrado. Realize a Análise Quantitativa primeiro.")
            
            strategy_key_to_display = f"{selected_stem_key_for_backtest}_sma_{bt_sma_short}_{bt_sma_long}"
            if strategy_key_to_display in st.session_state.backtests_executados:
                backtest_results_paths = st.session_state.backtests_executados[strategy_key_to_display]
                st.markdown("### Resultados do Backtest")
                if os.path.exists(backtest_results_paths['plot']):
                    st.image(backtest_results_paths['plot'])
                else:
                    st.warning("Arquivo de gráfico do backtest não encontrado.")
                
                if os.path.exists(backtest_results_paths['stats']):
                    df_stats = pd.read_csv(backtest_results_paths['stats'], index_col=0)
                    st.write("**Estatísticas do Backtest:**")
                    st.dataframe(df_stats)
                else:
                    st.warning("Arquivo de estatísticas do backtest não encontrado.")
        elif not selected_stem_key_for_backtest:
            st.info("Selecione um ativo com análise quantitativa realizada para executar o backtest.")

# --- Módulo: Recomendações ---
elif app_mode == "Recomendações":
    st.title("Módulo: Recomendações de Investimento")

    st.subheader("1. Análise de Cenário Macroeconômico (Visualização)")
    if st.button("Analisar/Atualizar Cenário Macroeconômico", key="analisar_macro_btn"):
        with st.spinner("Analisando cenário macroeconômico (placeholder)..."):
            try:
                st.session_state.macro_scenario_data = recomendacoes_module.analyze_macro_scenario()
                st.success("Análise de cenário macroeconômico (placeholder) concluída.")
            except Exception as e:
                st.error(f"Erro ao analisar cenário macroeconômico: {str(e)}")

    if st.session_state.macro_scenario_data:
        st.write("**Outlook Macroeconômico Atual (Placeholder):**")
        st.json(st.session_state.macro_scenario_data)
    else:
        st.info("Clique no botão acima para analisar o cenário macroeconômico (atualmente é um placeholder).")

    st.markdown("---")
    st.subheader("2. Geração de Recomendações")
    
    default_stems_rec = []
    if st.session_state.dados_coletados_info:
        quant_stems = list(st.session_state.ativos_analisados_quant.keys())
        if quant_stems:
            default_stems_rec = quant_stems[:min(2, len(quant_stems))] 
        else: 
            default_stems_rec = list(st.session_state.dados_coletados_info.keys())[:min(2, len(st.session_state.dados_coletados_info.keys()))]
    
    ticker_stems_input_rec_str = st.text_area("Stems dos Tickers para Recomendações (separados por vírgula, ex: br_PETR4_SA, us_AAPL)", ", ".join(default_stems_rec), key="ticker_stems_rec")

    if st.button("Gerar Recomendações", key="gerar_recomendacoes_btn"):
        if not ticker_stems_input_rec_str:
            st.warning("Por favor, insira os stems dos tickers para gerar recomendações.")
        elif not st.session_state.macro_scenario_data:
            st.warning("Por favor, analise o cenário macroeconômico primeiro (botão acima).")
        else:
            stems_list_rec = [s.strip() for s in ticker_stems_input_rec_str.split(",") if s.strip()]
            if not stems_list_rec:
                st.warning("Nenhum stem de ticker válido fornecido.")
            else:
                missing_data_for_stems_rec = False
                for stem_rec_check in stems_list_rec:
                    if stem_rec_check not in st.session_state.dados_coletados_info or stem_rec_check not in st.session_state.ativos_analisados_quant:
                        st.warning(f"Dados de coleta ou análise quantitativa ausentes para o stem '{stem_rec_check}'. Certifique-se de que os dados foram coletados e a análise quantitativa foi executada para todos os stems listados no módulo 'Análise de Ativos'.")
                        missing_data_for_stems_rec = True
                        break
                if not missing_data_for_stems_rec:
                    with st.spinner("Gerando recomendações..."):
                        try:
                            recomendacoes_result = recomendacoes_module.generate_recommendations(stems_list_rec, st.session_state.macro_scenario_data)
                            st.session_state.recomendacoes_geradas_data = recomendacoes_result
                            st.success("Recomendações geradas!")
                        except Exception as e:
                            st.error(f"Erro ao gerar recomendações: {str(e)}")
    
    if st.session_state.recomendacoes_geradas_data:
        st.write("**Recomendações Geradas:**")
        df_recs = pd.DataFrame(st.session_state.recomendacoes_geradas_data)
        if not df_recs.empty:
            cols_order_recs = ['ticker', 'recomendacao', 'score', 'justificativas']
            actual_cols_recs = [col for col in cols_order_recs if col in df_recs.columns]
            st.dataframe(df_recs[actual_cols_recs])
        else:
            st.info("Nenhuma recomendação foi gerada ou o resultado está vazio.")

# --- Módulo: Otimização de Carteira ---
elif app_mode == "Otimização de Carteira":
    st.title("Módulo: Otimização de Carteira")

    st.subheader("1. Seleção de Ativos para Otimização")
    available_stems_for_opt = {stem: f"{st.session_state.dados_coletados_info[stem]['ticker']} ({st.session_state.dados_coletados_info[stem]['region']})" 
                                for stem in st.session_state.ativos_analisados_quant.keys()}
    
    if not available_stems_for_opt or len(available_stems_for_opt) < 2:
        st.warning("Nenhum ativo com análise quantitativa disponível ou menos de dois ativos. Realize a Análise Quantitativa no módulo 'Análise de Ativos' para pelo menos dois ativos antes de otimizar.")
    else:
        selected_stems_for_opt = st.multiselect(
            "Selecione os Ativos para incluir na Otimização (mínimo 2):",
            options=list(available_stems_for_opt.keys()),
            format_func=lambda x: available_stems_for_opt[x],
            default=list(available_stems_for_opt.keys())[:min(2, len(available_stems_for_opt))] 
        )

        if len(selected_stems_for_opt) < 2:
            st.warning("Por favor, selecione pelo menos 2 ativos para otimização.")
        else:
            optimization_type = st.selectbox("Método de Otimização:", ["max_sharpe", "min_volatility"], key="opt_type")

            if st.button("Otimizar Carteira", key="run_optimization_btn"):
                with st.spinner("Carregando dados e otimizando carteira..."):
                    prices_df_opt = otimizacao_carteira.load_stock_prices_for_optimization(selected_stems_for_opt)
                    
                    if prices_df_opt is not None and not prices_df_opt.empty and len(prices_df_opt.columns) >= 2:
                        optimal_weights, performance_metrics = otimizacao_carteira.optimize_portfolio(prices_df_opt, optimization_method=optimization_type)
                        
                        if optimal_weights and performance_metrics:
                            # Calcular intervalo de confiança
                            ret_anual, vol_anual, _ = performance_metrics
                            lower_bound, upper_bound = otimizacao_carteira.calculate_return_confidence_interval(ret_anual, vol_anual)
                            
                            st.session_state.otimizacoes_realizadas[optimization_type] = {
                                'stems': selected_stems_for_opt,
                                'weights': optimal_weights,
                                'performance': performance_metrics,
                                'confidence_interval': (lower_bound, upper_bound) if lower_bound is not None else None
                            }
                            st.success(f"Otimização ({optimization_type}) concluída!")
                            st.experimental_rerun()
                        else:
                            st.error("Falha ao otimizar a carteira. Verifique os logs ou os dados de entrada. Certifique-se que os arquivos CSV de análise quantitativa existem e contêm dados válidos para os ativos selecionados.")
                    else:
                        st.error("Não foi possível carregar dados de preços suficientes ou válidos para os ativos selecionados. Certifique-se de que a análise quantitativa foi feita e os arquivos CSV existem e não estão vazios.")

            if optimization_type in st.session_state.otimizacoes_realizadas:
                opt_results = st.session_state.otimizacoes_realizadas[optimization_type]
                # Verificar se os stems da otimização atual correspondem aos selecionados
                if set(opt_results['stems']) == set(selected_stems_for_opt):
                    st.subheader(f"Resultados da Otimização: {optimization_type.replace('_', ' ').title()}")
                    st.write("**Ativos Selecionados:**", ", ".join([st.session_state.dados_coletados_info[s]['ticker'] for s in opt_results['stems']]))
                    
                    st.write("**Pesos Ótimos:**")
                    df_weights = pd.DataFrame(list(opt_results['weights'].items()), columns=["Ativo", "Peso"])
                    df_weights["Peso"] = df_weights["Peso"].map(lambda x: f"{x*100:.2f}%")
                    st.table(df_weights)

                    st.write("**Performance Esperada da Carteira:**")
                    perf_data = {
                        "Retorno Anual Esperado": f"{opt_results['performance'][0]*100:.2f}%",
                        "Volatilidade Anual": f"{opt_results['performance'][1]*100:.2f}%",
                        "Sharpe Ratio": f"{opt_results['performance'][2]:.2f}"
                    }
                    st.json(perf_data)

                    if opt_results.get('confidence_interval'):
                        lower_b, upper_b = opt_results['confidence_interval']
                        st.write("**Projeção de Ganhos/Perdas (Intervalo de Confiança de 95% para Retorno em 12 Meses):**")
                        st.metric(label="Limite Inferior", value=f"{lower_b*100:.2f}%")
                        st.metric(label="Limite Superior", value=f"{upper_b*100:.2f}%")
                        st.caption("Este intervalo representa a faixa esperada de retorno da carteira otimizada nos próximos 12 meses, com 95% de confiança, assumindo que as condições históricas de mercado (retorno médio e volatilidade) se mantenham.")
                    else:
                        st.warning("Não foi possível calcular a projeção de ganhos/perdas para esta carteira.")

# --- Módulo: Cenário Macroeconômico ---
elif app_mode == "Cenário Macroeconômico":
    st.title("Módulo: Análise de Cenário Macroeconômico")
    st.info("Esta seção é um placeholder. A coleta e análise detalhada de dados macroeconômicos não está implementada nesta versão.")
    
    if st.button("Carregar Dados Macroeconômicos (Placeholder)", key="load_macro_placeholder"):
        with st.spinner("Carregando dados macro (placeholder)..."):
            recomendacoes_module.fetch_and_save_macro_data("NY.GDP.MKTP.CD", "BRA", "Brasil_GDP") 
            st.session_state.dados_macro_coletados["BRA_GDP"] = "Dados de PIB do Brasil (placeholder) carregados/verificados."
            st.success("Operação de dados macro (placeholder) concluída.")

    if st.session_state.dados_macro_coletados:
        st.write("**Dados Macroeconômicos Carregados (Exemplo Placeholder):**")
        st.json(st.session_state.dados_macro_coletados)

# Rodapé (opcional)
st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido por Manus AI")

