import streamlit as st
import pandas as pd
import yfinance as yf
import torch
import pytorch_lightning as pl
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import QuantileLoss
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BTC Forecast Sergio", layout="wide")
st.title("📈 Прогноз BTC: Модель TFT + MVRV")

# 1. Загрузка данных с принудительным преобразованием типов
@st.cache_data
def get_btc_data():
    df = yf.download('BTC-USD', start='2020-01-01')
    df = df.reset_index()
    # ПРИНУДИТЕЛЬНО делаем колонку Close числом (float)
    df['Close'] = df['Close'].astype(float)
    df['time_idx'] = (df['Date'] - df['Date'].min()).dt.days
    df['group'] = 0
    # Добавляем MVRV и тоже в float
    df['mvrv'] = (df['Close'] / df['Close'].rolling(30).mean()).astype(float)
    return df.dropna().reset_index(drop=True)

try:
    data = get_btc_data()

    # 2. Описание архитектуры
    def load_model(data):
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
        
        try:
            model.load_state_dict(torch.load("btc_model.weights", map_location=torch.device('cpu')))
            return model, training
        except:
            return None, training

    model, training = load_model(data)

    # 3. Отрисовка
    st.subheader("История цены и прогноз")
    if model:
        st.success("Модель успешно загружена!")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['Date'].tail(100), data['Close'].tail(100), label="Реальность")
        ax.set_title("График BTC (Последние 100 дней)")
        st.pyplot(fig)
    else:
        st.warning("Веса модели не загружены, показываю просто график цен.")
        st.line_chart(data.set_index('Date')['Close'])

except Exception as e:
    st.error(f"Произошла ошибка при подготовке данных: {e}")

st.write(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")
