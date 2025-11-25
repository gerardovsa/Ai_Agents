# find_api_url_issues.ps1
# Diagnostic script to find API URL configuration issues

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " API URL Configuration Diagnostic" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "UI")) {
    Write-Host "ERROR: Must run from AI_agents root directory" -ForegroundColor Red
    Write-Host "Current location: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Checking for hardcoded localhost:5001..." -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor DarkGray

$localhostFiles = Get-ChildItem -Path "UI" -Recurse -Include *.js, *.html -ErrorAction SilentlyContinue |
Select-String -Pattern "localhost:5001" -CaseSensitive

if ($localhostFiles) {
    foreach ($match in $localhostFiles) {
        $relPath = $match.Path -replace [regex]::Escape((Get-Location).Path + "\"), ""
        Write-Host " FOUND: $relPath : Line $($match.LineNumber)" -ForegroundColor Red
        Write-Host "        $($match.Line.Trim())" -ForegroundColor DarkRed
    }
}
else {
    Write-Host " None found (GOOD)" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Checking window.API_BASE_URL usage..." -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor DarkGray

$apiBaseUsage = Get-ChildItem -Path "UI" -Recurse -Include *.js -ErrorAction SilentlyContinue |
Select-String -Pattern "window\.API_BASE_URL" |
Select-Object -First 10

if ($apiBaseUsage) {
    foreach ($match in $apiBaseUsage) {
        $relPath = $match.Path -replace [regex]::Escape((Get-Location).Path + "\"), ""
        Write-Host " OK: $relPath : Line $($match.LineNumber)" -ForegroundColor Green
    }
    Write-Host " ... (showing first 10)" -ForegroundColor DarkGray
}
else {
    Write-Host " WARNING: No files found using window.API_BASE_URL" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "3. Checking ThreadManager files..." -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor DarkGray

$threadManagerFiles = Get-ChildItem -Path "UI\modules\thread-manager" -Filter *.js -ErrorAction SilentlyContinue

if ($threadManagerFiles) {
    foreach ($file in $threadManagerFiles) {
        Write-Host " Found: $($file.Name)" -ForegroundColor Cyan
        
        # Check for API URL usage in this file
        $apiUsage = Select-String -Path $file.FullName -Pattern "API.*URL|localhost" -CaseSensitive
        if ($apiUsage) {
            foreach ($line in $apiUsage | Select-Object -First 3) {
                Write-Host "        Line $($line.LineNumber): $($line.Line.Trim())" -ForegroundColor White
            }
        }
    }
}
else {
    Write-Host " ERROR: ThreadManager files not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Checking script load order in HTML..." -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor DarkGray

$htmlFile = "UI\business-ai-platform-v2.html"
if (Test-Path $htmlFile) {
    # Find where API_BASE_URL is set
    $apiSetLine = Select-String -Path $htmlFile -Pattern "window\.API_BASE_URL\s*=" | Select-Object -First 1
    
    # Find where ThreadManager is loaded
    $threadManagerLine = Select-String -Path $htmlFile -Pattern "thread-manager.*\.js" | Select-Object -First 1
    
    if ($apiSetLine -and $threadManagerLine) {
        Write-Host " API_BASE_URL set at line: $($apiSetLine.LineNumber)" -ForegroundColor Cyan
        Write-Host " ThreadManager loaded at line: $($threadManagerLine.LineNumber)" -ForegroundColor Cyan
        
        if ($apiSetLine.LineNumber -lt $threadManagerLine.LineNumber) {
            Write-Host " Load order: CORRECT (API_BASE_URL before ThreadManager)" -ForegroundColor Green
        }
        else {
            Write-Host " Load order: WRONG (ThreadManager before API_BASE_URL!)" -ForegroundColor Red
        }
    }
    else {
        Write-Host " WARNING: Could not determine load order" -ForegroundColor Yellow
    }
}
else {
    Write-Host " ERROR: business-ai-platform-v2.html not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Checking render-config.js..." -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor DarkGray

$renderConfigFile = "UI\render-config.js"
if (Test-Path $renderConfigFile) {
    Write-Host " Found: render-config.js" -ForegroundColor Green
    
    # Check for Render URL
    $renderUrl = Select-String -Path $renderConfigFile -Pattern "onrender\.com" | Select-Object -First 1
    if ($renderUrl) {
        Write-Host " Render URL configured: $($renderUrl.Line.Trim())" -ForegroundColor Cyan
    }
    else {
        Write-Host " WARNING: No Render URL found in config" -ForegroundColor Yellow
    }
}
else {
    Write-Host " ERROR: render-config.js not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Diagnostic Complete" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host "1. Ensure window.API_BASE_URL is set BEFORE any modules load" -ForegroundColor White
Write-Host "2. Use: window.API_BASE_URL || 'http://localhost:5001' as fallback" -ForegroundColor White
Write-Host "3. Check Render deployment logs for actual API_BASE_URL value" -ForegroundColor White
Write-Host ""
