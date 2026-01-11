import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="BTC Monitor", layout="wide")
st.title("📊 Мониторинг BTC (Данные Yahoo Finance)")

# 1. Загрузка реальных данных
@st.cache_data
def get_data():
    # Берем данные за последние полгода
    df = yf.download('BTC-USD', period='6mo', interval='1d')
    return df

try:
    df = get_data()
    last_price = float(df['Close'].iloc[-1])
    
    # 2. Считаем простой скользящий тренд (SMA 20) - это честнее, чем рандом
    df['SMA20'] = df['Close'].rolling(window=20).mean()

    # 3. Рисуем график
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Реальная цена
    ax.plot(df.index, df['Close'], label='Цена BTC (USD)', color='#1f77b4', lw=2)
    
    # Линия тренда (вместо безумного прогноза)
    ax.plot(df.index, df['SMA20'], label='Линия тренда (SMA 20)', color='#ff7f0e', linestyle='--')

    ax.set_title(f"Текущий курс: ${last_price:,.2f}", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Устанавливаем нормальный масштаб (не в миллионах!)
    ax.set_ylim(df['Close'].min() * 0.9, df['Close'].max() * 1.1)

    st.pyplot(fig)
    
    st.write("Прогноз на 30 дней временно отключен, чтобы не выдавать ошибки. Сейчас на графике — реальный рыночный тренд.")

except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")
