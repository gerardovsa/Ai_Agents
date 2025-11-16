# ==================== BUSINESS AI PLATFORM LAUNCHER (PowerShell) ====================
# Launch Flask backend + UI from any directory
# Usage: .\BISTART.ps1 or just "BISTART" if added to PATH

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   BUSINESS AI PLATFORM LAUNCHER" -ForegroundColor Yellow
Write-Host "   [SUPABASE MODE - PostgreSQL Database]" -ForegroundColor Cyan
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

Write-Host "[0/4] Cleaning up zombie Python processes..." -ForegroundColor Yellow

# Kill ALL Python processes (Flask zombies + any leftover processes)
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "      Found $($pythonProcs.Count) Python process(es) - stopping all..." -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        Write-Host "      Stopping PID $($proc.Id)..." -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "      [OK] All Python processes stopped" -ForegroundColor Green
}
else {
    Write-Host "      [OK] No Python processes to clean" -ForegroundColor Green
}
Write-Host ""

Write-Host "[1/4] Checking for existing Flask servers on port 5001..." -ForegroundColor Yellow

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
    }
    else {
        Write-Host "      [OK] Port 5001 is available" -ForegroundColor Green
    }
}
catch {
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
    }
    else {
        Write-Host "      [OK] Port 5001 is available" -ForegroundColor Green
    }
}
Write-Host ""

Write-Host "[2/4] Starting Flask Backend with Supabase..." -ForegroundColor Green
Write-Host "      Location: $FLASK_DIR" -ForegroundColor Gray
Write-Host "      Port: 5001" -ForegroundColor Gray
Write-Host "      Database: Supabase PostgreSQL" -ForegroundColor Cyan
Write-Host ""

# Start Flask in new PowerShell window with Supabase environment variables
$flaskCommand = @"
Set-Location '$FLASK_DIR'
`$env:PYTHONIOENCODING='utf-8'
`$env:DEBUG='true'
`$env:FLASK_ENV='development'
`$env:USE_SUPABASE='true'
`$env:RENDER='true'
`$env:SUPABASE_URL='https://ryoicrdifiqhqpsnjmdo.supabase.co'
`$env:SUPABASE_SERVICE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5b2ljcmRpZmlxaHFwc25qbWRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjY2NDI0NSwiZXhwIjoyMDc4MjQwMjQ1fQ.ebI6qfDzSt1skNm0hsBD-blyR7AJJUej5BcN-Bpp3PI'
`$env:SUPABASE_DB_URL='postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres'
Write-Host ''
Write-Host '[SUPABASE MODE] Connected to PostgreSQL Database' -ForegroundColor Cyan
Write-Host '[DEV MODE] Debug enabled - dev-mode-token accepted' -ForegroundColor Yellow
Write-Host 'Flask Backend Running on http://localhost:5001' -ForegroundColor Green
Write-Host ''
python flask_app.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $flaskCommand

# Wait 3 seconds for Flask to initialize
Start-Sleep -Seconds 3

Write-Host "[3/4] Opening Platform in Browser..." -ForegroundColor Green
Write-Host ""

# Open browser to platform (direct file access)
$UI_FILE = "$UI_DIR\business-ai-platform-v2.html"
Start-Process $UI_FILE

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PLATFORM LAUNCHED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Flask Backend:  http://localhost:5001" -ForegroundColor White
Write-Host "   UI Platform:    file:///$UI_DIR/business-ai-platform-v2.html" -ForegroundColor White
Write-Host "" 
Write-Host "   Note: UI opened directly from file system" -ForegroundColor Gray
Write-Host "         Connected to Flask backend on port 5001" -ForegroundColor Gray
Write-Host ""
Write-Host "    Flask Backend:  http://localhost:5001" -ForegroundColor Yellow
Write-Host "    UI Platform:    Opened in default browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "    1 PowerShell window opened:" -ForegroundColor White
Write-Host "    - Flask Backend (Port 5001)" -ForegroundColor Gray
Write-Host ""
Write-Host "    Press Ctrl+C in each window to stop servers" -ForegroundColor Magenta
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Return to original directory
Set-Location $ORIGINAL_DIR

Write-Host ""
Read-Host "Press Enter to exit launcher"
