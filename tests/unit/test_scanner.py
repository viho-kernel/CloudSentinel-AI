import pytest
from app.models.schemas import IaCType, Severity
from app.services.scanner_engine import scanner_engine

def test_dockerfile_scan_detects_root_user():
    content = "FROM python:3.12-slim\nRUN apt-get update\nCMD ['python', 'app.py']"
    findings, risk_score = scanner_engine.scan(IaCType.DOCKERFILE, content)
    
    rule_ids = [f.rule_id for f in findings]
    assert "CS-DOCKER-001" in rule_ids
    assert risk_score > 0

def test_dockerfile_scan_detects_secrets():
    content = "FROM alpine:3.19\nENV API_KEY='sk_live_secret123'\nUSER 10001"
    findings, _ = scanner_engine.scan(IaCType.DOCKERFILE, content)
    
    rule_ids = [f.rule_id for f in findings]
    assert "CS-DOCKER-002" in rule_ids

def test_kubernetes_scan_detects_privileged_and_root():
    content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-pod
spec:
  template:
    spec:
      containers:
      - name: test
        image: nginx
        securityContext:
          privileged: true
          runAsNonRoot: false
    """
    findings, risk = scanner_engine.scan(IaCType.KUBERNETES, content)
    rule_ids = [f.rule_id for f in findings]
    assert "CS-K8S-001" in rule_ids
    assert "CS-K8S-003" in rule_ids
    assert risk >= 25

def test_terraform_scan_detects_open_firewall():
    content = """
resource "google_compute_firewall" "allow_all" {
  name    = "allow-ssh"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["0.0.0.0/0"]
}
"""
    findings, risk = scanner_engine.scan(IaCType.TERRAFORM, content)
    rule_ids = [f.rule_id for f in findings]
    assert "CS-TF-GCP-001" in rule_ids
