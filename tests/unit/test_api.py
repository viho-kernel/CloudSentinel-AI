import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data

def test_ready_readiness_probe():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "cloudsentinel_http_requests_total" in response.text

def test_scan_api_endpoint():
    payload = {
        "iac_type": "dockerfile",
        "content": "FROM node:latest\nCMD ['node', 'index.js']",
        "file_name": "Dockerfile"
    }
    response = client.post("/api/v1/scan/iac", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_findings"] > 0
    assert data["status"] in ["FAILED_SECURITY_GATE", "PASSED"]

def test_samples_endpoint():
    response = client.get("/api/v1/samples/dockerfile")
    assert response.status_code == 200
    assert "FROM" in response.json()["content"]
