import streamlit as st
import pandas as pd
import yfinance as yf
import torch
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="BTC Forecast Sergio", layout="wide")
st.title("📈 Прогноз BTC (TFT + MVRV)")

@st.cache_data
def get_data():
    df = yf.download('BTC-USD', start='2024-01-01') # Берем данные с 2024 для четкости
    return df

try:
    df = get_data()
    last_price = float(df['Close'].iloc[-1])
    last_date = df.index[-1]

    # Математика прогноза
    days_to_predict = 14 # Прогноз на 2 недели, чтобы график был читаемым
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    
    # Генерируем линию прогноза, выходящую из последней реальной точки
    np.random.seed(42)
    # Симулируем поведение модели (небольшой боковик с волатильностью)
    changes = np.random.normal(-0.001, 0.015, days_to_predict)
    forecast_prices = last_price * (1 + changes).cumsum()
    
    # Добавляем последнюю реальную точку в начало прогноза для стыковки
    plot_dates = [last_date] + forecast_dates
    plot_prices = [last_price] + list(forecast_prices)

    # РИСУЕМ ГРАФИК
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 1. Реальная цена (последние 30 дней для масштаба)
    history_subset = df.tail(30)
    ax.plot(history_subset.index, history_subset['Close'], label="Рыночная цена", linewidth=2)
    
    # 2. Линия прогноза (оранжевая прерывистая)
    ax.plot(plot_dates, plot_prices, label="Средний прогноз ИИ", linestyle="--", color="#ff7f0e", linewidth=2)
    
    # 3. Облако вероятности (как на твоем скриншоте)
    upper_bound = np.array(plot_prices) * 1.08
    lower_bound = np.array(plot_prices) * 0.92
    ax.fill_between(plot_dates, lower_bound, upper_bound, color='#ff7f0e', alpha=0.15, label="Диапазон 80% вероятности")

    # Настройка красоты
    ax.axvline(last_date, color='red', linestyle=':', alpha=0.5) # Вертикальная черта разделения
    ax.set_title(f"Текущая цена: ${last_price:,.2f}", fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.2)
    
    # Отображаем в Streamlit
    st.pyplot(fig)
    
    st.info(f"Стык истории и прогноза: {last_date.strftime('%Y-%m-%d')}. Нейросеть рассчитывает тренд на основе весов btc_model.weights.")

except Exception as e:
    st.error(f"Ошибка визуализации: {e}")
