import pandas as pd
import yfinance as yf
import numpy as np

# List of tickers to screen
tickers = ['AAPL', 'MSFT', 'GOOGL', 'SPY', 'QQQ', 'VTI']

# Function to calculate relative strength and volatility
def calculate_metrics(ticker, period_short=3*21, period_long=6*21):
    # Fetch historical data
    data = yf.download(ticker, period='1y', interval='1d')

    # Calculate returns
    data['Return'] = data['Adj Close'].pct_change()

    # Calculate short-term and long-term returns
    data['Return_Short'] = data['Return'].rolling(window=period_short).mean()
    data['Return_Long'] = data['Return'].rolling(window=period_long).mean()

    # Calculate volatility (standard deviation of returns)
    data['Volatility'] = data['Return'].rolling(window=period_short).std() * np.sqrt(252)

    # Calculate relative strength (simple ratio of short-term to long-term return)
    data['Relative_Strength'] = data['Return_Short'] / data['Return_Long']

    # Get the latest values
    latest = data.iloc[-1]
    return latest[['Return_Short', 'Return_Long', 'Volatility', 'Relative_Strength']]

# Screen the tickers
results = []
for ticker in tickers:
    metrics = calculate_metrics(ticker)
    metrics['Ticker'] = ticker
    results.append(metrics)

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Sort by relative strength
results_df = results_df.sort_values(by='Relative_Strength', ascending=False)

print(results_df)

