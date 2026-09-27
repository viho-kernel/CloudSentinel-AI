import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_scan_and_ai_remediation_lifecycle():
    # 1. Fetch vulnerable sample
    sample_res = client.get("/api/v1/samples/dockerfile")
    assert sample_res.status_code == 200
    dockerfile_content = sample_res.json()["content"]

    # 2. Trigger scan
    scan_res = client.post("/api/v1/scan/iac", json={
        "iac_type": "dockerfile",
        "content": dockerfile_content,
        "file_name": "Dockerfile"
    })
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["total_findings"] >= 1
    target_finding = scan_data["findings"][0]

    # 3. Request AI remediation
    remediate_res = client.post("/api/v1/remediate/ai", json={
        "finding_id": target_finding["id"],
        "rule_id": target_finding["rule_id"],
        "iac_type": "dockerfile",
        "original_code": dockerfile_content,
        "snippet": target_finding["snippet"],
        "title": target_finding["title"],
        "description": target_finding["description"]
    })
    assert remediate_res.status_code == 200
    ai_data = remediate_res.json()
    assert len(ai_data["explanation"]) > 10
    assert len(ai_data["code_diff"]) > 5
    assert ai_data["confidence_score"] > 0.5
