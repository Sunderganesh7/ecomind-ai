import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_security_headers():
    response = client.get("/api/v1/health")
    # Health endpoint may not trigger middleware in test unless correctly chained, let's check
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY"
    assert "referrer-policy" in response.headers
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

def test_request_size_limit_allowed():
    # Sending a small payload
    payload = "a" * 1024 # 1KB
    # Health endpoint doesn't accept POST usually, let's just send to a non-existent or existing endpoint
    # Actually, any POST will go through middleware
    response = client.post("/api/v1/health", content=payload, headers={"Content-Length": str(len(payload))})
    assert response.status_code != 413 # May be 405 Method Not Allowed, but not 413

def test_request_size_limit_exceeded():
    payload = "a" * (settings.MAX_REQUEST_SIZE + 1)
    response = client.post("/api/v1/health", content=payload, headers={"Content-Length": str(len(payload))})
    assert response.status_code == 413
    assert response.json()["error"]["message"] == "Request entity too large"

def test_cors_headers():
    # Test preflight
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Requested-With",
    }
    response = client.options("/api/v1/health", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_error_sanitization():
    # Force an unhandled exception or test validation error
    response = client.get("/api/v1/profiles/not_an_int")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == 422
    assert "message" in data["error"]
    assert "details" in data["error"]

    # We cannot easily trigger a 500 error without modifying code, but we can verify
    # the exception handler is registered in the app.
    # A generic test could be checking that standard exceptions don't expose stack traces.
