import pandas as pd
import json
import os

DATA_DIR = "."

def load_processed_data(ticker_stem):
    """Carrega dados quantitativos e fundamentalistas processados."""
    quant_file = os.path.join(DATA_DIR, f"{ticker_stem}_quant_analysis.csv")
    # O insights_file agora é gerado pelo yfinance no coleta_dados.py
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
                insights_data = json.load(f) # Carrega o JSON gerado por yfinance
        except Exception as e:
            print(f"Erro ao carregar insights de {insights_file}: {e}")
            
    return df_quant, insights_data

def analyze_macro_scenario():
    """Analisa o cenário macroeconômico (placeholder/simplificado)."""
    print("\n--- Análise de Cenário Macroeconômico (Simplificada) ---")
    
    macro_outlook = {
        "BR": "Neutro", 
        "US": "Neutro",
        "detail": "A coleta de dados macroeconômicos detalhados não está implementada nesta versão. Usando outlook padrão."
    }
    
    # Tenta carregar dados de inflação do Brasil se existirem (exemplo, mas coleta_dados.py é placeholder para macro)
    inflation_file_br = os.path.join(DATA_DIR, "macro_BRA_FP.CPI.TOTL.ZG.csv") # Nome de arquivo exemplo
    if os.path.exists(inflation_file_br):
        try:
            df_inflation_br = pd.read_csv(inflation_file_br, index_col='Ano')
            if not df_inflation_br.empty and 'Valor' in df_inflation_br.columns:
                last_inflation = df_inflation_br['Valor'].iloc[-1]
                detail_br = f"Última inflação anual (Brasil, se dados disponíveis): {last_inflation:.2f}%"
                if last_inflation > 7:
                    macro_outlook["BR"] = "Negativo (Inflação Alta)"
                elif last_inflation < 3:
                    macro_outlook["BR"] = "Positivo (Inflação Baixa)"
                else:
                    macro_outlook["BR"] = "Neutro (Inflação Controlada)"
                macro_outlook["detail_br"] = detail_br
            else:
                 macro_outlook["detail_br"] = "Dados de inflação do Brasil encontrados, mas em formato inesperado."
        except Exception as e:
            macro_outlook["detail_br"] = f"Erro ao processar dados de inflação do Brasil: {e}"
    else:
        macro_outlook["detail_br"] = "Arquivo de dados de inflação do Brasil (macro_BRA_FP.CPI.TOTL.ZG.csv) não encontrado."

    print(f"Cenário Macroeconômico Brasil: {macro_outlook['BR']}")
    print(f"Cenário Macroeconômico US: {macro_outlook['US']}")
    print(f"Detalhe: {macro_outlook.get('detail_br', macro_outlook['detail'])}")
    
    return macro_outlook

def generate_recommendations(tickers_stems, macro_scenario):
    """Gera recomendações com base em análises e cenário macro, adaptado para yfinance insights."""
    print("\n--- Geração de Recomendações (yfinance) ---")
    recommendations = []

    for stem in tickers_stems:
        ticker_name_from_stem = stem.split('_', 1)[1].replace('_', ".") # Ex: br_PETR4_SA -> PETR4.SA
        country_code = stem.split('_')[0].upper() # BR ou US
        
        df_quant, insights = load_processed_data(stem)
        
        if df_quant is None:
            print(f"Dados quantitativos não encontrados para {ticker_name_from_stem} (stem: {stem}), pulando recomendação.")
            recommendations.append({
                "ticker": ticker_name_from_stem,
                "recomendacao": "Dados Insuficientes",
                "score": 0,
                "justificativas": ["Dados quantitativos ausentes."]
            })
            continue

        recommendation_score = 0
        reasons = []

        # Análise Quantitativa (RSI)
        if \'RSI\' in df_quant.columns and not df_quant[\'RSI\'].empty:
            last_rsi = df_quant[\'RSI\'].iloc[-1]
            reasons.append(f"RSI atual: {last_rsi:.2f}")
            if last_rsi < 30:
                recommendation_score += 2 
                reasons.append("Ativo sobrevendido (RSI < 30)")
            elif last_rsi > 70:
                recommendation_score -= 1 
                reasons.append("Ativo sobrecomprado (RSI > 70)")
            else:
                recommendation_score += 1 
        else:
            reasons.append("RSI não disponível nos dados quantitativos.")
        
        # Análise Fundamentalista (Rating de Analistas do yfinance)
        if insights and insights.get("recommendationKey"):
            rating_key = insights.get("recommendationKey").lower()
            reasons.append(f"Recomendação de Analistas (yfinance): {rating_key.replace(\'_\', \' \').title()}")
            if rating_key in ["strong_buy", "buy"]:
                recommendation_score += 2
            elif rating_key in ["sell", "strong_sell", "underperform"]:
                recommendation_score -=1
            elif rating_key == "hold":
                recommendation_score +=0
            # other keys like "none" or "no_opinion" might not adjust score
        else:
            reasons.append("Recomendação de analistas (recommendationKey) não disponível nos insights do yfinance.")
        
        # Cenário Macroeconômico do País
        country_macro_outlook_detail = macro_scenario.get(country_code, "Neutro")
        # A estrutura de macro_scenario é agora um dict com BR, US, detail, detail_br
        # Usar o outlook específico do país
        actual_country_outlook = "Neutro" # Default
        if country_code == "BR":
            actual_country_outlook = macro_scenario.get("BR", "Neutro")
        elif country_code == "US": # Exemplo para US, pode ser mais genérico
            actual_country_outlook = macro_scenario.get("US", "Neutro")
        
        reasons.append(f"Cenário Macro ({country_code}): {actual_country_outlook}")
        if "Positivo" in actual_country_outlook:
            recommendation_score += 1
        elif "Negativo" in actual_country_outlook:
            recommendation_score -= 1

        final_recommendation = "Manter/Neutro"
        if recommendation_score >= 3:
            final_recommendation = "Comprar"
        elif recommendation_score <= 0:
            final_recommendation = "Vender/Evitar"
            
        recommendations.append({
            "ticker": ticker_name_from_stem,
            "recomendacao": final_recommendation,
            "score": recommendation_score,
            "justificativas": reasons
        })
        
        print(f"Recomendação para {ticker_name_from_stem}: {final_recommendation} (Score: {recommendation_score})")
        for reason in reasons:
            print(f"  - {reason}")

    return recommendations

if __name__ == "__main__":
    # Certifique-se que os arquivos CSV e JSON de exemplo (br_PETR4_SA_*, us_AAPL_*)
    # foram gerados usando o NOVO coleta_dados.py (com yfinance) e o NOVO analise_quantitativa.py
    # antes de executar este teste.
    # python coleta_dados.py
    # python analise_quantitativa.py (se ele salva algo que este módulo lê diretamente, mas parece que não)
    
    print("Executando teste do módulo de recomendações adaptado para yfinance...")
    
    # Simular dados coletados e analisados que o app.py teria no session_state
    # Gerar arquivos de exemplo se não existirem
    if not os.path.exists("br_PETR4_SA_chart.csv") or not os.path.exists("br_PETR4_SA_insights.json"):
        print("Gerando arquivos de exemplo para PETR4.SA...")
        import coleta_dados as cd
        cd.fetch_and_save_stock_chart(symbol="PETR4.SA", region="BR", filename_prefix="br")
        cd.fetch_and_save_stock_insights(symbol="PETR4.SA", region="BR", filename_prefix="br")
    
    if not os.path.exists("us_AAPL_chart.csv") or not os.path.exists("us_AAPL_insights.json"):
        print("Gerando arquivos de exemplo para AAPL...")
        import coleta_dados as cd
        cd.fetch_and_save_stock_chart(symbol="AAPL", region="US", filename_prefix="us")
        cd.fetch_and_save_stock_insights(symbol="AAPL", region="US", filename_prefix="us")

    # Gerar arquivos de análise quantitativa de exemplo
    import analise_quantitativa as aq
    df_petr4_hist = aq.load_stock_chart_data("br_PETR4_SA")
    if df_petr4_hist is not None:
        df_petr4_hist[\'SMA_20\'] = aq.calculate_moving_average(df_petr4_hist, 20)
        df_petr4_hist[\'SMA_50\'] = aq.calculate_moving_average(df_petr4_hist, 50)
        df_petr4_hist[\'RSI\'] = aq.calculate_rsi(df_petr4_hist, 14)
        df_petr4_hist.to_csv("br_PETR4_SA_quant_analysis.csv")
        print("Arquivo br_PETR4_SA_quant_analysis.csv gerado/atualizado.")

    df_aapl_hist = aq.load_stock_chart_data("us_AAPL")
    if df_aapl_hist is not None:
        df_aapl_hist[\'SMA_20\'] = aq.calculate_moving_average(df_aapl_hist, 20)
        df_aapl_hist[\'SMA_50\'] = aq.calculate_moving_average(df_aapl_hist, 50)
        df_aapl_hist[\'RSI\'] = aq.calculate_rsi(df_aapl_hist, 14)
        df_aapl_hist.to_csv("us_AAPL_quant_analysis.csv")
        print("Arquivo us_AAPL_quant_analysis.csv gerado/atualizado.")

    macro_data = analyze_macro_scenario()
    
    tickers_to_analyze = ["br_PETR4_SA", "us_AAPL"]
    # Verificar se os arquivos _quant_analysis.csv existem para os tickers_to_analyze
    missing_quant_files = False
    for stem_check in tickers_to_analyze:
        if not os.path.exists(f"{stem_check}_quant_analysis.csv"):
            print(f"AVISO: Arquivo {stem_check}_quant_analysis.csv não encontrado. A recomendação para este ativo pode ser afetada.")
            missing_quant_files = True
    
    if missing_quant_files:
        print("Execute o módulo analise_quantitativa.py ou certifique-se que os arquivos _quant_analysis.csv são gerados antes das recomendações.")

    recs = generate_recommendations(tickers_to_analyze, macro_data)
    
    if recs:
        output_filepath = os.path.join(DATA_DIR, "recomendacoes_geradas_yfinance.json")
        with open(output_filepath, \'w\', encoding=\'utf-8\') as f:
            json.dump(recs, f, indent=4, ensure_ascii=False)
        print(f"\nRecomendações (yfinance) salvas em: {output_filepath}")
    else:
        print("\nNenhuma recomendação gerada.")

    print("\nScript de recomendações (adaptado para yfinance) concluído.")

