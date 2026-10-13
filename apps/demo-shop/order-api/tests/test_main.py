import time
from app.config import settings

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "order-api", "version": "0.1.0"}

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_list_orders(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.json()) >= 5

def test_get_order(client):
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_order_not_found(client):
    response = client.get("/api/orders/999")
    assert response.status_code == 404

def test_create_order(client):
    response = client.post("/api/orders", json={"product_id": 2, "quantity": 3})
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == 2
    assert data["quantity"] == 3
    assert data["status"] == "pending"

def test_failure_mode_error(client, monkeypatch):
    monkeypatch.setattr(settings, "FAILURE_MODE", "error")
    statuses = []
    for _ in range(10):
        resp = client.get("/api/orders")
        statuses.append(resp.status_code)
    assert 500 in statuses

def test_failure_mode_slow(client, monkeypatch):
    monkeypatch.setattr(settings, "FAILURE_MODE", "slow")
    start = time.time()
    response = client.get("/api/orders")
    duration = time.time() - start
    assert duration >= 2
    assert response.status_code == 200
