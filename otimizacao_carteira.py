import pandas as pd
import numpy as np
import json
import os
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions
from scipy.stats import norm # Para o intervalo de confiança

DATA_DIR = "."

def load_stock_prices_for_optimization(ticker_stems):
    """Carrega os preços de fechamento ajustados para uma lista de tickers."""
    all_prices = pd.DataFrame()
    for stem in ticker_stems:
        # O nome do arquivo quant_analysis é gerado no módulo analise_quantitativa
        # Ex: br_PETR4_SA_quant_analysis.csv
        quant_file = os.path.join(DATA_DIR, f"{stem}_quant_analysis.csv")
        if os.path.exists(quant_file):
            try:
                df_quant = pd.read_csv(quant_file, index_col='Timestamp', parse_dates=True)
                # O ticker real para PyPortfolioOpt é a parte do stem após o prefixo da região
                # Ex: br_PETR4_SA -> PETR4_SA. Precisamos remover o prefixo e o underline.
                # No entanto, PyPortfolioOpt espera os nomes das colunas como os tickers (ex: "PETR4.SA", "AAPL")
                # O stem já é algo como "br_PETR4_SA", então o ticker é "PETR4.SA"
                # A função split("_")[1] pegaria "PETR4_SA". Precisamos garantir que o nome da coluna seja o ticker correto.
                # O ideal é que o nome da coluna no CSV já seja o ticker correto.
                # Vamos assumir que o stem é prefixo_TICKER e o nome da coluna será TICKER
                # ticker_name = stem.split("_", 1)[1] # Ex: "PETR4_SA" ou "AAPL"
                # Se o stem for "br_PETR4_SA", o ticker é "PETR4.SA". Se for "us_AAPL", é "AAPL".
                parts = stem.split("_", 1)
                ticker_name = parts[1].replace("_", ".") if len(parts) > 1 else parts[0]

                if 'Adj Close' in df_quant.columns:
                    current_prices = df_quant[["Adj Close"]].rename(columns={"Adj Close": ticker_name})
                    if all_prices.empty:
                        all_prices = current_prices
                    else:
                        all_prices = all_prices.join(current_prices, how='outer')
            except Exception as e:
                print(f"Erro ao carregar dados quantitativos de {quant_file}: {e}")
        else:
            print(f"Arquivo não encontrado: {quant_file} para o stem {stem}")
    
    if not all_prices.empty:
        all_prices.fillna(method='ffill', inplace=True)
        all_prices.dropna(inplace=True) 
    return all_prices

def optimize_portfolio(prices_df, optimization_method="max_sharpe"):
    """Otimiza a carteira usando o método especificado."""
    if prices_df.empty or len(prices_df.columns) < 2:
        print("Dados de preços insuficientes para otimização (necessário pelo menos 2 ativos).")
        return None, None

    print(f"\n--- Otimização de Carteira ({optimization_method}) ---")
    
    try:
        mu = expected_returns.mean_historical_return(prices_df)
        S = risk_models.sample_cov(prices_df)
    except Exception as e:
        print(f"Erro ao calcular retornos esperados ou covariância: {e}")
        print(f"Verifique se há dados suficientes e se os preços são válidos. DataFrame de preços:\n{prices_df.info()}")
        return None, None

    ef = EfficientFrontier(mu, S)
    weights = None
    if optimization_method == "max_sharpe":
        ef.add_objective(objective_functions.L2_reg, gamma=0.1) 
        try:
            weights = ef.max_sharpe()
        except Exception as e:
            print(f"Erro ao otimizar para max_sharpe: {e}")
            return None, None
    elif optimization_method == "min_volatility":
        try:
            weights = ef.min_volatility()
        except Exception as e:
            print(f"Erro ao otimizar para min_volatility: {e}")
            return None, None
    else:
        print(f"Método de otimização '{optimization_method}' não suportado.")
        return None, None
        
    cleaned_weights = ef.clean_weights()
    try:
        performance = ef.portfolio_performance(verbose=False) # verbose=False para não imprimir no console
    except Exception as e:
        print(f"Erro ao calcular performance do portfólio: {e}")
        return cleaned_weights, None # Retorna pesos mesmo se performance falhar
    
    return cleaned_weights, performance

def calculate_return_confidence_interval(expected_annual_return, annual_volatility, confidence_level=0.95):
    """Calcula o intervalo de confiança para o retorno anualizado."""
    if expected_annual_return is None or annual_volatility is None:
        return None, None
    
    # Z-score para o nível de confiança (ex: 1.96 para 95%)
    z_score = norm.ppf(1 - (1 - confidence_level) / 2)
    
    lower_bound = expected_annual_return - (z_score * annual_volatility)
    upper_bound = expected_annual_return + (z_score * annual_volatility)
    
    return lower_bound, upper_bound

def suggest_contributions(current_portfolio_value, current_weights, optimal_weights, new_contribution_amount):
    """Sugere aportes para alcançar os pesos ótimos."""
    print("\n--- Sugestão de Aportes --- ")
    if not current_weights or not optimal_weights:
        print("Pesos atuais ou ótimos não fornecidos.")
        return {}

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
    
    print(f"Soma dos aportes sugeridos: R${sum(suggestions.values()):.2f}")
    return suggestions

if __name__ == "__main__":
    # Gerar arquivos de exemplo se não existirem (para teste local)
    stems_for_test = ["br_PETR4_SA", "us_AAPL"]
    for stem_test in stems_for_test:
        quant_file_test = os.path.join(DATA_DIR, f"{stem_test}_quant_analysis.csv")
        if not os.path.exists(quant_file_test):
            print(f"Gerando arquivo de teste {quant_file_test}...")
            # Criar um CSV de exemplo simples
            dates_test = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
            data_test = {
                'Timestamp': dates_test,
                'Open': [10, 10.1, 10.2],
                'High': [10.5, 10.6, 10.7],
                'Low': [9.9, 10.0, 10.1],
                'Close': [10.1, 10.2, 10.3],
                'Adj Close': [10.1, 10.2, 10.3],
                'Volume': [1000, 1100, 1200]
            }
            df_test = pd.DataFrame(data_test)
            df_test.set_index('Timestamp', inplace=True)
            df_test.to_csv(quant_file_test)

    prices = load_stock_prices_for_optimization(stems_for_test)

    if prices is not None and not prices.empty and len(prices.columns) >=2:
        optimal_weights_sharpe, performance_sharpe = optimize_portfolio(prices, optimization_method="max_sharpe")
        if optimal_weights_sharpe and performance_sharpe:
            print("\nPesos Ótimos (Max Sharpe Ratio):")
            for ticker, weight in optimal_weights_sharpe.items():
                 print(f"  {ticker}: {weight:.4f}")
            print(f"Performance Esperada (Retorno, Volatilidade, Sharpe): {performance_sharpe}")
            
            # Teste da nova função
            ret_anual, vol_anual, _ = performance_sharpe
            lower, upper = calculate_return_confidence_interval(ret_anual, vol_anual)
            if lower is not None and upper is not None:
                print(f"Intervalo de Confiança (95%) para Retorno em 12 Meses: {lower*100:.2f}% a {upper*100:.2f}%")
            else:
                print("Não foi possível calcular o intervalo de confiança.")

            # Salvar resultados
            sharpe_results_to_save = {
                "weights": {k: v for k, v in optimal_weights_sharpe.items()},
                "performance": list(performance_sharpe) if performance_sharpe is not None else None,
                "confidence_interval_12m_95pct": {"lower_bound": lower, "upper_bound": upper} if lower is not None else None
            }
            with open(os.path.join(DATA_DIR, "optimized_portfolio_max_sharpe.json"), "w") as f:
                json.dump(sharpe_results_to_save, f, indent=4)
            print("Resultados da otimização Max Sharpe (com intervalo de confiança) salvos.")

    else:
        print("Não foi possível carregar dados de preços suficientes para otimização.")

    print("\nScript de otimização de carteira concluído.")

