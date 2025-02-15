import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

def get_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)['Adj Close']
    return data

def calculate_returns(data, period):
    return data.pct_change(period).iloc[-1]

def calculate_volatility(data, period):
    return data.pct_change().rolling(period).std().iloc[-1]

def normalize(series):
    return (series - series.min()) / (series.max() - series.min()) * 100

st.sidebar.title("ETF Screener Parameters")
tickers = st.sidebar.text_area("Enter tickers separated by commas", "SPY,QQQ,IWM")
tickers = [t.strip() for t in tickers.split(',')]

return_a_period = st.sidebar.selectbox("ReturnA Period", [5, 10, 20, 60, 90])
return_b_period = st.sidebar.selectbox("ReturnB Period", [5, 10, 20, 60, 90])
vol_period = st.sidebar.selectbox("Volatility Period", [5, 10, 20, 60, 90])

weight_a = st.sidebar.slider("Weight for ReturnA", 0, 100, 40)
weight_b = st.sidebar.slider("Weight for ReturnB", 0, 100, 30)
weight_vol = st.sidebar.slider("Weight for Volatility", 0, 100, 30)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-02-15"))

if st.sidebar.button("Run Screener"):
    data = get_data(tickers, start_date, end_date)
    ret_a = calculate_returns(data, return_a_period)
    ret_b = calculate_returns(data, return_b_period)
    vol = calculate_volatility(data, vol_period)

    ret_a_norm = normalize(ret_a)
    ret_b_norm = normalize(ret_b)
    vol_norm = normalize(vol)

    rating = ret_a_norm * weight_a/100 + ret_b_norm * weight_b/100 + vol_norm * weight_vol/100

    results = pd.DataFrame({
        'ReturnA': ret_a,
        'ReturnB': ret_b,
        'Volatility': vol,
        'Rating': rating
    })
    st.write(results.sort_values(by='Rating', ascending=False))
