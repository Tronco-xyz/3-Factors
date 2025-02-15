import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title('ETF/Stock Screener')

# Inputs
tickers = st.text_input('Tickers (comma-separated)', 'SPY,QQQ,IWM')
return_a_period = st.number_input('Return A Period (days)', min_value=1, value=90)
return_b_period = st.number_input('Return B Period (days)', min_value=1, value=30)
volatility_period = st.number_input('Volatility Period (days)', min_value=1, value=30)
return_a_weight = st.number_input('Return A Weight', min_value=0.0, max_value=1.0, value=0.4)
return_b_weight = st.number_input('Return B Weight', min_value=0.0, max_value=1.0, value=0.3)
volatility_weight = st.number_input('Volatility Weight', min_value=0.0, max_value=1.0, value=0.3)

# Validate weights
if return_a_weight + return_b_weight + volatility_weight != 1.0:
    st.error("The sum of weights must be equal to 1.")
else:
    # Function to calculate performance
    def calculate_performance(data, period):
        return data['Close'].pct_change(period).mean()

    # Function to calculate volatility
    def calculate_volatility(data, period):
        return data['Close'].pct_change().rolling(window=period).std().mean() * np.sqrt(252)

    # Cache data download
    @st.cache_data
    def get_ticker_data(ticker):
        try:
            df = yf.Ticker(ticker).history(period="2y")
            if df.empty:
                st.warning(f"No data available for {ticker}")
            return df
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    # Screen button
    if st.button('Screen'):
        tickers_list = [ticker.strip() for ticker in tickers.split(',')]
        results = []
        for ticker in tickers_list:
            df = get_ticker_data(ticker)
            if not df.empty:
                perf_a = calculate_performance(df, return_a_period)
                perf_b = calculate_performance(df, return_b_period)
                volatility = calculate_volatility(df, volatility_period)
                results.append({
                    'Ticker': ticker,
                    'Performance A': perf_a,
                    'Performance B': perf_b,
                    'Volatility': volatility
                })

        if results:
            results_df = pd.DataFrame(results)
            results_df['Performance A Rank'] = results_df['Performance A'].rank(ascending=False)
            results_df['Performance B Rank'] = results_df['Performance B'].rank(ascending=False)
            results_df['Volatility Rank'] = results_df['Volatility'].rank(ascending=True)
            results_df['Overall Rank'] = (
                results_df['Performance A Rank'] * return_a_weight +
                results_df['Performance B Rank'] * return_b_weight +
                results_df['Volatility Rank'] * volatility_weight
            )
            results_df = results_df.sort_values(by='Overall Rank')

            st.dataframe(results_df)
        else:
            st.warning("No valid data to display.")
