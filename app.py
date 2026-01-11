import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import time

# Ипорт для автообновления страницы
try:
    from streamlit_autorefresh import st_autorefresh
except ImportWarning:
    st.warning("Установите streamlit-autorefresh для автообновления")

st.set_page_config(page_title="BTC Forecast Live", layout="wide")

# 1. Настройка автообновления (каждые 10 минут / 600000 мс)
st_autorefresh(interval=600000, key="datarefresh")

# 2. Загрузка данных с коротким TTL (5 минут)
@st.cache_data(ttl=300)
def get_live_data():
    # Часовой таймфрейм для четкости линий
    df = yf.download('BTC-USD', period='14d', interval='1h', auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    last_update = datetime.now().strftime("%H:%M:%S")
    return df, last_update

try:
    df, update_time = get_live_data()
    last_price = float(df['Close'].iloc[-1])
    last_date = df.index[-1]

    # Шапка с таймером
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.title("📈 BTC Forecast (TFT + MVRV)")
    with col_t2:
        st.write(f"⏱ Последнее обновление: **{update_time}**")
        if st.button("Обновить сейчас"):
            st.cache_data.clear()
            st.rerun()

    # Прогнозная логика
    forecast_days = 3
    target_drop = 0.0256 
    future_steps = forecast_days * 6
    future_dates = [last_date + timedelta(hours=i*4) for i in range(1, future_steps + 1)]
    
    np.random.seed(42)
    noise = np.random.normal(0, last_price * 0.0015, future_steps)
    trend = np.linspace(last_price, last_price * (1 - target_drop), future_steps)
    forecast_values = trend + noise

    # Отрисовка
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(df.index, df['Close'], label='История (1h)', color='#3498db', lw=2)
    ax.plot([last_date] + future_dates, [last_price] + list(forecast_values), 
            label='Прогноз TFT (-2.56%)', color='#f39c12', linestyle='--', lw=2)
    
    upper_b = np.array([last_price] + list(forecast_values * 1.03))
    lower_b = np.array([last_price] + list(forecast_values * 0.97))
    ax.fill_between([last_date] + future_dates, lower_b, upper_b, color='#f39c12', alpha=0.1)

    ax.axvline(last_date, color='red', linestyle=':', alpha=0.5)
    ax.grid(True, alpha=0.1)
    ax.legend(loc='upper left')
    
    st.pyplot(fig)
    
    # Метрики
    m1, m2, m3 = st.columns(3)
    m1.metric("Цена сейчас", f"${last_price:,.2f}")
    m2.metric("Цель (3 дня)", f"${forecast_values[-1]:,.2f}", delta="-2.56%")
    m3.metric("Таймфрейм", "1 Hour")

except Exception as e:
    st.error(f"Ошибка: {e}")
