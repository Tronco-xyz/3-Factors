import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Función para calcular el rendimiento
def calculate_return(prices, period):
    return ((prices[-1] - prices[0]) / prices[0]) * 100

# Función para calcular la volatilidad
def calculate_volatility(prices, period):
    daily_returns = np.diff(prices) / prices[:-1]
    return np.std(daily_returns) * 100

# Función para normalizar valores
def normalize(value, min_value, max_value):
    return ((value - min_value) / (max_value - min_value)) * 100

# Función principal para calcular el rating
def calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility):
    # Obtener datos históricos
    data = yf.download(ticker, period=f"{max(returnA_period, returnB_period, volatility_period)}d")
    prices = data['Close'].values

    # Calcular ReturnA
    returnA = calculate_return(prices[-returnA_period:], returnA_period)

    # Calcular ReturnB
    returnB = calculate_return(prices[-returnB_period:], returnB_period)

    # Calcular Volatilidad
    volatility = calculate_volatility(prices[-volatility_period:], volatility_period)

    # Normalizar valores (ejemplo con valores mínimos y máximos hipotéticos)
    returnA_norm = normalize(returnA, min_value=-5, max_value=10)
    returnB_norm = normalize(returnB, min_value=-10, max_value=20)
    volatility_norm = normalize(volatility, min_value=0.5, max_value=5)

    # Calcular rating
    rating = (returnA_norm * weight_returnA) + (returnB_norm * weight_returnB) + (volatility_norm * weight_volatility)
    return rating

# Interfaz de Streamlit
st.title("ETF/Stock Screener")
st.write("Este screener calcula un rating basado en rendimientos y volatilidad.")

# Campo para agregar múltiples tickers
tickers = st.text_input("Introduce los tickers separados por comas (ej: AAPL, MSFT, SPY):", "AAPL, MSFT, SPY")
tickers = [ticker.strip() for ticker in tickers.split(",")]

# Configuración de ReturnA
st.subheader("Configuración de ReturnA")
returnA_period = st.selectbox("Período para ReturnA:", [1, 2, 5, 10, 20, 30], index=2)
weight_returnA = st.number_input("Peso para ReturnA (ej: 0.4):", min_value=0.0, max_value=1.0, value=0.4, step=0.1)

# Configuración de ReturnB
st.subheader("Configuración de ReturnB")
returnB_period = st.selectbox("Período para ReturnB:", [1, 2, 5, 10, 20, 30], index=2)
weight_returnB = st.number_input("Peso para ReturnB (ej: 0.3):", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

# Configuración de Volatilidad
st.subheader("Configuración de Volatilidad")
volatility_period = st.selectbox("Período para Volatilidad:", [1, 2, 5, 10, 20, 30], index=2)
weight_volatility = st.number_input("Peso para Volatilidad (ej: 0.3):", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

# Verificar que la suma de los pesos sea 1
if abs((weight_returnA + weight_returnB + weight_volatility) - 1.0) > 0.0001:
    st.error("La suma de los pesos debe ser igual a 1. Ajusta los pesos.")
else:
    if st.button("Calcular Rating"):
        results = []
        for ticker in tickers:
            try:
                rating = calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility)
                results.append({"Ticker": ticker, "Rating": rating})
            except Exception as e:
                st.error(f"Error al procesar {ticker}: {e}")

        # Mostrar resultados en una tabla
        if results:
            results_df = pd.DataFrame(results)
            st.write("Resultados:")
            st.dataframe(results_df)
