# ============================================================================
# Apply prime-loaded Location Fix to Supabase Database
# ============================================================================
# This script executes the SQL fix to add 'prime-loaded' to the location
# CHECK constraint in the sessions.threads table.
#
# Date: November 24, 2025
# Issue: Database constraint rejecting 'prime-loaded' location
# ============================================================================

Write-Host "`n=== PRIME-LOADED LOCATION FIX ===" -ForegroundColor Cyan
Write-Host "This will add 'prime-loaded' to the location CHECK constraint`n" -ForegroundColor Yellow

# Check if PostgreSQL CLI is available
$psqlAvailable = Get-Command psql -ErrorAction SilentlyContinue

if ($psqlAvailable) {
    Write-Host "✅ PostgreSQL CLI (psql) found" -ForegroundColor Green
    Write-Host "`nExecuting SQL fix..." -ForegroundColor Yellow
    
    # Run the SQL file
    psql -h aws-0-us-east-1.pooler.supabase.com -U postgres.yqyrbvamrzpggpvqhpik -d postgres -f "FIX_PRIME_LOADED_CONSTRAINT.sql"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ FIX APPLIED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "`nNext steps:" -ForegroundColor Cyan
        Write-Host "  1. Refresh your browser (Ctrl+F5)" -ForegroundColor White
        Write-Host "  2. Try dropping a thread on Prime again" -ForegroundColor White
        Write-Host "  3. Thread should now load successfully!`n" -ForegroundColor White
    }
    else {
        Write-Host "`n❌ FIX FAILED - See error above" -ForegroundColor Red
    }
}
else {
    Write-Host "⚠️  PostgreSQL CLI (psql) not found" -ForegroundColor Yellow
    Write-Host "`nMANUAL STEPS REQUIRED:" -ForegroundColor Cyan
    Write-Host "1. Go to Supabase Dashboard: https://supabase.com/dashboard" -ForegroundColor White
    Write-Host "2. Select your project" -ForegroundColor White
    Write-Host "3. Click 'SQL Editor' in left sidebar" -ForegroundColor White
    Write-Host "4. Click 'New Query'" -ForegroundColor White
    Write-Host "5. Copy contents of: FIX_PRIME_LOADED_CONSTRAINT.sql" -ForegroundColor White
    Write-Host "6. Paste into SQL Editor" -ForegroundColor White
    Write-Host "7. Click 'Run' (or Ctrl+Enter)" -ForegroundColor White
    Write-Host "8. Verify success message appears`n" -ForegroundColor White
    
    Write-Host "Opening SQL file for you..." -ForegroundColor Yellow
    Start-Process "FIX_PRIME_LOADED_CONSTRAINT.sql"
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
