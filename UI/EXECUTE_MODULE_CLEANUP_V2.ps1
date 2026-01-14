# Module Cleanup Script - Simplified Version
# Moves 4 misplaced items from modules_external

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MODULE FOLDER CLEANUP - EXECUTING" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$baseDir = "C:\Users\gpoli\GIT\AI_agents\UI"

# Phase 1: Create target folders
Write-Host "[1/5] Creating target folders..." -ForegroundColor Cyan

$folders = @(
    "$baseDir\components",
    "$baseDir\components\thread-cards-external",
    "$baseDir\docs\modules"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "  Exists: $folder" -ForegroundColor Yellow
    }
}

Write-Host ""

# Phase 2: Move production-analytics into inhouse-kanban
Write-Host "[2/5] Moving production-analytics..." -ForegroundColor Cyan

$source = "$baseDir\modules_external\production-analytics"
$dest = "$baseDir\modules_external\inhouse-kanban\production-analytics"

if (Test-Path $source) {
    if (Test-Path $dest) {
        Write-Host "  WARNING: Destination exists, removing old version..." -ForegroundColor Yellow
        Remove-Item $dest -Recurse -Force
    }
    Move-Item $source $dest -Force
    Write-Host "  SUCCESS: Moved to inhouse-kanban/production-analytics" -ForegroundColor Green
} else {
    Write-Host "  SKIP: production-analytics not found" -ForegroundColor Yellow
}

Write-Host ""

# Phase 3: Move communication-hub to components
Write-Host "[3/5] Moving communication-hub..." -ForegroundColor Cyan

$source = "$baseDir\modules_external\communication-hub"
$dest = "$baseDir\components\communication-hub"

if (Test-Path $source) {
    if (Test-Path $dest) {
        Write-Host "  WARNING: Destination exists, removing old version..." -ForegroundColor Yellow
        Remove-Item $dest -Recurse -Force
    }
    Move-Item $source $dest -Force
    Write-Host "  SUCCESS: Moved to components/communication-hub" -ForegroundColor Green
} else {
    Write-Host "  SKIP: communication-hub not found" -ForegroundColor Yellow
}

Write-Host ""

# Phase 4: Move thread-cards to components
Write-Host "[4/5] Moving thread-cards..." -ForegroundColor Cyan

$source = "$baseDir\modules_external\thread-cards"
$dest = "$baseDir\components\thread-cards-external"

if (Test-Path $source) {
    if (Test-Path $dest) {
        Write-Host "  WARNING: Destination exists, removing old version..." -ForegroundColor Yellow
        Remove-Item $dest -Recurse -Force
    }
    Move-Item $source $dest -Force
    Write-Host "  SUCCESS: Moved to components/thread-cards-external" -ForegroundColor Green
} else {
    Write-Host "  SKIP: thread-cards not found" -ForegroundColor Yellow
}

Write-Host ""

# Phase 5: Move docs to docs/modules
Write-Host "[5/5] Moving docs..." -ForegroundColor Cyan

$source = "$baseDir\modules_external\docs"
$dest = "$baseDir\docs\modules"

if (Test-Path $source) {
    if (Test-Path $dest) {
        Write-Host "  WARNING: Destination exists, removing old version..." -ForegroundColor Yellow
        Remove-Item $dest -Recurse -Force
    }
    Move-Item $source $dest -Force
    Write-Host "  SUCCESS: Moved to docs/modules" -ForegroundColor Green
} else {
    Write-Host "  SKIP: docs not found" -ForegroundColor Yellow
}

Write-Host ""

# Verification
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$externalCount = (Get-ChildItem "$baseDir\modules_external" -Directory).Count
$internalCount = (Get-ChildItem "$baseDir\modules_internal" -Directory).Count
$componentsCount = (Get-ChildItem "$baseDir\components" -Directory -ErrorAction SilentlyContinue).Count

Write-Host "Results:" -ForegroundColor Green
Write-Host "  modules_external: $externalCount folders (should be 13)" -ForegroundColor White
Write-Host "  modules_internal: $internalCount folders (should be 18)" -ForegroundColor White
Write-Host "  components: $componentsCount folders (should be 2+)" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Hard refresh browser (CTRL+SHIFT+R)" -ForegroundColor White
Write-Host "  2. Test module loading - sidebar should show 13 modules" -ForegroundColor White
Write-Host "  3. Verify inhouse-kanban has production-analytics subfolder" -ForegroundColor White
Write-Host "  4. MANUAL REVIEW: UI\modules_external\inhouse-print (unknown purpose)" -ForegroundColor White

Write-Host "`n========================================`n" -ForegroundColor Cyan

Write-Host "Press Enter to close..." -ForegroundColor Yellow
$null = Read-Host
