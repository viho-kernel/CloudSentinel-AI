import re
import uuid
from typing import List, Tuple
from app.models.schemas import Finding, IaCType, Severity, ScanResponse
from app.core.security import VULNERABILITIES_DETECTED_TOTAL

class ScannerEngine:
    """Enterprise Static Security Analysis Engine for Infrastructure-as-Code."""

    @staticmethod
    def calculate_risk_score(findings: List[Finding]) -> int:
        """Calculates a normalized 0-100 risk score based on finding severities."""
        if not findings:
            return 0
        weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 1,
        }
        raw_score = sum(weights.get(f.severity, 0) for f in findings)
        return min(100, raw_score)

    def scan_dockerfile(self, content: str) -> List[Finding]:
        findings = []
        lines = content.splitlines()

        has_user = False
        has_healthcheck = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Rule: USER check
            if stripped.upper().startswith("USER "):
                user_val = stripped.split(None, 1)[1].strip()
                if user_val in ["0", "root"]:
                    findings.append(Finding(
                        id=str(uuid.uuid4()),
                        rule_id="CS-DOCKER-001",
                        title="Explicit Root User Execution",
                        description="Container is explicitly configured to execute as root user, presenting privilege escalation vectors.",
                        severity=Severity.CRITICAL,
                        iac_type=IaCType.DOCKERFILE,
                        line_number=idx,
                        snippet=stripped,
                        recommendation="Define an unprivileged user (e.g., 'USER appuser' or UID 10001).",
                        compliance_framework="CIS Docker Benchmark 4.1"
                    ))
                else:
                    has_user = True

            # Rule: HEALTHCHECK check
            if stripped.upper().startswith("HEALTHCHECK "):
                has_healthcheck = True

            # Rule: Mutable :latest tag
            if stripped.upper().startswith("FROM "):
                if ":latest" in stripped or (":" not in stripped.split()[1] and "@" not in stripped.split()[1]):
                    findings.append(Finding(
                        id=str(uuid.uuid4()),
                        rule_id="CS-DOCKER-003",
                        title="Base Image Uses Mutable 'latest' Tag",
                        description="Using unpinned or 'latest' tags causes non-deterministic builds and unintended breaking or vulnerable dependency ingestion.",
                        severity=Severity.MEDIUM,
                        iac_type=IaCType.DOCKERFILE,
                        line_number=idx,
                        snippet=stripped,
                        recommendation="Pin the image version to a specific semantic version or SHA256 digest (e.g., python:3.12-slim@sha256:...).",
                        compliance_framework="CIS Docker Benchmark 4.2"
                    ))

            # Rule: ADD instead of COPY
            if stripped.upper().startswith("ADD "):
                # Allow if downloading tarball or remote url, otherwise warn
                if not re.search(r'\.(tar|gz|bz2|xz)', stripped, re.IGNORECASE):
                    findings.append(Finding(
                        id=str(uuid.uuid4()),
                        rule_id="CS-DOCKER-004",
                        title="Insecure Use of ADD Instead of COPY",
                        description="ADD has implicit tar extraction and remote URL fetching behaviors that can trigger Tar-bomb attacks or unexpected behavior.",
                        severity=Severity.MEDIUM,
                        iac_type=IaCType.DOCKERFILE,
                        line_number=idx,
                        snippet=stripped,
                        recommendation="Use COPY for local filesystem transfer unless archive auto-extraction is explicitly required.",
                        compliance_framework="CIS Docker Benchmark 4.9"
                    ))

            # Rule: Leaked secrets in ENV or ARG
            secret_pattern = re.compile(r'(PASSWORD|SECRET|API_KEY|TOKEN|PRIVATE_KEY)\s*[:=]', re.IGNORECASE)
            if (stripped.upper().startswith("ENV ") or stripped.upper().startswith("ARG ")) and secret_pattern.search(stripped):
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-DOCKER-002",
                    title="Hardcoded Credential or Secret in Container Image",
                    description="Embedding secrets in ENV or ARG variables permanently leaks them inside image layers visible to anyone who pulls the image.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.DOCKERFILE,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Never store secrets in image metadata. Inject via Secret Manager, environment variables at runtime, or BuildKit secret mounts.",
                    compliance_framework="OWASP A07:2021-Identification and Authentication Failures"
                ))

            # Rule: Sudo usage in RUN
            if stripped.upper().startswith("RUN ") and "sudo " in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-DOCKER-007",
                    title="Sudo Executed Inside Container Build",
                    description="Installing or running sudo introduces unnecessary setuid binaries that escalate attack surfaces.",
                    severity=Severity.HIGH,
                    iac_type=IaCType.DOCKERFILE,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Remove sudo; run setup steps as root during early build stages and switch to non-root USER before CMD.",
                    compliance_framework="CIS Docker Benchmark 4.5"
                ))

        # Check for missing non-root USER
        if not has_user:
            findings.append(Finding(
                id=str(uuid.uuid4()),
                rule_id="CS-DOCKER-001",
                title="Missing Non-Root User Specification",
                description="Dockerfile does not specify a non-root USER directive. By default, the container will execute as root.",
                severity=Severity.HIGH,
                iac_type=IaCType.DOCKERFILE,
                line_number=len(lines),
                snippet="[EndOfFile] No USER directive found",
                recommendation="Add 'USER 10001' or create and specify an unprivileged application user before ENTRYPOINT.",
                compliance_framework="CIS Docker Benchmark 4.1"
            ))

        # Check for missing HEALTHCHECK
        if not has_healthcheck:
            findings.append(Finding(
                id=str(uuid.uuid4()),
                rule_id="CS-DOCKER-005",
                title="Missing Container HEALTHCHECK Instruction",
                description="Without a HEALTHCHECK, orchestrators like Docker or Kubernetes cannot reliably determine internal service health.",
                severity=Severity.LOW,
                iac_type=IaCType.DOCKERFILE,
                line_number=len(lines),
                snippet="[EndOfFile] No HEALTHCHECK directive found",
                recommendation="Add 'HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/healthz || exit 1'.",
                compliance_framework="CIS Docker Benchmark 4.6"
            ))

        return findings

    def scan_kubernetes(self, content: str) -> List[Finding]:
        findings = []
        lines = content.splitlines()

        has_limits = False
        has_probes = False
        has_security_context = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            if "privileged: true" in stripped.lower():
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-K8S-001",
                    title="Privileged Container Execution Enabled",
                    description="Privileged containers inherit all Linux kernel capabilities of the host, granting full root access to the node.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.KUBERNETES,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'securityContext.privileged: false'.",
                    compliance_framework="CIS Kubernetes Benchmark 5.2.1"
                ))

            if "allowprivilegeescalation: true" in stripped.lower():
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-K8S-002",
                    title="Privilege Escalation Allowed",
                    description="Processes inside the container can gain more privileges than their parent process (e.g. via setuid binaries).",
                    severity=Severity.HIGH,
                    iac_type=IaCType.KUBERNETES,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'securityContext.allowPrivilegeEscalation: false'.",
                    compliance_framework="CIS Kubernetes Benchmark 5.2.5"
                ))

            if "runasnonroot: false" in stripped.lower() or "runasuser: 0" in stripped.lower():
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-K8S-003",
                    title="Container Configured to Run As Root (UID 0)",
                    description="Running pods as root compromises the node boundary in case of container escape vulnerabilities.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.KUBERNETES,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'securityContext.runAsNonRoot: true' and 'runAsUser: 10001'.",
                    compliance_framework="CIS Kubernetes Benchmark 5.2.6"
                ))

            if "hostpath:" in stripped.lower():
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-K8S-004",
                    title="HostPath Volume Mount Detected",
                    description="Mounting the host filesystem allows containers to read or tamper with host secrets, docker sockets, or other pod data.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.KUBERNETES,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Use PersistentVolumeClaims (PVCs) or ConfigMaps instead of direct hostPath mounts.",
                    compliance_framework="CIS Kubernetes Benchmark 5.2.4"
                ))

            if "readonlyrootfilesystem: false" in stripped.lower():
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-K8S-005",
                    title="Writable Root Filesystem",
                    description="A writable root filesystem enables attackers to install malware or download exploit binaries.",
                    severity=Severity.HIGH,
                    iac_type=IaCType.KUBERNETES,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'securityContext.readOnlyRootFilesystem: true' and mount emptyDir volumes for temp storage.",
                    compliance_framework="CIS Kubernetes Benchmark 5.2.7"
                ))

            if "limits:" in stripped.lower():
                has_limits = True
            if "livenessprobe:" in stripped.lower() or "readinessprobe:" in stripped.lower():
                has_probes = True
            if "securitycontext:" in stripped.lower():
                has_security_context = True

        if not has_limits and ("kind: deployment" in content.lower() or "kind: pod" in content.lower()):
            findings.append(Finding(
                id=str(uuid.uuid4()),
                rule_id="CS-K8S-006",
                title="Missing Resource Limits (CPU/Memory)",
                description="Without resource limits, rogue or compromised pods can cause Denial of Service (DoS) by starving neighbors of RAM and CPU.",
                severity=Severity.HIGH,
                iac_type=IaCType.KUBERNETES,
                line_number=None,
                snippet="resources: missing limits",
                recommendation="Define 'resources.limits.cpu' and 'resources.limits.memory' alongside 'requests'.",
                compliance_framework="CIS Kubernetes Benchmark 5.2.8"
            ))

        if not has_probes and ("kind: deployment" in content.lower()):
            findings.append(Finding(
                id=str(uuid.uuid4()),
                rule_id="CS-K8S-007",
                title="Missing Liveness & Readiness Probes",
                description="Orchestrator cannot verify if application is live or ready to accept traffic, leading to dropped requests during deploys.",
                severity=Severity.MEDIUM,
                iac_type=IaCType.KUBERNETES,
                line_number=None,
                snippet="missing livenessProbe / readinessProbe",
                recommendation="Configure livenessProbe (GET /healthz) and readinessProbe (GET /ready).",
                compliance_framework="Kubernetes Reliability Standards"
            ))

        return findings

    def scan_terraform(self, content: str) -> List[Finding]:
        findings = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Rule: Open CIDR 0.0.0.0/0 on sensitive ports in GCP firewall
            if "0.0.0.0/0" in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-TF-GCP-001",
                    title="VPC Firewall Ingress Open to the Entire Internet (0.0.0.0/0)",
                    description="Allowing inbound traffic from 0.0.0.0/0 exposes cloud resources directly to internet-wide reconnaissance and brute-force attacks.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.TERRAFORM,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Restrict source_ranges to specific trusted enterprise CIDRs or use Cloud IAP (Identity-Aware Proxy).",
                    compliance_framework="CIS Google Cloud Computing Platform Benchmark 3.6"
                ))

            # Rule: GCS Bucket with Uniform Bucket Level Access disabled
            if "uniform_bucket_level_access" in stripped and "false" in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-TF-GCP-002",
                    title="GCS Uniform Bucket-Level Access Disabled",
                    description="Disabling uniform bucket-level access permits legacy per-object ACLs, drastically increasing risk of accidental public data leakage.",
                    severity=Severity.HIGH,
                    iac_type=IaCType.TERRAFORM,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'uniform_bucket_level_access = true' to enforce unified IAM permissions.",
                    compliance_framework="CIS Google Cloud Computing Platform Benchmark 5.2"
                ))

            # Rule: Public allUsers access
            if "allUsers" in stripped or "allAuthenticatedUsers" in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-TF-GCP-003",
                    title="Public Access Granted (allUsers / allAuthenticatedUsers)",
                    description="Granting IAM access to allUsers makes internal buckets, functions, or services accessible by anyone on the public web.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.TERRAFORM,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Remove public members and restrict access to authenticated Service Accounts or Groups.",
                    compliance_framework="CIS Google Cloud Computing Platform Benchmark 5.1"
                ))

            # Rule: Overly broad IAM roles
            if "roles/owner" in stripped or "roles/editor" in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-TF-GCP-004",
                    title="Primitive IAM Role (Owner / Editor) Assigned",
                    description="Primitive roles violate Least Privilege by granting broad destructive privileges across all GCP services in the project.",
                    severity=Severity.HIGH,
                    iac_type=IaCType.TERRAFORM,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Use granular Predefined Roles (e.g., roles/storage.objectViewer, roles/container.admin) or Custom Roles.",
                    compliance_framework="CIS Google Cloud Computing Platform Benchmark 1.4"
                ))

            # Rule: Legacy ABAC in GKE
            if "enable_legacy_abac" in stripped and "true" in stripped:
                findings.append(Finding(
                    id=str(uuid.uuid4()),
                    rule_id="CS-TF-GCP-005",
                    title="GKE Legacy ABAC Enabled",
                    description="Legacy Attribute-Based Access Control bypasses RBAC, granting all cluster accounts unrestricted API server access.",
                    severity=Severity.CRITICAL,
                    iac_type=IaCType.TERRAFORM,
                    line_number=idx,
                    snippet=stripped,
                    recommendation="Set 'enable_legacy_abac = false' and rely strictly on Kubernetes RBAC.",
                    compliance_framework="CIS Google Cloud Computing Platform Benchmark 4.1"
                ))

        return findings

    def scan(self, iac_type: IaCType, content: str, file_name: str = "unknown") -> Tuple[List[Finding], int]:
        """Runs the rule engine against provided IaC and records Prometheus metrics."""
        if iac_type == IaCType.DOCKERFILE:
            findings = self.scan_dockerfile(content)
        elif iac_type == IaCType.KUBERNETES:
            findings = self.scan_kubernetes(content)
        elif iac_type == IaCType.TERRAFORM:
            findings = self.scan_terraform(content)
        else:
            findings = []

        # Record metric telemetry
        for f in findings:
            VULNERABILITIES_DETECTED_TOTAL.labels(
                severity=f.severity.value,
                iac_type=iac_type.value,
                rule_id=f.rule_id
            ).inc()

        risk_score = self.calculate_risk_score(findings)
        return findings, risk_score

scanner_engine = ScannerEngine()
