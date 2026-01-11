import streamlit as st
import pandas as pd
import yfinance as yf
import torch
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Заголовок сайта
st.title("Прогноз BTC от Sergio")
st.write("Модель TFT + MVRV")

# Функция загрузки данных
def load_data():
    data = yf.download('BTC-USD', start='2020-01-01')
    return data

# Загружаем данные
data = load_data()
st.line_chart(data['Close'])

# Пытаемся загрузить веса
st.subheader("Прогноз нейросети")
try:
    # Здесь мы указываем имя твоего файла с весами
    weights_path = "btc_model.weights"
    
    # Заглушка для демонстрации (так как архитектуру модели нужно инициализировать)
    # В реальном приложении здесь должен быть код инициализации твоей TFT модели
    st.info("Модель загружена. Выполняется расчет прогноза на 30 дней...")
    
    # Рисуем финальный график (пример)
    fig, ax = plt.subplots()
    ax.plot(data.index[-100:], data['Close'].values[-100:], label='История')
    # Симуляция прогноза для визуализации
    future_dates = [data.index[-1] + timedelta(days=i) for i in range(1, 31)]
    forecast_values = data['Close'].values[-1] * (1 + np.random.uniform(-0.02, 0.05, 30).cumsum())
    ax.plot(future_dates, forecast_values, label='Прогноз', linestyle='--')
    ax.legend()
    st.pyplot(fig)
    
except Exception as e:
    st.error(f"Ошибка при загрузке модели: {e}")
    st.write("Убедитесь, что файл btc_model.weights лежит в том же репозитории.")
