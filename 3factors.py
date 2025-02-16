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
    return ((value - min_value) / (max_value - min_value)) * 99

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
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=max(returnA_days, returnB_days, volatility_days))
        data = yf.download(ticker, start=start_date, end=end_date)

        # Verificar si hay suficientes datos
        if len(data) < max(returnA_days, returnB_days, volatility_days):
            raise ValueError(f"No hay suficientes datos para {ticker} en el período seleccionado.")

        prices = data['Close'].dropna().values.flatten()  # Asegurarse de que prices sea un array unidimensional y eliminar valores faltantes

        # Verificar nuevamente si hay suficientes datos después de eliminar valores faltantes
        if len(prices) < max(returnA_days, returnB_days, volatility_days):
            raise ValueError(f"No hay suficientes datos para {ticker} en el período seleccionado después de eliminar valores faltantes.")

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
        rating = (returnA
