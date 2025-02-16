import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import datetime

# Configuración del tema oscuro
st.set_page_config(page_title="ETF/Stock Screener", layout="wide", initial_sidebar_state="expanded")

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
    if max_value == min_value:
        raise ValueError("El valor mínimo no puede ser igual al valor máximo.")
    return ((value - min_value) / (max_value - min_value)) * 99

# Función para convertir períodos a días
def convert_period_to_days(period):
    period = period.lower()
    if "day" in period:
        days = int(period.split()[0])
    elif "month" in period:
        months = int(period.split()[0])
        days = months * 30  # Aproximación de 30 días por mes
    else:
        raise ValueError("Período no válido. Usa '1 day', '5 days' o similar.")
    
    return days

# Función para calcular el rating
def calculate_rating(ticker, return_period, weight_return):
    try:
        data = yf.download(ticker)
        close_prices = data['Close']
        
        if len(close_prices) < convert_period_to_days(return_period):
            raise ValueError(f"No hay suficientes datos históricos para el período {return_period}.")

        returns = calculate_return(close_prices, return_period)
    except Exception as e:
        st.error(f"Error al calcular el rating para {ticker}: {e}")
        return None
    
    normalized_returns = normalize(returns, -100, 100) * weight_return
    return {
        'Ticker': ticker,
        'Return Period': return_period,
        'Rating': normalized_returns
    }

# Interfaz de Streamlit
st.title("ETF/Stock Screener")

# Entradas del usuario
tickers = st.text_input("Introduce los tickers separados por comas (ej: AAPL,GOOGL)", "AAPL")
return_periods = {
    '1 day': convert_period_to_days('1 day'),
    '5 days': convert_period_to_days('5 days'),
    '10 days': convert_period_to_days('10 days')
}
weight_return_1day = st.slider("Peso del rendimiento de 1 día (%)", min_value=0, max_value=100, value=30)
weight_return_5days = st.slider("Peso del rendimiento de 5 días (%)", min_value=0, max_value=100, value=30)

# Validación
total_weight = weight_return_1day + weight_return_5days
if total_weight != 100:
    st.error(f"La suma de los pesos debe ser 100%. Actual: {total_weight}%")
else:
    # Calcular rating
    tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    results = []
    
    for ticker in tickers_list:
        result_1day = calculate_rating(ticker, '1 day', weight_return_1day)
        result_5days = calculate_rating(ticker, '5 days', weight_return_5days)
        
        if result_1day is not None:
            results.append(result_1day)
            
        if result_5days is not None:
            results.append(result_5days)

    # Mostrar resultados
    if results:
        results_df = pd.DataFrame(results).set_index('Ticker')
        st.write("Resultados:")
        st.dataframe(results_df)
    else:
        st.write("No se encontraron resultados para los tickers proporcionados.")
