# ==================== BUSINESS AI PLATFORM STOPPER ====================
# Stop Flask backend and UI server
# Usage: .\BISTOP.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Red
Write-Host "   STOPPING BUSINESS AI PLATFORM" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

# Kill Flask processes (port 5001)
Write-Host "[1/2] Stopping Flask Backend (Port 5001)..." -ForegroundColor Yellow
$flaskProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*flask_app.py*"
}

if ($flaskProcesses) {
    $flaskProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "      Stopped Flask process (PID: $($_.Id))" -ForegroundColor Green
    }
} else {
    Write-Host "      No Flask processes found" -ForegroundColor Gray
}

# Kill UI server processes (port 8080)
Write-Host ""
Write-Host "[2/2] Stopping UI Server (Port 8080)..." -ForegroundColor Yellow
$uiProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*http.server*8080*"
}

if ($uiProcesses) {
    $uiProcesses | ForEach-Object {
        Stop-Process -Id $_.Id -Force
        Write-Host "      Stopped UI server process (PID: $($_.Id))" -ForegroundColor Green
    }
} else {
    Write-Host "      No UI server processes found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Red
Write-Host "   ALL SERVERS STOPPED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

Read-Host "Press Enter to exit"
