import datetime
import uuid
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.models.schemas import (
    ScanRequest, ScanResponse, RemediateRequest, RemediateResponse,
    HealthResponse, IaCType
)
from app.services.scanner_engine import scanner_engine
from app.services.gemini_service import gemini_service

router = APIRouter()

# Preloaded sample files with realistic real-world vulnerabilities for instant testing
SAMPLE_FILES = {
    "dockerfile": """# Insecure Legacy Dockerfile
FROM python:latest

# Exposes sensitive credentials in metadata
ENV API_KEY="sk_live_938172948172941"
ENV DB_PASSWORD="SuperSecretPassword123!"

WORKDIR /app
ADD app.tar.gz /app/
RUN apt-get update && apt-get install -y sudo curl

# Missing USER directive -> Runs as root!
CMD ["python", "main.py"]
""",
    "kubernetes": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-microservice
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: payment
  template:
    metadata:
      labels:
        app: payment
    spec:
      containers:
      - name: payment
        image: payment-api:latest
        securityContext:
          privileged: true
          allowPrivilegeEscalation: true
          readOnlyRootFilesystem: false
          runAsNonRoot: false
        volumeMounts:
        - mountPath: /var/run/docker.sock
          name: docker-sock
      volumes:
      - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
""",
    "terraform": """# Insecure GCP Infrastructure
resource "google_compute_firewall" "allow_all" {
  name    = "allow-public-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "3389", "5432"]
  }

  # Vulnerability: Open to the whole world!
  source_ranges = ["0.0.0.0/0"]
}

resource "google_storage_bucket" "data_lake" {
  name          = "enterprise-data-lake-raw"
  location      = "US"
  force_destroy = true

  # Vulnerability: Legacy ACLs enabled
  uniform_bucket_level_access = false
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.data_lake.name
  role   = "roles/storage.objectViewer"
  # Vulnerability: Public anonymous data exposure!
  member = "allUsers"
}
"""
}

@router.get("/healthz", response_model=HealthResponse, tags=["SRE & Probes"])
async def liveness_probe():
    """Kubernetes liveness probe: verifies the process is running and responding."""
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        ai_status="live_gemini" if gemini_service.is_live() else "heuristic_fallback",
        gcp_project=settings.GCP_PROJECT_ID
    )

@router.get("/ready", response_model=HealthResponse, tags=["SRE & Probes"])
async def readiness_probe():
    """Kubernetes readiness probe: verifies the service is ready to accept production traffic."""
    return HealthResponse(
        status="ready",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        ai_status="live_gemini" if gemini_service.is_live() else "heuristic_fallback",
        gcp_project=settings.GCP_PROJECT_ID
    )

@router.post("/api/v1/scan/iac", response_model=ScanResponse, tags=["DevSecOps Scanner"])
async def scan_infrastructure_code(request: ScanRequest):
    """Scans Dockerfile, Kubernetes, or Terraform configurations against CIS benchmarks."""
    findings, risk_score = scanner_engine.scan(
        iac_type=request.iac_type,
        content=request.content,
        file_name=request.file_name or "uploaded_iac"
    )

    crit = sum(1 for f in findings if f.severity.value == "CRITICAL")
    high = sum(1 for f in findings if f.severity.value == "HIGH")
    med = sum(1 for f in findings if f.severity.value == "MEDIUM")
    low = sum(1 for f in findings if f.severity.value == "LOW")

    return ScanResponse(
        scan_id=str(uuid.uuid4()),
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        file_name=request.file_name or "sample",
        iac_type=request.iac_type,
        risk_score=risk_score,
        status="FAILED_SECURITY_GATE" if (crit > 0 or high > 0) else "PASSED",
        total_findings=len(findings),
        critical_count=crit,
        high_count=high,
        medium_count=med,
        low_count=low,
        findings=findings
    )

@router.post("/api/v1/remediate/ai", response_model=RemediateResponse, tags=["AI Copilot"])
async def remediate_with_ai(request: RemediateRequest):
    """Invokes Google Gemini to explain the vulnerability and produce an automated patch diff."""
    try:
        response = await gemini_service.remediate_vulnerability(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Remediation failed: {str(e)}"
        )

@router.get("/api/v1/samples/{iac_type}", tags=["DevSecOps Scanner"])
async def get_sample_code(iac_type: IaCType):
    """Provides pre-configured vulnerable IaC templates for hands-on learning and testing."""
    sample = SAMPLE_FILES.get(iac_type.value)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"iac_type": iac_type.value, "content": sample}
