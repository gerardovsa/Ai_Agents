# AI Agent Server Health Check
# Comprehensive stability monitoring

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "AI AGENT SERVER HEALTH CHECK" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$serverUrl = "http://localhost:5001"
$healthy = $true

# 1. Check if server is running
Write-Host "1. Checking server status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$serverUrl/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   Server is running" -ForegroundColor Green
    }
} catch {
    Write-Host "   ERROR: Server is not responding" -ForegroundColor Red
    $healthy = $false
}

# 2. Check database connection
Write-Host "`n2. Checking database..." -ForegroundColor Yellow
$dbPath = "C:\Users\gpoli\GIT\AI_agents\data\sessions.db"
if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length / 1KB
    Write-Host "   Database exists: $dbSize KB" -ForegroundColor Green
    
    # Check for locks
    try {
        $lockPath = "$dbPath-wal"
        if (Test-Path $lockPath) {
            $walSize = (Get-Item $lockPath).Length / 1KB
            Write-Host "   WAL file: $walSize KB (good - using WAL mode)" -ForegroundColor Green
        } else {
            Write-Host "   WARNING: No WAL file found" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   WARNING: Could not check WAL file" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ERROR: Database not found at $dbPath" -ForegroundColor Red
    $healthy = $false
}

# 3. Check Python processes
Write-Host "`n3. Checking Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*AI_agents*"}
if ($pythonProcesses) {
    Write-Host "   Found $($pythonProcesses.Count) AI_agents Python process(es)" -ForegroundColor Green
    foreach ($proc in $pythonProcesses) {
        $cpuPercent = [math]::Round($proc.CPU, 2)
        $memoryMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
        Write-Host "   - PID $($proc.Id): CPU: ${cpuPercent}s, Memory: ${memoryMB} MB" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ERROR: No AI_agents Python processes found" -ForegroundColor Red
    $healthy = $false
}

# 4. Check port availability
Write-Host "`n4. Checking port 5001..." -ForegroundColor Yellow
$portCheck = Test-NetConnection -ComputerName localhost -Port 5001 -WarningAction SilentlyContinue
if ($portCheck.TcpTestSucceeded) {
    Write-Host "   Port 5001 is open and accepting connections" -ForegroundColor Green
} else {
    Write-Host "   ERROR: Port 5001 is not accessible" -ForegroundColor Red
    $healthy = $false
}

# 5. Check Waitress installation
Write-Host "`n5. Checking Waitress (production server)..." -ForegroundColor Yellow
try {
    $waitressCheck = python -c "import waitress; print('installed')" 2>&1
    if ($waitressCheck -eq "installed") {
        Write-Host "   Waitress is installed (production mode)" -ForegroundColor Green
    } else {
        Write-Host "   WARNING: Waitress not installed (using Flask dev server)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   WARNING: Could not check Waitress installation" -ForegroundColor Yellow
}

# 6. Check memory usage
Write-Host "`n6. Checking system memory..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$totalMemGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMemGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedPercent = [math]::Round((($totalMemGB - $freeMemGB) / $totalMemGB) * 100, 2)
Write-Host "   Total: ${totalMemGB} GB, Free: ${freeMemGB} GB, Used: ${usedPercent}%" -ForegroundColor Cyan
if ($usedPercent -gt 90) {
    Write-Host "   WARNING: High memory usage (${usedPercent}%)" -ForegroundColor Yellow
}

# 7. Check disk space
Write-Host "`n7. Checking disk space..." -ForegroundColor Yellow
$drive = Get-PSDrive C
$freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
$usedSpaceGB = [math]::Round($drive.Used / 1GB, 2)
$totalSpaceGB = [math]::Round(($drive.Free + $drive.Used) / 1GB, 2)
$diskUsedPercent = [math]::Round(($usedSpaceGB / $totalSpaceGB) * 100, 2)
Write-Host "   C: drive - Total: ${totalSpaceGB} GB, Free: ${freeSpaceGB} GB, Used: ${diskUsedPercent}%" -ForegroundColor Cyan
if ($freeSpaceGB -lt 5) {
    Write-Host "   WARNING: Low disk space (${freeSpaceGB} GB free)" -ForegroundColor Yellow
}

# 8. Check API endpoints
Write-Host "`n8. Testing API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    "/health",
    "/api/agent/session",
    "/api/tools/list"
)

foreach ($endpoint in $endpoints) {
    try {
        $testResponse = Invoke-WebRequest -Uri "$serverUrl$endpoint" -TimeoutSec 5 -ErrorAction Stop
        if ($testResponse.StatusCode -eq 200 -or $testResponse.StatusCode -eq 400) {
            Write-Host "   $endpoint - OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "   $endpoint - ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $healthy = $false
    }
}

# Final Summary
Write-Host "`n================================" -ForegroundColor Cyan
if ($healthy) {
    Write-Host "OVERALL STATUS: HEALTHY" -ForegroundColor Green
    Write-Host "Server is stable and ready" -ForegroundColor Green
} else {
    Write-Host "OVERALL STATUS: ISSUES DETECTED" -ForegroundColor Red
    Write-Host "Check errors above and fix issues" -ForegroundColor Red
}
Write-Host "================================`n" -ForegroundColor Cyan

# Return exit code
if ($healthy) {
    exit 0
} else {
    exit 1
}
