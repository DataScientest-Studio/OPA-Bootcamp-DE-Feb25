import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

# Binance API endpoint for historical data
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def fetch_historical_data(symbol="BTCUSDT", interval="1h", limit=1000):
    """
    Fetch historical data from Binance API.
    Args:
        symbol (str): Trading pair (e.g., BTCUSDT).
        interval (str): Time interval (e.g., 1h, 1d).
        limit (int): Number of data points to fetch (max 1000 per request).
    Returns:
        pd.DataFrame: Historical data as a DataFrame.
    """
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(BINANCE_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df[["timestamp", "close"]]

def prepare_data(data, time_steps=60):
    """
    Prepare data for LSTM training.
    Args:
        data (pd.DataFrame): DataFrame containing the 'close' prices.
        time_steps (int): Number of time steps to use for prediction.
    Returns:
        np.array, np.array, MinMaxScaler: Features (X), target (y), and scaler.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data["close"].values.reshape(-1, 1))
    X, y = [], []
    for i in range(time_steps, len(scaled_data)):
        X.append(scaled_data[i-time_steps:i, 0])
        y.append(scaled_data[i, 0])
    return np.array(X), np.array(y), scaler

def build_lstm_model(input_shape):
    """
    Build an LSTM model for time series prediction.
    Args:
        input_shape (tuple): Shape of the input data (time_steps, features).
    Returns:
        keras.Model: Compiled LSTM model.
    """
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model

def train_and_save_model(symbol="BTCUSDT", interval="1h", time_steps=60, epochs=10, batch_size=32):
    """
    Train an LSTM model on historical Binance data and save it locally.
    Args:
        symbol (str): Trading pair (e.g., BTCUSDT).
        interval (str): Time interval (e.g., 1h, 1d).
        time_steps (int): Number of time steps to use for prediction.
        epochs (int): Number of training epochs.
        batch_size (int): Batch size for training.
    """
    # Fetch historical data
    print(f"Fetching historical data for {symbol}...")
    data = fetch_historical_data(symbol, interval)
    
    # Prepare data
    print("Preparing data...")
    X, y, scaler = prepare_data(data, time_steps)
    X = X.reshape((X.shape[0], X.shape[1], 1))  # Reshape for LSTM

    # Split into training and testing sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Build and train the model
    print("Building and training the model...")
    model = build_lstm_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, validation_data=(X_test, y_test),
              epochs=epochs, batch_size=batch_size, verbose=1)

    # Save the model and scaler
    print("Saving the model and scaler...")
    model.save("lstm_model.h5")  # Save the model
    joblib.dump(scaler, "scaler.pkl")  # Save the scaler
    print("Model and scaler saved successfully!")

if __name__ == "__main__":
    train_and_save_model()