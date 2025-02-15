import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Function to calculate relative strength and volatility
def calculate_metrics(ticker, period_short=3*21, period_long=6*21):
    # Fetch historical data
    data = yf.download(ticker, period='1y', interval='1d')

    # Debug: Print columns to check data availability
    st.write(f"Columns for {ticker}: {data.columns}")

    # Check if 'Adj Close' is in the DataFrame
    if 'Adj Close' not in data.columns:
        st.error(f"'Adj Close' data not available for {ticker}")
        return None

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

# List of tickers to screen
tickers = ['AAPL', 'MSFT', 'GOOGL', 'SPY', 'QQQ', 'VTI']

# Screen the tickers
results = []
for ticker in tickers:
    metrics = calculate_metrics(ticker)
    if metrics is not None:
        metrics['Ticker'] = ticker
        results.append(metrics)

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Sort by relative strength
results_df = results_df.sort_values(by='Relative_Strength', ascending=False)

# Display results in Streamlit
st.dataframe(results_df)
