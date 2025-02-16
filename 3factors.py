import pandas as pd
import numpy as np
import yfinance as yf

# List of ETF tickers to analyze
etf_tickers = ['QQQ', 'MDY', 'SPY']

# Define timeframes
returnA_period = '6mo'
returnB_period = '3mo'
volatility_period = '90d'

# Weights for each factor
weights = {
    'ReturnA': 0.4,
    'ReturnB': 0.3,
    'Volatility': 0.3
}

def calculate_returns(data, period):
    if len(data) == 0:
        return np.nan
    return (data[-1] / data[0]) - 1

def calculate_volatility(data):
    if len(data) < 2:
        return np.nan
    daily_returns = data.pct_change().dropna()
    return daily_returns.std() * np.sqrt(252)  # Annualize volatility

def screen_etfs(tickers, returnA_period, returnB_period, volatility_period, weights):
    results = []

    for ticker in tickers:
        try:
            # Fetch historical data
            data = yf.download(ticker, period=volatility_period)['Adj Close']

            if data.empty:
                print(f"No data available for {ticker} in the specified period.")
                continue

            # Calculate returns
            returnA = calculate_returns(data.tail(126).tolist(), returnA_period)  # 6 months ~ 126 trading days
            returnB = calculate_returns(data.tail(63).tolist(), returnB_period)   # 3 months ~ 63 trading days

            # Calculate volatility
            volatility = calculate_volatility(data)

            # Calculate weighted score
            score = (returnA * weights['ReturnA']) + (returnB * weights['ReturnB']) - (volatility * weights['Volatility'])

            results.append({
                'Ticker': ticker,
                'ReturnA': returnA,
                'ReturnB': returnB,
                'Volatility': volatility,
                'Score': score
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Convert results to DataFrame and sort by score
    df_results = pd.DataFrame(results).sort_values(by='Score', ascending=False)
    return df_results

# Screen ETFs
ranked_etfs = screen_etfs(etf_tickers, returnA_period, returnB_period, volatility_period, weights)
print(ranked_etfs)
