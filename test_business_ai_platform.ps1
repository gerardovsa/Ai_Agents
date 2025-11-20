# BUSINESS AI PLATFORM V2 - COMPLETE SMOKE TEST (PowerShell)
# Tests all routes, database connections, and module integrations

Write-Host "`n" -NoNewline
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "BUSINESS AI PLATFORM V2 - COMPLETE SMOKE TEST" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @{
    passed = 0
    failed = 0
    warnings = 0
}

$baseUrl = "http://localhost:5001"

# Helper functions
function Print-Section {
    param([string]$text)
    Write-Host "`n--------------------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor White
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
}

function Print-Success {
    param([string]$text)
    Write-Host "   $text" -ForegroundColor Green
}

function Print-Error {
    param([string]$text)
    Write-Host "   $text" -ForegroundColor Red
}

function Print-Warning {
    param([string]$text)
    Write-Host "   $text" -ForegroundColor Yellow
}

# ============================================================================
# TEST 1: Database Connections
# ============================================================================
Print-Section "TEST 1: Database Connections (Supabase)"

try {
    $pythonCheck = python -c "import sys; sys.path.insert(0, 'AI_infrastructure'); from shared.database_utils import is_using_supabase; print('supabase' if is_using_supabase() else 'sqlite')" 2>$null
    
    if ($pythonCheck -eq "supabase") {
        Print-Success "Using Supabase PostgreSQL"
        $testResults.passed++
    } elseif ($pythonCheck -eq "sqlite") {
        Print-Warning "Using SQLite (should be Supabase in production)"
        $testResults.warnings++
    } else {
        Print-Error "Could not determine database mode"
        $testResults.failed++
    }
    
    # Test schemas
    $schemas = @("ai_infrastructure", "sessions", "synergy_sessions")
    foreach ($schema in $schemas) {
        try {
            $result = python -c "import sys; sys.path.insert(0, 'AI_infrastructure'); from shared.database_utils import get_database_connection; conn = get_database_connection('$schema'); cursor = conn.cursor(); cursor.execute('SELECT 1'); print('OK')" 2>$null
            
            if ($result -eq "OK") {
                Print-Success "$schema schema: CONNECTED"
                $testResults.passed++
            } else {
                Print-Error "$schema schema: FAILED"
                $testResults.failed++
            }
        } catch {
            Print-Error "$schema schema: ERROR - $_"
            $testResults.failed++
        }
    }
} catch {
    Print-Error "Database connection test failed: $_"
    $testResults.failed++
}

# ============================================================================
# TEST 2: Flask Server Status
# ============================================================================
Print-Section "TEST 2: Flask Server Status"

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Print-Success "Flask server: RUNNING on port 5001"
        $testResults.passed++
    } else {
        Print-Error "Flask server: UNHEALTHY (status $($response.StatusCode))"
        $testResults.failed++
    }
} catch {
    if ($_.Exception.Message -match "Unable to connect") {
        Print-Error "Flask server: NOT RUNNING (connection refused)"
        Print-Warning "Run 'BISTART' to start the server"
        $testResults.failed++
    } else {
        Print-Error "Flask server test failed: $_"
        $testResults.failed++
    }
}

# ============================================================================
# TEST 3: Authentication Routes
# ============================================================================
Print-Section "TEST 3: Authentication Routes - /api/auth/*"

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/platforms" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/auth/platforms: SUCCESS"
    if ($response.platforms) {
        Print-Success "   Found $($response.platforms.Count) platform configurations"
    }
    $testResults.passed++
} catch {
    Print-Error "/api/auth/platforms: FAILED - $_"
    $testResults.failed++
}

# ============================================================================
# TEST 4: Thread Management Routes
# ============================================================================
Print-Section "TEST 4: Thread Management Routes - /api/threads/*"

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/threads/list" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/threads/list: SUCCESS"
    if ($response -is [Array]) {
        Print-Success "   Found $($response.Count) threads"
        $activeCount = ($response | Where-Object { -not $_.archived }).Count
        Print-Success "   Active threads: $activeCount"
    }
    $testResults.passed++
} catch {
    Print-Error "/api/threads/list: FAILED - $_"
    $testResults.failed++
}

# ============================================================================
# TEST 5: Automation Canvas Routes
# ============================================================================
Print-Section "TEST 5: Automation Canvas Routes - /api/automation/*"

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/automation/workflows" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/automation/workflows: SUCCESS"
    if ($response -is [Array]) {
        Print-Success "   Found $($response.Count) workflows"
    }
    $testResults.passed++
} catch {
    Print-Error "/api/automation/workflows: FAILED - $_"
    $testResults.failed++
}

# ============================================================================
# TEST 6: Synergy Dashboard Routes
# ============================================================================
Print-Section "TEST 6: Synergy Dashboard Routes - /api/kanban/*"

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/kanban/sessions" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/kanban/sessions: SUCCESS"
    if ($response -is [Array]) {
        Print-Success "   Found $($response.Count) Kanban cards"
        
        # Count by column
        $columns = $response | Group-Object -Property column_name
        foreach ($col in $columns) {
            Print-Success "   $($col.Name): $($col.Count) cards"
        }
    }
    $testResults.passed++
} catch {
    Print-Error "/api/kanban/sessions: FAILED - $_"
    $testResults.failed++
}

# ============================================================================
# TEST 7: Agent Routes
# ============================================================================
Print-Section "TEST 7: AI Agent Routes - /api/agent/*"

try {
    # Test Prime agent status
    $response = Invoke-RestMethod -Uri "$baseUrl/api/agent/prime/status" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/agent/prime/status: SUCCESS"
    if ($response.status) {
        Print-Success "   Prime status: $($response.status)"
    }
    $testResults.passed++
} catch {
    Print-Error "/api/agent/prime/status: FAILED - $_"
    $testResults.failed++
}

try {
    # Test agent-1 status
    $response = Invoke-RestMethod -Uri "$baseUrl/api/agent/agent-1/status" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/agent/agent-1/status: SUCCESS"
    $testResults.passed++
} catch {
    Print-Error "/api/agent/agent-1/status: FAILED - $_"
    $testResults.failed++
}

# ============================================================================
# TEST 8: WooCommerce Routes
# ============================================================================
Print-Section "TEST 8: WooCommerce Routes - /api/woocommerce/*"

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/woocommerce/orders?limit=5" -TimeoutSec 5 -ErrorAction Stop
    Print-Success "/api/woocommerce/orders: SUCCESS"
    if ($response -is [Array]) {
        Print-Success "   Found $($response.Count) orders"
    }
    $testResults.passed++
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Print-Warning "/api/woocommerce/orders: NOT CONFIGURED (expected)"
        $testResults.warnings++
    } else {
        Print-Warning "WooCommerce routes test: $_"
        $testResults.warnings++
    }
}

# ============================================================================
# TEST 9: HTML File Structure
# ============================================================================
Print-Section "TEST 9: HTML File Structure - business-ai-platform-v2.html"

$htmlPath = "UI\business-ai-platform-v2.html"
if (Test-Path $htmlPath) {
    $content = Get-Content $htmlPath -Raw
    
    $checks = @(
        @{Name="Supabase JS library"; Pattern="@supabase/supabase-js"},
        @{Name="ThreadManager reference"; Pattern="ThreadManager"},
        @{Name="AutomationsSidebar"; Pattern="AutomationsSidebar"},
        @{Name="synergyBoard reference"; Pattern="synergyBoard"},
        @{Name="MultiAgent reference"; Pattern="MultiAgent"},
        @{Name="window.SUPABASE_URL"; Pattern="window.SUPABASE_URL"},
        @{Name="window.SUPABASE_ANON_KEY"; Pattern="window.SUPABASE_ANON_KEY"}
    )
    
    foreach ($check in $checks) {
        if ($content -match $check.Pattern) {
            Print-Success "$($check.Name): FOUND"
            $testResults.passed++
        } else {
            Print-Error "$($check.Name): NOT FOUND"
            $testResults.failed++
        }
    }
} else {
    Print-Error "business-ai-platform-v2.html: NOT FOUND"
    $testResults.failed++
}

# ============================================================================
# TEST 10: Module JavaScript Files
# ============================================================================
Print-Section "TEST 10: Module JavaScript Files - UI/modules/*"

$moduleFiles = @(
    @{Path="UI\modules\threads\thread_manager.js"; Component="ThreadManager"},
    @{Path="UI\modules\threads\components\user_auth.js"; Component="UserAuth"},
    @{Path="UI\modules\threads\components\account_profile.js"; Component="AccountProfile"},
    @{Path="UI\modules\prompt-library.js"; Component="PromptLibrary"}
)

foreach ($file in $moduleFiles) {
    if (Test-Path $file.Path) {
        $content = Get-Content $file.Path -Raw
        if ($content -match $file.Component) {
            Print-Success "$($file.Path): FOUND ($($file.Component))"
            $testResults.passed++
        } else {
            Print-Warning "$($file.Path): FOUND but component pattern not matched"
            $testResults.warnings++
        }
    } else {
        Print-Error "$($file.Path): NOT FOUND"
        $testResults.failed++
    }
}

# Check inline modules in HTML (synergyBoard, AutomationCanvas, etc.)
Print-Section "TEST 11: Inline Modules in HTML"

$htmlPath = "UI\business-ai-platform-v2.html"
if (Test-Path $htmlPath) {
    $content = Get-Content $htmlPath -Raw
    
    $inlineModules = @(
        @{Name="SynergyBoard"; Pattern="synergyBoard\s*="},
        @{Name="AutomationsSidebar"; Pattern="AutomationsSidebar\s*="},
        @{Name="MultiAgent functions"; Pattern="MultiAgent\."},
        @{Name="BrowserContext"; Pattern="BrowserContext\s*="}
    )
    
    foreach ($module in $inlineModules) {
        if ($content -match $module.Pattern) {
            Print-Success "$($module.Name): FOUND (inline)"
            $testResults.passed++
        } else {
            Print-Warning "$($module.Name): NOT FOUND (may use different pattern)"
            $testResults.warnings++
        }
    }
} else {
    Print-Error "business-ai-platform-v2.html: NOT FOUND"
    $testResults.failed++
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$totalTests = $testResults.passed + $testResults.failed + $testResults.warnings
$passRate = if ($totalTests -gt 0) { ($testResults.passed / $totalTests * 100) } else { 0 }

Write-Host "   Total Tests: $totalTests"
Write-Host "   Passed: $($testResults.passed)" -ForegroundColor Green
Write-Host "   Failed: $($testResults.failed)" -ForegroundColor Red
Write-Host "   Warnings: $($testResults.warnings)" -ForegroundColor Yellow
Write-Host ""

$passRateColor = if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" }
Write-Host "   Pass Rate: " -NoNewline
Write-Host ("{0:N1}%" -f $passRate) -ForegroundColor $passRateColor

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host ""

if ($testResults.failed -eq 0) {
    Write-Host "ALL CRITICAL TESTS PASSED" -ForegroundColor Black -BackgroundColor Green
    Write-Host "Business AI Platform is ready for use!" -ForegroundColor Green
    $exitCode = 0
} elseif ($testResults.failed -le 3) {
    Write-Host "SOME TESTS FAILED" -ForegroundColor Black -BackgroundColor Yellow
    Write-Host "Platform is mostly functional but needs attention" -ForegroundColor Yellow
    $exitCode = 1
} else {
    Write-Host "CRITICAL FAILURES DETECTED" -ForegroundColor Black -BackgroundColor Red
    Write-Host "Platform may not function correctly" -ForegroundColor Red
    $exitCode = 2
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
if ($testResults.failed -gt 0) {
    Write-Host "   1. Review failed tests above"
    Write-Host "   2. Check Flask server logs for errors"
    Write-Host "   3. Verify Supabase credentials in .env.master"
    Write-Host "   4. Re-run: .\test_business_ai_platform.ps1"
} else {
    Write-Host "   1. Open http://localhost:5001/ui/business-ai-platform-v2.html"
    Write-Host "   2. Test thread creation in AI Prime panel"
    Write-Host "   3. Test Synergy board card creation"
    Write-Host "   4. Test Automation canvas workflow creation"
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
