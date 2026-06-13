# Work Timeline Tool - Quick Start Script (PowerShell)
# Run this to generate your timeline dashboard

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Work Timeline Tool - Quick Start" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if config.py exists
if (-not (Test-Path "config.py")) {
    Write-Host "[ERROR] config.py not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create config.py from config_template.py:" -ForegroundColor Yellow
    Write-Host "  1. Copy config_template.py to config.py"
    Write-Host "  2. Edit config.py with your project paths"
    Write-Host "  3. Run this script again"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Found config.py - checking Python..." -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Gray
}
catch {
    Write-Host "[ERROR] Python not found! Please install Python 3.x" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[2/3] Generating timeline..." -ForegroundColor Green
python create_focused_timeline.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Timeline generation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[3/3] Opening dashboard..." -ForegroundColor Green
Start-Process "focused_timeline_detailed.html"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "   SUCCESS! Timeline dashboard generated" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "The dashboard has been opened in your browser." -ForegroundColor White
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "  - focused_timeline_detailed.html"
Write-Host ""
Write-Host "To regenerate with new data, run this script again." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
