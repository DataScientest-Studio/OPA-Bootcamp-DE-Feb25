import logging

from FlaskRestAPI.app.definition import app_version
from FlaskRestAPI.app.httpresponses import *

logger = logging.getLogger(__name__)

def test_Cryptocoincandle_get_ticker_not_found(client):
    logger.info("GET .../opa/info - ticker NOT found")
    response = client.get("opa/candels?ticker=BTCTUSD&startDate=20001201000000&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NOT_FOUND

def test_Cryptocoincandle_get_interval_not_found(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    response = client.post("opa/cryptocoins", json=coins)
    response = client.get("opa/candels?ticker=BTC&startDate=20001201000000&interval=1d")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NOT_FOUND

def test_Cryptocoincandle_get_wrong_star_date(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    response = client.post("opa/cryptocoins", json=coins)
    logging.debug("Add interval Week/1w")
    intervals = [{'name_long': 'Week', 'name_short': '1w'}]
    client.post('opa/intervals', json=intervals)
    logger.info("GET .../opa/candels - no data retrieved")
    response = client.get("opa/candels?ticker=BTC&startDate=200012010000&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_BAD_REQUEST

def test_Cryptocoincandle_get_no_data(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    response = client.post("opa/cryptocoins", json=coins)
    logging.debug("Add interval Week/1w")
    intervals = [{'name_long': 'Week', 'name_short': '1w'}]
    client.post('opa/intervals', json=intervals)
    logger.info("GET .../opa/candels - no data retrieved")
    response = client.get("opa/candels?ticker=BTC&startDate=20001201000000&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NO_CONTENT

def test_Cryptocoincandle_get_OK(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    client.post("opa/cryptocoins", json=coins)
    logging.debug("Add interval Week/1w")
    intervals = [{'name_long': 'Week', 'name_short': '1w'}]
    client.post('opa/intervals', json=intervals)
    candels = [{"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-28T13:38:01.180072+02:00"},
                {"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-27T13:38:01.180072+02:00"}]
    response = client.post("opa/candels", json=candels)
    logger.info("GET .../opa/candels - two record received")
    response = client.get("opa/candels?ticker=BTC&startDate=20250401000000&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    data = response.get_json()
    assert len(data) == 2, f"Expected 2 items, but got {len(data)}"

def test_Cryptocoincandle_get_data_between(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    client.post("opa/cryptocoins", json=coins)
    logging.debug("Add interval Week/1w")
    intervals = [{'name_long': 'Week', 'name_short': '1w'}]
    client.post('opa/intervals', json=intervals)
    candels = [{"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-28T13:38:01.180072+02:00"},
                {"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-27T13:38:01.180072+02:00"}]
    response = client.post("opa/candels", json=candels)
    logger.info("GET .../opa/candels - two record received")
    response = client.get("opa/candels?ticker=BTC&startDate=20250401000000&endDate=20250427235959&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    data = response.get_json()
    assert len(data) == 1, f"Expected 1 items, but got {len(data)}"

def test_Cryptocoincandle_get_between_no_data(client):
    logging.debug("Add ticker BTC")
    coins = [{"name":"BTCTUSD", "ticker":"BTC"}]
    client.post("opa/cryptocoins", json=coins)
    logging.debug("Add interval Week/1w")
    intervals = [{'name_long': 'Week', 'name_short': '1w'}]
    client.post('opa/intervals', json=intervals)
    candels = [{"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-28T13:38:01.180072+02:00"},
                {"crypto_id": 1, "interval_id": 1,"open_price":1.2, "close_price":1.31,
                "high_price": 1.4, "low_price":1.19,
                "volume": 1200.0, "close_time":"2025-04-27T13:38:01.180072+02:00"}]
    response = client.post("opa/candels", json=candels)
    logger.info("GET .../opa/candels - two record received")
    response = client.get("opa/candels?ticker=BTC&startDate=20250401000000&endDate=20250427133800&interval=1w")
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NO_CONTENT
    data = response.get_json(force=True, silent=True)
    assert data is None, f"Expected 0 items, but got {len(data) if data is not None else 0}"
