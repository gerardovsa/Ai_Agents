# AI_agents Cleanup Script for Render Deployment
# Generated: October 30, 2025
# Purpose: Clean codebase, archive unnecessary files, prepare for Docker deployment

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$rootDir = "c:\Users\gpoli\GIT\AI_agents"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CLEANUP FOR RENDER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Create archive directories
$archiveDirs = @(
    "$rootDir\ARCHIVE\tests_$timestamp",
    "$rootDir\ARCHIVE\documentation_$timestamp",
    "$rootDir\ARCHIVE\old_scripts_$timestamp",
    "$rootDir\ARCHIVE\backup_$timestamp"
)

foreach ($dir in $archiveDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

Write-Host "[1/8] Archiving test scripts..." -ForegroundColor Yellow

# Archive all root-level test scripts (30+ files)
$testFiles = @(
    "test_ai_demo.py",
    "test_ai_simple_demo.py",
    "test_ai_tool_execution.py",
    "test_claude_v3_google_docs.py",
    "test_complete_flow.py",
    "test_comprehensive.py",
    "test_credential_fetcher.py",
    "test_current_connections.py",
    "test_database_connection.py",
    "test_database_visualizer.py",
    "test_env_master_loading.py",
    "test_google_doc_creation.py",
    "test_google_doc_now.py",
    "test_integration_v3.py",
    "test_integration_v3_simple.py",
    "test_live_responses.py",
    "test_m365_oauth.py",
    "test_multi_dir_registry.py",
    "test_oauth_and_docs.py",
    "test_oauth_consolidation.py",
    "test_oauth_query.py",
    "test_oauth_status_fix.py",
    "test_profile_builder_fixed.py",
    "test_profile_oauth_status.py",
    "test_real_execution.py",
    "test_registry_direct.py",
    "test_sqlite_stock.py",
    "test_stock_endpoints.py",
    "test_tool_call_direct.py",
    "test_tool_debug.py",
    "test_tool_execution_real.py",
    "test_v3_chat.py",
    "test_v3_client.py",
    "test_v3_request.py"
)

$testCount = 0
foreach ($file in $testFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination "$rootDir\ARCHIVE\tests_$timestamp\" -Force
        $testCount++
    }
}
Write-Host "  Archived $testCount test files" -ForegroundColor Green

Write-Host "`n[2/8] Archiving duplicate check scripts..." -ForegroundColor Yellow

# Archive duplicate database check scripts
$checkFiles = @(
    "check_databases.py",
    "check_tables.py",
    "check_tables_quick.py",
    "check_token_validity.py",
    "check_users.py",
    "check_users_and_credentials.py",
    "analyze_database_tables.py",
    "list_all_tables.py",
    "quick_test_db_visualizer.py"
)

$checkCount = 0
foreach ($file in $checkFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination "$rootDir\ARCHIVE\old_scripts_$timestamp\" -Force
        $checkCount++
    }
}
Write-Host "  Archived $checkCount check scripts" -ForegroundColor Green

Write-Host "`n[3/8] Archiving one-time migration scripts..." -ForegroundColor Yellow

# Archive migration/cleanup scripts
$migrationFiles = @(
    "migrate_database_consolidation.py",
    "cleanup_databases.py",
    "extract_database_schemas.py",
    "debug_tool_format.py",
    "verify_oauth_system.py",
    "verify_stock_module.py"
)

$migCount = 0
foreach ($file in $migrationFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination "$rootDir\ARCHIVE\old_scripts_$timestamp\" -Force
        $migCount++
    }
}
Write-Host "  Archived $migCount migration scripts" -ForegroundColor Green

Write-Host "`n[4/8] Deleting old deployment files..." -ForegroundColor Yellow

# Delete Render-specific files (not using anymore, using Docker)
$renderFiles = @(
    "check_render_service.py",
    "deploy_to_render_api.py"
)

$renderCount = 0
foreach ($file in $renderFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Remove-Item -Path $filePath -Force
        $renderCount++
    }
}
Write-Host "  Deleted $renderCount old Render scripts" -ForegroundColor Green

Write-Host "`n[5/8] Deleting obsolete backend files..." -ForegroundColor Yellow

# Delete old backend (Synergy backend kept per user request)
$oldBackend = @(
    "database_analysis.txt",
    "render.yaml.backup"
)

$backendCount = 0
foreach ($file in $oldBackend) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Remove-Item -Path $filePath -Force
        $backendCount++
    }
}
Write-Host "  Deleted $backendCount obsolete files" -ForegroundColor Green

Write-Host "`n[6/8] Archiving token files..." -ForegroundColor Yellow

# Archive old OAuth token files (keep credentials per user request)
$tokenFiles = @(
    "token_calendar_desktop.json",
    "token_desktop.json",
    "token_gmail_desktop.json",
    "token_tasks_desktop.json",
    "token_unified_desktop.json"
)

$tokenCount = 0
foreach ($file in $tokenFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination "$rootDir\ARCHIVE\backup_$timestamp\" -Force
        $tokenCount++
    }
}
Write-Host "  Archived $tokenCount token files" -ForegroundColor Green

Write-Host "`n[7/8] Archiving redundant documentation..." -ForegroundColor Yellow

# Archive redundant documentation (keep SOURCE_OF_TRUTH as primary)
$docFiles = @(
    "AGENT_ROUTES_ACTION_CHECKLIST.md",
    "AGENT_ROUTES_ARCHITECTURE_DIAGRAMS.md",
    "AGENT_ROUTES_DETAILED_FINDINGS.md",
    "AGENT_ROUTES_QUICK_REFERENCE.md",
    "AGENT_ROUTES_REBUILD_ANALYSIS.md",
    "AGENT_ROUTES_REBUILD_INDEX.md",
    "AGENT_ROUTES_REBUILD_SUMMARY.md",
    "AGENT_ROUTES_V3_COMPLETE_SUMMARY.md",
    "AGENT_ROUTES_V3_FINAL_COMPARISON.md",
    "AGENT_ROUTES_V3_VISUAL_GUIDE.md",
    "V3_COMPARISON_AND_INTEGRATION.md",
    "V4_MIGRATION_PLAN.md",
    "V4_MODULAR_ARCHITECTURE.md",
    "FLASK_REFACTOR_INSTRUCTIONS.md",
    "REDUNDANT_FILES_ANALYSIS.md",
    "CLEANUP_PLAN.md"
)

$docCount = 0
foreach ($file in $docFiles) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination "$rootDir\ARCHIVE\documentation_$timestamp\" -Force
        $docCount++
    }
}
Write-Host "  Archived $docCount documentation files" -ForegroundColor Green

Write-Host "`n[8/8] Consolidating OAuth documentation..." -ForegroundColor Yellow

# Consolidate OAuth documentation
$oauthDocs = @(
    "OAUTH_ENV_MASTER_COMPLETE.md",
    "OAUTH_FIX_IMPLEMENTATION_SUMMARY.md",
    "OAUTH_FLOW_ANALYSIS_AND_FIX.md",
    "OAUTH_SCHEMA_FIX_COMPLETE.md",
    "OAUTH_TESTING_GUIDE.md"
)

$oauthDocDir = "$rootDir\ARCHIVE\documentation_$timestamp\oauth"
New-Item -ItemType Directory -Force -Path $oauthDocDir | Out-Null

$oauthCount = 0
foreach ($file in $oauthDocs) {
    $filePath = Join-Path $rootDir $file
    if (Test-Path $filePath) {
        Move-Item -Path $filePath -Destination $oauthDocDir -Force
        $oauthCount++
    }
}
Write-Host "  Consolidated $oauthCount OAuth docs" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test files archived:       $testCount" -ForegroundColor White
Write-Host "Check scripts archived:    $checkCount" -ForegroundColor White
Write-Host "Migration scripts archived: $migCount" -ForegroundColor White
Write-Host "Render files deleted:      $renderCount" -ForegroundColor White
Write-Host "Backend files deleted:     $backendCount" -ForegroundColor White
Write-Host "Token files archived:      $tokenCount" -ForegroundColor White
Write-Host "Documentation archived:    $docCount" -ForegroundColor White
Write-Host "OAuth docs consolidated:   $oauthCount" -ForegroundColor White
Write-Host "`nTotal files processed:     $($testCount + $checkCount + $migCount + $renderCount + $backendCount + $tokenCount + $docCount + $oauthCount)" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  KEPT FOR RENDER DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SYNERGY SCRIPTS:           KEPT" -ForegroundColor Green
Write-Host "  synergy_backend.py" -ForegroundColor White
Write-Host "  synergy_requirements.txt" -ForegroundColor White
Write-Host "`nSUPABASE:                  KEPT" -ForegroundColor Green
Write-Host "  Supabase/ folder" -ForegroundColor White
Write-Host "`nCLOUDFLARE:                KEPT" -ForegroundColor Green
Write-Host "  Cloudflare/ folder" -ForegroundColor White
Write-Host "`nRENDER_BACKEND:            KEPT" -ForegroundColor Green
Write-Host "  Render_backend/ folder" -ForegroundColor White
Write-Host "`nCREDENTIALS:               KEPT" -ForegroundColor Green
Write-Host "  credentials_desktop.json" -ForegroundColor White
Write-Host "  credentials_web.json" -ForegroundColor White
Write-Host "  vsa-anythingllm-project-ab7c8caf8c47.json" -ForegroundColor White
Write-Host "`nDOCKER:                    KEPT" -ForegroundColor Green
Write-Host "  docker-compose.yml" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PRIMARY DOCUMENTATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI_INFRASTRUCTURE_SOURCE_OF_TRUTH.md   PRIMARY" -ForegroundColor Green
Write-Host "V4_INTEGRATION_COMPLETE_SUMMARY.md     CURRENT STATUS" -ForegroundColor Green
Write-Host "V4_BUILD_COMPLETE.md                   MODULE DETAILS" -ForegroundColor Green
Write-Host "V4_ARCHITECTURE_STATUS.md              MODULE STATUS" -ForegroundColor Green
Write-Host "BACKEND_QUICK_START.md                 QUICK START" -ForegroundColor Green
Write-Host "CALCULATOR_INTEGRATION_COMPLETE.md     CALCULATOR DOCS" -ForegroundColor Green
Write-Host "CALCULATOR_QUICK_START.md              CALCULATOR START" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ARCHIVE LOCATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARCHIVE\tests_$timestamp\" -ForegroundColor White
Write-Host "ARCHIVE\documentation_$timestamp\" -ForegroundColor White
Write-Host "ARCHIVE\documentation_$timestamp\oauth\" -ForegroundColor White
Write-Host "ARCHIVE\old_scripts_$timestamp\" -ForegroundColor White
Write-Host "ARCHIVE\backup_$timestamp\" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "Ready for Render deployment with Docker" -ForegroundColor Cyan
Write-Host "All critical files preserved" -ForegroundColor Cyan
Write-Host "Archive created: ARCHIVE\*_$timestamp\" -ForegroundColor Cyan
