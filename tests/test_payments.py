import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import DB_PATH

@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Give each test a fresh database so tests do not depend on previous runs.
    test_db = tmp_path / "test_payments.db"
    monkeypatch.setattr("app.database.DB_PATH", test_db)
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_successful_payment_is_saved(client):
    response = client.post("/payments", json={"amount": 125.50, "currency": "INR"})
    assert response.status_code == 201
    body = response.json()["payment"]
    assert body["status"] == "succeeded"
    assert body["amount"] == 125.5
    assert client.get(f"/payments/{body['id']}").json()["payment"]["status"] == "succeeded"

def test_simulated_decline_is_saved_as_failed(client):
    response = client.post("/payments", json={"amount": 80, "simulate_decline": True})
    assert response.status_code == 201
    assert response.json()["payment"]["status"] == "failed"

@pytest.mark.parametrize("amount", [0, -1, -0.01])
def test_non_positive_amount_is_rejected(client, amount):
    response = client.post("/payments", json={"amount": amount})
    assert response.status_code == 422

def test_missing_amount_is_rejected(client):
    assert client.post("/payments", json={"currency": "INR"}).status_code == 422

def test_unknown_payment_returns_404(client):
    response = client.get("/payments/pay_doesnotexist")
    assert response.status_code == 404

def test_idempotency_key_prevents_duplicate_payment(client):
    headers = {"Idempotency-Key": "order-abc-123"}
    first = client.post("/payments", json={"amount": 49.99}, headers=headers)
    second = client.post("/payments", json={"amount": 49.99}, headers=headers)
    assert first.status_code == 201 and second.status_code == 201
    assert first.json()["payment"]["id"] == second.json()["payment"]["id"]
    assert len(client.get("/payments").json()["payments"]) == 1

def test_invalid_currency_is_rejected(client):
    response = client.post("/payments", json={"amount": 10, "currency": "12!"})
    assert response.status_code == 422
