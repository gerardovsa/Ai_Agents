# ==================== BUSINESS AI PLATFORM LAUNCHER (PowerShell) ====================
# Launch Flask backend + UI from any directory
# Usage: .\BISTART.ps1 or just "BISTART" if added to PATH

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   BUSINESS AI PLATFORM LAUNCHER" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$FLASK_DIR = "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure"
$UI_DIR = "C:\Users\gpoli\GIT\AI_agents\UI"
$ORIGINAL_DIR = Get-Location

# Check if Flask app exists
if (-not (Test-Path "$FLASK_DIR\flask_app.py")) {
    Write-Host "[ERROR] Flask app not found at: $FLASK_DIR\flask_app.py" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if UI exists
if (-not (Test-Path "$UI_DIR\business-ai-platform-v2.html")) {
    Write-Host "[ERROR] UI not found at: $UI_DIR\business-ai-platform-v2.html" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Starting Flask Backend..." -ForegroundColor Green
Write-Host "      Location: $FLASK_DIR" -ForegroundColor Gray
Write-Host "      Port: 5001" -ForegroundColor Gray
Write-Host ""

# Start Flask in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$FLASK_DIR'; Write-Host 'Flask Backend Running on http://localhost:5001' -ForegroundColor Green; python flask_app.py"

# Wait 3 seconds for Flask to initialize
Start-Sleep -Seconds 3

Write-Host "[2/3] Starting UI Server..." -ForegroundColor Green
Write-Host "      Location: $UI_DIR" -ForegroundColor Gray
Write-Host "      Port: 8080" -ForegroundColor Gray
Write-Host ""

# Start UI server in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$UI_DIR'; Write-Host 'UI Server Running on http://localhost:8080' -ForegroundColor Green; python -m http.server 8080"

# Wait 2 seconds for UI server to start
Start-Sleep -Seconds 2

Write-Host "[3/3] Opening Platform in Browser..." -ForegroundColor Green
Write-Host ""

# Open browser to platform
Start-Process "http://localhost:8080/business-ai-platform-v2.html"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PLATFORM LAUNCHED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "    Flask Backend:  http://localhost:5001" -ForegroundColor Yellow
Write-Host "    UI Platform:    http://localhost:8080/business-ai-platform-v2.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "    2 PowerShell windows opened:" -ForegroundColor White
Write-Host "    1. Flask Backend (Port 5001)" -ForegroundColor Gray
Write-Host "    2. UI Server (Port 8080)" -ForegroundColor Gray
Write-Host ""
Write-Host "    Press Ctrl+C in each window to stop servers" -ForegroundColor Magenta
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Return to original directory
Set-Location $ORIGINAL_DIR

Write-Host ""
Read-Host "Press Enter to exit launcher"
