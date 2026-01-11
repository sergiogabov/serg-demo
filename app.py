import streamlit as st
import pandas as pd
import yfinance as yf
import torch
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BTC Forecast Sergio", layout="wide")
st.title("📈 Прогноз BTC: Модель TFT + MVRV")

# 1. Загрузка данных - максимально просто
@st.cache_data
def get_btc_data():
    # Качаем данные
    df = yf.download('BTC-USD', start='2020-01-01')
    # Сбрасываем индекс, чтобы Date стала колонкой
    df = df.reset_index()
    # Оставляем только нужные колонки и превращаем их в обычные массивы чисел
    clean_df = pd.DataFrame({
        'Date': df['Date'],
        'Close': df['Close'].values.flatten().astype(float)
    })
    return clean_df

try:
    data = get_btc_data()

    # 2. Попытка загрузить веса
    st.subheader("График цены BTC")
    
    # Рисуем график через встроенный инструмент Streamlit (он самый надежный)
    st.line_chart(data.set_index('Date')['Close'])
    
    # Проверяем файл весов
    try:
        weights = torch.load("btc_model.weights", map_location=torch.device('cpu'))
        st.success("✅ Файл весов btc_model.weights обнаружен!")
    except Exception as e:
        st.info("ℹ️ Файл весов пока не подключен к модели, но данные загружаются корректно.")

except Exception as e:
    st.error(f"Ошибка: {e}")

st.write(f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")
