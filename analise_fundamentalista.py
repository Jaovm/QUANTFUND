import json
import os
import pandas as pd

DATA_DIR = "."

def load_stock_insights_data(symbol_filename_stem):
    """Carrega os dados de insights de uma ação a partir de um arquivo JSON."""
    filepath = os.path.join(DATA_DIR, f"{symbol_filename_stem}_insights.json")
    if not os.path.exists(filepath):
        print(f"Arquivo de insights não encontrado: {filepath}")
        return None
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Erro ao carregar dados de insights de {filepath}: {e}")
        return None

def extract_fundamental_indicators(insights_data, symbol):
    """Extrai e exibe indicadores fundamentalistas chave dos dados de insights do yfinance."""
    if insights_data is None:
        print(f"Dados de insights não fornecidos para {symbol}.")
        return None

    print(f"\n--- Análise Fundamentalista para {symbol} (yfinance) ---")
    
    fundamental_metrics = {}

    # Informações Gerais
    if insights_data.get("longName"):
        fundamental_metrics["Nome Longo"] = insights_data["longName"]
    if insights_data.get("symbol"):
        fundamental_metrics["Símbolo"] = insights_data["symbol"]
    if insights_data.get("currency"):
        fundamental_metrics["Moeda"] = insights_data["currency"]
    if insights_data.get("exchange"):
        fundamental_metrics["Bolsa"] = insights_data["exchange"]
    if insights_data.get("sector"):
        fundamental_metrics["Setor"] = insights_data["sector"]
    if insights_data.get("industry"):
        fundamental_metrics["Indústria"] = insights_data["industry"]
    if insights_data.get("fullTimeEmployees"):
        fundamental_metrics["Funcionários"] = insights_data["fullTimeEmployees"]

    # Métricas de Valuation
    if insights_data.get("marketCap") is not None:
        fundamental_metrics["Capitalização de Mercado"] = insights_data["marketCap"]
    if insights_data.get("trailingPE") is not None:
        fundamental_metrics["P/L (Trailing)"] = round(insights_data["trailingPE"], 2)
    if insights_data.get("forwardPE") is not None:
        fundamental_metrics["P/L (Forward)"] = round(insights_data["forwardPE"], 2)
    if insights_data.get("priceToBook") is not None:
        fundamental_metrics["P/VP (Price/Book)"] = round(insights_data["priceToBook"], 2)
    if insights_data.get("priceToSalesTrailing12Months") is not None:
        fundamental_metrics["P/S (Trailing 12M)"] = round(insights_data["priceToSalesTrailing12Months"], 2)
    if insights_data.get("enterpriseValue") is not None:
        fundamental_metrics["Valor da Empresa (EV)"] = insights_data["enterpriseValue"]
    if insights_data.get("enterpriseToRevenue") is not None:
        fundamental_metrics["EV/Receita"] = round(insights_data["enterpriseToRevenue"], 2)
    if insights_data.get("enterpriseToEbitda") is not None:
        fundamental_metrics["EV/EBITDA"] = round(insights_data["enterpriseToEbitda"], 2)

    # Métricas de Rentabilidade e Margens
    if insights_data.get("profitMargins") is not None:
        fundamental_metrics["Margem de Lucro"] = f"{round(insights_data['profitMargins'] * 100, 2)}%"
    if insights_data.get("grossMargins") is not None:
        fundamental_metrics["Margem Bruta"] = f"{round(insights_data['grossMargins'] * 100, 2)}%"
    if insights_data.get("ebitdaMargins") is not None:
        fundamental_metrics["Margem EBITDA"] = f"{round(insights_data['ebitdaMargins'] * 100, 2)}%"
    if insights_data.get("operatingMargins") is not None:
        fundamental_metrics["Margem Operacional"] = f"{round(insights_data['operatingMargins'] * 100, 2)}%"
    if insights_data.get("returnOnAssets") is not None:
        fundamental_metrics["ROA (Return on Assets)"] = f"{round(insights_data['returnOnAssets'] * 100, 2)}%"
    if insights_data.get("returnOnEquity") is not None:
        fundamental_metrics["ROE (Return on Equity)"] = f"{round(insights_data['returnOnEquity'] * 100, 2)}%"

    # Dividendos
    if insights_data.get("dividendYield") is not None:
        fundamental_metrics["Dividend Yield"] = f"{round(insights_data['dividendYield'] * 100, 2)}%"
    if insights_data.get("dividendRate") is not None:
        fundamental_metrics["Dividendo por Ação (Anual)"] = insights_data["dividendRate"]
    if insights_data.get("payoutRatio") is not None:
        fundamental_metrics["Payout Ratio"] = f"{round(insights_data['payoutRatio'] * 100, 2)}%"
    if insights_data.get("fiveYearAvgDividendYield") is not None:
        fundamental_metrics["Dividend Yield Médio (5 Anos)"] = round(insights_data["fiveYearAvgDividendYield"], 2)
    if insights_data.get("lastDividendValue") is not None:
        fundamental_metrics["Último Dividendo (Valor)"] = insights_data["lastDividendValue"]
    if insights_data.get("lastDividendDate") is not None: # Timestamp
        fundamental_metrics["Último Dividendo (Data)"] = pd.to_datetime(insights_data["lastDividendDate"], unit='s').strftime('%Y-%m-%d')

    # Recomendações de Analistas
    if insights_data.get("recommendationKey") is not None:
        fundamental_metrics["Recomendação Analistas (Chave)"] = insights_data["recommendationKey"].upper()
    if insights_data.get("recommendationMean") is not None:
        fundamental_metrics["Recomendação Analistas (Média)"] = insights_data["recommendationMean"]
    if insights_data.get("numberOfAnalystOpinions") is not None:
        fundamental_metrics["Número de Opiniões de Analistas"] = insights_data["numberOfAnalystOpinions"]
    if insights_data.get("targetMeanPrice") is not None:
        fundamental_metrics["Preço Alvo Médio"] = insights_data["targetMeanPrice"]
    if insights_data.get("targetHighPrice") is not None:
        fundamental_metrics["Preço Alvo Máximo"] = insights_data["targetHighPrice"]
    if insights_data.get("targetLowPrice") is not None:
        fundamental_metrics["Preço Alvo Mínimo"] = insights_data["targetLowPrice"]

    # Outras Métricas
    if insights_data.get("beta") is not None:
        fundamental_metrics["Beta"] = round(insights_data["beta"], 2)
    if insights_data.get("shortRatio") is not None:
        fundamental_metrics["Short Ratio"] = round(insights_data["shortRatio"], 2)
    if insights_data.get("bookValue") is not None:
        fundamental_metrics["Valor Patrimonial por Ação (Book Value)"] = round(insights_data["bookValue"], 2)
    if insights_data.get("earningsQuarterlyGrowth") is not None:
        fundamental_metrics["Crescimento Lucro (Trimestral)"] = f"{round(insights_data['earningsQuarterlyGrowth'] * 100, 2)}%"
    if insights_data.get("revenueGrowth") is not None: # Geralmente é TTM
        fundamental_metrics["Crescimento Receita (Anualizado)"] = f"{round(insights_data['revenueGrowth'] * 100, 2)}%"

    if not fundamental_metrics:
        print(f"Não foram encontrados dados fundamentalistas significativos nos insights do yfinance para {symbol}.")
        return None
    
    # Imprimir os resultados para fins de log (opcional, já que serão exibidos na UI)
    # for key, value in fundamental_metrics.items():
    #     print(f"  {key}: {value}")

    return fundamental_metrics

if __name__ == "__main__":
    # Certifique-se de que os arquivos JSON de exemplo (br_PETR4_SA_insights.json, us_AAPL_insights.json)
    # foram gerados usando o NOVO coleta_dados.py (com yfinance) antes de executar este teste.
    
    # Para gerar os arquivos de exemplo, execute no terminal (no diretório do projeto):
    # python coleta_dados.py

    all_fundamental_data = {}

    # Exemplo com PETR4.SA
    petr4_stem = "br_PETR4_SA"
    insights_petr4 = load_stock_insights_data(petr4_stem)
    if insights_petr4:
        print(f"Dados de insights carregados para {petr4_stem}")
        fund_petr4 = extract_fundamental_indicators(insights_petr4, "PETR4.SA")
        if fund_petr4:
            all_fundamental_data["PETR4.SA"] = fund_petr4
            print(f"Métricas fundamentalistas extraídas para PETR4.SA: {len(fund_petr4)} itens")
        else:
            print(f"Nenhuma métrica fundamentalista extraída para PETR4.SA")
    else:
        print(f"Falha ao carregar insights para {petr4_stem}. Certifique-se que o arquivo JSON existe e foi gerado pelo novo coleta_dados.py.")

    # Exemplo com AAPL
    aapl_stem = "us_AAPL"
    insights_aapl = load_stock_insights_data(aapl_stem)
    if insights_aapl:
        print(f"Dados de insights carregados para {aapl_stem}")
        fund_aapl = extract_fundamental_indicators(insights_aapl, "AAPL")
        if fund_aapl:
            all_fundamental_data["AAPL"] = fund_aapl
            print(f"Métricas fundamentalistas extraídas para AAPL: {len(fund_aapl)} itens")
        else:
            print(f"Nenhuma métrica fundamentalista extraída para AAPL")
    else:
        print(f"Falha ao carregar insights para {aapl_stem}. Certifique-se que o arquivo JSON existe e foi gerado pelo novo coleta_dados.py.")
    
    if all_fundamental_data:
        output_filepath = os.path.join(DATA_DIR, "fundamental_analysis_summary_yfinance.json")
        with open(output_filepath, 'w') as f:
            json.dump(all_fundamental_data, f, indent=4, ensure_ascii=False)
        print(f"\nResumo da análise fundamentalista (yfinance) salvo em: {output_filepath}")
    else:
        print("\nNenhum dado fundamentalista compilado para salvar.")

    print("\nScript de análise fundamentalista (adaptado para yfinance) concluído.")

