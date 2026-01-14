# Archive & Cleanup Plan - v6 Branch

**Date:** November 15, 2025  
**Purpose:** Organize and archive non-production files before deployment  
**Target:** 200+ test scripts, 100+ utility files, 50+ migration scripts

---

## 📋 **ARCHIVE STRATEGY**

### **Goal:**
- Archive all test/check/analyze scripts from root directory
- Keep production-critical files only
- Organize by category for easy recovery if needed

### **Categories to Archive:**

---

## 1️⃣ **TEST SCRIPTS (150+ files in root)**

### **Move to:** `archive/test_scripts/`

**Files Pattern:**
```
test_*.py
check_*.py
analyze_*.py
debug_*.py
verify_*.py
trace_*.py
smoke_test_*.py
quick_*.py
```

**Examples:**
```
Root Files to Archive:
├── test_ai_settings_flow.py
├── test_append_mode.py
├── test_database_routes.py
├── test_device_lock.py
├── test_end_to_end_synergy.py
├── test_gmail_detailed.py
├── test_google_docs_fixes.py
├── test_internal_docs.py
├── test_message_save_fix.py
├── test_synergy_ui_fixes.py
├── test_thread_assignments_comprehensive.py
├── test_tool_truncation.py
├── test_xero_tools.py
├── check_all_messages.py
├── check_all_threads_with_agent2.py
├── check_database_tables.py
├── check_messages.py
├── check_oauth_tokens.py
├── check_sessions_db.py
├── check_synergy_data.py
├── check_thread_assignments.py
├── check_threads_schema.py
├── check_users_table.py
├── analyze_agent_tracking.py
├── analyze_duplicate_tables.py
├── analyze_infrastructure_db.py
├── analyze_message_payload.py
├── analyze_synergy_structure.py
├── analyze_thread_manager.py
├── debug_documents_rendering.py
├── debug_synergy_display.py
├── debug_synergy_threads.py
├── verify_database_complete.py
├── verify_synergy_sync.py
├── verify_thread_system.py
└── ... (120+ more similar files)
```

**Total:** ~150 files (15-20 MB)

---

## 2️⃣ **DATABASE UTILITY SCRIPTS (80+ files in root)**

### **Move to:** `archive/database_utilities/`

**Files Pattern:**
```
add_*.py
create_*.py
fix_*.py
migrate_*.py
update_*.py
cleanup_*.py
drop_*.py
rebuild_*.py
repair_*.py
reset_*.py
restore_*.py
consolidate_*.py
```

**Examples:**
```
Root Files to Archive:
├── add_ai_settings_columns.py
├── add_columns_only.py
├── add_missing_columns.py
├── add_user1_prompts.py
├── create_default_user.py
├── create_internal_docs_table.py
├── create_thread_assignments_fix.py
├── create_user_1.py
├── fix_agent_assignment_spaces.py
├── fix_corrupted_database.py
├── fix_database_malformed.py
├── fix_database_schema.py
├── fix_double_encoded_json.py
├── fix_messages_table.py
├── fix_synergy_database_schema.py
├── fix_threads_schema_branch_point.py
├── fix_unicode_escape_errors.py
├── fix_users_table.py
├── migrate_messages_to_threads.py
├── migrate_saved_threads.py
├── update_agent_routes_db.py
├── update_all_routes_db.py
├── update_email_alias_helpers.py
├── cleanup_infrastructure_db.py
├── cleanup_orphaned_assignments.py
├── clean_all_duplicates.py
├── drop_sessions_table.py
├── rebuild_database.py
├── repair_synergy_sync.py
├── reset_sessions_database.py
├── restore_from_backup.py
└── ... (50+ more similar files)
```

**Total:** ~80 files (8-10 MB)

---

## 3️⃣ **ANALYSIS & REPORTING SCRIPTS (30+ files in root)**

### **Move to:** `archive/analysis_reports/`

**Files Pattern:**
```
get_*.py
query_*.py
search_*.py
inspect_*.py
explain_*.py
compare_*.py
audit_*.py
calculate_*.py
find_*.py
```

**Examples:**
```
Root Files to Archive:
├── get_all_database_schemas.py
├── get_drive_file_ids.py
├── get_github_copilot_fees.py
├── get_synergy_schema.py
├── query_synergy_session.py
├── query_vinyl_stock.py
├── search_all_vinyl_stocks.py
├── inspect_all_database_schemas.py
├── inspect_database_schemas.py
├── inspect_migrated_sessions.py
├── explain_thread_ids.py
├── compare_file_sizes.py
├── audit_all_document_fields.py
├── audit_synergy_sessions.py
├── calculate_ai_costs.py
├── find_custom_column.py
├── find_messages_db.py
├── find_mixed_column.py
├── find_phantom_assignments.py
└── ... (10+ more similar files)
```

**Total:** ~30 files (3-5 MB)

---

## 4️⃣ **TIMELINE & VISUALIZATION SCRIPTS (20+ files in root)**

### **Move to:** `archive/timelines_and_reports/`

**Files Pattern:**
```
*_timeline.py
*_timeline.html
*_timeline.json
*_analysis.py
*_analysis.json
*_report.html
master_*.py
combined_*.py
detailed_*.py
```

**Examples:**
```
Root Files to Archive:
├── ai_agents_accurate_timeline.html
├── ai_agents_accurate_timeline.json
├── ai_agents_timeline.html
├── ai_agents_timeline.json
├── ai_agents_work_hours.html
├── ai_agents_work_hours.json
├── all_projects_summary.txt
├── all_projects_work_hours.json
├── analyze_all_projects_complete.py
├── analyze_file_metadata_accurate.py
├── analyze_project_development_patterns.py
├── combined_project_timeline.html
├── combined_project_timeline.py
├── combined_timeline_v2_detailed.html
├── combined_timeline_v3_ultra_detailed.html
├── create_master_timeline.py
├── create_project_gantt_chart.py
├── detailed_size_comparison.py
├── master_timeline_all_projects.html
├── project_development_analysis.json
├── project_gantt_chart.html
├── work_quote_dashboard.html
└── work_quote_report.html
```

**Total:** ~25 files (10-15 MB HTML/JSON)

---

## 5️⃣ **DEPLOYMENT & MIGRATION SCRIPTS (40+ files in root)**

### **Move to:** `archive/deployment_scripts/`

**Files Pattern:**
```
apply_*.py
trigger_*.py
upload_*.py
sync_*.py
setup_*.py
```

**Examples:**
```
Root Files to Archive:
├── apply_fix2.py
├── apply_google_forms_fixes.py
├── trigger_render_deploy.py
├── upload_fresh_sessions_db.py
├── sync_synergy_threads.py
├── setup_auto_backup.py
└── ... (30+ more similar files)
```

**Total:** ~40 files (4-5 MB)

---

## 6️⃣ **DOCUMENTATION FILES (200+ .md files in root)**

### **Strategy:** Keep essential docs, archive old/completed docs

**Keep in Root (Production-Critical):**
```
✅ KEEP IN ROOT:
├── README.md (main project readme)
├── RENDER_DEPLOYMENT_GUIDE.md (deployment instructions)
├── DATABASE_CONNECTIONS_UPDATE_COMPLETE.md (current session)
├── V6_DEPLOYMENT_FIXES.md (current session)
├── SUPABASE_TOOLS_COMPLETE.md (production database)
├── SUPABASE_CLI_GUIDE.md (production tools)
├── SUPABASE_QUICK_REFERENCE.md (quick lookup)
└── config.example.py (configuration template)
```

**Move to:** `archive/documentation/`

```
ARCHIVE TO archive/documentation/:
├── All *_COMPLETE.md files (finished features)
├── All *_ANALYSIS.md files (completed analysis)
├── All *_FIX_COMPLETE.md files (finished fixes)
├── All *_IMPLEMENTATION_COMPLETE.md files (done implementations)
├── All *_SUMMARY.md files (historical summaries)
├── ACCURATE_TODO_STATUS.md
├── AGENT2_THREAD_ANALYSIS.md
├── AI_MEMORY_AND_REDUNDANT_DISCOVERY_ANALYSIS.md
├── AI_SETTINGS_FLOW_ANALYSIS.md
├── ANSWERS_TO_YOUR_QUESTIONS.md
├── AUTO_THREAD_TITLE_GENERATION.md
├── CLEANUP_SUMMARY_NOV8_2025.md
├── COMMUNICATION_HUB_DIAGNOSTIC.md
├── COMPLETE_DATABASE_SCHEMAS.json
├── COMPLETE_THREAD_UI_IMPLEMENTATION.md
├── COMPLETE_WORK_QUOTE.md
├── COMPREHENSIVE_CLI_API_TOOLS_FOR_AI_AGENTS.md
├── CONVERSATION_PRUNING_COMPLETE.md
├── CORRECTION_NOV9.md
├── CREDENTIAL_INJECTION_ANALYSIS.md
├── CRITICAL_BUG_FIXES_NOV9.md
├── DATABASE_CLEANUP_COMPLETE.md
├── DATABASE_SCHEMAS.json
├── DATABASE_SCHEMA_FIX_COMPLETE.md
├── DATABASE_VERIFICATION_COMPLETE.md
├── DEPLOYMENT_STATUS.md
├── DEPLOYMENT_SUCCESS.md
├── DETAILED_WORK_TIMELINE.md
├── DEVICE_LOCK_IMPLEMENTATION_COMPLETE.md
├── DEVICE_NAMING_FEATURE_COMPLETE.md
├── DISCOVER_AND_STATE_IMPLEMENTATION_COMPLETE.md
├── DRAG_DROP_IMPLEMENTATION_COMPLETE.md
├── EMAIL_SYNERGY_COORDINATOR_COMPLETE.md
├── EMPTY_THREAD_SAVE_FIX_NOV14.md
├── ENHANCED_LOGGING_COMPLETE.md
├── ERROR_ANALYSIS_NOV15.md
├── ERROR_HIGHLIGHTING_FEATURE.md
├── FILE_ATTACHMENT_FEATURE_IMPLEMENTATION.md
├── FIXES_COMPLETE.md
├── FLOW_TRACE_COMPLETE_ANALYSIS.md
├── GOOGLE_DOCS_403_FIX_NOV9.md
├── GOOGLE_FORMS_FIXES_COMPLETE_NOV10.md
├── IMPLEMENTATION_SUMMARY_NOV8_2025.md
├── INTERNAL_DOCS_IMPLEMENTATION_COMPLETE.md
├── ISOLATION_FIX_DEPLOYMENT_CHECKLIST.md
├── LOGGING_STANDARDIZATION_COMPLETE.md
├── MESSAGE_STORAGE_COMPLETE_ANALYSIS.md
├── MULTI_AGENT_THINKING_PULSE_CONFIRMED.md
├── OAUTH_COLUMNS_FIX_COMPLETE.md
├── PHANTOM_THREADS_FIXED.md
├── PROMPT_LIBRARY_IMPLEMENTATION_COMPLETE.md
├── SESSION_ISOLATION_FIX_SUMMARY.md
├── SYNERGY_DRAG_DROP_FIX_COMPLETE.md
├── SYNERGY_FIELD_FIXES_COMPLETE.md
├── SYNERGY_REFERENCE_IMPLEMENTATION_COMPLETE.md
├── SYNERGY_THREAD_LINKING_IMPLEMENTATION_NOV9_2025.md
├── SYNERGY_UI_FIXES_NOV9_2025.md
├── TABLE_CONSOLIDATION_COMPLETE.md
├── THREAD_ASSIGNMENTS_ANALYSIS_COMPLETE.md
├── THREAD_FIXES_COMPLETE.md
├── THREAD_MANAGEMENT_IMPLEMENTATION_COMPLETE.md
├── THREAD_MESSAGE_LINKING_FIX_COMPLETE.md
├── THREAD_UI_FIXES_COMPLETE_NOV14_2025.md
├── TODO_STATUS_NOVEMBER_9.md
├── TOOL_RESULT_EXTRACTION_FIX_COMPLETE.md
├── TOOL_USE_VALIDATION_FIX_NOV11.md
├── UNICODE_ESCAPE_FIX_COMPLETE.md
├── UNIFIED_THREAD_INFO_SUMMARY.md
├── UNIVERSAL_CARD_FIX_COMPLETE.md
├── USER_MANAGEMENT_IMPLEMENTATION_COMPLETE.md
├── WELCOME_SYSTEM_COMPLETE.md
├── WORK_QUOTE_COMPREHENSIVE.md
├── WORK_SUMMARY_NOV9_2025.md
├── XERO_INTEGRATION_INVESTIGATION_COMPLETE.md
└── ... (150+ more .md files)
```

**Total:** ~200 files (50-60 MB)

---

## 7️⃣ **ALREADY ARCHIVED DIRECTORIES**

These folders already exist and contain archived content:

```
✅ EXISTING ARCHIVES (DO NOT TOUCH):
├── archive/ (various old files)
├── ARCHIVE_OCT30_2025/ (October 2025 archived code)
├── docs/archive/ (old documentation)
└── testing_tools/ (organized test utilities)
```

---

## 🎯 **FILES TO KEEP IN ROOT (Production-Critical)**

### **Essential Scripts (11 files):**
```
✅ KEEP - Core Startup:
├── BISTART.bat
├── BISTART.ps1
├── BISTOP.ps1
├── CHAT.bat
├── chat.ps1
├── CHATM.bat
├── CHATM.ps1
├── startup.sh
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### **Essential Config (8 files):**
```
✅ KEEP - Configuration:
├── .env.example
├── .env.master
├── .gitignore
├── .dockerignore
├── config.py
├── config.example.py
├── render.yaml
└── service-account.json
```

### **Essential Documentation (10 files):**
```
✅ KEEP - Active Docs:
├── README.md
├── RENDER_DEPLOYMENT_GUIDE.md
├── DATABASE_CONNECTIONS_UPDATE_COMPLETE.md
├── V6_DEPLOYMENT_FIXES.md
├── ARCHIVE_CLEANUP_PLAN.md (this file)
├── SUPABASE_TOOLS_COMPLETE.md
├── SUPABASE_CLI_GUIDE.md
├── SUPABASE_QUICK_REFERENCE.md
├── AI_AGENTS_TOOL_ARCHITECTURE_ANALYSIS.md
└── COMPLETE_SYSTEM_DOCUMENTATION.md
```

**Total to Keep:** ~30 files in root

---

## 📦 **ARCHIVE DIRECTORY STRUCTURE**

```
AI_agents/
├── archive/
│   ├── test_scripts/            (150 files - test_*.py, check_*.py, debug_*.py)
│   ├── database_utilities/      (80 files - fix_*.py, migrate_*.py, update_*.py)
│   ├── analysis_reports/        (30 files - analyze_*.py, query_*.py, inspect_*.py)
│   ├── timelines_and_reports/   (25 files - *_timeline.*, *_report.html)
│   ├── deployment_scripts/      (40 files - apply_*.py, trigger_*.py, upload_*.py)
│   └── documentation/           (200 files - *_COMPLETE.md, *_ANALYSIS.md, *_FIX.md)
│
├── AI_infrastructure/           (✅ KEEP - Production code)
├── google_workspace/            (✅ KEEP - Production code)
├── Microsoft_365_Connection/    (✅ KEEP - Production code)
├── tools/                       (✅ KEEP - Production code)
├── UI/                          (✅ KEEP - Production frontend)
├── data/                        (✅ KEEP - SQLite databases)
├── scripts/                     (✅ KEEP - Organized scripts)
│   ├── startup/                 (BISTART, BISTOP, chat, SYNERGY_START)
│   ├── testing/                 (8 organized test scripts)
│   ├── maintenance/             (8 cleanup/fix scripts)
│   ├── deployment/              (5 deployment scripts)
│   └── utilities/               (Helper scripts)
│
├── BISTART.bat                  (✅ KEEP)
├── BISTART.ps1                  (✅ KEEP)
├── chat.ps1                     (✅ KEEP)
├── config.py                    (✅ KEEP)
├── render.yaml                  (✅ KEEP)
├── README.md                    (✅ KEEP)
├── RENDER_DEPLOYMENT_GUIDE.md   (✅ KEEP)
└── ... (10 more essential files)
```

---

## 🚀 **EXECUTION PLAN**

### **Phase 1: Create Archive Structure**

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Create archive directories
New-Item -ItemType Directory -Path "archive\test_scripts" -Force
New-Item -ItemType Directory -Path "archive\database_utilities" -Force
New-Item -ItemType Directory -Path "archive\analysis_reports" -Force
New-Item -ItemType Directory -Path "archive\timelines_and_reports" -Force
New-Item -ItemType Directory -Path "archive\deployment_scripts" -Force
New-Item -ItemType Directory -Path "archive\documentation" -Force
```

### **Phase 2: Move Test Scripts**

```powershell
# Move all test/check/analyze/debug/verify scripts
Get-ChildItem -Path . -Filter "test_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "check_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "analyze_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "debug_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "verify_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "trace_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "smoke_test_*.py" | Move-Item -Destination "archive\test_scripts\"
Get-ChildItem -Path . -Filter "quick_*.py" | Move-Item -Destination "archive\test_scripts\"
```

### **Phase 3: Move Database Utilities**

```powershell
# Move all database utility scripts
Get-ChildItem -Path . -Filter "add_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "create_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "fix_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "migrate_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "update_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "cleanup_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "clean_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "drop_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "rebuild_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "repair_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "reset_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "restore_*.py" | Move-Item -Destination "archive\database_utilities\"
Get-ChildItem -Path . -Filter "consolidate_*.py" | Move-Item -Destination "archive\database_utilities\"
```

### **Phase 4: Move Analysis & Reporting**

```powershell
# Move all analysis/query/inspect scripts
Get-ChildItem -Path . -Filter "get_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "query_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "search_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "inspect_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "explain_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "compare_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "audit_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "calculate_*.py" | Move-Item -Destination "archive\analysis_reports\"
Get-ChildItem -Path . -Filter "find_*.py" | Move-Item -Destination "archive\analysis_reports\"
```

### **Phase 5: Move Timelines & Reports**

```powershell
# Move timeline/report files
Get-ChildItem -Path . -Filter "*_timeline.*" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "*_report.html" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "*_analysis.json" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "*_work_hours.*" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "master_*.py" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "combined_*.py" | Move-Item -Destination "archive\timelines_and_reports\"
Get-ChildItem -Path . -Filter "detailed_*.py" | Move-Item -Destination "archive\timelines_and_reports\"
```

### **Phase 6: Move Deployment Scripts**

```powershell
# Move deployment/trigger/upload/sync scripts
Get-ChildItem -Path . -Filter "apply_*.py" | Move-Item -Destination "archive\deployment_scripts\"
Get-ChildItem -Path . -Filter "trigger_*.py" | Move-Item -Destination "archive\deployment_scripts\"
Get-ChildItem -Path . -Filter "upload_*.py" | Move-Item -Destination "archive\deployment_scripts\"
Get-ChildItem -Path . -Filter "sync_*.py" | Move-Item -Destination "archive\deployment_scripts\"
Get-ChildItem -Path . -Filter "setup_*.py" | Move-Item -Destination "archive\deployment_scripts\"
```

### **Phase 7: Move Completed Documentation**

```powershell
# Move completed/historical documentation
Get-ChildItem -Path . -Filter "*_COMPLETE.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "*_ANALYSIS.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "*_FIX*.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "*_IMPLEMENTATION_COMPLETE.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "*_SUMMARY.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "TODO_STATUS_*.md" | Move-Item -Destination "archive\documentation\"
Get-ChildItem -Path . -Filter "*_NOV*.md" | Move-Item -Destination "archive\documentation\"
```

---

## ✅ **VERIFICATION CHECKLIST**

After archiving, verify:

- [ ] Root directory has ~30 files (down from 500+)
- [ ] All startup scripts still in root (BISTART.bat, chat.ps1, etc.)
- [ ] All config files still in root (.env.master, config.py, render.yaml)
- [ ] Essential docs still in root (README.md, RENDER_DEPLOYMENT_GUIDE.md)
- [ ] Production code folders untouched (AI_infrastructure/, tools/, UI/)
- [ ] Archive folders populated (test_scripts/, database_utilities/, etc.)
- [ ] Git tracks moves (use `git add` to stage)

---

## 📊 **EXPECTED RESULTS**

### **Before Cleanup:**
```
Root directory: ~500 files (200+ .py, 200+ .md, 100+ other)
Total size: ~150 MB
```

### **After Cleanup:**
```
Root directory: ~30 files (essential only)
Total size: ~10 MB

archive/ directory: ~525 files
Total size: ~140 MB
```

### **Benefits:**
- ✅ Cleaner root directory (easier navigation)
- ✅ Faster git operations (fewer files to track)
- ✅ Easier deployment (only production files)
- ✅ Better organization (categorized by purpose)
- ✅ Files preserved (can be recovered if needed)

---

## 🔧 **ONE-COMMAND CLEANUP SCRIPT**

Create `EXECUTE_CLEANUP.ps1`:

```powershell
# EXECUTE_CLEANUP.ps1 - One-command archive operation

Write-Host "🗂️  Starting archive cleanup..." -ForegroundColor Cyan

# Create directories
$archiveDirs = @(
    "archive\test_scripts",
    "archive\database_utilities",
    "archive\analysis_reports",
    "archive\timelines_and_reports",
    "archive\deployment_scripts",
    "archive\documentation"
)

foreach ($dir in $archiveDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Move test scripts
$testPatterns = @("test_*.py", "check_*.py", "analyze_*.py", "debug_*.py", "verify_*.py", "trace_*.py", "smoke_test_*.py", "quick_*.py")
foreach ($pattern in $testPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\test_scripts\" -Force
}

# Move database utilities
$dbPatterns = @("add_*.py", "create_*.py", "fix_*.py", "migrate_*.py", "update_*.py", "cleanup_*.py", "clean_*.py", "drop_*.py", "rebuild_*.py", "repair_*.py", "reset_*.py", "restore_*.py", "consolidate_*.py")
foreach ($pattern in $dbPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\database_utilities\" -Force
}

# Move analysis reports
$analysisPatterns = @("get_*.py", "query_*.py", "search_*.py", "inspect_*.py", "explain_*.py", "compare_*.py", "audit_*.py", "calculate_*.py", "find_*.py")
foreach ($pattern in $analysisPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\analysis_reports\" -Force
}

# Move timelines
$timelinePatterns = @("*_timeline.*", "*_report.html", "*_analysis.json", "*_work_hours.*", "master_*.py", "combined_*.py", "detailed_*.py")
foreach ($pattern in $timelinePatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\timelines_and_reports\" -Force
}

# Move deployment scripts
$deployPatterns = @("apply_*.py", "trigger_*.py", "upload_*.py", "sync_*.py", "setup_*.py")
foreach ($pattern in $deployPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\deployment_scripts\" -Force
}

# Move completed documentation
$docPatterns = @("*_COMPLETE.md", "*_ANALYSIS.md", "*_FIX*.md", "*_IMPLEMENTATION_COMPLETE.md", "*_SUMMARY.md", "TODO_STATUS_*.md", "*_NOV*.md")
foreach ($pattern in $docPatterns) {
    Get-ChildItem -Path . -Filter $pattern -File | Move-Item -Destination "archive\documentation\" -Force
}

Write-Host "✅ Archive cleanup complete!" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  - Test scripts: archive\test_scripts\"
Write-Host "  - Database utilities: archive\database_utilities\"
Write-Host "  - Analysis reports: archive\analysis_reports\"
Write-Host "  - Timelines: archive\timelines_and_reports\"
Write-Host "  - Deployment scripts: archive\deployment_scripts\"
Write-Host "  - Documentation: archive\documentation\"
```

**Execute:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
.\EXECUTE_CLEANUP.ps1
```

---

## ⚠️ **CAUTIONS**

1. **Do NOT archive:**
   - BISTART.bat / BISTART.ps1 (startup scripts)
   - config.py / .env.master (configuration)
   - render.yaml (deployment config)
   - README.md (project documentation)
   - service-account.json (Google OAuth)

2. **Test after archiving:**
   - Run `BISTART` to verify Flask starts
   - Run `CHAT "test message"` to verify AI agent works
   - Check all production routes load

3. **Git commit separately:**
   - Archive cleanup should be its own commit
   - Don't mix with v6 deployment commit

---

**Ready to execute cleanup?** 🗑️

Would you like me to:
1. Create the `EXECUTE_CLEANUP.ps1` script
2. Run it to archive all files
3. Verify the cleanup was successful
4. Then proceed with v6 commit?
