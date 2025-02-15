import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Función para calcular el rendimiento
def calculate_return(prices, period):
    return ((prices[-1] - prices[0]) / prices[0]) * 100

# Función para calcular la volatilidad
def calculate_volatility(prices, period):
    if len(prices) < 2:
        raise ValueError("No hay suficientes datos para calcular la volatilidad.")
    daily_returns = np.diff(prices) / prices[:-1]
    return np.std(daily_returns) * 100

# Función para normalizar valores
def normalize(value, min_value, max_value):
    return ((value - min_value) / (max_value - min_value)) * 100

# Función para convertir períodos a días
def convert_period_to_days(period):
    if "day" in period:
        return int(period.split()[0])
    elif "month" in period:
        return int(period.split()[0]) * 30
    else:
        raise ValueError("Período no válido")

# Función principal para calcular el rating
def calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility):
    try:
        # Convertir períodos a días
        returnA_days = convert_period_to_days(returnA_period)
        returnB_days = convert_period_to_days(returnB_period)
        volatility_days = convert_period_to_days(volatility_period)

        # Obtener datos históricos
        data = yf.download(ticker, period=f"{max(returnA_days, returnB_days, volatility_days)}d")
        prices = data['Close'].values

        # Verificar si hay suficientes datos
        if len(prices) < max(returnA_days, returnB_days, volatility_days):
            raise ValueError(f"No hay suficientes datos para {ticker} en el período seleccionado.")

        # Calcular ReturnA
        returnA = calculate_return(prices[-returnA_days:], returnA_days)

        # Calcular ReturnB
        returnB = calculate_return(prices[-returnB_days:], returnB_days)

        # Calcular Volatilidad
        volatility = calculate_volatility(prices[-volatility_days:], volatility_days)

        # Normalizar valores (ejemplo con valores mínimos y máximos hipotéticos)
        returnA_norm = normalize(returnA, min_value=-5, max_value=10)
        returnB_norm = normalize(returnB, min_value=-10, max_value=20)
        volatility_norm = normalize(volatility, min_value=0.5, max_value=5)

        # Calcular rating
        rating = (returnA_norm * weight_returnA) + (returnB_norm * weight_returnB) + (volatility_norm * weight_volatility)
        return rating
    except Exception as e:
        st.warning(f"Error al procesar {ticker}: {str(e)}")
        return None

# Interfaz de Streamlit
st.title("ETF/Stock Screener")
st.write("Este screener calcula un rating basado en rendimientos y volatilidad.")

# Campo para agregar múltiples tickers
tickers = st.text_input("Introduce los tickers separados por comas (ej: AAPL, MSFT, SPY):", "AAPL, MSFT, SPY")
tickers = [ticker.strip() for ticker in tickers.split(",")]

# Configuración de ReturnA
st.subheader("Configuración de ReturnA")
returnA_period = st.selectbox("Período para ReturnA:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"])
weight_returnA = st.number_input("Peso para ReturnA (%):", min_value=0.0, max_value=100.0, value=40.0, step=0.01, format="%.2f")

# Configuración de ReturnB
st.subheader("Configuración de ReturnB")
returnB_period = st.selectbox("Período para ReturnB:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"])
weight_returnB = st.number_input("Peso para ReturnB (%):", min_value=0.0, max_value=100.0, value=30.0, step=0.01, format="%.2f")

# Configuración de Volatilidad
st.subheader("Configuración de Volatilidad")
volatility_period = st.selectbox("Período para Volatilidad:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"])
weight_volatility = st.number_input("Peso para Volatilidad (%):", min_value=0.0, max_value=100.0, value=30.0, step=0.01, format="%.2f")

# Verificar que la suma de los pesos sea 100%
total_weight = weight_returnA + weight_returnB + weight_volatility
if abs(total_weight - 100.0) > 0.0001:
    st.error(f"La suma de los pesos debe ser 100%. Actual: {total_weight:.2f}%")
else:
    # Convertir pesos a decimales
    weight_returnA /= 100.0
    weight_returnB /= 100.0
    weight_volatility /= 100.0

    if st.button("Calcular Rating"):
        results = []
        for ticker in tickers:
            rating = calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility)
            if rating is not None:
                results.append({"Ticker": ticker, "Rating": rating})

        # Mostrar resultados en una tabla
        if results:
            results_df = pd.DataFrame(results)
            st.write("Resultados:")
            st.dataframe(results_df)
