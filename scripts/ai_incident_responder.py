#!/usr/bin/env python3
"""
==============================================================
CloudSentinel AI - SRE Incident Responder & Log Analyzer
Simulates autonomous AIOps triage during production incidents.
==============================================================
"""

import sys
import os
import json
import datetime

# Ensure cross-platform UTF-8 console output for emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Mock realistic incident payloads
SAMPLE_INCIDENTS = {
    "oom": {
        "title": "Pod OOMKilled - Payment Microservice",
        "service": "payment-api",
        "environment": "production",
        "log_excerpt": """
[2026-09-27T03:15:02Z] WARN: Memory allocation spike detected: 510MiB / 512MiB limit.
[2026-09-27T03:15:04Z] FATAL: runtime: out of memory: cannot allocate 8388608-byte block
[2026-09-27T03:15:05Z] Kubelet: Pod 'payment-microservice-7bf8696-9xk2p' terminated (OOMKilled, exit code 137)
"""
    },
    "crashloop": {
        "title": "CrashLoopBackOff - Missing Vault Secret",
        "service": "auth-service",
        "environment": "staging",
        "log_excerpt": """
[2026-09-27T03:18:10Z] INFO: Initializing CloudSentinel Auth Service...
[2026-09-27T03:18:11Z] ERROR: Failed to retrieve secret 'jwt-private-key' from SecretManager: 403 PermissionDenied
[2026-09-27T03:18:12Z] CRITICAL: Service account 'cloudsentinel-staging-app-sa' lacks 'roles/secretmanager.secretAccessor' on project 'cloudsentinel-staging'.
[2026-09-27T03:18:12Z] Process exiting with status 1
"""
    }
}

def analyze_incident(incident_key="crashloop"):
    incident = SAMPLE_INCIDENTS.get(incident_key, SAMPLE_INCIDENTS["crashloop"])
    print("=" * 70)
    print(f"🚨 CLOUDSENTINEL AI: SRE AUTONOMOUS INCIDENT TRIAGE")
    print(f"Incident:    {incident['title']}")
    print(f"Environment: {incident['environment'].upper()}")
    print(f"Service:     {incident['service']}")
    print(f"Timestamp:   {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("=" * 70)
    print("\n[1] RAW INGESTED LOGS:")
    print(incident["log_excerpt"].strip())
    
    print("\n[2] RUNNING AI ROOT CAUSE ANALYSIS (RCA)...")
    
    # Check for live Gemini key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are an SRE on-call lead.
Perform a Root Cause Analysis (RCA) and generate a Runbook Remediation for this incident:
Incident: {incident['title']}
Environment: {incident['environment']}
Logs:
{incident['log_excerpt']}

Provide:
1. Executive Summary
2. Root Cause
3. Immediate Fix (Kubernetes or IAM command)
4. Long-term Prevention
"""
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            print("\n[3] AI INCIDENT POST-MORTEM & REMEDIATION PLAN:")
            print(res.text)
            return
        except Exception as e:
            print(f"(Live Gemini API call failed: {e}. Switching to heuristic RCA engine.)")

    # Heuristic SRE analysis
    if incident_key == "crashloop":
        print("""
[3] AI INCIDENT POST-MORTEM & REMEDIATION PLAN:

📌 EXECUTIVE SUMMARY:
The service is stuck in CrashLoopBackOff because it failed to fetch 'jwt-private-key' from Google Cloud Secret Manager due to an IAM authorization failure (HTTP 403).

🔍 ROOT CAUSE:
The Workload Identity Service Account 'cloudsentinel-staging-app-sa' was not granted the 'roles/secretmanager.secretAccessor' IAM role on the target secret or project.

⚡ IMMEDIATE RUNBOOK REMEDIATION:
Run the following gcloud command to grant least-privilege secret accessor permissions immediately:

$ gcloud projects add-iam-policy-binding cloudsentinel-staging \\
    --member="serviceAccount:cloudsentinel-staging-app-sa@cloudsentinel-staging.iam.gserviceaccount.com" \\
    --role="roles/secretmanager.secretAccessor"

Then restart the stuck deployment:
$ kubectl rollout restart deployment/cloudsentinel-core-staging -n cloudsentinel-staging

🛡️ LONG-TERM PREVENTION:
Update 'terraform/modules/iam/main.tf' to ensure Secret Manager permissions are declared in code, preventing drift between environments.
""")
    else:
        print("""
[3] AI INCIDENT POST-MORTEM & REMEDIATION PLAN:

📌 EXECUTIVE SUMMARY:
Pod terminated with exit code 137 (OOMKilled) after exceeding its 512Mi memory limit.

🔍 ROOT CAUSE:
Memory leak or sudden high request traffic spike overwhelmed the existing memory limit before the Horizontal Pod Autoscaler could trigger a replica scale-out.

⚡ IMMEDIATE RUNBOOK REMEDIATION:
Patch Kubernetes deployment to temporarily increase memory limits:

$ kubectl set resources deployment payment-microservice \\
    --limits=memory=1Gi,cpu=1000m \\
    --requests=memory=512Mi,cpu=250m

🛡️ LONG-TERM PREVENTION:
Tune Horizontal Pod Autoscaler (HPA) to scale on 60% memory utilization threshold rather than 80%.
""")

if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "crashloop"
    analyze_incident(choice)
