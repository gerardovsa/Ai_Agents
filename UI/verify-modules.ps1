Write-Host "`n=== MODULE SYSTEM VERIFICATION ===" -ForegroundColor Cyan

Write-Host "`n1. Checking Flask Server..." -ForegroundColor Yellow
$flaskProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.MainWindowTitle -like "*flask*" -or 
    (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine -like "*flask_app.py*"
}

if ($flaskProcess) {
    Write-Host "   ✓ Flask server is running (PID: $($flaskProcess.Id -join ', '))" -ForegroundColor Green
}
else {
    Write-Host "   ✗ Flask server NOT running" -ForegroundColor Red
    Write-Host "   → Run: BISTART" -ForegroundColor Yellow
}

Write-Host "`n2. Checking Module Files..." -ForegroundColor Yellow
$moduleFiles = @(
    "UI/js/module-manager.js",
    "UI/js/module-base.js",
    "UI/js/module-loader.js",
    "UI/external/modules/manifest.json"
)

foreach ($file in $moduleFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $file MISSING" -ForegroundColor Red
    }
}

Write-Host "`n3. Checking Manifest Content..." -ForegroundColor Yellow
if (Test-Path "UI/external/modules/manifest.json") {
    try {
        $manifest = Get-Content "UI/external/modules/manifest.json" | ConvertFrom-Json
        $enabledModules = $manifest.modules | Where-Object { $_.enabled -eq $true }
        Write-Host "   ✓ Manifest valid" -ForegroundColor Green
        Write-Host "   ✓ $($manifest.modules.Count) total modules" -ForegroundColor Green
        Write-Host "   ✓ $($enabledModules.Count) enabled modules" -ForegroundColor Green
        
        Write-Host "`n   Enabled Modules:" -ForegroundColor Cyan
        foreach ($mod in $enabledModules) {
            Write-Host "     - $($mod.name)" -ForegroundColor White
        }
    }
    catch {
        Write-Host "   ✗ Manifest parse error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "   ✗ Manifest not found" -ForegroundColor Red
}

Write-Host "`n4. Testing HTTP Access..." -ForegroundColor Yellow
$ports = @(5001, 5000)
$serverFound = $false

foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/external/modules/manifest.json" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "   ✓ Manifest accessible at http://localhost:$port (Status: $($response.StatusCode))" -ForegroundColor Green
        $serverFound = $true
        
        Write-Host "`n5. Testing Main Page..." -ForegroundColor Yellow
        try {
            $pageResponse = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 2 -ErrorAction Stop
            Write-Host "   ✓ Main page accessible (Status: $($pageResponse.StatusCode))" -ForegroundColor Green
        }
        catch {
            Write-Host "   ⚠ Main page not accessible: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        break
    }
    catch {
        Write-Host "   ✗ Port $port not accessible" -ForegroundColor Red
    }
}

if (-not $serverFound) {
    Write-Host "`n   → Start server with: BISTART" -ForegroundColor Yellow
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "1. If server not running: Run BISTART" -ForegroundColor White
Write-Host "2. Open browser: http://localhost:5001" -ForegroundColor White
Write-Host "3. Press F12 to open Developer Tools" -ForegroundColor White
Write-Host "4. Check Console tab for module loading messages" -ForegroundColor White
Write-Host "5. Look for module icons in sidebar (between Multi-Agent and Settings)" -ForegroundColor White

Write-Host "`n=== DEBUG COMMANDS ===" -ForegroundColor Cyan
Write-Host "View manifest:  Get-Content UI/external/modules/manifest.json | ConvertFrom-Json | Format-List" -ForegroundColor Yellow
Write-Host "Check modules:  Get-ChildItem UI/external/modules -Directory | Select Name" -ForegroundColor Yellow
Write-Host "Test page:      Start-Process 'http://localhost:5001'" -ForegroundColor Yellow

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
