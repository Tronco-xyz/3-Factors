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
        volatility_days = convert_period_to_days
