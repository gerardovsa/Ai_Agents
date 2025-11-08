# Test Tabulator Data Flow
# Opens the test page in default browser

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Tabulator Data Flow Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Flask backend is running
Write-Host "Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/health" -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Flask backend is running" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Flask backend not running!" -ForegroundColor Red
    Write-Host "   Please start the backend first with: BISTART" -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Get the test file path
$testFile = Join-Path $PSScriptRoot "test_tabulator_data_flow.html"

if (-not (Test-Path $testFile)) {
    Write-Host "❌ Test file not found: $testFile" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Test file found" -ForegroundColor Green
Write-Host "`nOpening test page in browser..." -ForegroundColor Cyan
Write-Host "File: $testFile`n" -ForegroundColor Gray

# Open in default browser
Start-Process $testFile

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Instructions:" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Click '🚀 Run All Tests' button" -ForegroundColor White
Write-Host "2. Watch each test execute:" -ForegroundColor White
Write-Host "   - Reorder Dashboard" -ForegroundColor Gray
Write-Host "   - Profit Analysis" -ForegroundColor Gray
Write-Host "   - AI Analytics" -ForegroundColor Gray
Write-Host "   - SQL Viewer (dynamic columns)" -ForegroundColor Gray
Write-Host "3. Verify data appears in Tabulator tables" -ForegroundColor White
Write-Host "4. Check logs for any errors" -ForegroundColor White
Write-Host "5. Review summary stats at bottom`n" -ForegroundColor White

Write-Host "Expected Result:" -ForegroundColor Yellow
Write-Host "✅ 4/4 tests passed" -ForegroundColor Green
Write-Host "✅ All Tabulator tables populated with API data" -ForegroundColor Green
Write-Host "✅ Dynamic columns generated for SQL Viewer" -ForegroundColor Green
Write-Host "`n========================================`n" -ForegroundColor Cyan

Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
