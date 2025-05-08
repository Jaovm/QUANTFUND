import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import pandas as pd
import json
import os

# Inicializa o cliente da API
client = ApiClient()

# Define o diretório de dados
DATA_DIR = "."
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_and_save_stock_chart(symbol, region, filename_prefix):
    """Busca dados históricos de uma ação e salva em CSV."""
    try:
        print(f"Buscando dados históricos para {symbol}...")
        stock_data = client.call_api('YahooFinance/get_stock_chart', query={'symbol': symbol, 'region': region, 'interval': '1d', 'range': '5y', 'includeAdjustedClose': True})
        if stock_data and stock_data.get('chart') and stock_data['chart'].get('result'):
            result = stock_data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {})
            quotes = indicators.get('quote', [{}])[0]
            adjclose = indicators.get('adjclose', [{}])[0].get('adjclose', [])

            if not all([timestamps, quotes.get('open'), quotes.get('high'), quotes.get('low'), quotes.get('close'), quotes.get('volume'), adjclose]):
                print(f"Dados incompletos para {symbol}. Verifique a resposta da API.")
                # print(f"Resposta da API para {symbol}: {json.dumps(stock_data, indent=2)}")
                return

            df = pd.DataFrame({
                'Timestamp': pd.to_datetime(timestamps, unit='s'),
                'Open': quotes.get('open'),
                'High': quotes.get('high'),
                'Low': quotes.get('low'),
                'Close': quotes.get('close'),
                'Volume': quotes.get('volume'),
                'Adj Close': adjclose
            })
            df.set_index('Timestamp', inplace=True)
            filepath = os.path.join(DATA_DIR, f"{filename_prefix}_{symbol.replace('.', '_')}_chart.csv")
            df.to_csv(filepath)
            print(f"Dados de {symbol} salvos em {filepath}")
        else:
            print(f"Não foi possível obter dados para {symbol}. Resposta: {stock_data}")
    except Exception as e:
        print(f"Erro ao buscar dados para {symbol}: {e}")
        # print(f"Resposta da API (em caso de erro) para {symbol}: {json.dumps(stock_data, indent=2) if 'stock_data' in locals() else 'N/A'}")

def fetch_and_save_stock_insights(symbol, filename_prefix):
    """Busca insights de uma ação e salva em JSON (pois a estrutura é complexa)."""
    try:
        print(f"Buscando insights para {symbol}...")
        insights_data = client.call_api('YahooFinance/get_stock_insights', query={'symbol': symbol})
        if insights_data and insights_data.get('finance') and insights_data['finance'].get('result'):
            filepath = os.path.join(DATA_DIR, f"{filename_prefix}_{symbol.replace('.', '_')}_insights.json")
            with open(filepath, 'w') as f:
                json.dump(insights_data['finance']['result'], f, indent=4)
            print(f"Insights de {symbol} salvos em {filepath}")
        else:
            print(f"Não foi possível obter insights para {symbol}. Resposta: {insights_data}")
    except Exception as e:
        print(f"Erro ao buscar insights para {symbol}: {e}")

def fetch_and_save_macro_data(indicator, country_code, country_name):
    """Busca dados macroeconômicos e salva em CSV."""
    try:
        print(f"Buscando dados macroeconômicos para {country_name} ({indicator})...")
        macro_data = client.call_api('DataBank/indicator_data', query={'indicator': indicator, 'country': country_code})
        if macro_data and macro_data.get('data'):
            # A API retorna os dados como um dicionário de ano: valor
            # Vamos transformar isso em um DataFrame com colunas 'Ano' e 'Valor'
            data_dict = macro_data['data']
            df = pd.DataFrame(list(data_dict.items()), columns=['Ano', 'Valor'])
            df = df.dropna(subset=['Valor']) # Remove anos com valor nulo
            df['Ano'] = pd.to_numeric(df['Ano'])
            df.sort_values(by='Ano', inplace=True)
            df.set_index('Ano', inplace=True)
            filepath = os.path.join(DATA_DIR, f"macro_{country_code}_{indicator.replace('.', '_')}.csv")
            df.to_csv(filepath)
            print(f"Dados macroeconômicos de {country_name} salvos em {filepath}")
        else:
            print(f"Não foi possível obter dados macroeconômicos para {country_name}. Resposta: {macro_data}")
    except Exception as e:
        print(f"Erro ao buscar dados macroeconômicos para {country_name}: {e}")

if __name__ == "__main__":
    # Ação Brasileira
    fetch_and_save_stock_chart(symbol="PETR4.SA", region="BR", filename_prefix="br")
    fetch_and_save_stock_insights(symbol="PETR4.SA", filename_prefix="br")

    # Ação Internacional
    fetch_and_save_stock_chart(symbol="AAPL", region="US", filename_prefix="us")
    fetch_and_save_stock_insights(symbol="AAPL", filename_prefix="us")

    # Dados Macroeconômicos (PIB do Brasil)
    # Para encontrar o código do indicador: client.call_api('DataBank/indicator_list', query={'q': 'GDP at market prices (current US$)'})
    # Para o Brasil, o código é 'BRA'
    fetch_and_save_macro_data(indicator="NY.GDP.MKTP.CD", country_code="BRA", country_name="Brasil")
    fetch_and_save_macro_data(indicator="FP.CPI.TOTL.ZG", country_code="BRA", country_name="Brasil_Inflacao") # Inflação Anual Brasil
    fetch_and_save_macro_data(indicator="FR.INR.RINR", country_code="BRA", country_name="Brasil_Taxa_Juros_Real") # Taxa de Juros Real Brasil

    print("Coleta de dados concluída.")

