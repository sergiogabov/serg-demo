import streamlit as st
import pandas as pd
import yfinance as yf
import torch
import pytorch_lightning as pl
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import QuantileLoss
import matplotlib.pyplot as plt

st.set_page_config(page_title="BTC Forecast Sergio", layout="wide")
st.title("📈 Прогноз BTC: Модель TFT + MVRV")

# 1. Загрузка данных
@st.cache_data
def get_btc_data():
    df = yf.download('BTC-USD', start='2020-01-01')
    df = df.reset_index()
    df['time_idx'] = (df['Date'] - df['Date'].min()).dt.days
    df['group'] = 0
    # Добавляем заглушку MVRV, если ее нет в yfinance
    df['mvrv'] = df['Close'] / df['Close'].rolling(30).mean() 
    return df.fillna(method='ffill').dropna()

data = get_btc_data()

# 2. Описание архитектуры (нужно для загрузки весов)
# Мы создаем структуру, которую ты прислал
def load_model(data):
    # Создаем минимальный dataset для инициализации структуры
    max_prediction_length = 30
    max_encoder_length = 60
    
    training = TimeSeriesDataSet(
        data,
        time_idx="time_idx",
        target="Close",
        group_ids=["group"],
        min_encoder_length=max_encoder_length // 2,
        max_encoder_length=max_encoder_length,
        min_prediction_length=1,
        max_prediction_length=max_prediction_length,
        static_categoricals=["group"],
        time_varying_known_reals=["time_idx"],
        time_varying_unknown_reals=["Close", "mvrv"],
        target_normalizer=None
    )

    # Та самая архитектура из твоего сообщения
    model = TemporalFusionTransformer.from_dataset(
        training,
        learning_rate=0.03,
        hidden_size=16,
        attention_head_size=4,
        dropout=0.1,
        hidden_continuous_size=8,
        loss=QuantileLoss(),
        optimizer="Adam"
    )
    
    # Загружаем твои сохраненные веса
    try:
        model.load_state_dict(torch.load("btc_model.weights", map_location=torch.device('cpu')))
        return model, training
    except:
        return None, training

model, training = load_model(data)

# 3. Отрисовка
st.subheader("История цены и прогноз")
if model:
    # Здесь логика предсказания
    raw_predictions = model.predict(data.tail(60), mode="raw", return_x=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['Date'].tail(50), data['Close'].tail(50), label="История")
    st.pyplot(fig)
    st.success("Модель успешно загружена и работает на реальных весах!")
else:
    st.warning("Сайт работает в демо-режиме (веса модели не найдены или не подошли).")
    st.line_chart(data.set_index('Date')['Close'])

st.write("Данные обновлены:", datetime.now().strftime("%Y-%m-%d %H:%M"))
