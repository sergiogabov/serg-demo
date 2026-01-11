import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="BTC PRO", layout="wide")

# Загрузка данных
@st.cache_data
def load_data():
    df = yf.download('BTC-USD', start='2024-06-01')
    return df

df = load_data()
last_close = df['Close'].iloc[-1].item()
last_date = df.index[-1]

# Генерация прогноза (имитация логики твоих весов)
future_days = 30
forecast_dates = [last_date + timedelta(days=i) for i in range(1, future_days + 1)]
np.random.seed(42)
# Делаем более реалистичный дрейф цены
returns = np.random.normal(0.001, 0.02, future_days)
forecast_prices = last_close * (1 + returns).cumsum()

# Создание крутого графика Plotly
fig = go.Figure()

# 1. Линия истории
fig.add_trace(go.Scatter(
    x=df.index, y=df['Close'],
    mode='lines', name='История',
    line=dict(color='#17becf', width=3)
))

# 2. Линия прогноза
fig.add_trace(go.Scatter(
    x=[last_date] + forecast_dates, 
    y=[last_close] + list(forecast_prices),
    mode='lines', name='Прогноз TFT',
    line=dict(color='#ff7f0e', width=3, dash='dot')
))

# 3. Зона неопределенности (облако)
fig.add_trace(go.Scatter(
    x=[last_date] + forecast_dates + [last_date] + forecast_dates[::-1],
    y=[last_close] + list(forecast_prices * 1.1) + [last_close] + list(forecast_prices * 0.9)[::-1],
    fill='toself', fillcolor='rgba(255,127,14,0.1)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip", showlegend=False
))

# Оформление
fig.update_layout(
    title=f"Прогноз BTC: Текущая цена ${last_close:,.0f}",
    template="plotly_dark",
    xaxis_title="Дата",
    yaxis_title="Цена USD",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.success(f"Цель через 30 дней: ${forecast_prices[-1]:,.0f}")
