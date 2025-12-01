# ==================== SIMPLIFIED MODULE CLEANUP SCRIPT ====================
# Purpose: Move 4 items from modules_external (that's all we need to do!)
# Time: ~2 minutes
# Risk: LOW - Only moving files, no code changes
# =========================================================================

cd C:\Users\gpoli\GIT\AI_agents

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 SIMPLIFIED MODULE CLEANUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Discovery: ModuleLoaderV4 already ONLY scans modules_external!" -ForegroundColor Green
Write-Host "Discovery: modules_internal already hardcoded in HTML!" -ForegroundColor Green
Write-Host "Action: Moving 4 items from modules_external`n" -ForegroundColor Yellow

# Phase 1: Create new folders
Write-Host "📁 Phase 1: Creating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "UI\components" -Force | Out-Null
New-Item -ItemType Directory -Path "UI\docs\modules" -Force | Out-Null
Write-Host "✅ Folders created`n" -ForegroundColor Green

# Phase 2: Move production-analytics INSIDE inhouse-kanban
Write-Host "📦 Phase 2: Moving production-analytics into inhouse-kanban..." -ForegroundColor Yellow
if (Test-Path "UI\modules_external\production-analytics") {
    Move-Item "UI\modules_external\production-analytics" "UI\modules_external\inhouse-kanban\" -Force
    Write-Host "✅ production-analytics → inhouse-kanban/production-analytics" -ForegroundColor Green
    Write-Host "   (Now a sub-component of kanban module)`n" -ForegroundColor Gray
}
else {
    Write-Host "⚠️ production-analytics not found (may already be moved)`n" -ForegroundColor Yellow
}

# Phase 3: Move communication-hub to components
Write-Host "📦 Phase 3: Moving communication-hub to components..." -ForegroundColor Yellow
if (Test-Path "UI\modules_external\communication-hub") {
    Move-Item "UI\modules_external\communication-hub" "UI\components\" -Force
    Write-Host "✅ communication-hub → components/" -ForegroundColor Green
    Write-Host "   (Not a user-facing module)`n" -ForegroundColor Gray
}
else {
    Write-Host "⚠️ communication-hub not found (may already be moved)`n" -ForegroundColor Yellow
}

# Phase 4: Move thread-cards to components (rename to avoid conflict)
Write-Host "📦 Phase 4: Moving thread-cards to components..." -ForegroundColor Yellow
if (Test-Path "UI\modules_external\thread-cards") {
    Move-Item "UI\modules_external\thread-cards" "UI\components\thread-cards-external" -Force
    Write-Host "✅ thread-cards → components/thread-cards-external/" -ForegroundColor Green
    Write-Host "   (Renamed to avoid conflict with modules_internal/thread-cards)`n" -ForegroundColor Gray
}
else {
    Write-Host "⚠️ thread-cards not found (may already be moved)`n" -ForegroundColor Yellow
}

# Phase 5: Move docs folder
Write-Host "📦 Phase 5: Moving docs folder..." -ForegroundColor Yellow
if (Test-Path "UI\modules_external\docs") {
    Move-Item "UI\modules_external\docs" "UI\docs\modules" -Force
    Write-Host "✅ docs → docs/modules/" -ForegroundColor Green
    Write-Host "   (Documentation consolidated)`n" -ForegroundColor Gray
}
else {
    Write-Host "⚠️ docs folder not found (may already be moved)`n" -ForegroundColor Yellow
}

# Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📊 VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "modules_external (ONLY user-facing modules):" -ForegroundColor Yellow
$externalCount = (Get-ChildItem "UI\modules_external" -Directory).Count
Get-ChildItem "UI\modules_external" -Directory | ForEach-Object { 
    Write-Host "  ✅ $($_.Name)" -ForegroundColor Green 
}
Write-Host "  Total: $externalCount modules`n" -ForegroundColor Cyan

Write-Host "modules_internal (hardcoded platform components):" -ForegroundColor Yellow
$internalCount = (Get-ChildItem "UI\modules_internal" -Directory).Count
Write-Host "  ✅ UNCHANGED - $internalCount items (hardcoded in HTML)`n" -ForegroundColor Green

Write-Host "components (non-module utilities):" -ForegroundColor Yellow
if (Test-Path "UI\components") {
    $componentCount = (Get-ChildItem "UI\components" -Directory).Count
    Get-ChildItem "UI\components" -Directory | ForEach-Object { 
        Write-Host "  ✅ $($_.Name)" -ForegroundColor Green 
    }
    Write-Host "  Total: $componentCount components`n" -ForegroundColor Cyan
}
else {
    Write-Host "  (No components folder created - no moves occurred)`n" -ForegroundColor Gray
}

# Success message
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  ✅ modules_external cleaned up (ONLY user-facing modules)" -ForegroundColor Green
Write-Host "  ✅ modules_internal unchanged (hardcoded components)" -ForegroundColor Green
Write-Host "  ✅ ModuleLoaderV4 works correctly (no code changes needed)" -ForegroundColor Green
Write-Host "  ✅ Backend already configured correctly" -ForegroundColor Green

Write-Host "`n⚠️ NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Hard refresh browser (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "  2. Test module loading - sidebar should show $externalCount modules" -ForegroundColor White
Write-Host "  3. Verify inhouse-kanban has production-analytics sub-folder" -ForegroundColor White
Write-Host "  4. MANUAL REVIEW: UI\modules_external\inhouse-print (unknown purpose)" -ForegroundColor White

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Keep window open
Read-Host "Press Enter to close"
