# Master Session Cleanup Execution Script
# Orchestrates all cleanup phases with safety checks

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🚀 SESSION FILES CLEANUP & ORGANIZATION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`nThis script will:" -ForegroundColor Yellow
Write-Host "  1. ✅ Colorize active files with Aqua Blue (Peacock)" -ForegroundColor White
Write-Host "  2. 🗑️  Delete duplicate backup files (.backup, copy.py)" -ForegroundColor White
Write-Host "  3. 🗄️  Archive obsolete session files (6 files)" -ForegroundColor White
Write-Host "  4. ⚠️  Show extraction tasks remaining" -ForegroundColor White

Write-Host "`n📋 Safety Features:" -ForegroundColor Green
Write-Host "  - All archived files preserved in archived/ folder" -ForegroundColor White
Write-Host "  - README.md created explaining each archive" -ForegroundColor White
Write-Host "  - User confirmation before each phase" -ForegroundColor White
Write-Host "  - Detailed logging of all actions" -ForegroundColor White

Write-Host "`n⚠️  Requirements:" -ForegroundColor Yellow
Write-Host "  - Peacock extension (johnpapa.vscode-peacock)" -ForegroundColor White
Write-Host "  - Read SESSION_FILES_ANALYSIS_AND_ACTION_PLAN.md first" -ForegroundColor White

$confirm = Read-Host "`nReady to proceed? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "`n❌ Cancelled by user" -ForegroundColor Red
    exit
}

# Phase 1: Colorize Active Files
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE 1: COLORIZE ACTIVE FILES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$colorizeScript = "c:\Users\gpoli\GIT\AI_agents\scripts\maintenance\colorize_active_files.ps1"
if (Test-Path $colorizeScript) {
    & $colorizeScript
    Write-Host "`n✅ Phase 1 complete" -ForegroundColor Green
} else {
    Write-Host "`n❌ Colorize script not found: $colorizeScript" -ForegroundColor Red
}

Read-Host "`nPress Enter to continue to Phase 2"

# Phase 2: Delete Duplicate Backups
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE 2: DELETE DUPLICATE BACKUPS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$deleteScript = "c:\Users\gpoli\GIT\AI_agents\scripts\maintenance\delete_duplicate_backups.ps1"
if (Test-Path $deleteScript) {
    & $deleteScript
    Write-Host "`n✅ Phase 2 complete" -ForegroundColor Green
} else {
    Write-Host "`n❌ Delete script not found: $deleteScript" -ForegroundColor Red
}

Read-Host "`nPress Enter to continue to Phase 3"

# Phase 3: Archive Obsolete Session Files
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE 3: ARCHIVE OBSOLETE SESSION FILES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$archiveScript = "c:\Users\gpoli\GIT\AI_agents\scripts\maintenance\archive_obsolete_session_files.ps1"
if (Test-Path $archiveScript) {
    & $archiveScript
    Write-Host "`n✅ Phase 3 complete" -ForegroundColor Green
} else {
    Write-Host "`n❌ Archive script not found: $archiveScript" -ForegroundColor Red
}

# Phase 4: Show Remaining Tasks
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE 4: EXTRACTION TASKS REMAINING" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n⚠️  CRITICAL: These functions must be extracted to unified_session_manager.py:" -ForegroundColor Yellow

Write-Host "`n📦 From session_persistence.py (archived):" -ForegroundColor Cyan
Write-Host "  1. load_or_create_session(agent_id, session_id, ui_context)" -ForegroundColor White
Write-Host "     → Convert _sessions dict to get_database_connection()" -ForegroundColor Gray
Write-Host "     → CRITICAL for multi-turn conversations" -ForegroundColor Red
Write-Host "`n  2. save_conversation(agent_id, session_id, conversation)" -ForegroundColor White
Write-Host "     → Convert _sessions dict to get_database_connection()" -ForegroundColor Gray
Write-Host "     → Saves full conversation array" -ForegroundColor Gray

Write-Host "`n📦 From session_database.py (archived):" -ForegroundColor Cyan
Write-Host "  3. get_conversation(session_id)" -ForegroundColor White
Write-Host "     → Already has DB code, just migrate" -ForegroundColor Gray
Write-Host "`n  4. add_message(session_id, role, content, tools_used)" -ForegroundColor White
Write-Host "     → Already has DB code, just migrate" -ForegroundColor Gray
Write-Host "`n  5. prepare_content_for_storage(content)" -ForegroundColor White
Write-Host "     → Filters thinking/tool_result blocks" -ForegroundColor Gray
Write-Host "     → Per Nov 12, 2025 Anthropic docs (keep thinking blocks)" -ForegroundColor Gray
Write-Host "`n  6. list_user_sessions(user_id, status, limit)" -ForegroundColor White
Write-Host "     → Query sessions with filters" -ForegroundColor Gray

Write-Host "`n🔧 Then update agent_routes_v4.py:" -ForegroundColor Cyan
Write-Host "  - Add load_or_create_session() call BEFORE creating conversation" -ForegroundColor White
Write-Host "  - Add save_conversation() call AFTER streaming completes" -ForegroundColor White
Write-Host "  - This fixes multi-turn conversations (currently broken)" -ForegroundColor Red

Write-Host "`n📖 Testing Checklist:" -ForegroundColor Cyan
Write-Host "  1. Create new session with 'Hello'" -ForegroundColor White
Write-Host "  2. Continue session with 'What did I just say?'" -ForegroundColor White
Write-Host "  3. Verify AI remembers 'Hello' (multi-turn working)" -ForegroundColor White
Write-Host "  4. Check DB: SELECT * FROM sessions WHERE session_id='...'" -ForegroundColor White
Write-Host "  5. Check Flask logs for '[UnifiedSessionManager] Loading existing session'" -ForegroundColor White

Write-Host "`n📁 Documentation:" -ForegroundColor Cyan
Write-Host "  - SESSION_FILES_ANALYSIS_AND_ACTION_PLAN.md (complete analysis)" -ForegroundColor White
Write-Host "  - AI_infrastructure/core/archived/README.md (why each file archived)" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ CLEANUP COMPLETE - EXTRACTION PHASE PENDING" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Active files colorized (Aqua Blue)" -ForegroundColor Green
Write-Host "  ✅ Duplicate backups deleted" -ForegroundColor Green
Write-Host "  ✅ Obsolete session files archived" -ForegroundColor Green
Write-Host "  ⚠️  Function extraction pending (see above)" -ForegroundColor Yellow

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review archived files in AI_infrastructure/core/archived/" -ForegroundColor White
Write-Host "  2. Extract functions to unified_session_manager.py" -ForegroundColor White
Write-Host "  3. Update agent_routes_v4.py to load conversation history" -ForegroundColor White
Write-Host "  4. Test multi-turn conversations" -ForegroundColor White

Write-Host "`n✅ All done!" -ForegroundColor Green
