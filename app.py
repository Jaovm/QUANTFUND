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
if 'recomendacoes_geradas_data' not in st.session_state: # Renomeado para evitar conflito com o módulo
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
    - **Análise de Ativos:** Colete dados, visualize gráficos históricos, indicadores fundamentalistas e quantitativos de empresas.
    - **Backtesting:** Teste estratégias de investimento (ex: Cruzamento de Médias Móveis) com dados históricos.
    - **Recomendações:** Receba sugestões de ativos com base em múltiplos critérios e no cenário macroeconômico.
    - **Otimização de Carteira:** Construa e balanceie sua carteira de investimentos (ex: Max Sharpe, Mínima Volatilidade).
    - **Cenário Macroeconômico:** Colete e visualize dados macroeconômicos relevantes.
    
    **Como usar:**
    1. Comece pelo módulo "Análise de Ativos" para coletar dados de um ou mais tickers.
    2. Explore as análises fundamentalista e quantitativa para os ativos coletados.
    3. Utilize o módulo "Backtesting" para testar estratégias nos ativos com análise quantitativa.
    4. Gere "Recomendações" com base nas análises e no cenário macro.
    5. Otimize uma "Carteira" com os ativos desejados.
    6. Consulte o "Cenário Macroeconômico" para dados específicos.
    """)
    st.info("Lembre-se que os dados são obtidos de fontes públicas e podem ter limitações. Este painel é para fins educacionais e de demonstração.")

# --- Módulo: Análise de Ativos ---
elif app_mode == "Análise de Ativos":
    st.title("Módulo: Análise de Ativos")

    st.subheader("1. Coleta de Dados de Ativos")
    
    col1_coleta, col2_coleta = st.columns(2)
    with col1_coleta:
        ticker_input = st.text_input("Ticker do Ativo (ex: PETR4.SA, AAPL)", key="ticker_coleta", value=st.session_state.last_ticker_input)
    with col2_coleta:
        region_input = st.text_input("Região do Ativo (ex: BR, US)", key="region_coleta", value=st.session_state.last_region_input)

    if st.button("Buscar Dados Históricos e Insights", key="buscar_dados_btn"):
        if ticker_input and region_input:
            st.session_state.last_ticker_input = ticker_input
            st.session_state.last_region_input = region_input

            stem_key = f"{region_input.lower().strip()}_{ticker_input.upper().strip().replace(".", "_")}"
            coleta_dados_filename_prefix = region_input.lower().strip()
            
            with st.spinner(f"Buscando dados para {ticker_input.strip()}..."):
                try:
                    coleta_dados.fetch_and_save_stock_chart(symbol=ticker_input.strip(), region=region_input.strip(), filename_prefix=coleta_dados_filename_prefix)
                    symbol_part_for_filename = ticker_input.upper().strip().replace(".", "_")
                    chart_file_path = os.path.join(DATA_DIR, f"{coleta_dados_filename_prefix}_{symbol_part_for_filename}_chart.csv")
                    
                    coleta_dados.fetch_and_save_stock_insights(symbol=ticker_input.strip(), region=region_input.strip(), filename_prefix=coleta_dados_filename_prefix)
                    insights_file_path = os.path.join(DATA_DIR, f"{coleta_dados_filename_prefix}_{symbol_part_for_filename}_insights.json")

                    if os.path.exists(chart_file_path) and os.path.exists(insights_file_path):
                        st.session_state.dados_coletados_info[stem_key] = {
                            'ticker': ticker_input.strip(),
                            'region': region_input.strip(),
                            'chart_file': chart_file_path,
                            'insights_file': insights_file_path,
                            'stem': stem_key 
                        }
                        st.success(f"Dados históricos e insights para {ticker_input.strip()} coletados e salvos!")
                        st.experimental_rerun()
                    else:
                        missing_files_msg = "Arquivos não encontrados após a tentativa de coleta: "
                        if not os.path.exists(chart_file_path): missing_files_msg += f"{chart_file_path} "
                        if not os.path.exists(insights_file_path): missing_files_msg += f"{insights_file_path}"
                        st.error(f"Falha ao salvar/encontrar arquivos para {ticker_input.strip()}. {missing_files_msg}")
                
                except Exception as e:
                    st.error(f"Erro ao coletar dados para {ticker_input.strip()}: {str(e)}")
        else:
            st.warning("Por favor, preencha o ticker e a região do ativo.")

    available_stems_display = {info['stem']: f"{info['ticker']} ({info['region']})" for stem, info in st.session_state.dados_coletados_info.items()}
    options_for_select_asset = {"-": "Selecione um ativo"}
    options_for_select_asset.update(available_stems_display)

    selected_stem_key_for_display = st.selectbox(
        "Selecione um ativo para visualizar/analisar:", 
        options=list(options_for_select_asset.keys()), 
        format_func=lambda x: options_for_select_asset[x],
        key="select_ativo_analise"
    )
    
    st.markdown("---")
    st.subheader("2. Visualização de Dados Históricos")
    if selected_stem_key_for_display != "-" and selected_stem_key_for_display in st.session_state.dados_coletados_info:
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
    elif selected_stem_key_for_display == "-":
        st.info("Selecione um ativo na lista acima (após a coleta) para visualizar seus dados históricos.")

    st.markdown("---")
    st.subheader("3. Análise Fundamentalista")
    if selected_stem_key_for_display != "-" and selected_stem_key_for_display in st.session_state.dados_coletados_info:
        ativo_info = st.session_state.dados_coletados_info[selected_stem_key_for_display]
        st.write(f"**Análise Fundamentalista para: {ativo_info['ticker']} ({ativo_info['region']})**")
        insights_file = ativo_info['insights_file']
        if os.path.exists(insights_file):
            try:
                insights_data = analise_fundamentalista.load_stock_insights_data(ativo_info['stem']) 
                if insights_data:
                    if insights_data.get("instrumentInfo") and insights_data["instrumentInfo"].get("valuation"):
                        st.write("**Valuation:**")
                        st.json(insights_data["instrumentInfo"]["valuation"], expanded=False)
                    
                    if insights_data.get("recommendation"):
                        st.write("**Recomendações de Analistas (conforme API):**")
                        st.json(insights_data["recommendation"], expanded=False)
                    
                    st.write("**Indicadores Fundamentalistas Chave (Extraídos):**")
                    # Capturar prints da função extract_fundamental_indicators
                    # Esta função imprime, não retorna os prints diretamente. Para UI, idealmente retornaria.
                    # Por agora, vamos mostrar o que ela retorna (fundamental_metrics) e o usuário pode ver prints no console.
                    fundamental_metrics = analise_fundamentalista.extract_fundamental_indicators(insights_data, ativo_info['ticker'])
                    if fundamental_metrics:
                        df_fund = pd.DataFrame(list(fundamental_metrics.items()), columns=["Métrica", "Valor"])
                        st.table(df_fund)
                    else:
                        st.info("Não foram extraídos indicadores fundamentalistas chave ou a API não os forneceu para este ativo.")

                    if st.checkbox("Mostrar JSON completo de Insights", key=f"show_json_insights_{selected_stem_key_for_display}"):
                        st.json(insights_data)
                else:
                    st.warning(f"Não foi possível carregar os dados de insights para {ativo_info['ticker']}.")
            except Exception as e:
                st.error(f"Erro ao carregar ou exibir dados fundamentalistas de {insights_file}: {str(e)}")
        else:
            st.warning(f"Arquivo de insights ({insights_file}) não encontrado para {ativo_info['ticker']}. Tente coletar os dados novamente.")
    elif selected_stem_key_for_display == "-":
        st.info("Selecione um ativo na lista acima (após a coleta) para visualizar sua análise fundamentalista.")

    st.markdown("---")
    st.subheader("4. Análise Quantitativa")
    if selected_stem_key_for_display != "-" and selected_stem_key_for_display in st.session_state.dados_coletados_info:
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
                    if df_hist is not None:
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
                        st.error("Não foi possível carregar os dados históricos para cálculo quantitativo.")
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
                # Usar as janelas que foram usadas para gerar o arquivo, não as atuais da UI para exibição
                # Para isso, precisaríamos armazenar as janelas usadas ou parsear do nome do arquivo/colunas
                # Por simplicidade, vamos tentar encontrar colunas SMA e RSI genéricas ou com as janelas atuais da UI
                sma_short_col_name = f'SMA_{sma_short_window_quant}' # Assumindo que o arquivo foi gerado com estas janelas
                sma_long_col_name = f'SMA_{sma_long_window_quant}' # Assumindo que o arquivo foi gerado com estas janelas
                if sma_short_col_name in df_quant_results.columns: cols_to_plot_sma.append(sma_short_col_name)
                if sma_long_col_name in df_quant_results.columns: cols_to_plot_sma.append(sma_long_col_name)
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

    elif selected_stem_key_for_display == "-":
        st.info("Selecione um ativo na lista acima (após a coleta) para realizar a análise quantitativa.")

# --- Módulo: Backtesting ---
elif app_mode == "Backtesting":
    st.title("Módulo: Backtesting de Estratégias")

    if not st.session_state.ativos_analisados_quant:
        st.warning("Nenhum ativo com análise quantitativa realizada nesta sessão. Por favor, realize a Análise Quantitativa no módulo 'Análise de Ativos' primeiro.")
    else:
        available_stems_for_backtest_display = {stem: f"{st.session_state.dados_coletados_info[stem]['ticker']} ({st.session_state.dados_coletados_info[stem]['region']})" 
                                                for stem in st.session_state.ativos_analisados_quant.keys()}
        options_for_select_backtest_asset = {"-": "Selecione um ativo analisado"}
        options_for_select_backtest_asset.update(available_stems_for_backtest_display)

        selected_stem_key_for_backtest = st.selectbox(
            "Selecione um Ativo com Análise Quantitativa para Backtest:",
            options=list(options_for_select_backtest_asset.keys()),
            format_func=lambda x: options_for_select_backtest_asset[x],
            key="select_ativo_backtest"
        )

        if selected_stem_key_for_backtest != "-":
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
                            
                            # O backtest_module.run_sma_crossover_backtest usa as janelas passadas como argumento
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
                                st.error("Falha ao executar o backtest. Verifique os logs ou dados de entrada.")
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
        elif selected_stem_key_for_backtest == "-":
            st.info("Selecione um ativo com análise quantitativa realizada para executar o backtest.")

# --- Módulo: Recomendações ---
elif app_mode == "Recomendações":
    st.title("Módulo: Recomendações de Investimento")

    st.subheader("1. Análise de Cenário Macroeconômico (Visualização)")
    if st.button("Analisar/Atualizar Cenário Macroeconômico", key="analisar_macro_btn"):
        with st.spinner("Analisando cenário macroeconômico..."):
            try:
                # A função analyze_macro_scenario no módulo original imprime muito.
                # Para UI, seria melhor ela retornar os dados estruturados.
                # Por agora, vamos chamar e exibir o que ela retorna.
                st.session_state.macro_scenario_data = recomendacoes_module.analyze_macro_scenario()
                st.success("Análise de cenário macroeconômico concluída.")
            except Exception as e:
                st.error(f"Erro ao analisar cenário macroeconômico: {str(e)}")

    if st.session_state.macro_scenario_data:
        st.write("**Outlook Macroeconômico Atual:**")
        st.json(st.session_state.macro_scenario_data)
        st.caption("Detalhes da análise (se houver) podem estar visíveis no console do servidor.")
    else:
        st.info("Clique no botão acima para analisar o cenário macroeconômico. Certifique-se que os dados macroeconômicos necessários (ex: inflação Brasil) foram coletados previamente, se aplicável, através do módulo 'Cenário Macroeconômico'.")

    st.markdown("---")
    st.subheader("2. Geração de Recomendações")
    
    default_stems = []
    if st.session_state.dados_coletados_info:
        default_stems = list(st.session_state.dados_coletados_info.keys())[:2] # Pega até 2 stems como exemplo
    
    ticker_stems_input_rec = st.text_area("Stems dos Tickers para Recomendações (separados por vírgula, ex: br_PETR4_SA, us_AAPL)", ", ".join(default_stems), key="ticker_stems_rec")

    if st.button("Gerar Recomendações", key="gerar_recomendacoes_btn"):
        if not ticker_stems_input_rec:
            st.warning("Por favor, insira os stems dos tickers para gerar recomendações.")
        elif not st.session_state.macro_scenario_data:
            st.warning("Por favor, analise o cenário macroeconômico primeiro (botão acima).")
        else:
            stems_list = [s.strip() for s in ticker_stems_input_rec.split(",") if s.strip()]
            if not stems_list:
                st.warning("Nenhum stem de ticker válido fornecido.")
            else:
                missing_data_for_stems = False
                for stem_rec in stems_list:
                    if stem_rec not in st.session_state.dados_coletados_info or stem_rec not in st.session_state.ativos_analisados_quant:
                        st.warning(f"Dados de coleta ou análise quantitativa ausentes para o stem '{stem_rec}'. Certifique-se de que os dados foram coletados e a análise quantitativa foi executada para todos os stems listados no módulo 'Análise de Ativos'.")
                        missing_data_for_stems = True
                        break
                if not missing_data_for_stems:
                    with st.spinner("Gerando recomendações..."):
                        try:
                            recomendacoes_result = recomendacoes_module.generate_recommendations(stems_list, st.session_state.macro_scenario_data)
                            st.session_state.recomendacoes_geradas_data = recomendacoes_result
                            st.success("Recomendações geradas!")
                        except Exception as e:
                            st.error(f"Erro ao gerar recomendações: {str(e)}")
    
    if st.session_state.recomendacoes_geradas_data:
        st.write("**Recomendações Geradas:**")
        df_recs = pd.DataFrame(st.session_state.recomendacoes_geradas_data)
        # Reordenar colunas para melhor visualização se necessário
        if not df_recs.empty:
            cols_order = ['ticker', 'recomendacao', 'score', 'justificativas']
            # Garantir que todas as colunas esperadas existam
            actual_cols = [col for col in cols_order if col in df_recs.columns]
            st.dataframe(df_recs[actual_cols])
        else:
            st.info("Nenhuma recomendação foi gerada ou o resultado está vazio.")

elif app_mode == "Otimização de Carteira":
    st.title("Módulo: Otimização de Carteira")
    st.write("Em desenvolvimento...")

elif app_mode == "Cenário Macroeconômico":
    st.title("Módulo: Análise de Cenário Macroeconômico")
    st.write("Em desenvolvimento...")

# Rodapé (opcional)
st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido por Manus AI")

