from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EcoMind AI"
    assert data["version"] == "1.0.0"

def test_legacy_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EcoMind AI"
    assert data["version"] == "1.0.0"

def test_validation_error():
    # Attempting to hit an endpoint that does not exist or with bad parameters
    # As we only have health checks, let's test a non-existent route to verify standard 404 response
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    assert "error" in response.json()
