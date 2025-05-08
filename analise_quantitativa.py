import pandas as pd
import numpy as np
import json
import os

DATA_DIR = "."

def load_stock_chart_data(symbol_filename_stem):
    """Carrega os dados históricos de uma ação a partir de um arquivo CSV."""
    filepath = os.path.join(DATA_DIR, f"{symbol_filename_stem}_chart.csv")
    if not os.path.exists(filepath):
        print(f"Arquivo de dados históricos não encontrado: {filepath}")
        return None
    try:
        df = pd.read_csv(filepath, index_col='Timestamp', parse_dates=True)
        return df
    except Exception as e:
        print(f"Erro ao carregar dados históricos de {filepath}: {e}")
        return None

def calculate_moving_average(df, window, price_column='Adj Close'):
    """Calcula a média móvel simples."""
    if df is None or price_column not in df.columns:
        return None
    return df[price_column].rolling(window=window).mean()

def calculate_rsi(df, window=14, price_column='Adj Close'):
    """Calcula o Índice de Força Relativa (RSI)."""
    if df is None or price_column not in df.columns:
        return None
    delta = df[price_column].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

if __name__ == "__main__":
    # Exemplo com PETR4.SA
    petr4_stem = "br_PETR4_SA"
    df_petr4 = load_stock_chart_data(petr4_stem)

    if df_petr4 is not None:
        print(f"\n--- Análise Quantitativa para {petr4_stem.split('_')[1]} ---")
        df_petr4['SMA_50'] = calculate_moving_average(df_petr4, 50)
        df_petr4['SMA_200'] = calculate_moving_average(df_petr4, 200)
        df_petr4['RSI_14'] = calculate_rsi(df_petr4, 14)

        print("Últimos 5 dias com Médias Móveis e RSI:")
        print(df_petr4[['Adj Close', 'SMA_50', 'SMA_200', 'RSI_14']].tail())
        
        # Salvar o dataframe com indicadores para uso posterior ou visualização no Streamlit
        output_filepath = os.path.join(DATA_DIR, f"{petr4_stem}_quant_analysis.csv")
        df_petr4.to_csv(output_filepath)
        print(f"Análise quantitativa de {petr4_stem} salva em: {output_filepath}")

    # Exemplo com AAPL
    aapl_stem = "us_AAPL"
    df_aapl = load_stock_chart_data(aapl_stem)

    if df_aapl is not None:
        print(f"\n--- Análise Quantitativa para {aapl_stem.split('_')[1]} ---")
        df_aapl['SMA_50'] = calculate_moving_average(df_aapl, 50)
        df_aapl['SMA_200'] = calculate_moving_average(df_aapl, 200)
        df_aapl['RSI_14'] = calculate_rsi(df_aapl, 14)

        print("Últimos 5 dias com Médias Móveis e RSI:")
        print(df_aapl[['Adj Close', 'SMA_50', 'SMA_200', 'RSI_14']].tail())

        output_filepath = os.path.join(DATA_DIR, f"{aapl_stem}_quant_analysis.csv")
        df_aapl.to_csv(output_filepath)
        print(f"Análise quantitativa de {aapl_stem} salva em: {output_filepath}")

    print("\nScript de análise quantitativa concluído.")

