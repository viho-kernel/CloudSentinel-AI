// CloudSentinel AI - Client Dashboard Logic

let currentIaCType = "dockerfile";
let currentFindings = [];
let currentRawCode = "";

document.addEventListener("DOMContentLoaded", () => {
  initHealthCheck();
  initEventListeners();
  loadSample("dockerfile");
});

async function initHealthCheck() {
  try {
    const res = await fetch("/healthz");
    if (res.ok) {
      const data = await res.json();
      document.getElementById("env-badge").textContent = `ENV: ${data.environment.toUpperCase()}`;
      const aiTag = document.getElementById("ai-status-badge");
      if (data.ai_status === "live_gemini") {
        aiTag.textContent = "AI: GEMINI 2.5 (LIVE)";
        aiTag.style.color = "#34d399";
        aiTag.style.borderColor = "rgba(16, 185, 129, 0.4)";
      } else {
        aiTag.textContent = "AI: SIMULATED (STANDBY)";
      }
    }
  } catch (e) {
    console.warn("Health probe check deferred:", e);
  }
}

function initEventListeners() {
  // Tab switching
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentIaCType = tab.dataset.type;
      
      const fileLabels = {
        dockerfile: "Dockerfile",
        kubernetes: "deployment.yaml",
        terraform: "main.tf"
      };
      document.getElementById("editor-filename").textContent = fileLabels[currentIaCType] || "Manifest";
      loadSample(currentIaCType);
    });
  });

  // Action buttons
  document.getElementById("load-sample-btn").addEventListener("click", () => {
    loadSample(currentIaCType);
  });

  document.getElementById("run-scan-btn").addEventListener("click", runScan);

  // Modal close buttons
  document.getElementById("close-modal-btn").addEventListener("click", closeModal);
  document.getElementById("close-modal-bottom-btn").addEventListener("click", closeModal);

  // Copy code
  document.getElementById("copy-code-btn").addEventListener("click", () => {
    const code = document.getElementById("ai-patched").textContent;
    navigator.clipboard.writeText(code);
    const btn = document.getElementById("copy-code-btn");
    btn.textContent = "✓ Copied!";
    setTimeout(() => { btn.textContent = "📋 Copy Code"; }, 2000);
  });
}

async function loadSample(iacType) {
  try {
    const res = await fetch(`/api/v1/samples/${iacType}`);
    if (res.ok) {
      const data = await res.json();
      document.getElementById("iac-editor").value = data.content;
    }
  } catch (err) {
    console.error("Failed to load sample:", err);
  }
}

async function runScan() {
  const content = document.getElementById("iac-editor").value;
  if (!content.trim()) {
    alert("Please provide or load IaC code to scan!");
    return;
  }

  currentRawCode = content;
  const scanBtn = document.getElementById("run-scan-btn");
  scanBtn.disabled = true;
  scanBtn.textContent = "Scanning...";

  try {
    const res = await fetch("/api/v1/scan/iac", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        iac_type: currentIaCType,
        content: content,
        file_name: document.getElementById("editor-filename").textContent
      })
    });

    if (!res.ok) throw new Error("Scan request failed");

    const data = await res.json();
    currentFindings = data.findings;
    renderScanResults(data);
  } catch (err) {
    alert("Error executing DevSecOps scan: " + err.message);
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = "🔍 Run DevSecOps Scan";
  }
}

function renderScanResults(data) {
  // Update stats
  document.getElementById("posture-score").textContent = `${100 - data.risk_score} / 100`;
  document.getElementById("stat-critical").textContent = data.critical_count;
  document.getElementById("stat-high").textContent = data.high_count;
  document.getElementById("stat-med").textContent = data.medium_count + data.low_count;

  const statusPill = document.getElementById("gate-status-pill");
  const postureStatus = document.getElementById("posture-status");

  if (data.status === "FAILED_SECURITY_GATE") {
    statusPill.textContent = "CI/CD GATE: BLOCKED";
    statusPill.className = "gate-status failed";
    postureStatus.textContent = "High Risk - Action Required";
    postureStatus.style.color = "#f87171";
  } else {
    statusPill.textContent = "CI/CD GATE: PASSED";
    statusPill.className = "gate-status passed";
    postureStatus.textContent = "Compliant Posture";
    postureStatus.style.color = "#34d399";
  }

  // Render cards
  const container = document.getElementById("findings-container");
  if (data.findings.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon" style="color: #34d399;">🛡️</div>
        <h3>Zero Vulnerabilities Detected</h3>
        <p>This configuration complies with all CIS Benchmarks and enterprise cloud security policies!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = data.findings.map(f => `
    <div class="finding-card">
      <div class="finding-top">
        <div class="finding-title-group">
          <span class="severity-pill pill-${f.severity.toLowerCase()}">${f.severity}</span>
          <span class="finding-title">${f.title}</span>
        </div>
        <span class="finding-rule">${f.rule_id}</span>
      </div>
      <p class="finding-desc">${f.description}</p>
      <div class="finding-snippet">Line ${f.line_number || 'N/A'}: ${escapeHtml(f.snippet)}</div>
      <div class="finding-footer">
        <span class="compliance-tag">📌 ${f.compliance_framework}</span>
        <button class="remediate-btn" onclick="openRemediation('${f.id}')">
          ✨ Fix with Gemini AI
        </button>
      </div>
    </div>
  `).join("");
}

async function openRemediation(findingId) {
  const finding = currentFindings.find(f => f.id === findingId);
  if (!finding) return;

  const modal = document.getElementById("ai-modal");
  modal.classList.remove("hidden");

  document.getElementById("modal-title").textContent = `Remediating: ${finding.rule_id} - ${finding.title}`;
  document.getElementById("ai-explanation").textContent = "Gemini AI is analyzing security risk and generating patch...";
  document.getElementById("ai-attack").textContent = "Mapping threat actor attack vector...";
  document.getElementById("ai-diff").textContent = "Computing unified diff...";
  document.getElementById("ai-patched").textContent = "Synthesizing hardened code...";
  document.getElementById("ai-cve-badge").textContent = finding.compliance_framework;

  try {
    const res = await fetch("/api/v1/remediate/ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        finding_id: finding.id,
        rule_id: finding.rule_id,
        iac_type: currentIaCType,
        original_code: currentRawCode,
        snippet: finding.snippet,
        title: finding.title,
        description: finding.description
      })
    });

    if (!res.ok) throw new Error("Remediation request failed");
    const data = await res.json();

    document.getElementById("ai-explanation").textContent = data.explanation;
    document.getElementById("ai-attack").textContent = data.attack_scenario;
    document.getElementById("ai-diff").textContent = data.code_diff;
    document.getElementById("ai-patched").textContent = data.patched_code;
    document.getElementById("ai-confidence").textContent = `Model Confidence: ${Math.round(data.confidence_score * 100)}%`;
  } catch (err) {
    document.getElementById("ai-explanation").textContent = "Error: " + err.message;
  }
}

function closeModal() {
  document.getElementById("ai-modal").classList.add("hidden");
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
