# Script to Update BISTART Function in PowerShell Profile
# This will replace the existing BISTART function with the updated version

Write-Host "Updating BISTART function in PowerShell profile..." -ForegroundColor Cyan

# Read the current profile
$profileContent = Get-Content $PROFILE -Raw

# Find and replace the BISTART function
$oldFunctionPattern = '(?s)# ==============================================================\s*# AI Agents Business Intelligence - Global BISTART Command.*?Write-Host '' to launch AI Flask from anywhere'' -ForegroundColor Green'

$newFunction = @'
# ==============================================================
# AI Agents Business Intelligence - Global BISTART Command
# ==============================================================
# Usage: Just type 'BISTART' from any directory
# Launches: Flask AI Agent Server (port 5001) + Opens Business Platform UI
# ==============================================================

function BISTART {
    $ai_agents_path = 'C:\Users\gpoli\GIT\AI_agents\AI_infrastructure'
    $flask_script = 'flask_app.py'
    $ui_html = 'C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html'

    if (Test-Path (Join-Path $ai_agents_path $flask_script)) {
        Write-Host '' -ForegroundColor Green
        Write-Host '===================================================================' -ForegroundColor Cyan
        Write-Host '  Launching AI Agents Business Intelligence Platform' -ForegroundColor Yellow
        Write-Host '===================================================================' -ForegroundColor Cyan
        
        # Step 1: Kill any existing Flask processes on port 5001
        Write-Host '  🧹 Checking for existing Flask processes on port 5001...' -ForegroundColor Yellow
        $existingProcess = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue | 
                          Select-Object -ExpandProperty OwningProcess -First 1
        
        if ($existingProcess) {
            Write-Host "  🛑 Stopping existing Flask process (PID: $existingProcess)..." -ForegroundColor Yellow
            Stop-Process -Id $existingProcess -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Write-Host '  ✅ Existing Flask stopped' -ForegroundColor Green
        } else {
            Write-Host '  ✅ No existing Flask process found' -ForegroundColor Green
        }
        
        Write-Host ''
        Write-Host '  Flask AI:  ' -NoNewline -ForegroundColor White
        Write-Host 'http://localhost:5001' -ForegroundColor Green
        Write-Host '  Health:    ' -NoNewline -ForegroundColor White
        Write-Host 'http://localhost:5001/health' -ForegroundColor Green
        Write-Host '===================================================================' -ForegroundColor Cyan
        Write-Host ''

        # Step 2: Start Flask in background
        Write-Host '  🚀 Starting Flask server...' -ForegroundColor Cyan
        Set-Location $ai_agents_path
        
        $flaskProcess = Start-Process python -ArgumentList "flask_app.py" -WorkingDirectory $ai_agents_path -PassThru -WindowStyle Hidden
        
        # Step 3: Wait for Flask to be ready (health check)
        Write-Host '  ⏳ Waiting for Flask to be ready' -NoNewline -ForegroundColor Yellow
        $maxAttempts = 30
        $attempt = 0
        $flaskReady = $false

        while ($attempt -lt $maxAttempts -and -not $flaskReady) {
            Start-Sleep -Seconds 1
            try {
                $response = Invoke-WebRequest -Uri 'http://localhost:5001/health' -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $flaskReady = $true
                    Write-Host ''
                    Write-Host '  ✅ Flask is ready and healthy!' -ForegroundColor Green
                }
            } catch {
                Write-Host '.' -NoNewline -ForegroundColor Yellow
                $attempt++
            }
        }

        # Step 4: Open UI in browser only after Flask is ready
        if ($flaskReady) {
            Start-Sleep -Seconds 1
            if (Test-Path $ui_html) {
                Write-Host '  🌐 Opening Business AI Platform UI in browser...' -ForegroundColor Cyan
                Start-Process $ui_html
                Write-Host ''
                Write-Host '===================================================================' -ForegroundColor Cyan
                Write-Host '  ✅ READY! Flask is running (PID: ' -NoNewline -ForegroundColor Green
                Write-Host "$($flaskProcess.Id)" -NoNewline -ForegroundColor White
                Write-Host '), UI is open' -ForegroundColor Green
                Write-Host '===================================================================' -ForegroundColor Cyan
                Write-Host ''
                Write-Host '  Press Ctrl+C in Flask window to stop, or run:' -ForegroundColor Gray
                Write-Host "  Stop-Process -Id $($flaskProcess.Id)" -ForegroundColor Gray
                Write-Host ''
            } else {
                Write-Host '  ❌ Warning: UI file not found at:' -ForegroundColor Yellow
                Write-Host "  $ui_html" -ForegroundColor Gray
            }
        } else {
            Write-Host ''
            Write-Host '  ❌ Flask failed to start after 30 seconds' -ForegroundColor Red
            Write-Host '  Stopping Flask process...' -ForegroundColor Yellow
            Stop-Process -Id $flaskProcess.Id -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host '' -ForegroundColor Red
        Write-Host ' ❌ ERROR: AI Agents Flask script not found at:' -ForegroundColor Red
        Write-Host (Join-Path $ai_agents_path $flask_script) -ForegroundColor Yellow
        Write-Host ''
        Write-Host 'Expected location: C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py' -ForegroundColor Gray
        Write-Host ''
    }
}

Write-Host ' AI Agents BI Command Loaded: Type ' -NoNewline -ForegroundColor Green
Write-Host 'BISTART' -NoNewline -ForegroundColor Yellow
Write-Host ' to launch AI Flask + UI from anywhere' -ForegroundColor Green
'@

# Replace the old function with the new one
$updatedContent = $profileContent -replace $oldFunctionPattern, $newFunction

# Save the updated profile
$updatedContent | Set-Content $PROFILE -Force

Write-Host ""
Write-Host "✅ BISTART function updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Reloading profile..." -ForegroundColor Cyan
. $PROFILE

Write-Host ""
Write-Host "✅ Profile reloaded! You can now use BISTART to launch Flask + UI" -ForegroundColor Green
Write-Host ""
