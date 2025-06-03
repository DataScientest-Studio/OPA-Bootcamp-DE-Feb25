import requests
import logging
import os

logger = logging.getLogger(__name__) 

API_GET_COINS_ENDPOINGT = "/opa/cryptocoins"
API_GET_INTERVALS_ENDPOINT = "/opa/intervals"
API_GET_CRYPTO_COIN_CANDLE_ENDPOINT = "/opa/candels"
API_GET_MODELS_ENDPOINT = "/opa/models"

def api_get_coins():
    """
    Fetches asset data from an API.
    """
    opa_api = os.getenv("API_URL", "http://localhost:8088")
    response = requests.get(opa_api + API_GET_COINS_ENDPOINGT)
    if response.status_code != 200 & response.status_code != 204:
        e_msg = f"Error fetching coin data from API: {response.status_code} - {response.text}"
        # Log the error message
        logger.error(e_msg)
        # Raise an exception with the error message
        raise Exception(e_msg)
    else:
        logger.info(f"Successfully fetched coins data from API: {response.status_code}")
        # Return the JSON response if the request was successful
        return response.json()

def api_get_intervals():
    """
    Fetches interval data from an API.
    """
    opa_api = os.getenv("API_URL", "http://localhost:8088")
    response = requests.get(opa_api + API_GET_INTERVALS_ENDPOINT)
    if response.status_code != 200:
        e_msg = f"Error fetching interval data from API: {response.status_code} - {response.text}"
        # Log the error message
        logger.error(e_msg)
        # Raise an exception with the error message
        raise Exception(e_msg)
    else:
        logger.info(f"Successfully fetched interval data from API: {response.status_code}")
        # Return the JSON response if the request was successful
        return response.json()

def api_get_candels(ticker: str, startDate : str, endDate : str, interval: str):
    """
    Fetches crypto coin candle data from an API.
    """
    logger.debug(f"Fetching candle data for ticker: {ticker}, interval: {interval}")
    opa_api = os.getenv("API_URL", "http://localhost:8088")
    params = f"?ticker={ticker}&startDate={startDate}&endDate={endDate}&interval={interval}"
    logger.debug(f"API request parameters: {params}")
    response = requests.get(opa_api + API_GET_CRYPTO_COIN_CANDLE_ENDPOINT + params)
    if response.status_code != 200:
        e_msg = f"Error fetching candels data from API: {response.status_code} - {response.text}"
        # Log the error message
        logger.error(e_msg)
        # Raise an exception with the error message
        raise Exception(e_msg)
    else:
        logger.info(f"Successfully fetched candle data from API: {response.status_code}")
        # Return the JSON response if the request was successful
        return response.json()

def get_current_prices():
    """
    Fetches the current price of Bitcoin (BTC) in USDT from Binance API.
    Returns:
        float: Current price of Bitcoin in USDT.
        float: Current price of Pepecoin in USDT.
        float: Current price of Ripple in USDT.
    """
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    btcPrice = float(data['price'])

    url = "https://api.binance.com/api/v3/ticker/price?symbol=PEPEUSDT"
    response = requests.get(url)
    data = response.json()
    pepPrice = float(data['price'])

    url = "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT"
    response = requests.get(url)
    data = response.json()
    xrpPrice = float(data['price'])

    return btcPrice, pepPrice, xrpPrice

def api_get_available_models(ticker: str):
    logger.debug(f"Fetching models data for ticker: {ticker}")
    opa_api = os.getenv("API_URL", "http://localhost:8088")
    payload = {"ticker": ticker}
    headers = {"Content-Type": "application/json"}
    response = requests.post(opa_api + API_GET_MODELS_ENDPOINT, json=payload, headers=headers)
    if response.status_code != 200 and response.status_code != 204:
        e_msg = f"Error fetching modelsfrom API for ticker[{ticker}] : {response.status_code} - {response.text}"
        # Log the error message
        logger.error(e_msg)
        # Raise an exception with the error message
        raise Exception(e_msg)
    else:
        logger.info(f"Successfully fetched model data from API: {response.status_code}")
        # Return the JSON response if the request was successful
        return response.json()

