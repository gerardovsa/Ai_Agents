#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Business AI Platform UI Server Launcher
    
.DESCRIPTION
    Starts HTTP server on port 8080 to serve the UI and avoid CORS issues.
    Modules require HTTP protocol (not file://) to load manifest.json files.
    
.EXAMPLE
    .\START_UI.ps1
    
.NOTES
    Opens browser automatically after server starts
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Starting Business AI Platform UI                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found!" -ForegroundColor Red
    Write-Host "   Please install Python 3.x and add to PATH" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if port 8080 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  WARNING: Port 8080 is already in use!" -ForegroundColor Yellow
    Write-Host "   Attempting to kill process..." -ForegroundColor Yellow
    
    $processId = (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Select-Object -First 1
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "🚀 Starting UI server on http://localhost:8080..." -ForegroundColor Green
Write-Host ""

# Start server in background job
$job = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    python serve_ui.py
}

# Wait for server to start
Start-Sleep -Seconds 2

# Open browser
$url = "http://localhost:8080/business-ai-platform-v2.html"
Write-Host "🌐 Opening browser: $url" -ForegroundColor Cyan
Start-Process $url

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║ UI Server Running - Press Ctrl+C to stop                                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Receive job output in real-time
Receive-Job -Job $job -Wait

# Cleanup
Remove-Job -Job $job -Force
