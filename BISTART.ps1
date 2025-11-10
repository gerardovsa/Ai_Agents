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

Write-Host "[0/2] Checking for existing Flask servers on port 5001..." -ForegroundColor Yellow

# Method 1: Try Get-NetTCPConnection (works on Windows 10+)
try {
    $flaskProcesses = Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction Stop | 
                      Select-Object -ExpandProperty OwningProcess -Unique |
                      ForEach-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue } |
                      Where-Object { $_ -ne $null }
    
    if ($flaskProcesses) {
        Write-Host "      Found $($flaskProcesses.Count) process(es) on port 5001" -ForegroundColor Yellow
        foreach ($proc in $flaskProcesses) {
            Write-Host "      Stopping PID $($proc.Id) ($($proc.ProcessName))..." -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Write-Host "      [OK] Port 5001 cleared" -ForegroundColor Green
    } else {
        Write-Host "      [OK] Port 5001 is available" -ForegroundColor Green
    }
} catch {
    # Method 2: Fallback using netstat (works on all Windows versions)
    Write-Host "      Using fallback method (netstat)..." -ForegroundColor Gray
    $netstatOutput = netstat -aon | Select-String ":5001.*LISTENING"
    
    if ($netstatOutput) {
        $pids = $netstatOutput | ForEach-Object {
            if ($_ -match '\s+(\d+)\s*$') { $matches[1] }
        } | Select-Object -Unique
        
        Write-Host "      Found $($pids.Count) process(es) on port 5001" -ForegroundColor Yellow
        foreach ($processId in $pids) {
            Write-Host "      Stopping PID $processId..." -ForegroundColor Gray
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Write-Host "      [OK] Port 5001 cleared" -ForegroundColor Green
    } else {
        Write-Host "      [OK] Port 5001 is available" -ForegroundColor Green
    }
}
Write-Host ""

Write-Host "[1/2] Starting Flask Backend..." -ForegroundColor Green
Write-Host "      Location: $FLASK_DIR" -ForegroundColor Gray
Write-Host "      Port: 5001" -ForegroundColor Gray
Write-Host ""

# Start Flask in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$FLASK_DIR'; `$env:PYTHONIOENCODING='utf-8'; Write-Host 'Flask Backend Running on http://localhost:5001' -ForegroundColor Green; python flask_app.py"

# Wait 3 seconds for Flask to initialize
Start-Sleep -Seconds 3

Write-Host "[2/2] Opening Platform in Browser..." -ForegroundColor Green
Write-Host ""

# Open browser to platform
Start-Process "http://localhost:8080/business-ai-platform-v2.html"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PLATFORM LAUNCHED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Flask Backend:  http://localhost:5001" -ForegroundColor White
Write-Host "   UI Platform:    http://localhost:8080/business-ai-platform-v2.html" -ForegroundColor White
Write-Host "" 
Write-Host "   Note: Open business-ai-platform-v2.html directly in browser" -ForegroundColor Gray
Write-Host "         or serve UI folder with any web server on port 8080" -ForegroundColor Gray
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
