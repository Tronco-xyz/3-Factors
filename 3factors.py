import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title('ETF/Stock Screener')

# Inputs
time_periods = ['3-Months', '6-Months', '1-Year', '2-Years']
return_a_period_days = st.selectbox('Return A Period', time_periods)
return_b_period_days = st.selectbox('Return B Period', time_periods)
volatility_period_days = st.selectbox('Volatility Period', time_periods)

# Convert periods to days
period_mapping = {
    '3-Months': 63,
    '6-Months': 126,
    '1-Year': 252,
    '2-Years': 504
}

return_a_period = period_mapping[return_a_period_days]
return_b_period = period_mapping[return_b_period_days]
volatility_period = period_mapping[volatility_period_days]

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

    # Date and Assets selection
    date = st.date_input('Through', value=pd.to_datetime('2025-02-14'))
    num_assets = st.number_input('Number of Assets', min_value=1, value=100)

    # Screen button
    if st.button('Screen'):
        tickers_list = st.text_input('Tickers (comma-separated)', 'SPY,QQQ,IWM').split(',')
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
            results_df = results_df.sort_values(by='Overall Rank').head(num_assets)

            st.dataframe(results_df)

            # Pie chart for factor weights
            factors = ['Return A', 'Return B', 'Volatility']
            weights = [return_a_weight, return_b_weight, volatility_weight]
            fig, ax = plt.subplots()
            ax.pie(weights, labels=factors, autopct='%1.1f%%', startangle=90)
            st.pyplot(fig)
        else:
            st.warning("No valid data to display.")
