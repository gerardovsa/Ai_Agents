# Fix UI File Paths - November 30, 2025
# Fixes all 404 errors in business-ai-platform-v2.html by updating paths
# to match the November 29 shared resources reorganization

$htmlFile = "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"

Write-Host "`n=====================================================`n" -ForegroundColor Cyan
Write-Host "  UI PATH FIX SCRIPT - November 30, 2025" -ForegroundColor Cyan  
Write-Host "`n=====================================================`n" -ForegroundColor Cyan

Write-Host "[1/4] Reading HTML file..." -ForegroundColor Yellow
$content = Get-Content $htmlFile -Raw -Encoding UTF8

Write-Host "[2/4] Fixing paths..." -ForegroundColor Yellow

# Track changes
$changes = @()

# Fix pattern: modules/thread-cards/ -> modules_internal/thread-cards/
$count = ([regex]::Matches($content, 'modules/thread-cards/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/thread-cards/', 'modules_internal/thread-cards/'
    $changes += "  - Fixed $count references: modules/thread-cards/ -> modules_internal/thread-cards/"
}

# Fix pattern: modules/thread-manager/ -> modules_internal/thread-manager/
$count = ([regex]::Matches($content, 'modules/thread-manager/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/thread-manager/', 'modules_internal/thread-manager/'
    $changes += "  - Fixed $count references: modules/thread-manager/ -> modules_internal/thread-manager/"
}

# Fix pattern: modules/synergy/ -> modules_internal/synergy/
$count = ([regex]::Matches($content, 'modules/synergy/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/synergy/', 'modules_internal/synergy/'
    $changes += "  - Fixed $count references: modules/synergy/ -> modules_internal/synergy/"
}

# Fix pattern: modules/workflow/ -> modules_internal/workflow/
$count = ([regex]::Matches($content, 'modules/workflow/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/workflow/', 'modules_internal/workflow/'
    $changes += "  - Fixed $count references: modules/workflow/ -> modules_internal/workflow/"
}

# Fix pattern: modules/internal_docs/ -> modules_internal/internal_docs/
$count = ([regex]::Matches($content, 'modules/internal_docs/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/internal_docs/', 'modules_internal/internal_docs/'
    $changes += "  - Fixed $count references: modules/internal_docs/ -> modules_internal/internal_docs/"
}

# Fix pattern: modules/components/ -> modules_internal/components/
$count = ([regex]::Matches($content, 'modules/components/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/components/', 'modules_internal/components/'
    $changes += "  - Fixed $count references: modules/components/ -> modules_internal/components/"
}

# Fix pattern: modules/agents/ -> modules_internal/agents/
$count = ([regex]::Matches($content, 'modules/agents/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/agents/', 'modules_internal/agents/'
    $changes += "  - Fixed $count references: modules/agents/ -> modules_internal/agents/"
}

# Fix pattern: modules/shared/ -> shared/shared/
$count = ([regex]::Matches($content, 'modules/shared/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/shared/', 'shared/shared/'
    $changes += "  - Fixed $count references: modules/shared/ -> shared/shared/"
}

# Fix pattern: modules/woocommerce/ -> modules_external/woocommerce/
$count = ([regex]::Matches($content, 'modules/woocommerce/')).Count
if ($count -gt 0) {
    $content = $content -replace 'modules/woocommerce/', 'modules_external/woocommerce/'
    $changes += "  - Fixed $count references: modules/woocommerce/ -> modules_external/woocommerce/"
}

# Fix pattern: external/modules/ -> modules_external/ (for workflow-slug-integration)
$count = ([regex]::Matches($content, 'external/modules/')).Count
if ($count -gt 0) {
    $content = $content -replace 'external/modules/', 'modules_external/'
    $changes += "  - Fixed $count references: external/modules/ -> modules_external/"
}

# Fix pattern: modules/agent-status-indicator.js -> shared/js/agent-status-indicator.js
$content = $content -replace 'modules/agent-status-indicator\.js', 'shared/js/agent-status-indicator.js'
$changes += "  - Fixed: modules/agent-status-indicator.js -> shared/js/agent-status-indicator.js"

Write-Host "[3/4] Writing updated HTML..." -ForegroundColor Yellow
$content | Set-Content $htmlFile -Encoding UTF8 -NoNewline

Write-Host "[4/4] Verification..." -ForegroundColor Yellow
Write-Host ""
Write-Host "CHANGES APPLIED:" -ForegroundColor Green
foreach ($change in $changes) {
    Write-Host $change -ForegroundColor White
}

Write-Host "`n=====================================================`n" -ForegroundColor Cyan
Write-Host "  FIX COMPLETE - Restart BISTART to test" -ForegroundColor Green
Write-Host "`n=====================================================`n" -ForegroundColor Cyan

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Stop BISTART (Ctrl+C)" -ForegroundColor White
Write-Host "2. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White  
Write-Host "3. Run BISTART again" -ForegroundColor White
Write-Host "4. Check console for remaining 404 errors`n" -ForegroundColor White
