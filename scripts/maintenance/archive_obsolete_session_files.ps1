# Archive Obsolete Session Files Script
# Moves obsolete files to archived/ folder with documentation

Write-Host "`n🗄️ Archiving Obsolete Session Files" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$basePath = "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core"
$archivePath = "$basePath\archived"

# Create archive folder
if (-not (Test-Path $archivePath)) {
    New-Item -Path $archivePath -ItemType Directory -Force | Out-Null
    Write-Host "✅ Created archived folder: $archivePath" -ForegroundColor Green
} else {
    Write-Host "📁 Archive folder exists: $archivePath" -ForegroundColor Yellow
}

# Files to archive with reasons
$filesToArchive = @{
    "session_persistence.py" = "In-memory only - functionality extracted to unified_session_manager.py with Supabase persistence"
    "session_database.py" = "Complete but never called - valuable functions extracted to unified_session_manager.py"
    "session_handler.py" = "Duplicate of unified_session_manager.py but in-memory only (V4 component)"
    "streaming_agent_worker.py" = "Merged into combined_agent_worker.py - no longer needed"
    "conversation_manager.py" = "V4 sync mode experiment - not used in production streaming (agent_routes_v4.py)"
    "response_serializer.py" = "V4 component - functionality duplicated in combined_agent_worker.py SSE formatting"
}

Write-Host "`n📦 Files to archive:" -ForegroundColor Cyan
foreach ($file in $filesToArchive.Keys) {
    $sourcePath = "$basePath\$file"
    if (Test-Path $sourcePath) {
        Write-Host "  ✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n⚠️  This will move 6 files to archived/" -ForegroundColor Yellow
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "`n❌ Cancelled by user" -ForegroundColor Red
    exit
}

# Archive each file
$archived = 0
foreach ($file in $filesToArchive.Keys) {
    $sourcePath = "$basePath\$file"
    $destPath = "$archivePath\$file"
    
    if (Test-Path $sourcePath) {
        try {
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  ✅ Archived: $file" -ForegroundColor Green
            $archived++
        } catch {
            Write-Host "  ❌ Failed to archive: $file" -ForegroundColor Red
            Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠️  Skipped (not found): $file" -ForegroundColor Yellow
    }
}

# Create README in archived folder
$readmeContent = @"
# Archived Session Management Files
**Date Archived**: $(Get-Date -Format "yyyy-MM-dd")  
**Reason**: Consolidation into unified_session_manager.py

---

## Why These Files Were Archived

### session_persistence.py
**Original Purpose**: Simple in-memory session storage  
**Issue**: Data stored in `_sessions = {}` dict - lost on Flask restart  
**Replacement**: unified_session_manager.py with Supabase/SQLite persistence  
**Valuable Functions Extracted**: 
- load_or_create_session() - Critical for multi-turn conversations
- save_conversation() - Saves full conversation array

### session_database.py
**Original Purpose**: Complete SQLite session storage with 5 tables  
**Issue**: Never called by any route - complete implementation but unused  
**Replacement**: unified_session_manager.py  
**Valuable Functions Extracted**:
- create_session() - Full session creation with metadata
- add_message() - Stores messages with timestamps
- get_conversation() - Loads full conversation history
- prepare_content_for_storage() - Filters thinking/tool_result blocks
- list_user_sessions() - Query sessions with filters

### session_handler.py
**Original Purpose**: V4 modular session management  
**Issue**: In-memory only (`self.sessions = {}`), no database persistence  
**Replacement**: unified_session_manager.py  
**Note**: Only used by conversation_manager.py (V4 sync mode)

### streaming_agent_worker.py
**Original Purpose**: Streaming SSE response handling  
**Issue**: Functionality merged into combined_agent_worker.py  
**Replacement**: combined_agent_worker.py (complete merger)

### conversation_manager.py
**Original Purpose**: V4 synchronous conversation orchestrator  
**Issue**: Sync-only, not used in production streaming (agent_routes_v4.py)  
**Note**: Experimental V4 architecture - combined_agent_worker.py is production

### response_serializer.py
**Original Purpose**: Format Claude API responses for JSON/SSE  
**Issue**: Functionality duplicated in combined_agent_worker.py  
**Note**: V4 component - only used by conversation_manager.py

---

## Files NOT Archived (Active)

### unified_session_manager.py
✅ ACTIVE - Single source of truth for ALL session data  
✅ Supabase/SQLite dual-mode persistence  
✅ In-memory cache + SSE queues + execution locks  
✅ Used by agent_routes_v4.py and all production routes

### combined_agent_worker.py
✅ ACTIVE - Streaming agent worker with Claude API  
✅ SSE event streaming, tool execution, multi-turn conversations  
✅ Used by agent_routes_v4.py

### session_orchestrator.py
✅ ACTIVE - Google Tasks synchronization (niche but active)  
✅ Kanban visualization features

### tool_executor.py & tool_processor.py
✅ ACTIVE - V4 modular components (kept for future refactoring)  
✅ Clean architecture patterns for tool execution

### agent_state_manager.py
⚠️ NEEDS REVIEW - Overlaps with unified_session_manager.py  
⚠️ Consider merging into unified_session_manager.py

---

## Extraction Summary

All valuable functionality has been extracted to **unified_session_manager.py**:

1. ✅ load_or_create_session() - From session_persistence.py
2. ✅ save_conversation() - From session_persistence.py  
3. ✅ get_conversation() - From session_database.py
4. ✅ add_message() - From session_database.py
5. ✅ prepare_content_for_storage() - From session_database.py
6. ✅ list_user_sessions() - From session_database.py

**Result**: Single source of truth with complete functionality

---

## Recovery Instructions

If you need to restore any archived file:

``````powershell
# Restore specific file
Move-Item "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\archived\session_persistence.py" `
         "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\session_persistence.py"

# Restore all files
Get-ChildItem "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\archived\*.py" | `
    ForEach-Object { Move-Item $_.FullName "c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\" }
``````

**Warning**: Restoring files will create import conflicts. Review unified_session_manager.py first.

---

**Archived by**: AI Agent Analysis Script  
**Documentation**: SESSION_FILES_ANALYSIS_AND_ACTION_PLAN.md
"@

Set-Content -Path "$archivePath\README.md" -Value $readmeContent

Write-Host "`n✅ Created README.md in archived folder" -ForegroundColor Green
Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  Archived: $archived files" -ForegroundColor Green
Write-Host "  Location: $archivePath" -ForegroundColor White
Write-Host "  Documentation: $archivePath\README.md" -ForegroundColor White

Write-Host "`n✅ Archive complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
