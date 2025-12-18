# Quick status check for Computer Use setup

Write-Host "`n🔍 Computer Use Status Check" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# 1. Docker Desktop
Write-Host "`n1. Docker Desktop:" -ForegroundColor Yellow
$dockerCheck = docker ps 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not running - Run: .\START_DOCKER.ps1" -ForegroundColor Red
}

# 2. API Key
Write-Host "`n2. Anthropic API Key:" -ForegroundColor Yellow
if ($env:ANTHROPIC_API_KEY) {
    Write-Host "   ✅ Found in environment" -ForegroundColor Green
} else {
    # Try loading from .env
    $envPath = "..\..\..\..\..\..env"
    if (Test-Path $envPath) {
        Write-Host "   ✅ Found in .env file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Not found" -ForegroundColor Red
    }
}

# 3. Docker Image
Write-Host "`n3. Docker Image:" -ForegroundColor Yellow
$image = docker images computer-use-browser --format "{{.Repository}}:{{.Tag}}" 2>&1
if ($image -match "computer-use-browser") {
    Write-Host "   ✅ Built: $image" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not built - Building now..." -ForegroundColor Yellow
    Write-Host "      Run: docker-compose -f docker-compose.yml build" -ForegroundColor Gray
}

# 4. Container
Write-Host "`n4. Container:" -ForegroundColor Yellow
$container = docker ps -a --filter "name=computer-use-test" --format "{{.Names}}: {{.Status}}" 2>&1
if ($container -match "computer-use-test") {
    if ($container -match "Up") {
        Write-Host "   ✅ Running: $container" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Exists but stopped: $container" -ForegroundColor Yellow
        Write-Host "      Run: docker-compose -f docker-compose.yml up -d" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ Not created" -ForegroundColor Yellow
    Write-Host "      Run: docker-compose -f docker-compose.yml up -d" -ForegroundColor Gray
}

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Gray
Write-Host "Ready to test?" -ForegroundColor Cyan

if ($LASTEXITCODE -eq 0 -and $container -match "Up") {
    Write-Host "✅ YES! Run: python test_computer_use_auto.py" -ForegroundColor Green
} else {
    Write-Host "⚠️  Not yet - follow steps above" -ForegroundColor Yellow
}

Write-Host ""
