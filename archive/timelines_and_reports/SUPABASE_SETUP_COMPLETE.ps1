# SUPABASE SETUP AND MIGRATION - Complete Automation
# Run this after creating your Supabase project

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SUPABASE MIGRATION SETUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Install required Python packages
Write-Host "[1/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install psycopg2-binary supabase-py python-dotenv --quiet

# Step 2: Collect Supabase credentials
Write-Host "`n[2/6] Enter your Supabase credentials" -ForegroundColor Yellow
Write-Host "(Get these from: https://supabase.com/dashboard → Project Settings)`n" -ForegroundColor Gray

$SUPABASE_URL = Read-Host "Supabase Project URL (https://xxxxx.supabase.co)"
$SUPABASE_ANON_KEY = Read-Host "Supabase Anon Key (eyJhbGc...)"
$SUPABASE_SERVICE_KEY = Read-Host "Supabase Service Role Key (eyJhbGc...)"
$DB_PASSWORD = Read-Host "Database Password (from project creation)" -AsSecureString
$DB_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD))

# Extract project ID from URL
$PROJECT_ID = ($SUPABASE_URL -replace 'https://', '') -replace '.supabase.co', ''

# Build connection string
$SUPABASE_DB_URL = "postgresql://postgres:$DB_PASSWORD_PLAIN@db.$PROJECT_ID.supabase.co:5432/postgres"

Write-Host "`n[3/6] Saving credentials to .env file..." -ForegroundColor Yellow

# Create/update .env file
$envContent = @"
# Supabase Configuration (Added: $(Get-Date -Format 'yyyy-MM-dd HH:mm'))
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY
SUPABASE_DB_URL=$SUPABASE_DB_URL
USE_SUPABASE=true

# Legacy SQLite (backup)
USE_SQLITE=false
"@

Add-Content -Path ".env" -Value "`n$envContent"
Write-Host "  Credentials saved to .env file" -ForegroundColor Green

# Step 4: Test connection
Write-Host "`n[4/6] Testing Supabase connection..." -ForegroundColor Yellow
python Supabase/test_supabase_connection.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  Connection test failed. Check your credentials." -ForegroundColor Red
    exit 1
}

# Step 5: Run migration
Write-Host "`n[5/6] Starting database migration..." -ForegroundColor Yellow
Write-Host "  This will migrate all data from SQLite to PostgreSQL" -ForegroundColor Gray
Write-Host "  Estimated time: 5-15 minutes (depending on data size)`n" -ForegroundColor Gray

$confirmation = Read-Host "Ready to migrate? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "`nMigration cancelled. Run this script again when ready." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nMigrating databases..." -ForegroundColor Cyan
python Supabase/migrate_to_supabase.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  Migration failed. Check errors above." -ForegroundColor Red
    exit 1
}

# Step 6: Update Render environment variables
Write-Host "`n[6/6] Updating Render environment variables..." -ForegroundColor Yellow
Write-Host "  Manual step required:`n" -ForegroundColor Gray
Write-Host "  1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0" -ForegroundColor White
Write-Host "  2. Click 'Environment' tab" -ForegroundColor White
Write-Host "  3. Add these variables:" -ForegroundColor White
Write-Host "`n     SUPABASE_URL=$SUPABASE_URL" -ForegroundColor Cyan
Write-Host "     SUPABASE_KEY=$SUPABASE_ANON_KEY" -ForegroundColor Cyan
Write-Host "     SUPABASE_DB_URL=$SUPABASE_DB_URL" -ForegroundColor Cyan
Write-Host "     USE_SUPABASE=true`n" -ForegroundColor Cyan
Write-Host "  4. Click 'Save Changes'" -ForegroundColor White
Write-Host "  5. Service will auto-deploy with new config`n" -ForegroundColor White

Write-Host "========================================" -ForegroundColor Green
Write-Host "MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update Render environment variables (see above)" -ForegroundColor White
Write-Host "  2. Wait for Render to redeploy (2-3 minutes)" -ForegroundColor White
Write-Host "  3. Test your app at: https://ai-agents-backend-singapore.onrender.com" -ForegroundColor White
Write-Host "  4. Keep SQLite backups in data/ folder (just in case)`n" -ForegroundColor White

Write-Host "Database info:" -ForegroundColor Yellow
Write-Host "  Supabase Dashboard: $SUPABASE_URL" -ForegroundColor White
Write-Host "  Free tier: 8GB storage, 500MB database, 2GB bandwidth/day" -ForegroundColor White
Write-Host "  Automatic backups: Daily (retained 7 days)`n" -ForegroundColor White
