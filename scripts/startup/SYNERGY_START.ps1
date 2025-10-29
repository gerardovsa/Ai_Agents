# Synergy Dashboard Backend Launcher (PowerShell)
# ================================================
# Quick start script for PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SYNERGY DASHBOARD BACKEND SERVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Google service account credentials
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:GOOGLE_APPLICATION_CREDENTIALS = Join-Path $scriptPath "vsa-anythingllm-project-ab7c8caf8c47.json"
Write-Host "[INFO] Google service account: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Yellow
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[SUCCESS] Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if dependencies are installed
python -c "import flask" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
    pip install -r synergy_requirements.txt
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Start the server
Write-Host "[INFO] Starting Synergy Dashboard Backend..." -ForegroundColor Yellow
Write-Host "[INFO] Server will be available at http://localhost:5001" -ForegroundColor Cyan
Write-Host "[INFO] WebSocket at ws://localhost:5001/ws/synergy" -ForegroundColor Cyan
Write-Host "[INFO] Google Tasks/Calendar sync enabled" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python synergy_backend.py
