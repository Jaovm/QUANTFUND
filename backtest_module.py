import bt
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt

DATA_DIR = "."

def load_quant_analysis_data(symbol_filename_stem):
    """Carrega os dados de análise quantitativa de uma ação."""
    filepath = os.path.join(DATA_DIR, f"{symbol_filename_stem}_quant_analysis.csv")
    if not os.path.exists(filepath):
        print(f"Arquivo de análise quantitativa não encontrado: {filepath}")
        return None
    try:
        # O bt espera que o índice seja DatetimeIndex e as colunas de preço sejam nomeadas como o ticker
        # Nossos arquivos CSV já têm Timestamp como índice e colunas como 'Adj Close', 'SMA_50', etc.
        # Para o bt, precisamos de um DataFrame onde cada coluna é um ativo e os valores são os preços de fechamento.
        # Para uma estratégia simples com um único ativo, podemos renomear 'Adj Close' para o nome do ticker.
        df = pd.read_csv(filepath, index_col='Timestamp', parse_dates=True)
        ticker = symbol_filename_stem.split('_')[1] # e.g., PETR4 or AAPL
        if 'Adj Close' not in df.columns:
            print(f"Coluna 'Adj Close' não encontrada em {filepath}")
            return None
        # bt espera que os dados de preço estejam em uma coluna com o nome do ticker
        price_data = df[['Adj Close']].copy()
        price_data.columns = [ticker] # Renomeia a coluna 'Adj Close' para o ticker
        return price_data, df # Retorna os dados de preço para o bt e o df completo para indicadores
    except Exception as e:
        print(f"Erro ao carregar dados de análise quantitativa de {filepath}: {e}")
        return None, None

def run_sma_crossover_backtest(price_data, full_data_df, ticker_name, short_window=50, long_window=200):
    """Executa um backtest de cruzamento de médias móveis simples."""
    if price_data is None or full_data_df is None:
        print(f"Dados de preço ou completos ausentes para {ticker_name}")
        return None

    print(f"\n--- Backtest SMA Crossover para {ticker_name} ({short_window}x{long_window}) ---")

    # Certifique-se de que as colunas SMA existem no full_data_df
    sma_short_col = f'SMA_{short_window}'
    sma_long_col = f'SMA_{long_window}'

    if sma_short_col not in full_data_df.columns or sma_long_col not in full_data_df.columns:
        print(f"Colunas SMA ({sma_short_col}, {sma_long_col}) não encontradas nos dados completos para {ticker_name}.")
        print("Certifique-se de que a análise quantitativa foi executada e salvou essas colunas.")
        return None

    # Criar a estratégia: Comprar quando SMA curta cruza acima da SMA longa, Vender quando cruza abaixo.
    # Usaremos os dados de preço para o backtest e os dados completos para os sinais das SMAs.
    # O bt precisa de um DataFrame de sinais (1 para comprar, -1 para vender, 0 para manter)
    # Alinhar os índices é crucial aqui.
    signal_df = pd.DataFrame(index=full_data_df.index)
    signal_df[ticker_name] = 0 # Inicializa com 0 (manter)

    # Sinal de compra: SMA_short > SMA_long
    signal_df.loc[full_data_df[sma_short_col] > full_data_df[sma_long_col], ticker_name] = 1.0
    # Sinal de venda (short): SMA_short < SMA_long (para uma estratégia long-only, isso seria sair da posição)
    # Para simplificar, vamos apenas definir a posição para 0 quando o sinal de compra desaparece.
    # Uma abordagem mais robusta usaria bt.algos.SelectWhere ou similar.
    
    # bt.algos.WeighTarget requer um DataFrame de pesos alvo.
    # Vamos criar uma estratégia que aloca 100% ao ativo quando o sinal é de compra.
    target_weights = signal_df.copy()
    # Quando o sinal é 1 (compra), o peso é 1. Caso contrário, 0.
    target_weights[target_weights != 1] = 0 

    # Criar a estratégia de backtest com os pesos alvo
    strategy_sma_crossover = bt.Strategy(f'{ticker_name}_SMA_Crossover',
                                       [bt.algos.SelectAll(), # Seleciona todos os ativos (no nosso caso, apenas um)
                                        bt.algos.WeighTarget(target_weights),
                                        bt.algos.Rebalance()])

    # Criar o backtest
    # O bt espera que os dados de entrada (price_data) tenham colunas nomeadas com os tickers
    backtest = bt.Backtest(strategy_sma_crossover, price_data)
    
    # Executar o backtest
    try:
        results = bt.run(backtest)
    except Exception as e:
        print(f"Erro ao executar o backtest para {ticker_name}: {e}")
        print("Verifique os dados de entrada e a configuração da estratégia.")
        print(f"Price data head:\n{price_data.head()}")
        print(f"Target weights head:\n{target_weights.head()}")
        return None

    print(f"Backtest para {ticker_name} concluído.")
    return results

if __name__ == "__main__":
    # Exemplo com PETR4.SA
    petr4_stem = "br_PETR4_SA"
    petr4_price_data, df_petr4_full = load_quant_analysis_data(petr4_stem)
    if petr4_price_data is not None and df_petr4_full is not None:
        results_petr4 = run_sma_crossover_backtest(petr4_price_data, df_petr4_full, "PETR4", short_window=50, long_window=200)
        if results_petr4:
            print("\nResultados do Backtest para PETR4:")
            results_petr4.display()
            # Salvar gráfico de desempenho
            plot_filepath_petr4 = os.path.join(DATA_DIR, f"{petr4_stem}_sma_crossover_backtest.png")
            results_petr4.plot(title=f'Desempenho Backtest SMA Crossover PETR4')
            plt.savefig(plot_filepath_petr4)
            plt.close() # Fecha a figura para liberar memória
            print(f"Gráfico do backtest de PETR4 salvo em: {plot_filepath_petr4}")
            # Salvar estatísticas
            stats_filepath_petr4 = os.path.join(DATA_DIR, f"{petr4_stem}_sma_crossover_stats.csv")
            results_petr4.stats.to_csv(stats_filepath_petr4)
            print(f"Estatísticas do backtest de PETR4 salvas em: {stats_filepath_petr4}")

    # Exemplo com AAPL
    aapl_stem = "us_AAPL"
    aapl_price_data, df_aapl_full = load_quant_analysis_data(aapl_stem)
    if aapl_price_data is not None and df_aapl_full is not None:
        results_aapl = run_sma_crossover_backtest(aapl_price_data, df_aapl_full, "AAPL", short_window=50, long_window=200)
        if results_aapl:
            print("\nResultados do Backtest para AAPL:")
            results_aapl.display()
            # Salvar gráfico de desempenho
            plot_filepath_aapl = os.path.join(DATA_DIR, f"{aapl_stem}_sma_crossover_backtest.png")
            results_aapl.plot(title=f'Desempenho Backtest SMA Crossover AAPL')
            plt.savefig(plot_filepath_aapl)
            plt.close() # Fecha a figura para liberar memória
            print(f"Gráfico do backtest de AAPL salvo em: {plot_filepath_aapl}")
            # Salvar estatísticas
            stats_filepath_aapl = os.path.join(DATA_DIR, f"{aapl_stem}_sma_crossover_stats.csv")
            results_aapl.stats.to_csv(stats_filepath_aapl)
            print(f"Estatísticas do backtest de AAPL salvas em: {stats_filepath_aapl}")

    print("\nScript de backtesting concluído.")

