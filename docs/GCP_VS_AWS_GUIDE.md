# 🌩️ AWS vs. GCP: The DevOps & Cloud Security Engineer's Rosetta Stone

As someone who already knows **AWS**, transitioning to **Google Cloud Platform (GCP)** is surprisingly smooth once you map the mental models. GCP is known for cleaner networking, best-in-class managed Kubernetes (GKE), and native integration with AI models like Gemini.

Here is your comprehensive cheat-sheet and architectural translation guide:

---

## 🧭 1. Architectural & Resource Hierarchy

| AWS Mental Model | GCP Mental Model | Key Differences & Enterprise Nuance |
| :--- | :--- | :--- |
| **AWS Account** | **GCP Project** | In AWS, an Account is the root boundary. In GCP, resources live inside **Projects** (`project-id`). Projects are grouped under **Folders** and an **Organization**. |
| **AWS Organizations** | **GCP Organization** | GCP has a unified hierarchical resource tree: `Org -> Folders -> Projects -> Resources`. Policies (Organization Policies) flow downward via inheritance. |
| **AWS Management Account** | **GCP Organization Admin** | Central billing and policy governance across all sub-accounts/projects. |
| **AWS Regions & AZs** | **GCP Regions & Zones** | Very similar. E.g., `us-central1` (Region) has `us-central1-a`, `us-central1-b`, `us-central1-c` (Zones). |

---

## 🌐 2. Networking & Traffic Routing

| AWS Service | GCP Equivalent | The Big Enterprise Difference |
| :--- | :--- | :--- |
| **AWS VPC (Regional)** | **GCP VPC (Global)** | **Huge Difference!** An AWS VPC is tied to a single region. A GCP VPC is **Global** by default—you can have subnets in `us-central1`, `europe-west1`, and `asia-south1` inside the *same* VPC without needing VPC peering or Transit Gateways! |
| **Subnets (AZ-scoped)** | **Subnets (Region-scoped)** | In AWS, a subnet belongs to one AZ. In GCP, a subnet spans an entire **Region** (all zones in that region automatically share the subnet IP CIDR). |
| **Internet Gateway (IGW)** | **Default Internet Route** | GCP has built-in internet routing; you don't attach an IGW resource. |
| **NAT Gateway** | **Cloud NAT** | Cloud NAT is software-defined and distributed—no need to deploy separate NAT instances or manage NAT Gateways per AZ! |
| **Security Groups (Stateful)** | **VPC Firewall Rules** | GCP Firewall rules are applied per network using **Network Tags** or **Service Accounts** instead of ENIs. |
| **Network ACLs (Stateless)** | **Hierarchical Firewall Policies** | GCP provides Organization and Folder level firewalls enforced before project firewalls. |
| **Route 53** | **Cloud DNS** | Managed authoritative and private DNS service. |
| **ALB / NLB** | **Cloud Load Balancing** | GCP Load Balancers use single Anycast global IP addresses. Traffic enters Google's private fiber network at the edge closest to the client. |

---

## 🔐 3. Identity, Access & Cloud Security (IAM & Secrets)

| AWS Feature | GCP Feature | Security Best Practice & Difference |
| :--- | :--- | :--- |
| **IAM Users / Groups** | **Google Cloud IAM (Google Workspace / Cloud Identity)** | GCP doesn't create IAM users inside the cloud console; users are identities (e.g. `user@company.com`) managed via Google Identity or SSO/SAML. |
| **IAM Roles & Instance Profiles** | **Service Accounts (SA)** | In GCP, a Service Account has an email (`app@project-id.iam.gserviceaccount.com`). Compute resources (GKE, VMs, Cloud Run) attach to this Service Account. |
| **IAM Policies (JSON)** | **IAM Roles & Bindings** | Roles contain permissions (`storage.objects.get`). You create **IAM Policy Bindings** linking `Identity + Role + Resource`. |
| **IRSA (IAM Roles for Service Accounts)** | **Workload Identity Federation** | **Crucial for GKE!** Binds a Kubernetes Service Account (KSA) directly to a Google Cloud Service Account (GSA). No stored keys or JSON credential files needed in pods! |
| **AWS Secrets Manager / SSM Parameter Store** | **Secret Manager** | Highly encrypted, versioned key-value and secret storage with automatic rotation and IAM access control. |
| **AWS KMS** | **Cloud KMS (Key Management Service)** | Customer-managed encryption keys (CMEK) for encrypting disks, databases, and GCS buckets. |
| **AWS GuardDuty / Security Hub** | **Security Command Center (SCC)** | Centralized vulnerability management, threat detection, and CIS compliance scoring. |

---

## 💻 4. Compute & Container Orchestration

| AWS Service | GCP Equivalent | Notes for DevOps |
| :--- | :--- | :--- |
| **Amazon EKS** | **Google Kubernetes Engine (GKE)** | Google created Kubernetes. GKE is widely recognized as the most advanced, seamless managed Kubernetes platform (Autopilot or Standard modes). |
| **Amazon ECS / Fargate** | **Cloud Run** | Cloud Run is GCP's fully-managed serverless container platform. It scales down to 0, supports HTTP/WebSockets/gRPC, and is easier to configure than ECS. |
| **Amazon EC2** | **Compute Engine (GCE)** | Virtual machines with custom CPU/RAM configurations and live migration during host updates without VM reboots. |
| **AWS Lambda** | **Cloud Functions / Cloud Run functions** | Event-driven serverless code execution. |

---

## 📦 5. Storage, Artifacts & Databases

| AWS Service | GCP Equivalent | Notes |
| :--- | :--- | :--- |
| **Amazon S3** | **Google Cloud Storage (GCS)** | Object storage with bucket-level or object-level ACLs, uniform bucket-level access (recommended), and lifecycle rules (`gs://bucket-name`). |
| **Amazon ECR** | **Artifact Registry** | Universal package and container repository (`<region>-docker.pkg.dev/<project-id>/<repo>/<image>:<tag>`). Supports Docker, Helm, Maven, npm, Python wheels. |
| **Amazon RDS (PostgreSQL/MySQL)** | **Cloud SQL** | Managed relational database service with automated backups, high availability replicas, and private IP peering. |
| **Amazon DynamoDB** | **Firestore / Bigtable** | NoSQL document (Firestore) or wide-column high-throughput (Bigtable) database. |

---

## 📊 6. Observability, SRE & Operations

| AWS Service | GCP Equivalent | Notes |
| :--- | :--- | :--- |
| **Amazon CloudWatch Logs** | **Cloud Logging** | Powerful query language, log sinks to BigQuery/GCS/PubSub, and real-time streaming. |
| **Amazon CloudWatch Metrics** | **Cloud Monitoring** | Golden signals, metric alerting, and native Prometheus Managed Service support. |
| **AWS CloudTrail** | **Cloud Audit Logs** | Admin Activity and Data Access audit trail for compliance and forensic investigations. |

---

## 🤖 7. AI & DevSecOps Synergy: Why GCP + Gemini?
In our **CloudSentinel AI** project:
- We run microservices on **GKE / Cloud Run**.
- Compute identities authenticate seamlessly to the **Google Gemini API** using Workload Identity (zero hardcoded API keys in production).
- Terraform provisions the Google Cloud infrastructure cleanly using declarative HCL with the `hashicorp/google` provider.
