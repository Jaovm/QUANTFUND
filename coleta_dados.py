import yfinance as yf
import pandas as pd
import json
import os

# Define o diretório de dados
DATA_DIR = "."
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_and_save_stock_chart(symbol, region, filename_prefix):
    """Busca dados históricos de uma ação usando yfinance e salva em CSV."""
    try:
        print(f"Buscando dados históricos para {symbol} com yfinance...")
        ticker = yf.Ticker(symbol)
        # Para o yfinance, a 'region' não é um parâmetro direto para history.
        # O ticker em si (ex: "PETR4.SA") já costuma incluir a informação de mercado.
        hist_data = ticker.history(period="5y", interval="1d", auto_adjust=False, actions=False) # auto_adjust=False para ter 'Adj Close'
        
        if hist_data.empty:
            print(f"Não foi possível obter dados históricos para {symbol} com yfinance.")
            return

        # yfinance retorna 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'.
        # Precisamos garantir que 'Adj Close' esteja presente ou calculá-lo se necessário, 
        # mas yfinance geralmente o fornece se auto_adjust=False e há dados suficientes.
        # Se 'Adj Close' não estiver lá, podemos usar 'Close' como um fallback ou tentar calcular.
        # No entanto, o yfinance.Ticker(symbol).history() já deve ter o Adj Close se disponível.
        # Vamos renomear o índice para 'Timestamp' para consistência com o código anterior.
        hist_data.index.name = "Timestamp"
        
        # Selecionar e renomear colunas para manter o formato esperado pelo restante do sistema, se possível.
        # O yfinance já retorna as colunas com os nomes corretos (Open, High, Low, Close, Volume).
        # A coluna 'Adj Close' é crucial.
        if 'Adj Close' not in hist_data.columns and 'Close' in hist_data.columns:
             print(f"Coluna 'Adj Close' não encontrada para {symbol}. Usando 'Close' como fallback para 'Adj Close'.")
             hist_data['Adj Close'] = hist_data['Close'] # Fallback simples
        elif 'Adj Close' not in hist_data.columns:
            print(f"Colunas 'Adj Close' e 'Close' não encontradas para {symbol}.")
            return

        filepath = os.path.join(DATA_DIR, f"{filename_prefix}_{symbol.replace('.', '_')}_chart.csv")
        hist_data.to_csv(filepath)
        print(f"Dados de {symbol} salvos em {filepath}")
        
    except Exception as e:
        print(f"Erro ao buscar dados históricos para {symbol} com yfinance: {e}")

def fetch_and_save_stock_insights(symbol, region, filename_prefix): # region pode não ser usado por yf.info
    """Busca informações/insights de uma ação usando yfinance e salva em JSON."""
    try:
        print(f"Buscando insights para {symbol} com yfinance...")
        ticker = yf.Ticker(symbol)
        insights_data = ticker.info
        
        if not insights_data:
            print(f"Não foi possível obter insights para {symbol} com yfinance (ticker.info retornou vazio).")
            # Tentar buscar um pouco de histórico para ver se o ticker é válido
            hist_check = ticker.history(period="1d")
            if hist_check.empty:
                print(f"Ticker {symbol} parece inválido ou não há dados disponíveis no yfinance.")
            return

        # A estrutura de ticker.info é diferente da API anterior.
        # O módulo analise_fundamentalista.py precisará ser adaptado para ler este novo formato.
        filepath = os.path.join(DATA_DIR, f"{filename_prefix}_{symbol.replace('.', '_')}_insights.json")
        with open(filepath, 'w') as f:
            json.dump(insights_data, f, indent=4)
        print(f"Insights de {symbol} salvos em {filepath}")
        
    except Exception as e:
        print(f"Erro ao buscar insights para {symbol} com yfinance: {e}")

def fetch_and_save_macro_data(indicator_code, country_code, country_name_display):
    """Placeholder para coleta de dados macroeconômicos. Requer uma fonte de dados pública e biblioteca apropriada."""
    print(f"\n--- Coleta de Dados Macroeconômicos para {country_name_display} ({indicator_code}) ---")
    print("AVISO: A coleta de dados macroeconômicos (ex: DataBank) não está implementada nesta versão, pois dependia de uma API interna.")
    print("Para implementar, seria necessário integrar uma biblioteca como 'wbdata' para o World Bank ou similar.")
    print("Por enquanto, esta função não coletará dados.")
    
    # Exemplo de como seria com wbdata (não será executado, apenas para ilustração)
    # try:
    #     import wbdata
    #     data_date = (pd.Timestamp.now() - pd.DateOffset(years=20)).strftime('%Y'), pd.Timestamp.now().strftime('%Y')
    #     df_macro = wbdata.get_dataframe({indicator_code: country_name_display}, country=country_code, data_date=data_date, convert_date=True)
    #     if df_macro.empty:
    #         print(f"Não foram encontrados dados para {indicator_code} para {country_code}")
    #         return
    #     df_macro.index.name = 'Ano'
    #     df_macro.rename(columns={country_name_display: 'Valor'}, inplace=True)
    #     df_macro.sort_index(inplace=True)
    #     filepath = os.path.join(DATA_DIR, f"macro_{country_code}_{indicator_code.replace('.', '_')}.csv")
    #     df_macro.to_csv(filepath)
    #     print(f"Dados macroeconômicos de {country_name_display} ({indicator_code}) salvos em {filepath} (EXEMPLO)")
    # except ImportError:
    #     print("Biblioteca 'wbdata' não instalada. Necessária para coletar dados do World Bank.")
    # except Exception as e:
    #     print(f"Erro ao tentar buscar dados macro (exemplo com wbdata): {e}")
    return None # Indica que não foram coletados dados

if __name__ == "__main__":
    # Ação Brasileira
    fetch_and_save_stock_chart(symbol="PETR4.SA", region="BR", filename_prefix="br")
    fetch_and_save_stock_insights(symbol="PETR4.SA", region="BR", filename_prefix="br")

    # Ação Internacional
    fetch_and_save_stock_chart(symbol="AAPL", region="US", filename_prefix="us")
    fetch_and_save_stock_insights(symbol="AAPL", region="US", filename_prefix="us")

    # Dados Macroeconômicos (Exemplo de chamada, mas a função está como placeholder)
    fetch_and_save_macro_data(indicator_code="NY.GDP.MKTP.CD", country_code="BRA", country_name_display="Brazil_GDP")
    fetch_and_save_macro_data(indicator_code="FP.CPI.TOTL.ZG", country_code="BRA", country_name_display="Brazil_Inflation")

    print("\nColeta de dados (com yfinance e placeholder para macro) concluída.")

