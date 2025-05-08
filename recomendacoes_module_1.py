import pandas as pd
import json
import os

DATA_DIR = "."

def load_processed_data(ticker_stem):
    """Carrega dados quantitativos e fundamentalistas processados."""
    quant_file = os.path.join(DATA_DIR, f"{ticker_stem}_quant_analysis.csv")
    insights_file = os.path.join(DATA_DIR, f"{ticker_stem}_insights.json")
    
    df_quant = None
    insights_data = None

    if os.path.exists(quant_file):
        try:
            df_quant = pd.read_csv(quant_file, index_col='Timestamp', parse_dates=True)
        except Exception as e:
            print(f"Erro ao carregar dados quantitativos de {quant_file}: {e}")
            
    if os.path.exists(insights_file):
        try:
            with open(insights_file, 'r') as f:
                insights_data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar insights de {insights_file}: {e}")
            
    return df_quant, insights_data

def analyze_macro_scenario():
    """Analisa o cenário macroeconômico (placeholder puro)."""
    print("\n--- Análise de Cenário Macroeconômico (Placeholder) ---")
    
    macro_outlook = {
        "BR": "Neutro",
        "US": "Neutro",
        "detail": "A coleta e análise de dados macroeconômicos detalhados não está implementada nesta versão. Usando outlook padrão."
    }
    
    print(f"Cenário Macroeconômico (Placeholder): {macro_outlook}")
    return macro_outlook

def generate_recommendations(tickers_stems, macro_scenario):
    """Gera recomendações com base em análises e cenário macro."""
    print("\n--- Geração de Recomendações ---")
    recommendations = []

    for stem in tickers_stems:
        # Extrai ticker e país do stem. Ex: "br_PETR4_SA" -> ticker="PETR4.SA", country_code="BR"
        parts = stem.split('_', 1)
        country_code = parts[0].upper()
        ticker_name = parts[1].replace('_', '.') if len(parts) > 1 else stem # Garante que o ticker seja reconstruído corretamente
        
        df_quant, insights = load_processed_data(stem)
        
        if df_quant is None:
            print(f"Dados quantitativos não encontrados para {ticker_name}, pulando recomendação.")
            recommendations.append({
                "ticker": ticker_name,
                "recomendacao": "Dados Insuficientes",
                "score": 0,
                "justificativas": ["Dados quantitativos não puderam ser carregados."]
            })
            continue

        recommendation_score = 0
        reasons = []

        # Análise Quantitativa (RSI)
        # Tentativa de encontrar a coluna RSI, independentemente do nome exato da janela (ex: RSI_14, RSI)
        rsi_col_found = None
        for col_name_rsi in df_quant.columns:
            if 'RSI' in col_name_rsi.upper():
                rsi_col_found = col_name_rsi
                break
        
        if rsi_col_found and not df_quant[rsi_col_found].empty:
            last_rsi = df_quant[rsi_col_found].iloc[-1]
            reasons.append(f"RSI ({rsi_col_found}) atual: {last_rsi:.2f}")
            if last_rsi < 30:
                recommendation_score += 2 
                reasons.append("Ativo sobrevendido (RSI < 30)")
            elif last_rsi > 70:
                recommendation_score -= 1 
                reasons.append("Ativo sobrecomprado (RSI > 70)")
            else:
                recommendation_score += 1 
        else:
            reasons.append("RSI não disponível ou dados vazios.")
        
        # Análise Fundamentalista (Rating de Analistas, se houver)
        # Adicionado tratamento para quando 'recommendation' ou 'rating' não existem
        if insights and isinstance(insights.get("recommendation"), dict) and insights["recommendation"].get("rating"):
            rating = insights["recommendation"]["rating"].upper()
            reasons.append(f"Rating de Analistas: {rating}")
            if rating in ["STRONG BUY", "BUY", "OUTPERFORM"]:
                recommendation_score += 2
            elif rating in ["SELL", "UNDERPERFORM"]:
                recommendation_score -=1
            elif rating == "HOLD":
                recommendation_score +=0
        else:
            reasons.append("Rating de analistas não disponível.")
        
        # Cenário Macroeconômico do País
        country_macro_outlook = macro_scenario.get(country_code, "Neutro")
        reasons.append(f"Cenário Macro ({country_code}): {country_macro_outlook}")
        if "Positivo" in country_macro_outlook:
            recommendation_score += 1
        elif "Negativo" in country_macro_outlook:
            recommendation_score -= 1

        final_recommendation = "Manter/Neutro"
        if recommendation_score >= 3:
            final_recommendation = "Comprar"
        elif recommendation_score <= 0:
            final_recommendation = "Vender/Evitar"
            
        recommendations.append({
            "ticker": ticker_name,
            "recomendacao": final_recommendation,
            "score": recommendation_score,
            "justificativas": reasons
        })
        
        print(f"Recomendação para {ticker_name}: {final_recommendation} (Score: {recommendation_score})")
        for reason in reasons:
            print(f"  - {reason}")

    return recommendations

if __name__ == "__main__":
    macro_data = analyze_macro_scenario()
    
    # Certifique-se que os arquivos de teste existem ou crie-os
    # Exemplo: criar um dummy br_PETR4_SA_quant_analysis.csv e br_PETR4_SA_insights.json
    # E um dummy us_AAPL_quant_analysis.csv e us_AAPL_insights.json
    
    tickers_to_analyze = ["br_PETR4_SA", "us_AAPL"]
    recs = generate_recommendations(tickers_to_analyze, macro_data)
    
    if recs:
        output_filepath = os.path.join(DATA_DIR, "recomendacoes_geradas.json")
        with open(output_filepath, 'w') as f:
            json.dump(recs, f, indent=4)
        print(f"\nRecomendações salvas em: {output_filepath}")

    print("\nScript de recomendações concluído.")

