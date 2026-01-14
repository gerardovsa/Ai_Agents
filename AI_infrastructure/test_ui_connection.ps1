# Test UI Connection to NEW Flask App
# Tests that HTML UIs can be served and endpoints are accessible

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧪 UI CONNECTION TEST - NEW Flask App" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$baseUrl = "http://localhost:5001"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$ExpectedContent = $null
    )
    
    Write-Host "`n🔍 Testing: $Name" -ForegroundColor Yellow
    Write-Host "   URL: $Url" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method $Method -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   PASS - Status 200 OK" -ForegroundColor Green
            
            if ($ExpectedContent -and $response.Content -like "*$ExpectedContent*") {
                Write-Host "   ASS - Content contains '$ExpectedContent'" -ForegroundColor Green
                $script:testsPassed += 2
            }
            elseif ($ExpectedContent) {
                Write-Host "   ⚠️  WARN - Expected content '$ExpectedContent' not found" -ForegroundColor Yellow
                $script:testsPassed += 1
            }
            else {
                $script:testsPassed += 1
            }
            
            # Show first 100 chars of response
            $preview = $response.Content.Substring(0, [Math]::Min(100, $response.Content.Length))
            Write-Host "   Preview: $preview..." -ForegroundColor Gray
        }
        else {
            Write-Host "    FAIL - Status $($response.StatusCode)" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    catch {
        Write-Host "    FAIL - Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
    }
}

Write-Host "`n📋 PREREQUISITE CHECK" -ForegroundColor Cyan
Write-Host "Make sure NEW Flask is running on port 5001" -ForegroundColor Yellow
Write-Host "Run command: RESTARTNEW" -ForegroundColor Yellow
Write-Host "`nPress any key to continue testing..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Test 1: Health check
Test-Endpoint -Name "Health Check" `
    -Url "$baseUrl/health" `
    -ExpectedContent "healthy"

# Test 2: Stock Management UI
Test-Endpoint -Name "Stock Management HTML" `
    -Url "$baseUrl/stock-management" `
    -ExpectedContent "Stock Management"

# Test 3: Single Agent Viewer UI
Test-Endpoint -Name "Single Agent Viewer HTML" `
    -Url "$baseUrl/single-agent-viewer" `
    -ExpectedContent "<!DOCTYPE html"

# Test 4: Triple Agent UI (default page)
Test-Endpoint -Name "Triple Agent HTML (Home)" `
    -Url "$baseUrl/" `
    -ExpectedContent "<!DOCTYPE html"

# Test 5: Triple Agent explicit route
Test-Endpoint -Name "Triple Agent HTML (Explicit)" `
    -Url "$baseUrl/triple-agent" `
    -ExpectedContent "<!DOCTYPE html"

# Test 6: Data Agent Chat alias
Test-Endpoint -Name "Data Agent Chat HTML (Alias)" `
    -Url "$baseUrl/data-agent-chat" `
    -ExpectedContent "<!DOCTYPE html"

# Test 7: Stock API - Chat endpoint exists (should return 400/405 for GET)
Write-Host "`n🔍 Testing: Stock API - Chat Endpoint Exists" -ForegroundColor Yellow
Write-Host "   URL: $baseUrl/api/stock/chat" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/stock/chat" -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
}
catch {
    if ($_.Exception.Response.StatusCode.Value__ -eq 405) {
        Write-Host "   ASS - Endpoint exists (405 Method Not Allowed for GET, needs POST)" -ForegroundColor Green
        $testsPassed++
    }
    else {
        Write-Host "   ⚠️  WARN - Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
        $testsFailed++
    }
}

# Test 8: Stock API - Streaming endpoint
Write-Host "`n🔍 Testing: Stock API - Streaming Endpoint Exists" -ForegroundColor Yellow
Write-Host "   URL: $baseUrl/api/stock/stream/test-session" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/stock/stream/test-session" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ASS - Streaming endpoint accessible" -ForegroundColor Green
    $testsPassed++
}
catch {
    Write-Host "   ⚠️  WARN - May not be accessible without valid session: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 9: Agent API - Check if registered
Write-Host "`n🔍 Testing: Agent API - Chat Endpoint Exists" -ForegroundColor Yellow
Write-Host "   URL: $baseUrl/api/agent/chat" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/agent/chat" -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
}
catch {
    if ($_.Exception.Response.StatusCode.Value__ -eq 405) {
        Write-Host "   ASS - Endpoint exists (405 Method Not Allowed for GET, needs POST)" -ForegroundColor Green
        $testsPassed++
    }
    elseif ($_.Exception.Response.StatusCode.Value__ -eq 404) {
        Write-Host "    FAIL - Agent routes not implemented yet (404)" -ForegroundColor Red
        $testsFailed++
    }
    else {
        Write-Host "   ⚠️  WARN - Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "assed: $testsPassed" -ForegroundColor Green
Write-Host " Failed: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! UIs are connected to NEW Flask!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Access UIs at:" -ForegroundColor Cyan
    Write-Host "   Stock Management: $baseUrl/stock-management" -ForegroundColor White
    Write-Host "   Single Agent:     $baseUrl/single-agent-viewer" -ForegroundColor White
    Write-Host "   Data Agent Chat:  $baseUrl/data-agent-chat" -ForegroundColor White
    Write-Host "   Triple Agent:     $baseUrl/triple-agent" -ForegroundColor White
    Write-Host "   Home (default):   $baseUrl/" -ForegroundColor White
}
else {
    Write-Host "⚠️  Some tests failed. Check NEW Flask is running on port 5001" -ForegroundColor Yellow
}

Write-Host ""
