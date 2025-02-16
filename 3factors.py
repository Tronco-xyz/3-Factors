from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import streamlit as st
import datetime

# Configuración del tema oscuro
st.set_page_config(page_title="ETF/Stock Screener", layout="wide", initial_sidebar_state="expanded")

# Configuración de la clave API de Alpha Vantage
api_key = '3WEW3GKD903BYVM1'

# Función para calcular el rendimiento
def calculate_return(prices, period):
    return ((prices[-1] - prices[0]) / prices[0]) * 100

# Función para calcular la volatilidad
def calculate_volatility(prices, period):
    if len(prices) < 2:
        raise ValueError("No hay suficientes datos para calcular la volatilidad.")
    daily_returns = np.diff(prices) / prices[:-1]
    return np.std(daily_returns) * np.sqrt(252) * 100  # Anualizar y convertir a porcentaje

# Función para normalizar valores
def normalize(value, min_value, max_value):
    return ((value - min_value) / (max_value - min_value)) * 99

# Función para convertir períodos a días
def convert_period_to_days(period):
    if "day" in period:
        return int(period.split()[0])
    elif "month" in period:
        return int(period.split()[0]) * 30
    else:
        raise ValueError("Período no válido")

# Función para obtener datos históricos de Alpha Vantage
def get_historical_data(ticker, period):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
    data = data['5. adjusted close'].dropna().values.flatten()
    return data

# Función principal para calcular el rating
def calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility):
    try:
        # Convertir períodos a días
        returnA_days = convert_period_to_days(returnA_period)
        returnB_days = convert_period_to_days(returnB_period)
        volatility_days = convert_period_to_days(volatility_period)

        # Obtener datos históricos
        prices = get_historical_data(ticker, max(returnA_days, returnB_days, volatility_days))

        # Verificar si hay suficientes datos
        if len(prices) < max(returnA_days, returnB_days, volatility_days):
            raise ValueError(f"No hay suficientes datos para {ticker} en el período seleccionado.")

        # Calcular ReturnA
        returnA = calculate_return(prices[-returnA_days:], returnA_days)

        # Calcular ReturnB
        returnB = calculate_return(prices[-returnB_days:], returnB_days)

        # Calcular Volatilidad
        volatility = calculate_volatility(prices[-volatility_days:], volatility_days)

        # Normalizar valores (ajustar los valores mínimos y máximos según sea necesario)
        returnA_norm = normalize(returnA, min_value=-50, max_value=100)
        returnB_norm = normalize(returnB, min_value=-50, max_value=100)
        volatility_norm = normalize(volatility, min_value=0, max_value=100)

        # Calcular rating
        rating = (returnA_norm * weight_returnA) + (returnB_norm * weight_returnB) + (volatility_norm * weight_volatility)

        return {
            "Symbol": ticker,
            "ReturnA": round(returnA, 2),
            "ReturnB": round(returnB, 2),
            "Volatility": round(volatility, 2),
            "RS Rating": round(rating, 2)
        }
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
returnA_period = st.selectbox("Período para ReturnA:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"], index=4)
weight_returnA = st.number_input("Peso para ReturnA (%):", min_value=0, max_value=100, value=40, step=1, format="%d")

# Configuración de ReturnB
st.subheader("Configuración de ReturnB")
returnB_period = st.selectbox("Período para ReturnB:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"], index=3)
weight_returnB = st.number_input("Peso para ReturnB (%):", min_value=0, max_value=100, value=30, step=1, format="%d")

# Configuración de Volatilidad
st.subheader("Configuración de Volatilidad")
volatility_period = st.selectbox("Período para Volatilidad:", ["1 day", "5 days", "10 days", "20 days", "3 months", "6 months", "12 months", "24 months"], index=3)
weight_volatility = st.number_input("Peso para Volatilidad (%):", min_value=0, max_value=100, value=30, step=1, format="%d")

# Verificar que la suma de los pesos sea 100%
total_weight = weight_returnA + weight_returnB + weight_volatility
if total_weight != 100:
    st.error(f"La suma de los pesos debe ser 100%. Actual: {total_weight}%")
else:
    # Convertir pesos a decimales
    weight_returnA /= 100.0
    weight_returnB /= 100.0
    weight_volatility /= 100.0

    if st.button("Calcular Rating"):
        results = []
        for ticker in tickers:
            result = calculate_rating(ticker, returnA_period, returnB_period, volatility_period, weight_returnA, weight_returnB, weight_volatility)
            if result is not None:
                results.append(result)

        # Mostrar resultados en una tabla
        if results:
            results_df = pd.DataFrame(results)
            st.write("Resultados:")
            st.dataframe(results_df)
        else:
            st.write("No se encontraron resultados para los tickers proporcionados.")
