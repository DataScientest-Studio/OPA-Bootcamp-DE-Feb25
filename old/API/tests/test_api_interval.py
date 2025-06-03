import logging

from FlaskRestAPI.app.httpresponses import *

logger = logging.getLogger(__name__)

def test_Interval_post_valid_many(client):
    logger.info("Add two Interval with name_short = 1H and with name_short = 1D")
    response = client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'},
        {'name_long': 'Day', 'name_short': '1D'}
    ])
    logger.debug(f"POST Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_CREATED
    data = response.get_json()
    assert len(data) == 2, f"Expected 2 items, but got {len(data)}"
    assert data[0]['id'] == 1
    assert data[0]['name_short'] == '1H'
    assert data[0]['name_long'] == 'Hour'
    assert data[1]['id'] == 2
    assert data[1]['name_short'] == '1D'
    assert data[1]['name_long'] == 'Day'

def test_Interval_post_duplicate_short_name(client):
    logger.info("Add Interval with name_short = 1H")
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'}
    ])
    logger.info("Add duplicated Interval with name_short = 1H")
    response = client.post('ope/intervals', json=[
        {'name_long': 'Duplicate Hour', 'name_short': '1H'}
    ])
    logger.debug(f"POST Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_CONFLICT
    assert 'Integrity error' in response.get_json()['message']

def test_Interval_get_all_200(client):
    logger.info("Add two Interval with name_short = 1H and with name_short = 1D")
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'},
        {'name_long': 'Day', 'name_short': '1D'}
    ])
    response = client.get('ope/intervals')
    logger.debug(f"GETReceived response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    assert len(response.get_json()) == 2

def test_Interval_get_by_id(client):
    logger.info("Add two Interval with name_short = 1H")
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'}
    ])
    response = client.get('ope/intervals/1')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    assert response.get_json()['name_short'] == '1H'

def test_Interval_get_nonexistent(client):
    logger.info("Get an noneexistent Interval item id = 999")
    response = client.get('ope/interval/999')
    logger.debug(f"GET Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_NOT_FOUND

def test_Interval_patch(client):
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'}
    ])
    response = client.patch('ope/intervals/1', json={
        'name_long': 'Updated Hour',
        'name_short': '1U'
    })
    logger.debug(f"PATCH Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    response_data = response.get_json()
    assert response_data['name_long'] == 'Updated Hour', f"Expected 'Updated Hour', but got '{response_data['name_long']}'"
    assert response_data['name_short'] == '1U', f"Expected '1U', but got '{response_data['name_short']}'"

def test_Interval_patch_no_data(client):
    response = client.patch('ope/intervals/1')
    logger.debug(f"PATCH Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_BAD_REQUEST

def test_Interval_delete_by_id(client):
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'}
    ])
    response = client.delete('ope/intervals/1')
    logger.debug(f"DELETE Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    assert 'deleted' in response.get_data(as_text=True)

def test_Interval_delete_all(client):
    client.post('ope/intervals', json=[
        {'name_long': 'Hour', 'name_short': '1H'},
        {'name_long': 'Day', 'name_short': '1D'}
    ])
    response = client.delete('ope/intervals')
    logger.debug(f"DELETE Received response: {response.status_code} - {response.text}")
    assert response.status_code == HTTP_OK
    assert 'deleted' in response.get_data(as_text=True)
    response = client.get('ope/intervals')
    assert len(response.get_json()) == 0, f"Expected 0 items, but got {len(response.get_json())}"
