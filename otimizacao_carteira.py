import pandas as pd
import numpy as np
import json
import os
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions

DATA_DIR = "."

def load_stock_prices_for_optimization(ticker_stems):
    """Carrega os preços de fechamento ajustados para uma lista de tickers."""
    all_prices = pd.DataFrame()
    for stem in ticker_stems:
        quant_file = os.path.join(DATA_DIR, f"{stem}_quant_analysis.csv")
        if os.path.exists(quant_file):
            try:
                df_quant = pd.read_csv(quant_file, index_col='Timestamp', parse_dates=True)
                ticker_name = stem.split('_')[1]
                if 'Adj Close' in df_quant.columns:
                    # Renomear para o nome do ticker para PyPortfolioOpt
                    current_prices = df_quant[["Adj Close"]].rename(columns={"Adj Close": ticker_name})
                    if all_prices.empty:
                        all_prices = current_prices
                    else:
                        all_prices = all_prices.join(current_prices, how='outer')
            except Exception as e:
                print(f"Erro ao carregar dados quantitativos de {quant_file}: {e}")
        else:
            print(f"Arquivo não encontrado: {quant_file}")
    
    if not all_prices.empty:
        all_prices.fillna(method='ffill', inplace=True) # Preenche NaNs com o último valor válido
        all_prices.dropna(inplace=True) # Remove linhas restantes com NaN (geralmente no início)
    return all_prices

def optimize_portfolio(prices_df, optimization_method="max_sharpe"):
    """Otimiza a carteira usando o método especificado."""
    if prices_df.empty or len(prices_df.columns) < 2:
        print("Dados de preços insuficientes para otimização (necessário pelo menos 2 ativos).")
        return None, None

    print(f"\n--- Otimização de Carteira ({optimization_method}) ---")
    
    # Calcular retornos esperados e matriz de covariância
    try:
        mu = expected_returns.mean_historical_return(prices_df)
        S = risk_models.sample_cov(prices_df)
    except Exception as e:
        print(f"Erro ao calcular retornos esperados ou covariância: {e}")
        print("Verifique se há dados suficientes e se os preços são válidos.")
        return None, None

    # Otimizar para a máxima Sharpe Ratio
    ef = EfficientFrontier(mu, S)
    
    weights = None
    if optimization_method == "max_sharpe":
        ef.add_objective(objective_functions.L2_reg, gamma=0.1) # Adiciona regularização L2 para evitar pesos extremos
        weights = ef.max_sharpe()
    elif optimization_method == "min_volatility":
        weights = ef.min_volatility()
    # Adicionar outros métodos conforme necessário (ex: efficient_risk, efficient_return)
    else:
        print(f"Método de otimização '{optimization_method}' não suportado.")
        return None, None
        
    cleaned_weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=True)
    
    return cleaned_weights, performance

def suggest_contributions(current_portfolio_value, current_weights, optimal_weights, new_contribution_amount):
    """Sugere aportes para alcançar os pesos ótimos."""
    print("\n--- Sugestão de Aportes --- ")
    if not current_weights or not optimal_weights:
        print("Pesos atuais ou ótimos não fornecidos.")
        return

    total_new_value = current_portfolio_value + new_contribution_amount
    suggestions = {}
    
    print(f"Valor atual da carteira: R${current_portfolio_value:.2f}")
    print(f"Novo aporte: R${new_contribution_amount:.2f}")
    print(f"Valor total da carteira após aporte: R${total_new_value:.2f}")

    for ticker in optimal_weights:
        optimal_value_ticker = total_new_value * optimal_weights.get(ticker, 0)
        current_value_ticker = current_portfolio_value * current_weights.get(ticker, 0)
        contribution_needed = optimal_value_ticker - current_value_ticker
        suggestions[ticker] = contribution_needed
        print(f"  {ticker}: Aportar R${contribution_needed:.2f} (Valor alvo: R${optimal_value_ticker:.2f}, Valor atual: R${current_value_ticker:.2f})")
    
    # Verificar se a soma das sugestões de aporte corresponde ao novo aporte total
    # (pode haver pequenas diferenças devido a arredondamento ou se o aporte não for suficiente para rebalancear)
    print(f"Soma dos aportes sugeridos: R${sum(suggestions.values()):.2f}")
    return suggestions

if __name__ == "__main__":
    # Tickers para incluir na otimização (devem ter dados processados)
    recs_file = os.path.join(DATA_DIR, "recomendacoes_geradas.json")
    recommended_tickers_stems = ["br_PETR4_SA", "us_AAPL"] # Default se o arquivo não existir ou estiver vazio
    
    if os.path.exists(recs_file):
        try:
            with open(recs_file, 'r') as f:
                recs_data = json.load(f)
            # Filtrar por recomendação de "Comprar" ou "Manter/Neutro"
            recommended_tickers_from_file = [rec['ticker'] for rec in recs_data if rec['recomendacao'] in ["Comprar", "Manter/Neutro"]]
            # Mapear de volta para stems (simplificado, assume que os nomes são únicos e correspondem)
            temp_stems = []
            # Ajustar para o nome correto do ticker que está nos arquivos (ex: PETR4.SA)
            if "PETR4" in recommended_tickers_from_file or "PETR4.SA" in recommended_tickers_from_file : temp_stems.append("br_PETR4_SA") 
            if "AAPL" in recommended_tickers_from_file: temp_stems.append("us_AAPL")
            if temp_stems: recommended_tickers_stems = temp_stems
            print(f"Tickers recomendados para otimização: {recommended_tickers_stems}")
        except Exception as e:
            print(f"Erro ao carregar recomendações: {e}. Usando tickers padrão.")

    if len(recommended_tickers_stems) < 2:
        print("Menos de 2 ativos recomendados. Adicionando PETR4.SA e AAPL por padrão para otimização.")
        recommended_tickers_stems = ["br_PETR4_SA", "us_AAPL"]

    prices = load_stock_prices_for_optimization(recommended_tickers_stems)

    if prices is not None and not prices.empty and len(prices.columns) >=2:
        # Otimização Max Sharpe
        optimal_weights_sharpe, performance_sharpe = optimize_portfolio(prices, optimization_method="max_sharpe")
        if optimal_weights_sharpe:
            print("Pesos Ótimos (Max Sharpe Ratio):")
            for ticker, weight in optimal_weights_sharpe.items():
                 print(f"  {ticker}: {weight:.4f}")
            # Salvar resultados
            sharpe_results = {"weights": optimal_weights_sharpe, "performance": performance_sharpe}
            with open(os.path.join(DATA_DIR, "optimized_portfolio_max_sharpe.json"), "w") as f:
                serializable_weights = {k: v for k, v in optimal_weights_sharpe.items()}
                sharpe_results_to_save = {"weights": serializable_weights, 
                                          "performance": list(performance_sharpe) if performance_sharpe is not None else None}
                json.dump(sharpe_results_to_save, f, indent=4)
            print("Resultados da otimização Max Sharpe salvos.")

        # Otimização Mínima Volatilidade
        optimal_weights_min_vol, performance_min_vol = optimize_portfolio(prices, optimization_method="min_volatility")
        if optimal_weights_min_vol:
            print("Pesos Ótimos (Mínima Volatilidade):")
            for ticker, weight in optimal_weights_min_vol.items():
                 print(f"  {ticker}: {weight:.4f}")
            min_vol_results = {"weights": optimal_weights_min_vol, "performance": performance_min_vol}
            with open(os.path.join(DATA_DIR, "optimized_portfolio_min_volatility.json"), "w") as f:
                serializable_weights_mv = {k: v for k, v in optimal_weights_min_vol.items()}
                min_vol_results_to_save = {"weights": serializable_weights_mv, 
                                           "performance": list(performance_min_vol) if performance_min_vol is not None else None}
                json.dump(min_vol_results_to_save, f, indent=4)
            print("Resultados da otimização Mínima Volatilidade salvos.")

        # Exemplo de Sugestão de Aporte (usando pesos da Max Sharpe)
        if optimal_weights_sharpe:
            carteira_atual_valor = 10000 
            current_weights_example = {ticker: 1/len(prices.columns) for ticker in prices.columns} 
            novo_aporte = 2000
            suggest_contributions(carteira_atual_valor, current_weights_example, optimal_weights_sharpe, novo_aporte)
    else:
        print("Não foi possível carregar dados de preços suficientes para otimização.")
        if prices is not None:
            print(f"DataFrame de preços carregado tem {len(prices.index)} linhas e {len(prices.columns)} colunas.")
            print(f"Colunas: {prices.columns}")
            # print(f"Head do DataFrame de preços:\n{prices.head()}")
            # print(f"Tail do DataFrame de preços:\n{prices.tail()}")


    print("\nScript de otimização de carteira concluído.")

