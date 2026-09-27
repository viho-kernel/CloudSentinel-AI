# 🛡️ CloudSentinel AI
> **Enterprise-Grade Autonomous Cloud Security & DevSecOps Platform**  
> *A full-lifecycle production project covering Software Development, DevSecOps, Multi-Environment Google Cloud Infrastructure (GCP), Kubernetes (K8s), and AI-Powered Autonomous Remediation.*

---

## 📌 Executive Summary
**CloudSentinel AI** is a complete, production-grade microservice platform engineered to replicate how elite tech companies build, secure, deploy, and operate software.

Instead of a toy demo, this project features:
- A high-performance **FastAPI** backend with Prometheus observability & cyber dashboard.
- A **Static Security Analysis Engine** enforcing CIS Benchmarks across Dockerfiles, Kubernetes manifests, and Google Cloud Terraform scripts.
- An **AI DevSecOps Copilot** powered by **Google Gemini** that explains vulnerabilities, outlines attack scenarios, and synthesizes unified diff patches.
- Production **Multi-Environment Infrastructure as Code (Terraform)** for Google Cloud (Custom Global VPC, Cloud NAT, Private GKE, Workload Identity, KMS/GCS).
- Production **Kubernetes Kustomize Overlays** (`dev`, `staging`, `prod`) with zero-trust network policies and CIS securityContexts.
- An 8-Stage **GitHub Actions CI/CD Pipeline** enforcing SAST (Bandit), Secret Scanning (GitLeaks), IaC policies (Checkov), and Container audits (Trivy).
- An **AIOps SRE Incident Responder** script simulating autonomous on-call triage during production outages.

---

## 🏛️ System Architecture

```text
                               +-------------------------------------+
                               |      Cloud Engineer / Analyst       |
                               +------------------+------------------+
                                                  |
                                                  v
                               +-------------------------------------+
                               |      Web Portal / REST API (8080)   |
                               |  - Fast API Microservice            |
                               |  - Static File Dashboard            |
                               |  - Prometheus /metrics Exporter     |
                               +--------+--------------------+-------+
                                        |                    |
                 +----------------------+                    +----------------------+
                 v                                                                  v
+---------------------------------+                               +---------------------------------+
|   CIS Static Security Engine    |                               |    Google Gemini AI Engine      |
|  - Dockerfile Rules (4.1, 4.6)  |                               |  - Attack Vector Simulation     |
|  - K8s securityContext (5.2)    |                               |  - Automated Unified Diff Patch |
|  - GCP Terraform Rules (3.6)    |                               |  - SRE Post-Mortem Generation   |
+---------------------------------+                               +---------------------------------+
```

---

## 👥 Enterprise Roles & Operating Model

```text
 💻 Software Engineers (Dev)   --> Feature branches (feature/*), Unit tests (>80%), OpenAPI specs
 🧪 QA / SDET Engineers        --> Integration & E2E smoke testing against Staging
 🛡️ DevSecOps Engineers        --> CI/CD security gating (SAST, Secrets, Container CVEs, SBOM)
 ⚡ SRE / Platform Engineers   --> Terraform IaC, GKE Kustomize overlays, Prometheus Golden Signals
```

---

## 🌐 Multi-Environment Topology

| Environment | Purpose | Kubernetes Overlay | Infrastructure Scale |
| :--- | :--- | :--- | :--- |
| **Local** | Developer workstation iteration | Docker Compose | 1 local container, local Prometheus |
| **Dev** | Rapid integration testing | `k8s/overlays/dev` | 1 pod, burstable compute, debug logs |
| **Staging** | Production mirror & security soak test | `k8s/overlays/staging` | 2 pods, staging database & secrets |
| **Production** | Live zero-downtime customer traffic | `k8s/overlays/prod` | 3+ pods, HPA autoscaling, multi-zone, TLS Ingress |

---

## 🚀 Quickstart: Running Locally

### Option 1: 1-Click PowerShell Dev Launcher (Recommended)
Open PowerShell in this directory:
```powershell
.\scripts\start_dev.ps1
```
This script will:
1. Create and activate a `.venv` virtual environment.
2. Install all required dependencies.
3. Run the automated Pytest suite.
4. Launch the application on `http://127.0.0.1:8080` with hot reloading!

### Option 2: Docker Compose Multi-Container Stack
```bash
cd docker
docker compose up --build
```
- **Web Dashboard**: [http://localhost:8080](http://localhost:8080)
- **Interactive Swagger API**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Prometheus Metrics**: [http://localhost:8080/metrics](http://localhost:8080/metrics)
- **Prometheus Dashboard**: [http://localhost:9090](http://localhost:9090)

---

## 🤖 Testing the AI DevSecOps Engine
1. Navigate to `http://127.0.0.1:8080`.
2. Click **Load Vulnerable Sample** on any tab (**Dockerfile**, **Kubernetes**, or **Terraform**).
3. Click **Run DevSecOps Scan**.
4. Observe the calculated **Security Posture Score** and rule violations.
5. Click **✨ Fix with Gemini AI** on any finding to inspect:
   - Technical Risk Explanation
   - Threat Actor Attack Vector
   - Unified Code Patch Diff
   - Production-hardened Code Output

---

## 🚨 Running the SRE AIOps Incident Responder
To simulate an on-call SRE incident triage:
```powershell
python .\scripts\ai_incident_responder.py crashloop
```
Or for an out-of-memory container termination:
```powershell
python .\scripts\ai_incident_responder.py oom
```

---

## 🌩️ Google Cloud Platform (GCP) vs. AWS Reference
For a complete translation of AWS concepts (VPC, IAM, EKS, ECR) to GCP (Global VPC, Workload Identity, GKE, Artifact Registry), see:
👉 [docs/GCP_VS_AWS_GUIDE.md](docs/GCP_VS_AWS_GUIDE.md)
