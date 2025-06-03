import logging

from FlaskRestAPI.app.definition import app_version
from FlaskRestAPI.app.httpresponses import *

logger = logging.getLogger(__name__)

def test_Info_get(client):
    logger.info("GET .../opa/info")
    response = client.get('opa/info')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    data = response.get_json()
    assert len(data.keys()) == 2, f"Expected 2 values, but got {data.keys()}"
    assert "info" in data.keys()
    assert "ApiDoc" in data.keys()
    assert f"Version {app_version}" in data['info']

def test_Info_get_wrong_endpoint(client):
    logger.info("GET .../opa/infos")
    response = client.get('opa/infos')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NOT_FOUND
