# Microsoft 365 Login Setup Script
# Guides you through configuration

Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "🔷 MICROSOFT 365 LOGIN SETUP" -ForegroundColor White
Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# Check if .env.master exists
$envFile = "C:\Users\gpoli\GIT\AI_agents\.env.master"

if (!(Test-Path $envFile)) {
    Write-Host "❌ .env.master file not found at:" -ForegroundColor Red
    Write-Host "   $envFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found .env.master file" -ForegroundColor Green
Write-Host ""

# Check current Microsoft credentials
Write-Host "📋 Checking current configuration..." -ForegroundColor Cyan
Write-Host ""

$envContent = Get-Content $envFile -Raw

$hasClientId = $envContent -match "MICROSOFT_CLIENT_ID="
$hasClientSecret = $envContent -match "MICROSOFT_CLIENT_SECRET="
$hasTenantId = $envContent -match "MICROSOFT_TENANT_ID="

if ($hasClientId) {
    Write-Host "✅ MICROSOFT_CLIENT_ID is set" -ForegroundColor Green
} else {
    Write-Host "❌ MICROSOFT_CLIENT_ID is NOT set" -ForegroundColor Red
}

if ($hasClientSecret) {
    Write-Host "✅ MICROSOFT_CLIENT_SECRET is set" -ForegroundColor Green
} else {
    Write-Host "❌ MICROSOFT_CLIENT_SECRET is NOT set" -ForegroundColor Red
}

if ($hasTenantId) {
    Write-Host "✅ MICROSOFT_TENANT_ID is set" -ForegroundColor Green
} else {
    Write-Host "⚠️  MICROSOFT_TENANT_ID is NOT set (will use 'common')" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# If not configured, guide user through setup
if (!$hasClientId -or !$hasClientSecret) {
    Write-Host "⚙️  AZURE AD SETUP REQUIRED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable Microsoft 365 login, you need to:" -ForegroundColor White
    Write-Host ""
    Write-Host "1️⃣  Create an Azure AD Application" -ForegroundColor Cyan
    Write-Host "   • Go to: https://portal.azure.com" -ForegroundColor Gray
    Write-Host "   • Navigate: Azure Active Directory → App registrations → New registration" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2️⃣  Configure Application" -ForegroundColor Cyan
    Write-Host "   • Name: Valor AI Platform" -ForegroundColor Gray
    Write-Host "   • Account types: Multi-tenant + Personal Microsoft accounts" -ForegroundColor Gray
    Write-Host "   • Redirect URI (Web): http://localhost:5001/api/auth/microsoft/callback" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3️⃣  Get Credentials" -ForegroundColor Cyan
    Write-Host "   • Copy Application (client) ID" -ForegroundColor Gray
    Write-Host "   • Create Client Secret (Certificates & secrets)" -ForegroundColor Gray
    Write-Host "   • Copy secret value (save immediately!)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4️⃣  API Permissions" -ForegroundColor Cyan
    Write-Host "   • Add: openid, profile, email, User.Read" -ForegroundColor Gray
    Write-Host "   • Optional: Mail.Read, Mail.Send, Calendars.Read, Files.ReadWrite" -ForegroundColor Gray
    Write-Host "   • Grant admin consent" -ForegroundColor Gray
    Write-Host ""
    Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
    
    # Prompt for credentials
    Write-Host "Would you like to add Microsoft credentials now?" -ForegroundColor Yellow
    $response = Read-Host "Enter [Y]es to continue, [N]o to skip"
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host ""
        Write-Host "📝 Enter your Azure AD credentials:" -ForegroundColor Cyan
        Write-Host ""
        
        $clientId = Read-Host "Application (client) ID"
        $clientSecret = Read-Host "Client secret value" -AsSecureString
        $clientSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret))
        
        Write-Host ""
        Write-Host "Tenant ID (press Enter for 'common' - allows personal + work accounts)" -ForegroundColor Gray
        $tenantId = Read-Host "Tenant ID [common]"
        if ([string]::IsNullOrWhiteSpace($tenantId)) {
            $tenantId = "common"
        }
        
        # Add to .env.master
        Write-Host ""
        Write-Host "💾 Adding credentials to .env.master..." -ForegroundColor Cyan
        
        $newConfig = @"

# ==================== MICROSOFT 365 OAUTH ====================
MICROSOFT_CLIENT_ID=$clientId
MICROSOFT_CLIENT_SECRET=$clientSecretPlain
MICROSOFT_TENANT_ID=$tenantId
"@
        
        Add-Content -Path $envFile -Value $newConfig
        
        Write-Host "✅ Credentials added successfully!" -ForegroundColor Green
        Write-Host ""
        
    } else {
        Write-Host ""
        Write-Host "⚠️  Skipped credential setup" -ForegroundColor Yellow
        Write-Host "   You can manually add to .env.master:" -ForegroundColor Gray
        Write-Host ""
        Write-Host "   MICROSOFT_CLIENT_ID=your_app_id" -ForegroundColor Gray
        Write-Host "   MICROSOFT_CLIENT_SECRET=your_secret" -ForegroundColor Gray
        Write-Host "   MICROSOFT_TENANT_ID=common" -ForegroundColor Gray
        Write-Host ""
    }
}

Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Restart the server:" -ForegroundColor White
Write-Host "   cd C:\Users\gpoli\GIT\AI_agents" -ForegroundColor Gray
Write-Host "   BISTART" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Open the platform:" -ForegroundColor White
Write-Host "   http://localhost:5001" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Click the Microsoft login button:" -ForegroundColor White
Write-Host "   'Sign in with Microsoft 365'" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Test with your Microsoft account" -ForegroundColor White
Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 For detailed instructions, see:" -ForegroundColor Cyan
Write-Host "   C:\Users\gpoli\GIT\AI_agents\MICROSOFT_365_LOGIN_SETUP_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Setup script complete!" -ForegroundColor Green
Write-Host ""
