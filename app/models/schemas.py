from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class IaCType(str, Enum):
    DOCKERFILE = "dockerfile"
    KUBERNETES = "kubernetes"
    TERRAFORM = "terraform"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class Finding(BaseModel):
    id: str = Field(..., description="Unique UUID for this finding")
    rule_id: str = Field(..., description="Standardized rule identifier (e.g., CS-DOCKER-001)")
    title: str = Field(..., description="Short summary of the vulnerability")
    description: str = Field(..., description="In-depth explanation of the security risk")
    severity: Severity = Field(..., description="Risk severity level")
    iac_type: IaCType = Field(..., description="Type of IaC scanned")
    line_number: Optional[int] = Field(None, description="Line number where issue was detected")
    snippet: str = Field(..., description="Problematic line or block of code")
    recommendation: str = Field(..., description="How to remediate according to best practices")
    compliance_framework: str = Field(..., description="CIS Benchmark, NIST, or OWASP identifier")

class ScanRequest(BaseModel):
    iac_type: IaCType = Field(..., description="Format of infrastructure file")
    content: str = Field(..., description="Raw text of the Dockerfile, K8s YAML, or Terraform .tf")
    file_name: Optional[str] = Field("unknown", description="Filename or resource identifier")

class ScanResponse(BaseModel):
    scan_id: str
    timestamp: str
    environment: str
    file_name: str
    iac_type: IaCType
    risk_score: int = Field(..., description="Calculated security risk score (0-100, lower is safer)")
    status: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: List[Finding]

class RemediateRequest(BaseModel):
    finding_id: str
    rule_id: str
    iac_type: IaCType
    original_code: str
    snippet: str
    title: str
    description: str

class RemediateResponse(BaseModel):
    finding_id: str
    rule_id: str
    explanation: str
    attack_scenario: str
    patched_code: str
    code_diff: str
    cve_or_cwe_reference: str
    confidence_score: float

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    ai_status: str
    gcp_project: str
