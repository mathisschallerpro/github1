import os
import importlib.util
import pytest
from uuid import uuid4

from fastapi.testclient import TestClient


def load_app_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'src', 'app.py')
    spec = importlib.util.spec_from_file_location('app_module', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def client():
    module = load_app_module()
    return TestClient(module.app)


def test_get_activities(client):
    # Arrange: client fixture ready
    # Act
    resp = client.get('/activities')

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert 'Chess Club' in data


def test_signup_adds_participant(client):
    # Arrange
    email = f'integration-{uuid4().hex}@example.com'
    resp = client.get('/activities')
    before = len(resp.json()['Chess Club']['participants'])

    # Act
    resp = client.post(f'/activities/Chess%20Club/signup?email={email}')

    # Assert
    assert resp.status_code == 200
    resp = client.get('/activities')
    after = len(resp.json()['Chess Club']['participants'])
    assert after == before + 1


def test_delete_participant(client):
    # Arrange
    email = f'to-remove-{uuid4().hex}@example.com'
    client.post(f'/activities/Chess%20Club/signup?email={email}')

    # Act
    resp = client.delete(f'/activities/Chess%20Club/participants?email={email}')

    # Assert
    assert resp.status_code == 200
    resp = client.get('/activities')
    participants = resp.json()['Chess Club']['participants']
    assert email not in participants
