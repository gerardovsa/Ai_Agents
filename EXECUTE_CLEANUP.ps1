# EXECUTE_CLEANUP.ps1 - Archive cleanup for v6 deployment
# Date: November 15, 2025
# Purpose: Move test/utility/analysis scripts from root to archive folders

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI AGENTS - ARCHIVE CLEANUP v6" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create archive directories
Write-Host "[1/7] Creating archive directories..." -ForegroundColor Yellow

$archiveDirs = @(
    "archive\test_scripts",
    "archive\database_utilities",
    "archive\analysis_reports",
    "archive\timelines_and_reports",
    "archive\deployment_scripts",
    "archive\documentation"
)

foreach ($dir in $archiveDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  Exists: $dir" -ForegroundColor Gray
    }
}

Write-Host ""

# Move test scripts
Write-Host "[2/7] Moving test scripts..." -ForegroundColor Yellow

$testPatterns = @("test_*.py", "check_*.py", "analyze_*.py", "debug_*.py", "verify_*.py", "trace_*.py", "smoke_test_*.py", "quick_*.py", "simple_*.py", "keep_*.py", "clear_*.py", "final_*.py")
$testCount = 0

foreach ($pattern in $testPatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        $files | Move-Item -Destination "archive\test_scripts\" -Force
        $testCount += $files.Count
    }
}

Write-Host "  Moved $testCount test script files" -ForegroundColor Green
Write-Host ""

# Move database utilities
Write-Host "[3/7] Moving database utilities..." -ForegroundColor Yellow

$dbPatterns = @("add_*.py", "create_*.py", "fix_*.py", "migrate_*.py", "update_*.py", "cleanup_*.py", "clean_*.py", "drop_*.py", "rebuild_*.py", "repair_*.py", "reset_*.py", "restore_*.py", "consolidate_*.py", "delete_*.py")
$dbCount = 0

foreach ($pattern in $dbPatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        $files | Move-Item -Destination "archive\database_utilities\" -Force
        $dbCount += $files.Count
    }
}

Write-Host "  Moved $dbCount database utility files" -ForegroundColor Green
Write-Host ""

# Move analysis reports
Write-Host "[4/7] Moving analysis reports..." -ForegroundColor Yellow

$analysisPatterns = @("get_*.py", "query_*.py", "search_*.py", "inspect_*.py", "explain_*.py", "compare_*.py", "audit_*.py", "calculate_*.py", "find_*.py")
$analysisCount = 0

foreach ($pattern in $analysisPatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        $files | Move-Item -Destination "archive\analysis_reports\" -Force
        $analysisCount += $files.Count
    }
}

Write-Host "  Moved $analysisCount analysis report files" -ForegroundColor Green
Write-Host ""

# Move timelines and reports
Write-Host "[5/7] Moving timelines and reports..." -ForegroundColor Yellow

$timelinePatterns = @("*_timeline.*", "*_report.html", "*_analysis.json", "*_work_hours.*", "master_timeline*.py", "master_timeline*.html", "combined_*.py", "combined_*.html", "detailed_*.py", "project_gantt*.html", "work_quote_dashboard*.html", "all_projects*.json", "all_projects*.txt", "project_development*.json", "commits_*.txt", "git_*.txt", "focused_*.html")
$timelineCount = 0

foreach ($pattern in $timelinePatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        $files | Move-Item -Destination "archive\timelines_and_reports\" -Force
        $timelineCount += $files.Count
    }
}

Write-Host "  Moved $timelineCount timeline/report files" -ForegroundColor Green
Write-Host ""

# Move deployment scripts
Write-Host "[6/7] Moving deployment scripts..." -ForegroundColor Yellow

$deployPatterns = @("apply_*.py", "trigger_*.py", "upload_*.py", "sync_*.py", "setup_*.py", "regenerate_*.py", "regenerate_*.bat", "run_*.py", "visualize_*.py", "validate_*.py")
$deployCount = 0

foreach ($pattern in $deployPatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        $files | Move-Item -Destination "archive\deployment_scripts\" -Force
        $deployCount += $files.Count
    }
}

Write-Host "  Moved $deployCount deployment script files" -ForegroundColor Green
Write-Host ""

# Move completed documentation
Write-Host "[7/7] Moving completed documentation..." -ForegroundColor Yellow

# Exclude files we want to keep
$excludeFiles = @(
    "README.md",
    "RENDER_DEPLOYMENT_GUIDE.md",
    "DATABASE_CONNECTIONS_UPDATE_COMPLETE.md",
    "V6_DEPLOYMENT_FIXES.md",
    "ARCHIVE_CLEANUP_PLAN.md",
    "SUPABASE_TOOLS_COMPLETE.md",
    "SUPABASE_CLI_GUIDE.md",
    "SUPABASE_QUICK_REFERENCE.md",
    "SUPABASE_MIGRATION_GUIDE.md",
    "AI_AGENTS_TOOL_ARCHITECTURE_ANALYSIS.md",
    "COMPLETE_SYSTEM_DOCUMENTATION.md"
)

$docPatterns = @(
    "*_COMPLETE.md",
    "*_ANALYSIS.md",
    "*_FIX*.md",
    "*_IMPLEMENTATION*.md",
    "*_SUMMARY.md",
    "*_SUMMARIES.md",
    "TODO_STATUS_*.md",
    "*_NOV*.md",
    "*_OCT*.md",
    "ACCURATE_*.md",
    "AGENT*.md",
    "AI_MEMORY*.md",
    "AI_SETTINGS*.md",
    "ANSWERS*.md",
    "AUTO_*.md",
    "CLEANUP_*.md",
    "CODEBASE_*.md",
    "COMMUNICATION_*.md",
    "COMPREHENSIVE_*.md",
    "CONVERSATION_*.md",
    "CORRECTION_*.md",
    "CREDENTIAL_*.md",
    "CRITICAL_*.md",
    "DATABASE_CLEANUP*.md",
    "DATABASE_PROTECTION*.md",
    "DATABASE_SCHEMAS*.md",
    "DATABASE_SCHEMA_FIX*.md",
    "DATABASE_VERIFICATION*.md",
    "DEPLOYMENT_STATUS*.md",
    "DEPLOYMENT_STEPS*.md",
    "DEPLOYMENT_SUCCESS*.md",
    "DETAILED_*.md",
    "DEVICE_*.md",
    "DEV_MODE*.md",
    "DIAGNOSE_*.js",
    "DISCOVER_*.md",
    "DOCUMENT_*.md",
    "DRAG_DROP_*.md",
    "EMAIL_*.md",
    "EMPTY_*.md",
    "ENHANCED_*.md",
    "ENHANCEMENTS_*.md",
    "ERROR_*.md",
    "FIELD_*.md",
    "FILE_*.md",
    "FINAL_*.md",
    "FIXES_*.md",
    "FIX_*.md",
    "FLOW_*.md",
    "FORMATTING_*.md",
    "GOOGLE_*.md",
    "HOURLY_*.md",
    "HTML_*.md",
    "ICON_*.md",
    "IMPLEMENTATION_ROADMAP*.md",
    "IMPLEMENTATION_STATUS*.md",
    "INPUT_*.md",
    "INTERNAL_DOCS_*.md",
    "INTERLEAVED_*.md",
    "ISOLATION_*.md",
    "LOGGING_*.md",
    "LONG_RUNNING_*.md",
    "MARKDOWN_*.md",
    "MESSAGE_*.md",
    "META_*.md",
    "MODULE_*.md",
    "MULTI_*.md",
    "NEXT_STEPS_*.md",
    "OAUTH_*.md",
    "OUTLOOK_*.md",
    "PHANTOM_*.md",
    "POPUP_*.md",
    "PREFERRED_*.md",
    "PROGRESS_*.md",
    "PROJECT_*.md",
    "PROMPT_*.md",
    "PRUNING_*.md",
    "QUICK_FIXES*.md",
    "QUICK_ISOLATION*.md",
    "QUICK_START_*.md",
    "QUOTE_*.md",
    "REAL_*.md",
    "RENDER_CREDENTIALS*.md",
    "RENDER_CURL*.txt",
    "RENDER_DATABASE_*.md",
    "RENDER_DEPLOYMENT_ANALYSIS*.md",
    "RENDER_DEPLOYMENT_CHECKLIST*.md",
    "RENDER_INTEGRATION*.md",
    "RENDER_MODULE*.md",
    "RENDER_OAUTH*.md",
    "RENDER_QUICK_START*.md",
    "RENDER_READY*.md",
    "RENDER_RESOURCE*.md",
    "RENDER_SYNTAX*.md",
    "RENDER_UPLOAD*.sh",
    "RENDER_WAL*.md",
    "RENDER_WORKER*.md",
    "SAVE_*.md",
    "SCHEMA_*.md",
    "SESSION_*.md",
    "SIGNATURE_*.md",
    "SMART_*.md",
    "SMOKE_TEST_*.md",
    "SPREADSHEET_*.md",
    "SYNERGY_*.md",
    "SYSTEM_PROMPT_*.md",
    "SYSTEM_PROMPT_*.txt",
    "TABLE_*.md",
    "TABULATOR_*.md",
    "TEMPERATURE_*.md",
    "TEST_RESULTS_*.md",
    "TEXT_*.md",
    "THINKING_*.md",
    "THREADMANAGER_*.md",
    "THREAD_*.md",
    "TIMELINE_*.md",
    "TIM_*.md",
    "TIPTAP_*.md",
    "TOKEN_*.md",
    "TOOL_*.md",
    "TWO_TABLES_*.md",
    "UI_*.md",
    "UNICODE_*.md",
    "UNIFIED_*.md",
    "UNIVERSAL_*.md",
    "UNLOAD_*.md",
    "USER_*.md",
    "VINYL_*.md",
    "WELCOME_*.md",
    "WORKSPACE_*.md",
    "WORK_*.md",
    "XERO_*.md",
    "XERO_*.json"
)

$docCount = 0

foreach ($pattern in $docPatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File -ErrorAction SilentlyContinue
    if ($files) {
        foreach ($file in $files) {
            # Check if file is in exclude list
            if ($excludeFiles -notcontains $file.Name) {
                Move-Item -Path $file.FullName -Destination "archive\documentation\" -Force
                $docCount++
            }
        }
    }
}

Write-Host "  Moved $docCount documentation files" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total files archived:" -ForegroundColor Yellow
Write-Host "  Test scripts:       $testCount files" -ForegroundColor White
Write-Host "  Database utilities: $dbCount files" -ForegroundColor White
Write-Host "  Analysis reports:   $analysisCount files" -ForegroundColor White
Write-Host "  Timelines/Reports:  $timelineCount files" -ForegroundColor White
Write-Host "  Deployment scripts: $deployCount files" -ForegroundColor White
Write-Host "  Documentation:      $docCount files" -ForegroundColor White
Write-Host ""

$totalCount = $testCount + $dbCount + $analysisCount + $timelineCount + $deployCount + $docCount

Write-Host "TOTAL: $totalCount files archived" -ForegroundColor Green
Write-Host ""

# Count remaining files in root
$remainingPy = (Get-ChildItem -Path . -Filter "*.py" -File).Count
$remainingMd = (Get-ChildItem -Path . -Filter "*.md" -File).Count

Write-Host "Remaining in root directory:" -ForegroundColor Yellow
Write-Host "  Python files:  $remainingPy" -ForegroundColor White
Write-Host "  Markdown files: $remainingMd" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review archived files in archive/ folder" -ForegroundColor White
Write-Host "  2. Test Flask app: BISTART" -ForegroundColor White
Write-Host "  3. Test AI agent: CHAT 'test message'" -ForegroundColor White
Write-Host "  4. Commit cleanup: git add . && git commit -m 'Archive cleanup for v6'" -ForegroundColor White
Write-Host ""
