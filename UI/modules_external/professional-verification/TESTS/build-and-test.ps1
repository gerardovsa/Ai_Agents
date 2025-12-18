# Build and Test Computer Use - One Command
# Run this to build Docker image and test Computer Use

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "  COMPUTER USE - BUILD AND TEST" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

# Step 1: Check and Start Docker
Write-Host "`n[1/4] Checking Docker Desktop..." -ForegroundColor Cyan

# Check if Docker is running
$dockerCheck = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! Docker Desktop is not running" -ForegroundColor Yellow
    Write-Host "  Starting Docker Desktop..." -ForegroundColor Cyan
    
    # Find and start Docker Desktop
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        
        # Wait for Docker to be ready (max 60 seconds)
        Write-Host "  Waiting for Docker to start..." -ForegroundColor Gray
        $timeout = 60
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 3
            $elapsed += 3
            
            $dockerCheck = docker ps 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  √ Docker Desktop started successfully" -ForegroundColor Green
                break
            }
            
            if ($elapsed % 10 -eq 0) {
                Write-Host "    Still waiting... ($elapsed/$timeout sec)" -ForegroundColor Gray
            }
        }
        
        if ($elapsed -ge $timeout) {
            Write-Host "  X Docker Desktop took too long to start" -ForegroundColor Red
            Write-Host "  Please check Docker Desktop manually" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host "  X Docker Desktop not found at: $dockerPath" -ForegroundColor Red
        Write-Host "  Please start Docker Desktop manually and run this again" -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "  √ Docker Desktop is running" -ForegroundColor Green
}

# Step 2: Build image
Write-Host "`n[2/4] Building Docker image..." -ForegroundColor Cyan
Write-Host "  (This may take 2-3 minutes on first build)" -ForegroundColor Gray

docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  √ Image built successfully" -ForegroundColor Green

# Step 3: Start container
Write-Host "`n[3/4] Starting container..." -ForegroundColor Cyan

# Stop existing container if running
docker stop computer-use-test 2>&1 | Out-Null
docker rm computer-use-test 2>&1 | Out-Null

docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Container failed to start!" -ForegroundColor Red
    exit 1
}

Write-Host "  √ Container started" -ForegroundColor Green
Write-Host "  Waiting for container to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Check container health
$containerStatus = docker ps --filter "name=computer-use-test" --format "{{.Status}}"
if ($containerStatus -match "Up") {
    Write-Host "  √ Container is healthy" -ForegroundColor Green
}
else {
    Write-Host "  ! Container status: $containerStatus" -ForegroundColor Yellow
}

# Step 4: Run test
Write-Host "`n[4/4] Running Computer Use test..." -ForegroundColor Cyan
Write-Host "  (Claude will browse isb.eco and extract info)" -ForegroundColor Gray
Write-Host ""

python test_computer_use_auto.py

# Check result
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n" -NoNewline
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 79) -ForegroundColor Green
    Write-Host "  SUCCESS! Computer Use is working!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host ("=" * 79) -ForegroundColor Green
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Check the screenshot that was saved" -ForegroundColor White
    Write-Host "  2. Try: python demo_computer_use_live.py" -ForegroundColor White
    Write-Host "  3. Use auto_enter_verification_results() in production" -ForegroundColor White
}
else {
    Write-Host "`n" -NoNewline
    Write-Host "=" -NoNewline -ForegroundColor Yellow
    Write-Host ("=" * 79) -ForegroundColor Yellow
    Write-Host "  Test completed with issues" -ForegroundColor Yellow
    Write-Host "=" -NoNewline -ForegroundColor Yellow
    Write-Host ("=" * 79) -ForegroundColor Yellow
    
    Write-Host "`nTroubleshooting:" -ForegroundColor Cyan
    Write-Host "  - Check logs: docker logs computer-use-test" -ForegroundColor White
    Write-Host "  - Restart: docker restart computer-use-test" -ForegroundColor White
    Write-Host "  - Rebuild: docker-compose build --no-cache" -ForegroundColor White
}

Write-Host ""
