import time
from app.config import settings

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "product-api", "version": "0.1.0"}

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

def test_list_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.json()) == 5

def test_get_product(client):
    response = client.get("/api/products/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_product_not_found(client):
    response = client.get("/api/products/999")
    assert response.status_code == 404

def test_failure_mode_error(client, monkeypatch):
    monkeypatch.setattr(settings, "FAILURE_MODE", "error")
    # Due to 50% probability, we might need a few tries
    statuses = []
    for _ in range(10):
        resp = client.get("/api/products")
        statuses.append(resp.status_code)
    assert 500 in statuses

def test_failure_mode_slow(client, monkeypatch):
    monkeypatch.setattr(settings, "FAILURE_MODE", "slow")
    start = time.time()
    response = client.get("/api/products")
    duration = time.time() - start
    assert duration >= 2
    assert response.status_code == 200
