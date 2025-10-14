import pytest
from app import app
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

@pytest.fixture
def client():
    app.testing = True
    app.secret_key = "test_secret_key"
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Check if the home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"<html" in response.data or b"<!DOCTYPE html" in response.data

def test_get_reservations_initially_empty(client):
    """Ensure no reservations exist when starting a new session"""
    response = client.get('/get_reservations')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data == []

def test_process_reservation_incomplete(client):
    """Test chatbot response when info is missing"""
    payload = {"message": "Book me an appointment", "current_reservation": {}}
    response = client.post('/process_reservation', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert data["success"] == True
