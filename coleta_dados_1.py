import yfinance as yf
import pandas as pd
import json
import os

# Define o diretório de dados
DATA_DIR = "."
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_and_save_stock_chart(symbol, region, filename_prefix):
    """Busca dados históricos de uma ação usando yfinance e salva em CSV.
    Para B3, o symbol deve ser no formato XXXXN.SA (ex: PETR4.SA).
    A região é usada para construir o nome do arquivo, mas não diretamente na chamada yfinance.
    """
    try:
        ticker_complete = symbol # yfinance espera o ticker completo, ex: PETR4.SA
        print(f"Buscando dados históricos para {ticker_complete} com yfinance...")
        ticker_obj = yf.Ticker(ticker_complete)
        # Para B3, o período de 5 anos é um bom padrão.
        # auto_adjust=False para obter 'Adj Close' separadamente.
        hist_data = ticker_obj.history(period="5y", interval="1d", auto_adjust=False, actions=False)
        
        if hist_data.empty:
            print(f"Não foi possível obter dados históricos para {ticker_complete} com yfinance. Verifique o ticker e a disponibilidade de dados.")
            return False # Indica falha

        hist_data.index.name = "Timestamp"
        
        if 'Adj Close' not in hist_data.columns and 'Close' in hist_data.columns:
             print(f"Coluna 'Adj Close' não encontrada para {ticker_complete}. Usando 'Close' como fallback para 'Adj Close'.")
             hist_data['Adj Close'] = hist_data['Close']
        elif 'Adj Close' not in hist_data.columns:
            print(f"Colunas 'Adj Close' e 'Close' não encontradas para {ticker_complete}. Não é possível salvar os dados do gráfico.")
            return False # Indica falha

        # Usar o filename_prefix (que é a região) e o símbolo para o nome do arquivo
        # Isso mantém a estrutura de nome de arquivo anterior: ex, br_PETR4_SA_chart.csv
        symbol_part_for_filename = ticker_complete.upper().replace(".", "_")
        filepath = os.path.join(DATA_DIR, f"{filename_prefix.lower()}_{symbol_part_for_filename}_chart.csv")
        hist_data.to_csv(filepath)
        print(f"Dados de {ticker_complete} salvos em {filepath}")
        return True # Indica sucesso
        
    except Exception as e:
        print(f"Erro ao buscar dados históricos para {symbol} com yfinance: {e}")
        return False # Indica falha

def fetch_and_save_stock_insights(symbol, region, filename_prefix):
    """Busca informações/insights de uma ação usando yfinance e salva em JSON.
    Para B3, o symbol deve ser no formato XXXXN.SA (ex: PETR4.SA).
    """
    try:
        ticker_complete = symbol
        print(f"Buscando insights para {ticker_complete} com yfinance...")
        ticker_obj = yf.Ticker(ticker_complete)
        insights_data = ticker_obj.info
        
        if not insights_data:
            print(f"Não foi possível obter insights para {ticker_complete} com yfinance (ticker.info retornou vazio).")
            # Tentar buscar um pouco de histórico para ver se o ticker é válido
            hist_check = ticker_obj.history(period="1d")
            if hist_check.empty:
                print(f"Ticker {ticker_complete} parece inválido ou não há dados disponíveis no yfinance.")
            return False # Indica falha

        symbol_part_for_filename = ticker_complete.upper().replace(".", "_")
        filepath = os.path.join(DATA_DIR, f"{filename_prefix.lower()}_{symbol_part_for_filename}_insights.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(insights_data, f, indent=4, ensure_ascii=False)
        print(f"Insights de {ticker_complete} salvos em {filepath}")
        return True # Indica sucesso
        
    except Exception as e:
        print(f"Erro ao buscar insights para {symbol} com yfinance: {e}")
        return False # Indica falha

def fetch_and_save_macro_data(indicator_code, country_code, country_name_display):
    """Placeholder para coleta de dados macroeconômicos. Requer uma fonte de dados pública e biblioteca apropriada."""
    print(f"\n--- Coleta de Dados Macroeconômicos para {country_name_display} ({indicator_code}) ---")
    print("AVISO: A coleta de dados macroeconômicos não está implementada nesta versão.")
    print("Para implementar, seria necessário integrar uma biblioteca como 'wbdata' para o World Bank ou similar.")
    return None

if __name__ == "__main__":
    # Teste para Ação Brasileira (B3)
    print("--- Testando Ação Brasileira (PETR4.SA) ---")
    success_chart_br = fetch_and_save_stock_chart(symbol="PETR4.SA", region="BR", filename_prefix="br")
    success_insights_br = fetch_and_save_stock_insights(symbol="PETR4.SA", region="BR", filename_prefix="br")
    print(f"Coleta PETR4.SA: Gráfico {'Sucesso' if success_chart_br else 'Falha'}, Insights {'Sucesso' if success_insights_br else 'Falha'}\n")

    # Teste para Ação Internacional
    print("--- Testando Ação Internacional (AAPL) ---")
    success_chart_us = fetch_and_save_stock_chart(symbol="AAPL", region="US", filename_prefix="us")
    success_insights_us = fetch_and_save_stock_insights(symbol="AAPL", region="US", filename_prefix="us")
    print(f"Coleta AAPL: Gráfico {'Sucesso' if success_chart_us else 'Falha'}, Insights {'Sucesso' if success_insights_us else 'Falha'}\n")

    # Teste para outra Ação Brasileira (MGLU3.SA)
    print("--- Testando Ação Brasileira (MGLU3.SA) ---")
    success_chart_mglu = fetch_and_save_stock_chart(symbol="MGLU3.SA", region="BR", filename_prefix="br")
    success_insights_mglu = fetch_and_save_stock_insights(symbol="MGLU3.SA", region="BR", filename_prefix="br")
    print(f"Coleta MGLU3.SA: Gráfico {'Sucesso' if success_chart_mglu else 'Falha'}, Insights {'Sucesso' if success_insights_mglu else 'Falha'}\n")

    # Teste para ticker inválido
    print("--- Testando Ticker Inválido (XYZW.SA) ---")
    success_chart_invalid = fetch_and_save_stock_chart(symbol="XYZW.SA", region="BR", filename_prefix="br")
    success_insights_invalid = fetch_and_save_stock_insights(symbol="XYZW.SA", region="BR", filename_prefix="br")
    print(f"Coleta XYZW.SA: Gráfico {'Sucesso' if success_chart_invalid else 'Falha'}, Insights {'Sucesso' if success_insights_invalid else 'Falha'}\n")

    # Dados Macroeconômicos (Chamada de exemplo, mas a função é placeholder)
    fetch_and_save_macro_data(indicator_code="NY.GDP.MKTP.CD", country_code="BRA", country_name_display="Brazil_GDP")

    print("\nColeta de dados (com yfinance e placeholder para macro) concluída.")

