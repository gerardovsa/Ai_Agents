# Communication Hub - Connection Test Script
# Tests Gmail & Outlook integration end-to-end

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "COMMUNICATION HUB CONNECTION TEST" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Configuration
$BACKEND_URL = "http://localhost:5001"
$API_BASE = "$BACKEND_URL/api/communication-hub"

# STEP 1: Check if Flask backend is running
Write-Host "[1/7] Checking Flask backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/v1/system/check" -Method GET -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  Success! Backend is running on $BACKEND_URL" -ForegroundColor Green
    }
} catch {
    Write-Host "  ERROR: Backend is not running!" -ForegroundColor Red
    Write-Host "  Please start the Flask backend with: BISTART" -ForegroundColor Yellow
    Write-Host "  Or run: cd C:\Users\gpoli\GIT\AI_agents; python AI_infrastructure\flask_app.py" -ForegroundColor Yellow
    exit 1
}

# STEP 2: Get JWT token (you need to replace this with actual login)
Write-Host "`n[2/7] Getting JWT token..." -ForegroundColor Yellow
$JWT_TOKEN = $env:TEST_JWT_TOKEN
if (-not $JWT_TOKEN) {
    Write-Host "  WARNING: No JWT token found in environment variable TEST_JWT_TOKEN" -ForegroundColor Red
    Write-Host "  To get a token, login via the UI and copy from localStorage.authToken" -ForegroundColor Yellow
    Write-Host "  Or run this in browser console: console.log(localStorage.getItem('authToken'))" -ForegroundColor Yellow
    Write-Host "`n  For testing, you can skip authentication (will use user_id=1)" -ForegroundColor Yellow
    $JWT_TOKEN = ""
}

$headers = @{
    "Content-Type" = "application/json"
}

if ($JWT_TOKEN) {
    $headers["Authorization"] = "Bearer $JWT_TOKEN"
    Write-Host "  Success! Using JWT token: $($JWT_TOKEN.Substring(0, 20))..." -ForegroundColor Green
} else {
    Write-Host "  Proceeding without authentication (will default to user_id=1)" -ForegroundColor Yellow
}

# STEP 3: Test /accounts endpoint
Write-Host "`n[3/7] Testing GET /accounts endpoint..." -ForegroundColor Yellow
try {
    $accountsResponse = Invoke-RestMethod -Uri "$API_BASE/accounts" -Method GET -Headers $headers -ErrorAction Stop
    
    if ($accountsResponse.success) {
        $count = $accountsResponse.count
        Write-Host "  Success! Found $count connected account(s):" -ForegroundColor Green
        
        foreach ($account in $accountsResponse.accounts) {
            $icon = if ($account.provider -eq 'gmail') { '📧' } else { '📬' }
            Write-Host "    $icon $($account.provider.ToUpper()): $($account.email)" -ForegroundColor Cyan
        }
        
        if ($count -eq 0) {
            Write-Host "`n  WARNING: No email accounts connected!" -ForegroundColor Red
            Write-Host "  User needs to connect Gmail or Outlook via OAuth flow" -ForegroundColor Yellow
            Write-Host "  Check: Settings > Integrations > Connect Email Account" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ERROR: $($accountsResponse.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Response: $($_.Exception.Response | ConvertTo-Json -Depth 3)" -ForegroundColor Red
}

# STEP 4: Test /emails endpoint
Write-Host "`n[4/7] Testing GET /emails endpoint..." -ForegroundColor Yellow
try {
    $emailsResponse = Invoke-RestMethod -Uri "$API_BASE/emails?account=all&limit=10" -Method GET -Headers $headers -ErrorAction Stop
    
    if ($emailsResponse.success) {
        $count = $emailsResponse.count
        Write-Host "  Success! Loaded $count email(s):" -ForegroundColor Green
        
        if ($count -gt 0) {
            # Show first 5 emails
            $emailsToShow = [Math]::Min(5, $count)
            for ($i = 0; $i -lt $emailsToShow; $i++) {
                $email = $emailsResponse.emails[$i]
                $readStatus = if ($email.is_read) { "📖" } else { "📩" }
                $provider = if ($email.provider -eq 'gmail') { 'Gmail' } else { 'Outlook' }
                Write-Host "    $readStatus [$provider] From: $($email.from)" -ForegroundColor Cyan
                Write-Host "       Subject: $($email.subject.Substring(0, [Math]::Min(60, $email.subject.Length)))..." -ForegroundColor Gray
            }
            
            if ($count -gt 5) {
                Write-Host "    ... and $($count - 5) more emails" -ForegroundColor Gray
            }
        } else {
            Write-Host "  No emails found (inbox may be empty or OAuth not configured)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ERROR: $($emailsResponse.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# STEP 5: Check OAuth credentials in database
Write-Host "`n[5/7] Checking OAuth credentials in database..." -ForegroundColor Yellow
Write-Host "  (This requires direct database access - skipping for now)" -ForegroundColor Gray
Write-Host "  To check manually, run this SQL query:" -ForegroundColor Yellow
Write-Host "    SELECT platform, email, is_active, is_valid FROM ai_infrastructure.oauth_tokens WHERE user_id = 1;" -ForegroundColor Gray

# STEP 6: Test tool registry (Gmail & Outlook tools)
Write-Host "`n[6/7] Checking Gmail & Outlook tool availability..." -ForegroundColor Yellow
try {
    cd "C:\Users\gpoli\GIT\AI_agents"
    $pythonCheck = python -c "from tools.registry_v3 import RegistryV3; registry = RegistryV3(); gmail = [t for t in registry.tools.keys() if 'gmail' in t]; outlook = [t for t in registry.tools.keys() if 'outlook' in t]; print(f'Gmail: {len(gmail)}, Outlook: {len(outlook)}')" 2>&1
    
    if ($pythonCheck -match "Gmail: (\d+), Outlook: (\d+)") {
        $gmailCount = $matches[1]
        $outlookCount = $matches[2]
        Write-Host "  Success! Gmail tools: $gmailCount, Outlook tools: $outlookCount" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Failed to load tool registry" -ForegroundColor Red
        Write-Host "  Output: $pythonCheck" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# STEP 7: Frontend module check (requires browser)
Write-Host "`n[7/7] Frontend module check (requires browser)..." -ForegroundColor Yellow
Write-Host "  Open browser and run this in console:" -ForegroundColor Cyan
Write-Host "    debugCommunicationHub()" -ForegroundColor White
Write-Host "`n  Expected output:" -ForegroundColor Yellow
Write-Host "    ✅ Module registered in window.ModuleRegistry" -ForegroundColor Gray
Write-Host "    ✅ Container exists: #tab-communication" -ForegroundColor Gray
Write-Host "    ✅ Initialized successfully" -ForegroundColor Gray

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

if ($accountsResponse.success -and $accountsResponse.count -gt 0) {
    Write-Host "STATUS: SUCCESS - Communication Hub is connected!" -ForegroundColor Green
    Write-Host "  Connected accounts: $($accountsResponse.count)" -ForegroundColor Green
    Write-Host "  Total emails available: $($emailsResponse.count)" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Open Communication Hub in browser" -ForegroundColor White
    Write-Host "  2. Click the Refresh button" -ForegroundColor White
    Write-Host "  3. Emails should load into the table" -ForegroundColor White
} elseif ($accountsResponse.success -and $accountsResponse.count -eq 0) {
    Write-Host "STATUS: PARTIAL SUCCESS - Backend is working but no accounts connected" -ForegroundColor Yellow
    Write-Host "`nAction required:" -ForegroundColor Cyan
    Write-Host "  1. User needs to connect Gmail or Outlook via OAuth" -ForegroundColor White
    Write-Host "  2. Navigate to: Settings > Integrations" -ForegroundColor White
    Write-Host "  3. Click 'Connect Gmail' or 'Connect Outlook'" -ForegroundColor White
    Write-Host "  4. Complete the OAuth authorization flow" -ForegroundColor White
} else {
    Write-Host "STATUS: FAILED - Backend not responding or errors occurred" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Cyan
    Write-Host "  1. Ensure Flask backend is running: BISTART" -ForegroundColor White
    Write-Host "  2. Check logs for errors: AI_infrastructure/logs/" -ForegroundColor White
    Write-Host "  3. Verify JWT token is valid (user logged in)" -ForegroundColor White
    Write-Host "  4. Check CORS settings in flask_app.py" -ForegroundColor White
}

Write-Host "`n======================================`n" -ForegroundColor Cyan
