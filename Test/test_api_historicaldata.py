import logging
from datetime import datetime
import tzlocal

from FlaskRestAPI.app.definition import app_version
from FlaskRestAPI.app.httpresponses import *

logger = logging.getLogger(__name__)

def test_Historicaldata_get_no_data(client):
    logger.info("GET .../ope/historicaldata")
    response = client.get('ope/historicaldata')
    assert response.status_code == HTTP_NO_CONTENT
    data = response.get_json(force=True, silent=True)
    assert data is None, f"Expected 0 items, but got {len(data) if data is not None else 0}"

def test_Historicaldata_get_OK(client):
    logger.info("GET .../ope/historicaldata")
    updated_at = {'updated_at': datetime.now(tzlocal.get_localzone()).isoformat()}
    response = client.post("ope/historicaldata", json=updated_at)
    response = client.get('ope/historicaldata')
    assert response.status_code == HTTP_OK
    data = response.get_json(force=True, silent=True)
    logging.info(f"Data received: {data}")
    assert len(data) == 1, f"Expected 1 item, but got {len(data)}"

def test_Historicaldata_post_no_data(client):
    logger.info("POST .../ope/historicaldata")
    response = client.post('ope/historicaldata')
    assert response.status_code == HTTP_BAD_REQUEST

def test_Historicaldata_post_OK(client):
    logger.info("POST .../ope/historicaldata")
    updated_at = {'updated_at': datetime.now(tzlocal.get_localzone()).isoformat()}
    response = client.post('ope/historicaldata', json=updated_at)
    assert response.status_code == HTTP_CREATED

def test_Historicaldata_post_invalid_date(client):
    logger.info("POST .../ope/historicaldata")
    updated_at = {'updated_at': '2023-99-99T99:99:99'}
    response = client.post("ope/historicaldata", json=updated_at)
    assert response.status_code == HTTP_BAD_REQUEST
