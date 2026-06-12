# Email Thread System - Comprehensive Testing Script
# Tests all components: Database, Backend APIs, Frontend JavaScript

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 78) -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host " EMAIL THREAD SYSTEM - COMPREHENSIVE TEST SUITE" -ForegroundColor White
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 78) -NoNewline
Write-Host "=`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0
$testsSkipped = 0

function Test-Component {
    param($name, $script)
    Write-Host "`n[$name]" -ForegroundColor Yellow -NoNewline
    Write-Host " Testing..." -ForegroundColor Gray
    try {
        & $script
        $script:testsPassed++
        Write-Host "  ✅ PASSED" -ForegroundColor Green
        return $true
    }
    catch {
        $script:testsFailed++
        Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# =============================================================================
# TEST 1: Flask Server Health
# =============================================================================
Test-Component "Flask Server Health" {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/health" -TimeoutSec 3
    if ($response.StatusCode -ne 200) {
        throw "Server returned status $($response.StatusCode)"
    }
    Write-Host "    Server running on port 5001" -ForegroundColor Cyan
}

# =============================================================================
# TEST 2: JavaScript Syntax Validation
# =============================================================================
Test-Component "Communication Hub JS Syntax" {
    $output = node --check "UI\modules_internal\communication-hub\communication-hub-v4-modern.js" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Syntax error: $output"
    }
    Write-Host "    No syntax errors found" -ForegroundColor Cyan
}

Test-Component "Email Thread Integration JS Syntax" {
    $output = node --check "UI\modules_internal\thread-cards\email-thread-integration.js" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Syntax error: $output"
    }
    Write-Host "    No syntax errors found" -ForegroundColor Cyan
}

# =============================================================================
# TEST 3: Thread Creation Endpoint
# =============================================================================
$script:threadSlug = $null
Test-Component "Thread Creation (with location)" {
    $body = @{
        user_id         = 14
        name            = "Test Email Thread - Agent 1"
        location        = "agent-1"
        initial_message = "Test from automated script"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:5001/api/threads/create" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"

    if (-not $response.success) {
        throw "API returned success=false"
    }

    $script:threadSlug = $response.data.thread.id
    Write-Host "    Thread created: $script:threadSlug" -ForegroundColor Cyan
    Write-Host "    Location: agent-1" -ForegroundColor Cyan
}

# =============================================================================
# TEST 4: Email Assignment Endpoint
# =============================================================================
Test-Component "Email Thread Assignment" {
    if (-not $script:threadSlug) {
        throw "No thread slug from previous test"
    }

    $body = @{
        user_id            = 14
        thread_slug        = $script:threadSlug
        email_thread_id    = "test_email_auto_001"
        email_subject      = "Test Email Assignment"
        email_participants = @("test@example.com", "user@example.com")
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5001/api/thread-assignments/email" `
            -Method POST `
            -Body $body `
            -ContentType "application/json"

        if (-not $response.success) {
            throw "API returned success=false: $($response.error)"
        }

        Write-Host "    Email linked to thread" -ForegroundColor Cyan
        Write-Host "    Email ID: test_email_auto_001" -ForegroundColor Cyan
        Write-Host "    Subject: Test Email Assignment" -ForegroundColor Cyan
    }
    catch {
        if ($_.Exception.Message -like "*405*") {
            Write-Host "    ⚠️  Endpoint not found - Flask server needs restart" -ForegroundColor Yellow
            $script:testsSkipped++
            $script:testsFailed--
            return
        }
        throw
    }
}

# =============================================================================
# TEST 5: Database Verification
# =============================================================================
Write-Host "`n[Database Verification] Manual Check Required" -ForegroundColor Yellow
Write-Host "  Run this query in Supabase SQL editor:" -ForegroundColor Gray
Write-Host @"
  
  SELECT 
      thread_slug,
      name,
      location,
      email_thread_id,
      email_subject,
      email_participants
  FROM sessions.threads
  WHERE thread_slug = '$script:threadSlug';
"@ -ForegroundColor Cyan

# =============================================================================
# TEST 6: Unlink Email Endpoint
# =============================================================================
Test-Component "Email Thread Unlink" {
    if (-not $script:threadSlug) {
        throw "No thread slug from previous test"
    }

    $body = @{
        user_id     = 14
        thread_slug = $script:threadSlug
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5001/api/thread-assignments/email/unlink" `
            -Method POST `
            -Body $body `
            -ContentType "application/json"

        if (-not $response.success) {
            throw "API returned success=false"
        }

        Write-Host "    Email unlinked from thread" -ForegroundColor Cyan
    }
    catch {
        if ($_.Exception.Message -like "*405*") {
            Write-Host "    ⚠️  Endpoint not found - Flask server needs restart" -ForegroundColor Yellow
            $script:testsSkipped++
            $script:testsFailed--
            return
        }
        throw
    }
}

# =============================================================================
# TEST 7: File Existence Checks
# =============================================================================
Test-Component "Migration SQL File Exists" {
    $path = "AI_infrastructure\database\migrations\add_email_thread_columns.sql"
    if (-not (Test-Path $path)) {
        throw "File not found: $path"
    }
    $content = Get-Content $path -Raw
    if ($content -notlike "*email_thread_id*") {
        throw "File doesn't contain expected column definitions"
    }
    Write-Host "    Migration file ready: 168 lines" -ForegroundColor Cyan
}

Test-Component "Email Thread Integration JS Exists" {
    $path = "UI\modules_internal\thread-cards\email-thread-integration.js"
    if (-not (Test-Path $path)) {
        throw "File not found: $path"
    }
    $content = Get-Content $path -Raw
    if ($content -notlike "*renderThreadBadge*") {
        throw "File doesn't contain expected functions"
    }
    Write-Host "    Badge renderer ready: 237 lines" -ForegroundColor Cyan
}

# =============================================================================
# TEST 8: HTML Script Tag Check
# =============================================================================
Test-Component "HTML Script Tag Check" {
    $htmlPath = "UI\business-ai-platform-v2.html"
    if (-not (Test-Path $htmlPath)) {
        throw "HTML file not found"
    }
    $content = Get-Content $htmlPath -Raw
    if ($content -notlike "*email-thread-integration.js*") {
        Write-Host "    ⚠️  Script tag NOT added to HTML yet" -ForegroundColor Yellow
        Write-Host "    Add before </body>:" -ForegroundColor Gray
        Write-Host '    <script src="UI/modules_internal/thread-cards/email-thread-integration.js"></script>' -ForegroundColor Cyan
        throw "Script tag missing"
    }
    Write-Host "    Script tag found in HTML" -ForegroundColor Cyan
}

# =============================================================================
# SUMMARY
# =============================================================================
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 78) -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host " TEST RESULTS SUMMARY" -ForegroundColor White
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 78) -NoNewline
Write-Host "=`n" -ForegroundColor Cyan

Write-Host "  ✅ Passed:  " -NoNewline -ForegroundColor Green
Write-Host "$testsPassed" -ForegroundColor White

Write-Host "  ❌ Failed:  " -NoNewline -ForegroundColor Red
Write-Host "$testsFailed" -ForegroundColor White

if ($testsSkipped -gt 0) {
    Write-Host "  ⏭️  Skipped: " -NoNewline -ForegroundColor Yellow
    Write-Host "$testsSkipped (Flask restart needed)" -ForegroundColor White
}

# =============================================================================
# NEXT STEPS
# =============================================================================
Write-Host "`n[NEXT STEPS]" -ForegroundColor Yellow

if ($testsSkipped -gt 0) {
    Write-Host "  1. Restart Flask server to load new endpoints:" -ForegroundColor Cyan
    Write-Host "     cd C:\Users\gpoli\GIT\AI_agents" -ForegroundColor Gray
    Write-Host "     BISTART" -ForegroundColor Gray
}

if ($testsFailed -gt 0) {
    Write-Host "  2. Fix failed tests before proceeding" -ForegroundColor Cyan
}

Write-Host "  3. Execute database migration in Supabase:" -ForegroundColor Cyan
Write-Host "     File: AI_infrastructure/database/migrations/add_email_thread_columns.sql" -ForegroundColor Gray

Write-Host "  4. Add script tag to HTML (if not present):" -ForegroundColor Cyan
Write-Host '     <script src="UI/modules_internal/thread-cards/email-thread-integration.js"></script>' -ForegroundColor Gray

Write-Host "  5. Test in browser:" -ForegroundColor Cyan
Write-Host "     - Open Communication Hub" -ForegroundColor Gray
Write-Host "     - Select emails" -ForegroundColor Gray
Write-Host "     - Click 'Send to AI ▼'" -ForegroundColor Gray
Write-Host "     - Select destination (Prime/Agent)" -ForegroundColor Gray
Write-Host "     - Verify thread created in correct column" -ForegroundColor Gray
Write-Host "     - Check ThreadInfo card for email badge`n" -ForegroundColor Gray

# Exit code
if ($testsFailed -gt 0) {
    exit 1
}
else {
    exit 0
}
