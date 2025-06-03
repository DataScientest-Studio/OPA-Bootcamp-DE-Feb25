import numpy as np
import pandas as pd
import requests
from tensorflow.keras.models import load_model
import joblib

# Binance API endpoint for historical data
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def fetch_historical_data(symbol="BTCUSDT", interval="1h", limit=60):
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

# Load the model and scaler
print("Loading the model and scaler...")
model = load_model("lstm_model.h5")  # Load the saved model
scaler = joblib.load("scaler.pkl")  # Load the saved scaler

# Fetch recent data for testing
symbol = "BTCUSDT"
interval = "1h"
print(f"Fetching recent data for {symbol}...")
recent_data = fetch_historical_data(symbol, interval, limit=60)  # Fetch the last 60 data points

# Prepare the data for prediction
recent_prices = recent_data["close"].values.reshape(-1, 1)
scaled_recent_prices = scaler.transform(recent_prices)
X_new = scaled_recent_prices.reshape((1, scaled_recent_prices.shape[0], 1))  # Reshape for LSTM

# Predict future price
print("Predicting the next price...")
predicted_price = model.predict(X_new)
predicted_price = scaler.inverse_transform(predicted_price)
print(f"Predicted Price: {predicted_price[0][0]}")