from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_restaurant():
    payload = {
        "name": "Restaurante Test",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 2
    }
    response = client.post("/api/v1/restaurants", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Restaurante Test"

def test_invalid_price():
    payload = {
        "name": "Restaurante Test",
        "category": "Mexicana",
        "city": "Puebla",
        "price": 10
    }
    response = client.post("/api/v1/restaurants", json=payload)
    assert response.status_code == 422