import io
import pytest
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == 'ok'

def test_remove_no_file(client):
    rv = client.post('/remove')
    assert rv.status_code == 400
    json_data = rv.get_json()
    assert 'error' in json_data

def test_remove_invalid_file(client):
    data = {
        'image': (io.BytesIO(b"notanimage"), 'test.txt')
    }
    rv = client.post('/remove', data=data, content_type='multipart/form-data')
    assert rv.status_code == 400
    json_data = rv.get_json()
    assert 'error' in json_data
