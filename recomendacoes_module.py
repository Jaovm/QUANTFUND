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
    """Analisa o cenário macroeconômico (placeholder/simplificado por enquanto)."""
    # TODO: Integrar dados macroeconômicos reais quando a coleta for bem-sucedida.
    # Por enquanto, vamos simular um cenário.
    print("\n--- Análise de Cenário Macroeconômico (Simplificada) ---")
    
    # Exemplo: Tentar carregar dados de inflação do Brasil se existirem
    inflation_file_br = os.path.join(DATA_DIR, "macro_BRA_FP_CPI_TOTL_ZG.csv")
    gdp_file_br = os.path.join(DATA_DIR, "macro_BRA_NY_GDP_MKTP_CD.csv")
    interest_rate_br = os.path.join(DATA_DIR, "macro_BRA_FR_INR_RINR.csv")

    macro_outlook = {
        "BR": "Neutro", # Default
        "US": "Neutro"  # Default
    }
    detailed_br_analysis = []

    if os.path.exists(inflation_file_br):
        try:
            df_inflation_br = pd.read_csv(inflation_file_br, index_col='Ano')
            if not df_inflation_br.empty:
                last_inflation = df_inflation_br['Valor'].iloc[-1]
                detailed_br_analysis.append(f"Última inflação anual (Brasil): {last_inflation:.2f}%")
                if last_inflation > 7:
                    macro_outlook["BR"] = "Negativo (Inflação Alta)"
                elif last_inflation < 3:
                    macro_outlook["BR"] = "Positivo (Inflação Baixa)"
                else:
                    macro_outlook["BR"] = "Neutro (Inflação Controlada)"
        except Exception as e:
            detailed_br_analysis.append(f"Erro ao processar dados de inflação do Brasil: {e}")
    else:
        detailed_br_analysis.append("Dados de inflação do Brasil não encontrados.")

    # Adicionar mais análises macro se os dados estiverem disponíveis
    # ... (PIB, Taxa de Juros, etc.)

    print(f"Cenário Macroeconômico Brasil: {macro_outlook['BR']}")
    for detail in detailed_br_analysis:
        print(f"  - {detail}")
    print(f"Cenário Macroeconômico US: {macro_outlook['US']} (Análise detalhada pendente)")
    
    return macro_outlook

def generate_recommendations(tickers_stems, macro_scenario):
    """Gera recomendações com base em análises e cenário macro."""
    print("\n--- Geração de Recomendações ---")
    recommendations = []

    for stem in tickers_stems:
        ticker_name = stem.split('_')[1] # e.g., PETR4.SA ou AAPL
        country_code = stem.split('_')[0].upper() # BR ou US
        
        df_quant, insights = load_processed_data(stem)
        
        if df_quant is None:
            print(f"Dados quantitativos não encontrados para {ticker_name}, pulando recomendação.")
            continue

        # Lógica de recomendação simples (exemplo)
        # Considerar RSI e recomendação de analistas (se disponível)
        # E o cenário macro do país do ativo
        
        recommendation_score = 0
        reasons = []

        # Análise Quantitativa (RSI)
        if 'RSI_14' in df_quant.columns and not df_quant['RSI_14'].empty:
            last_rsi = df_quant['RSI_14'].iloc[-1]
            reasons.append(f"RSI(14) atual: {last_rsi:.2f}")
            if last_rsi < 30:
                recommendation_score += 2 # Sobre-vendido, potencial compra
                reasons.append("Ativo sobrevendido (RSI < 30)")
            elif last_rsi > 70:
                recommendation_score -= 1 # Sobre-comprado, cautela
                reasons.append("Ativo sobrecomprado (RSI > 70)")
            else:
                recommendation_score += 1 # Neutro
        
        # Análise Fundamentalista (Rating de Analistas, se houver)
        if insights and insights.get("recommendation") and insights["recommendation"].get("rating"):
            rating = insights["recommendation"]["rating"].upper()
            reasons.append(f"Rating de Analistas: {rating}")
            if rating in ["STRONG BUY", "BUY", "OUTPERFORM"]:
                recommendation_score += 2
            elif rating in ["SELL", "UNDERPERFORM"]:
                recommendation_score -=1
            elif rating == "HOLD":
                recommendation_score +=0
        
        # Cenário Macroeconômico do País
        country_macro_outlook = macro_scenario.get(country_code, "Neutro")
        reasons.append(f"Cenário Macro ({country_code}): {country_macro_outlook}")
        if "Positivo" in country_macro_outlook:
            recommendation_score += 1
        elif "Negativo" in country_macro_outlook:
            recommendation_score -= 1

        # Decisão final de recomendação (exemplo)
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
    # Tentar coletar dados macroeconômicos novamente (apenas para teste local, idealmente seria um passo separado)
    # Comente ou remova esta parte se a coleta de dados macro ainda estiver falhando ou para evitar chamadas repetidas.
    # from coleta_dados import fetch_and_save_macro_data
    # print("Tentando atualizar dados macroeconômicos...")
    # fetch_and_save_macro_data(indicator="FP.CPI.TOTL.ZG", country_code="BRA", country_name="Brasil_Inflacao")
    # fetch_and_save_macro_data(indicator="NY.GDP.MKTP.CD", country_code="BRA", country_name="Brasil_PIB")
    # fetch_and_save_macro_data(indicator="FR.INR.RINR", country_code="BRA", country_name="Brasil_Taxa_Juros_Real")
    
    macro_data = analyze_macro_scenario()
    
    tickers_to_analyze = ["br_PETR4_SA", "us_AAPL"]
    recs = generate_recommendations(tickers_to_analyze, macro_data)
    
    # Salvar recomendações
    if recs:
        output_filepath = os.path.join(DATA_DIR, "recomendacoes_geradas.json")
        with open(output_filepath, 'w') as f:
            json.dump(recs, f, indent=4)
        print(f"\nRecomendações salvas em: {output_filepath}")

    print("\nScript de recomendações concluído.")

