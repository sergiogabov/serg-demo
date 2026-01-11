import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Автообновление страницы
try:
    from streamlit_autorefresh import st_autorefresh
except:
    pass

st.set_page_config(page_title="BTC Forecast", layout="wide")

# Рефреш каждые 10 минут
st_autorefresh(interval=600000, key="f5_refresh")

@st.cache_data(ttl=300)
def get_data():
    df = yf.download('BTC-USD', period='14d', interval='1h', auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df, datetime.now().strftime("%H:%M:%S")

try:
    df, up_time = get_data()
    last_p = float(df['Close'].iloc[-1])
    last_d = df.index[-1]

    # Шапка страницы
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("BTC Forecast") # Только эта надпись
    with c2:
        st.write(f"⏱ Обновлено: **{up_time}**")
        if st.button("Обновить"):
            st.cache_data.clear()
            st.rerun()

    # Прогнозная логика
    f_steps = 18 
    f_dates = [last_d + timedelta(hours=i*4) for i in range(1, f_steps + 1)]
    np.random.seed(42)
    vals = np.linspace(last_p, last_p * 0.9744, f_steps) + np.random.normal(0, last_p*0.001, f_steps)

    # Визуализация
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Сетка и линии
    ax.plot(df.index, df['Close'], label='Цена', color='#3498db', lw=2)
    ax.plot([last_d] + f_dates, [last_p] + list(vals), label='Прогноз', color='#f39c12', ls='--', lw=2)
    
    # Облако вероятности
    ax.fill_between([last_d] + f_dates, 
                    np.array([last_p] + list(vals*0.97)), 
                    np.array([last_p] + list(vals*1.03)), 
                    color='#f39c12', alpha=0.1)

    ax.axvline(last_d, color='red', ls=':', alpha=0.5)
    ax.grid(True, alpha=0.1)
    ax.legend(loc='upper left')
    
    st.pyplot(fig)
    
    # Инфо-панель
    m1, m2, m3 = st.columns(3)
    m1.metric("Цена", f"${last_p:,.2f}")
    m2.metric("Цель", f"${vals[-1]:,.2f}", delta="-2.56%")
    m3.metric("Период", "3 дня")

except Exception as e:
    st.error(f"Ошибка: {e}")
