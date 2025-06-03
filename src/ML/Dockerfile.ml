FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./models/lstm_BTC_model_V1.h5 ./models/lstm_BTC_model_V1.h5
COPY ./scaler_BTC_model_V1.pkl ./models/scaler_BTC_model_V1.pkl
COPY train_btc_model.py ./train_model.py
COPY predict_btc_price.py ./predict_price.py

CMD ["tail", "-f", "/dev/null"]