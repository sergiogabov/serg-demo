import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="BTC Live", layout="wide")
st.title("📊 Мониторинг котировок BTC")

@st.cache_data
def get_data():
    # Качаем данные за последние 3 месяца
    # auto_adjust=True и flat=True лечат ошибку с заголовками
    data = yf.download('BTC-USD', period='3mo', interval='1d', auto_adjust=True)
    return data

try:
    df = get_data()
    
    # Исправляем проблему MultiIndex (из-за которой вылетает ошибка)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Получаем последнюю цену как число
    last_price = float(df['Close'].iloc[-1])
    
    # Рисуем график
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Основная линия цены
    ax.plot(df.index, df['Close'], label='Цена закрытия (USD)', color='#1f77b4', lw=2)
    
    # Добавляем простое скользящее среднее для тренда
    sma = df['Close'].rolling(window=10).mean()
    ax.plot(df.index, sma, label='Тренд (SMA 10)', color='#ff7f0e', linestyle='--')

    ax.set_title(f"Актуальный курс: ${last_price:,.2f}", fontsize=14)
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    # Автоматически подбираем масштаб, чтобы график был четким
    ax.margins(x=0.01, y=0.1)

    st.pyplot(fig)
    
    # Выводим цифры крупно
    st.metric("BTC/USD", f"${last_price:,.2f}")

except Exception as e:
    st.error(f"Техническая ошибка: {e}")
    st.info("Попробуй обновить страницу через минуту.")
