import logging

from FlaskRestAPI.app.httpresponses import *

logger = logging.getLogger(__name__)

coins = [{"name":"BTCTUSD", "ticker":"BTC"},
        {"name":"BTCTEUR", "ticker":"BTCEUR"}]

def test_Cryptocoin_post(client):
    response = client.post("ope/cryptocoins", json=coins)
    logger.debug(f"POST Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_CREATED
    data = response.get_json()
    assert len(data) == 2, f"Expected 1 Crypto Coin record, but got {len(data)}"
    assert data[0]["id"] == 1
    assert data[0]["name"] == "BTCTUSD"
    assert data[0]["ticker"] == "BTC"
    assert data[1]["id"] == 2
    assert data[1]["name"] == "BTCTEUR"
    assert data[1]["ticker"] == "BTCEUR"

def test_Cryptocoin_get_no_content(client):
    logger.info("GET .../ope/cryptocoins")
    response = client.get('ope/cryptocoins')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NO_CONTENT
    assert response.is_json, "Expected None, got a JSON content"

def test_Cryptocoin_get_all(client):
    logger.info("GET .../ope/cryptocoins")
    response = client.post('ope/cryptocoins', json=coins)
    response = client.get('ope/cryptocoins')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    assert response.is_json, "Expected JSON, got None"
    data = response.get_json()
    assert len(data) == 2, f"Expected 2 Crypto Coin record, but got {len(data)}"
    assert data[0]["id"] == 1
    assert data[0]["name"] == "BTCTUSD"
    assert data[0]["ticker"] == "BTC"
    assert data[1]["id"] == 2
    assert data[1]["name"] == "BTCTEUR"
    assert data[1]["ticker"] == "BTCEUR"

def test_Cryptocoin_delete_one(client):
    logger.info("DELETE .../ope/cryptocoins/1")
    logger.info("DELETE - first POST a CryptoCoin")
    response = client.post("ope/cryptocoins", json=coins)
    logger.info("DELETE - previously posted item")
    response = client.delete("ope/cryptocoins/1")
    logger.debug(f"DELETE Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK

def test_Cryptocoin_delete_noneexistent(client):
    logger.info("DELETE .../ope/cryptocoins/999")
    response = client.delete("ope/cryptocoins/999")
    logger.debug(f"DELETE Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NOT_FOUND

def test_Cryptocoin_patch(client):
    response = client.post("ope/cryptocoins", json=coins)
    coins_update = [{"name":"BTCTUSDx", "ticker":"BTCx"}]
    response = client.patch("ope/cryptocoins/1", json=coins_update[0])
    assert response.status_code == HTTP_OK
    data = response.get_json()
    assert data["name"] == "BTCTUSDx"
    assert data["ticker"] == "BTCx"

def test_Cryptocoin_patch_integrity_err(client):
    response = client.post("ope/cryptocoins", json=coins)
    coins_update = [{"name":"BTCTEUR", "ticker":"BTC"}]
    response = client.patch("ope/cryptocoins/2", json=coins_update[0])
    assert response.status_code == HTTP_CONFLICT
