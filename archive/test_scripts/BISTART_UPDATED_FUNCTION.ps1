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
        Write-Host '  Flask AI:  ' -NoNewline -ForegroundColor White
        Write-Host 'http://localhost:5001' -ForegroundColor Green
        Write-Host '  Health:    ' -NoNewline -ForegroundColor White
        Write-Host 'http://localhost:5001/health' -ForegroundColor Green
        Write-Host '  UI:        ' -NoNewline -ForegroundColor White
        Write-Host 'Opening Business AI Platform...' -ForegroundColor Cyan
        Write-Host '  Tools:     ' -NoNewline -ForegroundColor White
        Write-Host '281 tools across 19 platforms' -ForegroundColor Cyan
        Write-Host '  Path:      ' -NoNewline -ForegroundColor White
        Write-Host $ai_agents_path -ForegroundColor Gray
        Write-Host '===================================================================' -ForegroundColor Cyan
        Write-Host ''

        # Open the UI in default browser
        if (Test-Path $ui_html) {
            Write-Host '  Opening Business AI Platform UI in browser...' -ForegroundColor Cyan
            Start-Process $ui_html
            Start-Sleep -Seconds 2
        } else {
            Write-Host '  Warning: UI file not found at:' -ForegroundColor Yellow
            Write-Host "  $ui_html" -ForegroundColor Gray
        }

        # Change to directory and run Flask
        Set-Location $ai_agents_path
        python flask_app.py
    } else {
        Write-Host '' -ForegroundColor Red
        Write-Host ' ERROR: AI Agents Flask script not found at:' -ForegroundColor Red
        Write-Host (Join-Path $ai_agents_path $flask_script) -ForegroundColor Yellow
        Write-Host ''
        Write-Host 'Expected location: C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py' -ForegroundColor Gray
        Write-Host ''
    }
}

Write-Host ' AI Agents BI Command Loaded: Type ' -NoNewline -ForegroundColor Green
Write-Host 'BISTART' -NoNewline -ForegroundColor Yellow
Write-Host ' to launch AI Flask + UI from anywhere' -ForegroundColor Green
