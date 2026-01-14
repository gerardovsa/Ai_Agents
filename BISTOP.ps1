# BISTOP - Stop AI Agent Flask Server
# Stops all Python processes related to AI_agents Flask app

Write-Host "Stopping AI Agent Flask Server..." -ForegroundColor Yellow

# Find and stop Flask processes
$processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*AI_agents*" -or 
    $_.CommandLine -like "*flask_app.py*" -or
    $_.CommandLine -like "*AI_infrastructure*"
}

if ($processes) {
    Write-Host "Found $($processes.Count) Flask process(es)" -ForegroundColor Cyan
    $processes | ForEach-Object {
        Write-Host "  Stopping PID $($_.Id)..." -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "[OK] Flask server stopped" -ForegroundColor Green
}
else {
    Write-Host "[INFO] No Flask processes found" -ForegroundColor Yellow
}
