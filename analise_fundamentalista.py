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
    """Extrai e exibe indicadores fundamentalistas chave dos dados de insights."""
    if insights_data is None:
        return None

    print(f"\n--- Análise Fundamentalista para {symbol} ---")
    
    fundamental_metrics = {}
    
    # Valuation (P/E, P/S, etc. podem estar aqui ou precisar de cálculo com dados de cotação)
    valuation = insights_data.get("instrumentInfo", {}).get("valuation")
    if valuation:
        print("\nValuation:")
        for key, value in valuation.items():
            display_key = key.replace('Value', ' Value').title()
            if isinstance(value, (str, int, float)):
                print(f"  {display_key}: {value}")
                fundamental_metrics[f"Valuation_{key}"] = value
            elif isinstance(value, dict) and 'fmt' in value: # Yahoo Finance often uses 'fmt' for formatted value
                print(f"  {display_key}: {value['fmt']}")
                fundamental_metrics[f"Valuation_{key}"] = value['fmt']

    # Company Snapshot (Pode ter Dividend Yield, Payout Ratio, etc.)
    company_snapshot = insights_data.get("companySnapshot")
    if company_snapshot:
        company_data = company_snapshot.get("company", {})
        # Tentativa de extrair dados de dividendos.
        if company_data.get("dividends") is not None:
            print(f"  Dividendos (Score): {company_data['dividends']}") # This is likely a score, not direct yield
            fundamental_metrics["Company_Dividend_Score"] = company_data['dividends']
        
    # Recommendation (Target Price, Rating)
    recommendation = insights_data.get("recommendation")
    if recommendation:
        print("\nRecomendações de Analistas:")
        if recommendation.get("targetPrice") is not None:
            print(f"  Preço Alvo: {recommendation['targetPrice']}")
            fundamental_metrics["Recommendation_TargetPrice"] = recommendation['targetPrice']
        if recommendation.get("provider") is not None:
            print(f"  Provedor: {recommendation['provider']}")
            fundamental_metrics["Recommendation_Provider"] = recommendation['provider']
        if recommendation.get("rating") is not None:
            print(f"  Rating: {recommendation['rating']}")
            fundamental_metrics["Recommendation_Rating"] = recommendation['rating']

    if not fundamental_metrics:
        print("Não foram encontrados dados fundamentalistas significativos nos insights fornecidos por esta API.")
        print("Métricas como P/L, P/VP, EV/EBITDA, Dividend Yield direto podem requerer outras fontes/endpoints.")

    return fundamental_metrics

if __name__ == "__main__":
    all_fundamental_data = {}

    # Exemplo com PETR4.SA
    petr4_stem = "br_PETR4_SA"
    insights_petr4 = load_stock_insights_data(petr4_stem)
    if insights_petr4:
        fund_petr4 = extract_fundamental_indicators(insights_petr4, petr4_stem.split('_')[1])
        if fund_petr4:
            all_fundamental_data[petr4_stem.split('_')[1]] = fund_petr4

    # Exemplo com AAPL
    aapl_stem = "us_AAPL"
    insights_aapl = load_stock_insights_data(aapl_stem)
    if insights_aapl:
        fund_aapl = extract_fundamental_indicators(insights_aapl, aapl_stem.split('_')[1])
        if fund_aapl:
            all_fundamental_data[aapl_stem.split('_')[1]] = fund_aapl
    
    # Salvar os dados fundamentalistas compilados
    if all_fundamental_data:
        output_filepath = os.path.join(DATA_DIR, "fundamental_analysis_summary.json")
        with open(output_filepath, 'w') as f:
            json.dump(all_fundamental_data, f, indent=4)
        print(f"\nResumo da análise fundamentalista salvo em: {output_filepath}")

    print("\nScript de análise fundamentalista concluído.")

