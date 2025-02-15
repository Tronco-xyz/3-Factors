import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

def get_data(tickers, period="2y"):
    data = yf.download(tickers, period=period, progress=False)["Adj Close"]
    return data

def calculate_returns(prices, period):
    return prices.pct_change(periods=period).iloc[-1]

def calculate_volatility(prices, period):
    return prices.pct_change().rolling(window=period).std().iloc[-1]

def normalize_series(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

st.title("ETF/Stock Screener")

with st.sidebar:
    tickers = st.text_area("Enter Tickers (comma-separated)").split(',')
    periods = {"5 days":5, "10 days":10, "20 days":20, "3 month":63, "6 month":126, "12 month":252, "24 month":504}
    returnA_period = st.selectbox("Select ReturnA Period", list(periods.keys()))
    returnB_period = st.selectbox("Select ReturnB Period", list(periods.keys()))
    volatility_period = st.selectbox("Select Volatility Period", list(periods.keys()))
    weights = {
        "ReturnA": st.slider("Weight for ReturnA", 0, 100, 40),
        "ReturnB": st.slider("Weight for ReturnB", 0, 100, 40),
        "Volatility": st.slider("Weight for Volatility", 0, 100, 20)
    }

data = get_data(tickers)
returnsA = calculate_returns(data, periods[returnA_period])
returnsB = calculate_returns(data, periods[returnB_period])
volatility = calculate_volatility(data, periods[volatility_period])

norm_returnA = normalize_series(returnsA)
norm_returnB = normalize_series(returnsB)
norm_volatility = normalize_series(volatility)

final_score = (norm_returnA * weights['ReturnA'] + norm_returnB * weights['ReturnB'] - norm_volatility * weights['Volatility']) / sum(weights.values())

results = pd.DataFrame({
    'ReturnA': returnsA,
    'ReturnB': returnsB,
    'Volatility': volatility,
    'Normalized ReturnA': norm_returnA,
    'Normalized ReturnB': norm_returnB,
    'Normalized Volatility': norm_volatility,
    'Final Score': final_score
})

st.dataframe(results.sort_values(by='Final Score', ascending=False))
