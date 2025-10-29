# Phase 2 Cleanup - Complete Execution Script
# Run this to execute all cleanup steps at once

$ErrorActionPreference = "Continue"

Write-Host "🚀 Starting Phase 2 Cleanup..." -ForegroundColor Green
Write-Host "This will take approximately 10 minutes" -ForegroundColor Yellow
Write-Host ""

# Step 1: Create archive structure
Write-Host "Step 1/14: Creating archive structure..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "docs\archive\authentication" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\google_workspace" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\microsoft_365" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\implementations" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\kanban" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\summaries" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\ui" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\archive\scripts" -Force | Out-Null
Write-Host "   ✅ Archive folders created" -ForegroundColor Green

# Step 2-8: Archive documentation (combined for speed)
Write-Host "Steps 2-8: Archiving documentation files..." -ForegroundColor Cyan

# Authentication
$authCount = 0
$authCount += (Get-ChildItem -Path . -Filter "ACCOUNT_LINKING_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
$authCount += (Get-ChildItem -Path . -Filter "AUTHENTICATION_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
$authCount += (Get-ChildItem -Path . -Filter "OAUTH_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
$authCount += (Get-ChildItem -Path . -Filter "LOGIN_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
$authCount += (Get-ChildItem -Path . -Filter "USER_AUTH_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
$authCount += (Get-ChildItem -Path . -Filter "HYBRID_AUTH_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\authentication\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Authentication: $authCount files" -ForegroundColor Yellow

# Google Workspace
$googleCount = 0
$googleCount += (Get-ChildItem -Path . -Filter "GOOGLE_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\google_workspace\" -Force; $_ } | Measure-Object).Count
$googleCount += (Get-ChildItem -Path . -Filter "GMAIL_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\google_workspace\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Google Workspace: $googleCount files" -ForegroundColor Yellow

# Microsoft 365
$msCount = (Get-ChildItem -Path . -Filter "MICROSOFT_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\microsoft_365\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Microsoft 365: $msCount files" -ForegroundColor Yellow

# Implementations
$implCount = 0
$implCount += (Get-ChildItem -Path . -Filter "*_IMPLEMENTATION_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force; $_ } | Measure-Object).Count
$implCount += (Get-ChildItem -Path . -Filter "*_INTEGRATION_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force; $_ } | Measure-Object).Count
$implCount += (Get-ChildItem -Path . -Filter "SMTP_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force; $_ } | Measure-Object).Count
$implCount += (Get-ChildItem -Path . -Filter "WOOCOMMERCE_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force; $_ } | Measure-Object).Count
$implCount += (Get-ChildItem -Path . -Filter "TOOL_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\implementations\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Implementations: $implCount files" -ForegroundColor Yellow

# Kanban
$kanbanCount = 0
$kanbanCount += (Get-ChildItem -Path . -Filter "KANBAN_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\kanban\" -Force; $_ } | Measure-Object).Count
$kanbanCount += (Get-ChildItem -Path . -Filter "SESSION_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\kanban\" -Force; $_ } | Measure-Object).Count
$kanbanCount += (Get-ChildItem -Path . -Filter "SYNERGY_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\kanban\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Kanban: $kanbanCount files" -ForegroundColor Yellow

# Summaries
$summaryCount = 0
$summaryCount += (Get-ChildItem -Path . -Filter "*_SUMMARY*.md" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch "CLEANUP_PHASE1_COMPLETE|PHASE2_EXECUTION_PLAN" } | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$summaryCount += (Get-ChildItem -Path . -Filter "*_COMPLETE*.md" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch "CLEANUP_PHASE1_COMPLETE" } | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$summaryCount += (Get-ChildItem -Path . -Filter "*_STATUS*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$summaryCount += (Get-ChildItem -Path . -Filter "CHANGES_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Summaries: $summaryCount files" -ForegroundColor Yellow

# Guides & Architecture
$guideCount = 0
$guideCount += (Get-ChildItem -Path . -Filter "*_GUIDE*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "*_STRATEGY*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "*_ARCHITECTURE*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "*_BLUEPRINT*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "DEPLOYMENT_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "WHEN_TO_USE_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "PLATFORM_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
$guideCount += (Get-ChildItem -Path . -Filter "SYSTEM_*.md" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\summaries\" -Force; $_ } | Measure-Object).Count
Write-Host "   📦 Guides: $guideCount files" -ForegroundColor Yellow

Write-Host "   ✅ Documentation archived" -ForegroundColor Green

# Step 9: Consolidate tests
Write-Host "Step 9: Consolidating test files..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "AI_infrastructure\tests" -Force | Out-Null

$testCount = 0
$testCount += (Get-ChildItem -Path . -Filter "test_*.py" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "AI_infrastructure\tests\" -Force; $_ } | Measure-Object).Count
$testCount += (Get-ChildItem -Path . -Filter "check_*.py" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "AI_infrastructure\tests\" -Force; $_ } | Measure-Object).Count

$uiTestCount = 0
$uiTestCount += (Get-ChildItem -Path "UI" -Filter "test-*.html" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\ui\" -Force; $_ } | Measure-Object).Count
$uiTestCount += (Get-ChildItem -Path "UI" -Filter "*-test.html" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\ui\" -Force; $_ } | Measure-Object).Count
$uiTestCount += (Get-ChildItem -Path "UI" -Filter "integration-test.html" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\ui\" -Force; $_ } | Measure-Object).Count
$uiTestCount += (Get-ChildItem -Path "UI" -Filter "credential-tester.html" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\ui\" -Force; $_ } | Measure-Object).Count
$uiTestCount += (Get-ChildItem -Path "UI" -Filter "grid-test.html" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\ui\" -Force; $_ } | Measure-Object).Count

Write-Host "   🧪 Python tests: $testCount files" -ForegroundColor Yellow
Write-Host "   🧪 UI tests: $uiTestCount files" -ForegroundColor Yellow
Write-Host "   ✅ Tests consolidated" -ForegroundColor Green

# Step 10: Remove superseded scripts
Write-Host "Step 10: Removing superseded scripts..." -ForegroundColor Cyan
$supersededScripts = @(
    "BISTART_DIRECT_UPDATE.ps1",
    "BISTART_MANUAL_UPDATE.ps1",
    "BISTART_NEW_VERSION.txt",
    "BISTART_UPDATED_FUNCTION.ps1",
    "SIMPLE_BISTART_UPDATE.ps1",
    "UPDATE_BISTART.ps1",
    "UPDATE_NOW.ps1"
)

$removedCount = 0
foreach ($script in $supersededScripts) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force
        $removedCount++
        Write-Host "   🗑️  Removed: $script" -ForegroundColor Red
    }
}
Write-Host "   ✅ $removedCount superseded scripts removed" -ForegroundColor Green

# Step 11: Archive one-time scripts
Write-Host "Step 11: Archiving one-time scripts..." -ForegroundColor Cyan

$scriptCount = 0
$scriptCount += (Get-ChildItem -Path . -Filter "setup_*.py" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\scripts\" -Force; $_ } | Measure-Object).Count
$scriptCount += (Get-ChildItem -Path . -Filter "setup_*.ps1" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\scripts\" -Force; $_ } | Measure-Object).Count
$scriptCount += (Get-ChildItem -Path . -Filter "create_*.py" -ErrorAction SilentlyContinue | ForEach-Object { Move-Item -Path $_.FullName -Destination "docs\archive\scripts\" -Force; $_ } | Measure-Object).Count

if (Test-Path "table_structure_analysis.py") {
    Move-Item -Path "table_structure_analysis.py" -Destination "docs\archive\scripts\" -Force
    $scriptCount++
}

Write-Host "   📦 Scripts: $scriptCount files" -ForegroundColor Yellow
Write-Host "   ✅ One-time scripts archived" -ForegroundColor Green

# Step 12: Remove old backups
Write-Host "Step 12: Removing old backup directories..." -ForegroundColor Cyan
$backupCount = 0
Get-ChildItem -Path . -Filter "AI_infrastructure_BACKUP_*" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
    Write-Host "   🗑️  Removed backup: $($_.Name)" -ForegroundColor Red
    $backupCount++
}
Write-Host "   ✅ $backupCount backup directories removed" -ForegroundColor Green

# Step 13: Create archive index
Write-Host "Step 13: Creating archive index..." -ForegroundColor Cyan

$authFilesCount = (Get-ChildItem "docs\archive\authentication" -ErrorAction SilentlyContinue | Measure-Object).Count
$googleFilesCount = (Get-ChildItem "docs\archive\google_workspace" -ErrorAction SilentlyContinue | Measure-Object).Count
$msFilesCount = (Get-ChildItem "docs\archive\microsoft_365" -ErrorAction SilentlyContinue | Measure-Object).Count
$implFilesCount = (Get-ChildItem "docs\archive\implementations" -ErrorAction SilentlyContinue | Measure-Object).Count
$kanbanFilesCount = (Get-ChildItem "docs\archive\kanban" -ErrorAction SilentlyContinue | Measure-Object).Count
$summaryFilesCount = (Get-ChildItem "docs\archive\summaries" -ErrorAction SilentlyContinue | Measure-Object).Count
$uiFilesCount = (Get-ChildItem "docs\archive\ui" -ErrorAction SilentlyContinue | Measure-Object).Count
$scriptFilesCount = (Get-ChildItem "docs\archive\scripts" -ErrorAction SilentlyContinue | Measure-Object).Count
$currentDate = Get-Date -Format "MMMM dd, yyyy"

# Create archive README content
"# Archived Documentation" | Out-File -FilePath "docs\archive\README.md" -Encoding UTF8
"" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"Last Updated: $currentDate" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"## Folder Structure" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**authentication/** - Files: $authFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**google_workspace/** - Files: $googleFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**microsoft_365/** - Files: $msFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**implementations/** - Files: $implFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**kanban/** - Files: $kanbanFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**summaries/** - Files: $summaryFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**ui/** - Files: $uiFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8
"**scripts/** - Files: $scriptFilesCount" | Out-File -FilePath "docs\archive\README.md" -Append -Encoding UTF8

Write-Host "   ✅ Archive index created" -ForegroundColor Green

# Step 14: Final cleanup report
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "🎉 PHASE 2 CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green

Write-Host "`n📊 Cleanup Statistics:" -ForegroundColor Yellow
$totalArchived = (Get-ChildItem "docs\archive" -Recurse -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
$totalTests = (Get-ChildItem "AI_infrastructure\tests" -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "   • Docs Archived: $totalArchived" -ForegroundColor Cyan
Write-Host "   • Tests Consolidated: $totalTests" -ForegroundColor Cyan
Write-Host "   • Scripts Removed: $removedCount" -ForegroundColor Cyan
Write-Host "   • Backups Removed: $backupCount" -ForegroundColor Cyan

Write-Host "`n📁 Current Root Files:" -ForegroundColor Yellow
$rootFiles = Get-ChildItem -Path . -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -in @('.md', '.py', '.ps1', '.bat', '.txt', '.json', '.yaml', '.yml') }
Write-Host "   • Total: $($rootFiles.Count)" -ForegroundColor Cyan

Write-Host "`n✅ Workspace is now clean and organized!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Review archived files in docs/archive/" -ForegroundColor White
Write-Host "   2. Commit changes to git" -ForegroundColor White
Write-Host "   3. Proceed to Phase 3: API Documentation" -ForegroundColor White

Write-Host ""
