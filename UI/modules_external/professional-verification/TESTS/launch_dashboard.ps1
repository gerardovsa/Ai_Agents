#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch AI Verification Dashboard with Live Monitoring
    
.DESCRIPTION
    This script will:
    1. Start Docker container (if needed)
    2. Start WebSocket server with HTTP server
    3. Open dashboard in browser
    4. Show real-time AI reasoning, commands, and results
    
.EXAMPLE
    .\launch_dashboard.ps1
    
.NOTES
    Created: December 18, 2025
    URL: http://localhost:8080/verification_dashboard.html
#>

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "🚀 AI VERIFICATION DASHBOARD LAUNCHER" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python dependencies are installed
Write-Host "Step 1: Checking Python dependencies..." -ForegroundColor Yellow
Write-Host ""

try {
    python -c "import websockets" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Installing websockets..." -ForegroundColor Yellow
        pip install websockets
    }
    
    python -c "import anthropic" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Installing anthropic..." -ForegroundColor Yellow
        pip install anthropic
    }
    
    Write-Host "   ✅ All dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not check dependencies" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Check Docker (optional)
Write-Host "Step 2: Checking Docker (optional for bash execution)..." -ForegroundColor Yellow
Write-Host ""

$dockerService = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue

if ($null -ne $dockerService -and $dockerService.Status -eq "Running") {
    Write-Host "   ✅ Docker Desktop is running" -ForegroundColor Green
    
    # Check if container exists
    $containerExists = docker ps -a --format "{{.Names}}" | Select-String "computer-use-verification"
    
    if ($containerExists) {
        # Check if running
        $containerRunning = docker ps --format "{{.Names}}" | Select-String "computer-use-verification"
        
        if (-not $containerRunning) {
            Write-Host "   Starting container..." -ForegroundColor Yellow
            docker start computer-use-verification 2>&1 | Out-Null
            Start-Sleep -Seconds 2
            Write-Host "   ✅ Container started" -ForegroundColor Green
        } else {
            Write-Host "   ✅ Container already running" -ForegroundColor Green
        }
    } else {
        Write-Host "   ⚠️  Container not built yet" -ForegroundColor Yellow
        Write-Host "      Run: .\run_complete_verification.ps1 to build" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  Docker not running (bash commands will be simulated)" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Start server
Write-Host "Step 3: Starting verification server..." -ForegroundColor Yellow
Write-Host ""

Write-Host "   Launching Python server with WebSocket and HTTP..." -ForegroundColor Gray
Write-Host ""

# Kill any existing Python processes on ports 8080 or 5555
$existingProcess = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "   Stopping existing server on port 8080..." -ForegroundColor Yellow
    Stop-Process -Id $existingProcess.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

$existingProcess = Get-NetTCPConnection -LocalPort 5555 -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "   Stopping existing server on port 5555..." -ForegroundColor Yellow
    Stop-Process -Id $existingProcess.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "✅ DASHBOARD READY" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "   🌐 Dashboard URL: http://localhost:8080/verification_dashboard.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "   📊 Features Available:" -ForegroundColor Yellow
Write-Host "      ✅ Real-time AI reasoning panel" -ForegroundColor Gray
Write-Host "      ✅ Live bash command execution" -ForegroundColor Gray
Write-Host "      ✅ System logs with timestamps" -ForegroundColor Gray
Write-Host "      ✅ Verification results display" -ForegroundColor Gray
Write-Host "      ✅ Progress statistics (iterations, tokens, time)" -ForegroundColor Gray
Write-Host "      ✅ VNC browser view (localhost:5900)" -ForegroundColor Gray
Write-Host ""
Write-Host "   🎯 Usage:" -ForegroundColor Yellow
Write-Host "      1. Dashboard will open in your browser" -ForegroundColor Gray
Write-Host "      2. Click 'Start Verification' button" -ForegroundColor Gray
Write-Host "      3. Watch AI work in real-time!" -ForegroundColor Gray
Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""

# Wait a moment then open browser
Start-Sleep -Seconds 2

Write-Host "   Opening dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8080/verification_dashboard.html"

Write-Host ""
Write-Host "   ⚡ Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the Python server (this will block)
python verification_server.py
