# ========================================================
# UPDATE BISTART FUNCTION - REMOVE PORT 4000 REFERENCES
# ========================================================
# This script updates the BISTART function in your PowerShell profile
# to use port 5001 instead of 4000

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  UPDATING BISTART TO PORT 5001" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$profilePath = $PROFILE

# Check if profile exists
if (-not (Test-Path $profilePath)) {
    Write-Host "[ERROR] Profile not found at: $profilePath" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Reading current profile..." -ForegroundColor Green
$content = Get-Content $profilePath -Raw

# Check if BISTART exists
if ($content -notmatch 'function BISTART') {
    Write-Host "[ERROR] BISTART function not found in profile" -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] Updating port references from 4000 to 5001..." -ForegroundColor Green

# Replace all occurrences of port 4000 with 5001
$updatedContent = $content -replace 'port 4000', 'port 5001'
$updatedContent = $updatedContent -replace 'LocalPort 4000', 'LocalPort 5001'
$updatedContent = $updatedContent -replace 'http://localhost:4000', 'http://localhost:5001'

# Count how many replacements were made
$count4000Before = ([regex]::Matches($content, '4000')).Count
$count4000After = ([regex]::Matches($updatedContent, '4000')).Count
$replacementCount = $count4000Before - $count4000After

Write-Host "      Replaced $replacementCount references to port 4000" -ForegroundColor Yellow

# Backup original profile
$backupPath = "$profilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "[3/3] Creating backup and saving..." -ForegroundColor Green
Copy-Item $profilePath $backupPath
Write-Host "      Backup saved to: $backupPath" -ForegroundColor Gray

# Save updated profile
Set-Content $profilePath $updatedContent -Encoding UTF8

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Replacements made: $replacementCount" -ForegroundColor Yellow
Write-Host "  Backup created: $backupPath" -ForegroundColor Gray
Write-Host ""
Write-Host "  NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Close this PowerShell window" -ForegroundColor Gray
Write-Host "  2. Open a NEW PowerShell window" -ForegroundColor Gray
Write-Host "  3. Run: BISTART" -ForegroundColor Gray
Write-Host "  4. You should now see port 5001 (not 4000)" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
