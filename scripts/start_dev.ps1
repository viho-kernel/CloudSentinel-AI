# ==============================================================
# CloudSentinel AI - Windows 1-Click Local Development Launcher
# ==============================================================

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  🛡️ CLOUDSENTINEL AI: DEV ENVIRONMENT LAUNCHER" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

Set-Location "E:\CloudSentinel-AI"

# 1. Virtual Environment Check
if (-not (Test-Path ".venv")) {
    Write-Host "[1/4] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/4] Virtual environment exists." -ForegroundColor Green
}

# 2. Activate Virtual Environment
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# 3. Install / Verify Dependencies
Write-Host "[3/4] Checking Python dependencies..." -ForegroundColor Yellow
pip install -q -r app\requirements.txt

# 4. Run Automated Unit Tests
Write-Host "[4/4] Running automated test suite (Pytest)..." -ForegroundColor Yellow
pytest tests\unit\ -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ All tests PASSED successfully!" -ForegroundColor Green
} else {
    Write-Host "`n! Warning: Some tests failed. Proceeding with caution." -ForegroundColor DarkYellow
}

Write-Host "`n------------------------------------------------------" -ForegroundColor Cyan
Write-Host "🚀 Starting CloudSentinel AI Server..." -ForegroundColor Green
Write-Host "👉 Web Dashboard:    http://127.0.0.1:8080" -ForegroundColor White
Write-Host "👉 Swagger API Docs: http://127.0.0.1:8080/docs" -ForegroundColor White
Write-Host "👉 Prometheus:       http://127.0.0.1:8080/metrics" -ForegroundColor White
Write-Host "------------------------------------------------------`n" -ForegroundColor Cyan

python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
