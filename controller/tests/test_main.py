def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_webhook(client):
    payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "KubePodCrashLooping",
                    "namespace": "default"
                }
            }
        ]
    }
    response = client.post("/webhooks/alertmanager", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_rules(client):
    response = client.get("/api/rules")
    assert response.status_code == 200
    assert "rules" in response.json()
