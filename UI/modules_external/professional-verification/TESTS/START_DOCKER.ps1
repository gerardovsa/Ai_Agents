# Simple script to start Docker Desktop and wait for it to be ready

Write-Host "`n🐳 Starting Docker Desktop..." -ForegroundColor Cyan

# Start Docker Desktop
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

if (!(Test-Path $dockerPath)) {
    Write-Host "❌ Docker Desktop not found at: $dockerPath" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if already running
$dockerCheck = docker ps 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker Desktop is already running!" -ForegroundColor Green
    exit 0
}

# Start it
Write-Host "Starting Docker Desktop.exe..." -ForegroundColor Yellow
Start-Process $dockerPath

Write-Host "`nWaiting for Docker to be ready..." -ForegroundColor Gray
Write-Host "(This usually takes 20-60 seconds)`n" -ForegroundColor Gray

# Wait for Docker to be ready
$timeout = 120  # 2 minutes max
$elapsed = 0

while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 5
    $elapsed += 5
    
    $dockerCheck = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Docker Desktop is ready!" -ForegroundColor Green
        Write-Host "`nYou can now run: .\build-and-test.ps1" -ForegroundColor Cyan
        exit 0
    }
    
    # Show progress every 10 seconds
    if ($elapsed % 10 -eq 0) {
        Write-Host "  Still waiting... ($elapsed seconds)" -ForegroundColor Gray
    }
}

Write-Host "`n❌ Docker Desktop failed to start within $timeout seconds" -ForegroundColor Red
Write-Host "Please check Docker Desktop manually" -ForegroundColor Yellow
exit 1
