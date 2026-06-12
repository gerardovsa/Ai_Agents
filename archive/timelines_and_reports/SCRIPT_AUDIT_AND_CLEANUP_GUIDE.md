# Script Audit & Cleanup Guide
**Date:** November 20, 2025  
**Purpose:** Identify active, archivable, and extractable scripts

---

## 📊 **EXECUTIVE SUMMARY**

### **Scripts Analysis:**
- **Total Backend Core**: 28 files in `AI_infrastructure/core/`
- **Total Routes**: 30+ files in `AI_infrastructure/routes/`
- **Total Frontend Modules**: 10+ JavaScript files
- **Status**: Many duplicates, unused legacy code, and scattered functionality

### **Key Findings:**
1. ✅ **5 actively used core files** (combined_agent_worker, unified_session_manager, agent_state_manager, unified_ai_client, prompt_injection_manager)
2. ❌ **8 obsolete session files** with overlapping functionality
3. ⚠️ **3 duplicate backend files** (.backup copies)
4. 🔄 **Frontend has good modular structure** but needs cleanup

---

## 🟢 **ACTIVELY USED SCRIPTS (Keep & Maintain)**

### **Backend Core (`AI_infrastructure/core/`)**

#### **1. `combined_agent_worker.py`** ✅ **CRITICAL - PRIMARY WORKER**
**Purpose:** Background worker for streaming AI responses  
**Used By:** `agent_routes_v4.py` (main agent endpoint)  
**Functions:**
- `run_agent_worker()` - Background worker with file support
- `run_simple_agent_worker()` - Synchronous text-only worker
- `agent_worker()` - CLI chat worker
- `execute_streaming_request()` - Multi-round streaming
- `validate_and_reorder_assistant_content()` - Block validation
- `prune_conversation_for_context_limit()` - Context management

**Status:** ✅ Active, critical, well-maintained  
**Action:** **KEEP** - This is the heart of the agent system

---

#### **2. `unified_session_manager.py`** ✅ **CRITICAL - SESSION PERSISTENCE**
**Purpose:** Single source of truth for ALL session data  
**Used By:** `flask_app.py`, `agent_routes_v4.py`, all session endpoints  
**Functions:**
- `create_session()` - Create with DB persistence (SQLite/Supabase)
- `get_session()` - Load from DB or cache
- `update_session()` - Save to DB
- `get_or_create_queue()` - SSE event streaming
- `acquire_lock()` / `release_lock()` - Thread safety
- `cleanup_old_sessions()` - Automatic pruning

**Database:** ✅ Supabase-compatible (dual mode: SQLite local / Supabase Render)  
**Status:** ✅ Active, critical, Supabase-ready  
**Action:** **KEEP** - Primary session system

---

#### **3. `agent_state_manager.py`** ✅ **ACTIVE - IN-MEMORY STATE**
**Purpose:** Lightweight in-memory state for agent UI  
**Used By:** `agent_routes_v4.py`, `thread_routes.py`  
**Functions:**
- `get_or_create_state()` - Get agent state
- `get_state()` - Retrieve state
- `update_state()` - Update state
- `clear_state()` - Clear agent memory

**Status:** ✅ Active, but should delegate to `unified_session_manager`  
**Action:** **KEEP** but consider merging with `unified_session_manager`

---

#### **4. `unified_ai_client.py`** ✅ **CRITICAL - AI PROVIDER**
**Purpose:** Initialize AI clients (Anthropic/OpenAI/DeepSeek)  
**Used By:** All agent routes  
**Functions:**
- `initialize_ai_client()` - Get AI client with API key rotation
- `UnifiedAIClient` class - Multi-provider abstraction

**Status:** ✅ Active, critical  
**Action:** **KEEP** - Central AI provider management

---

#### **5. `prompt_injection_manager.py`** ✅ **ACTIVE - PROMPT LIBRARY**
**Purpose:** Manage system prompts and prompt library  
**Used By:** `agent_routes_v4.py`, `prompt_library_routes.py`  
**Functions:**
- `get_prompt_manager()` - Get singleton instance
- `get_prompt()` - Retrieve prompt by ID
- `save_prompt()` - Save custom prompt
- `list_prompts()` - List all prompts

**Status:** ✅ Active  
**Action:** **KEEP** - Prompt management system

---

#### **6. `ip_location.py`** ✅ **ACTIVE - GEOLOCATION**
**Purpose:** Get user geolocation for context  
**Used By:** `agent_routes_v4.py`  
**Functions:**
- `get_location_dict()` - Get location data
- `get_location_for_prompt()` - Format for AI prompt

**Status:** ✅ Active  
**Action:** **KEEP** - Geolocation context

---

#### **7. `module_blueprint_loader.py`** ✅ **ACTIVE - ROUTE LOADER**
**Purpose:** Dynamically load Flask route modules  
**Used By:** `flask_app.py`  
**Status:** ✅ Active  
**Action:** **KEEP** - Dynamic route loading

---

### **Backend Routes (`AI_infrastructure/routes/`)**

#### **1. `agent_routes_v4.py`** ✅ **CRITICAL - MAIN AGENT API**
**Purpose:** Primary agent streaming endpoint  
**Endpoints:**
- `/api/agent/<agent_id>/start` - Start agent conversation
- `/api/agent/<agent_id>/stream` - SSE streaming
- `/api/agent/<agent_id>/stop` - Stop agent
- `/api/agent/chat` - Synchronous chat
- `/api/agent/cli` - CLI agent

**Status:** ✅ Active, recently updated for Supabase compatibility  
**Action:** **KEEP** - Main entry point

---

#### **2. `thread_routes.py`** ✅ **ACTIVE - THREAD MANAGEMENT**
**Purpose:** Thread CRUD operations  
**Endpoints:**
- `/api/threads` - List threads
- `/api/threads/<thread_id>` - Get thread
- `/api/threads/<thread_id>/messages` - Thread messages
- `/api/threads/save` - Save thread

**Status:** ✅ Active  
**Action:** **KEEP**

---

#### **3. Other Active Routes:**
- `automation_routes.py` ✅ Workflow automation
- `synergy_routes.py` ✅ Synergy project management
- `auth_routes.py` ✅ Authentication
- `oauth_routes.py` ✅ OAuth (Google/Microsoft)
- `file_routes.py` ✅ File upload handling
- `export_routes.py` ✅ Export threads
- `prompt_library_routes.py` ✅ Prompt management
- `quote_calculator_routes.py` ✅ InHouse calculator integration
- `scheduler_routes.py` ✅ Scheduled tasks
- `token_routes.py` ✅ Token counting
- `user_management_routes.py` ✅ User CRUD
- `user_preferences_routes.py` ✅ User settings
- `geolocation_routes.py` ✅ Location detection

**Action:** **KEEP ALL** - Active and functional

---

### **Frontend Modules (`UI/modules/`)**

#### **1. `modules/agents/prime_ai_chat.js`** ✅ **CRITICAL - PRIME PANEL**
**Purpose:** Main Prime AI chat interface  
**Functions:**
- `sendStreamingChatMessage()` - Stream messages to Prime
- `addChatMessage()` - Add message bubble
- `initChatPanel()` - Initialize Prime panel
- `toggleAutoScroll()` - Auto-scroll control
- `loadPlatformStatus()` - OAuth status

**Status:** ✅ Active, main UI entry point  
**Action:** **KEEP** - Critical UI component

---

#### **2. `modules/agents/agent-js.js`** ✅ **CRITICAL - AGENT LOGIC**
**Purpose:** Agent column business logic  
**Functions:**
- `sendAgentMessage()` - Send message to agent
- `handleAgentStreamEvent()` - Process SSE events
- `addAgentMessage()` - Add message bubble
- `loadThreadIntoAgent()` - Load conversation history
- `buildConversationHistoryForAPI()` - Format messages
- `initMultiAgent()` - Initialize multi-agent system

**Status:** ✅ Active, core agent functionality  
**Action:** **KEEP** - Essential for agent system

---

#### **3. `modules/agents/agent-ui.js`** ✅ **ACTIVE - AGENT UI RENDERING**
**Purpose:** Agent column UI rendering (modular component)  
**Status:** ✅ Active  
**Action:** **KEEP** - UI rendering module

---

#### **4. `modules/agents/agent-column.js`** ✅ **ACTIVE - COLUMN CONTROLLER**
**Purpose:** Agent column controller (modular component)  
**Status:** ✅ Active  
**Action:** **KEEP** - Column management

---

#### **5. `modules/agents/agent-input.js`** ✅ **ACTIVE - INPUT HANDLER**
**Purpose:** Agent input textarea handler (modular component)  
**Status:** ✅ Active  
**Action:** **KEEP** - Input management

---

#### **6. `modules/agents/UnifiedMessageRenderer.js`** ✅ **ACTIVE - MESSAGE RENDERER**
**Purpose:** Unified message rendering (replaces old renderer)  
**Status:** ✅ Active, modern renderer  
**Action:** **KEEP** - New rendering system

---

#### **7. `modules/shared/message_renderer.js`** ⚠️ **LEGACY BUT USED**
**Purpose:** Original message renderer  
**Status:** ⚠️ Being replaced by `UnifiedMessageRenderer.js`  
**Action:** **KEEP FOR NOW** - Migrate to UnifiedMessageRenderer, then archive

---

#### **8. `modules/threads/thread_manager.js`** ✅ **CRITICAL - THREAD OPERATIONS**
**Purpose:** Thread CRUD operations from frontend  
**Functions:**
- `MessageStore` class - In-memory message storage
- Thread UI management (sidebar, cards)
- OAuth account management
- Settings management
- Memory management

**Status:** ✅ Active, critical for thread management  
**Action:** **KEEP** - Essential for thread operations

---

#### **9. `visualisation_engine/streamingTwoRule.js`** ✅ **ACTIVE - TWO-RULE MARKDOWN**
**Purpose:** Two-rule markdown processor for streaming  
**Status:** ✅ Active  
**Action:** **KEEP** - Streaming markdown rendering

---

#### **10. `visualisation_engine/visualisation_copy.js`** ✅ **ACTIVE - VISUALIZATION**
**Purpose:** Chart/graph/table rendering engine  
**Status:** ✅ Active  
**Action:** **KEEP** - Visualization system

---

## 🔴 **OBSOLETE/DUPLICATE SCRIPTS (Archive)**

### **Backend Core (`AI_infrastructure/core/`) - 8 files to archive**

#### **1. `session_persistence.py`** ❌ **OBSOLETE - IN-MEMORY ONLY**
**Purpose:** In-memory session storage (no database)  
**Problem:** Doesn't persist to database, loses data on restart  
**Replaced By:** `unified_session_manager.py`  
**Action:** **ARCHIVE** - G_FOLDER pattern not implemented

---

#### **2. `session_database.py`** ❌ **UNUSED - COMPLETE BUT NEVER CALLED**
**Purpose:** SQLite session storage with full message history  
**Problem:** Has full implementation but never called by any route  
**Status:** Complete code, zero usage  
**Action:** **ARCHIVE** or **INTEGRATE** into `unified_session_manager.py`

---

#### **3. `session_handler.py`** ❌ **OBSOLETE - IN-MEMORY ONLY**
**Purpose:** V4 modular architecture session handler  
**Problem:** No persistence, in-memory dictionary only  
**Replaced By:** `unified_session_manager.py`  
**Action:** **ARCHIVE** - Superseded by unified manager

---

#### **4. `session_orchestrator.py`** ⚠️ **PARTIAL USE - GOOGLE TASKS ONLY**
**Purpose:** Session-aware task management (Kanban board)  
**Problem:** Only used for Google Tasks integration, not core sessions  
**Status:** Niche feature, limited usage  
**Action:** **KEEP** if using Google Tasks, otherwise **ARCHIVE**

---

#### **5. `streaming_agent_worker.py`** ❌ **OBSOLETE - MERGED**
**Purpose:** Streaming worker (old implementation)  
**Replaced By:** `combined_agent_worker.py` (unified version)  
**Action:** **ARCHIVE** - Merged into combined worker

---

#### **6. `conversation_manager.py`** ⚠️ **V4 SYNC MODE - LIMITED USE**
**Purpose:** V4 modular conversation orchestrator  
**Problem:** Only used for synchronous mode, not streaming  
**Status:** V4 architecture component, minimal usage  
**Action:** **KEEP** if V4 sync mode is used, otherwise **ARCHIVE**

---

#### **7. `response_serializer.py`** ⚠️ **V4 COMPONENT - LIMITED USE**
**Purpose:** V4 response serialization  
**Status:** V4 architecture component  
**Action:** **KEEP** if V4 is actively used, otherwise **ARCHIVE**

---

#### **8. `tool_executor.py` & `tool_processor.py`** ⚠️ **V4 COMPONENTS**
**Purpose:** V4 modular tool execution  
**Status:** V4 architecture components  
**Action:** **KEEP** if V4 is actively used, otherwise extract to `combined_agent_worker.py`

---

### **Backend Routes - 3 duplicates to remove**

#### **1. `thread_routes copy.py`** ❌ **DUPLICATE BACKUP**
**Action:** **DELETE** - Backup file, not used

---

#### **2. `automation_routes.py.backup`** ❌ **DUPLICATE BACKUP**
**Action:** **DELETE** - Backup file, not used

---

#### **3. `compat_sessions.py`** ❌ **COMPATIBILITY SHIM**
**Purpose:** Legacy compatibility layer  
**Action:** **DELETE** if no longer needed

---

### **Backend Threads - 3 backups to remove**

#### **1. `threads/message_manager.py.backup`** ❌ **BACKUP**
**Action:** **DELETE**

---

#### **2. `threads/thread_manager.py.backup`** ❌ **BACKUP**
**Action:** **DELETE**

---

#### **3. `threads/thread_sharing_manager.py.backup`** ❌ **BACKUP**
**Action:** **DELETE**

---

## 🔄 **SCRIPTS NEEDING REFACTORING**

### **Functions to Extract & Consolidate**

#### **1. Extract from `session_database.py` → `unified_session_manager.py`**

**Useful Functions:**
```python
# session_database.py (UNUSED but has good functions)
- save_session() - Write complete session to SQLite
- load_session() - Read session with full history  
- list_user_sessions() - Get all sessions for user
- update_activity_log() - Track session events
```

**Action:** Extract these functions and add to `unified_session_manager.py`  
**Why:** `unified_session_manager` needs full conversation persistence (G_FOLDER pattern)

---

#### **2. Merge `agent_state_manager.py` → `unified_session_manager.py`**

**Overlap:**
- Both manage session state
- Both have in-memory caching
- `agent_state_manager` is lightweight wrapper

**Action:** Consolidate into single session manager  
**Why:** Reduce duplication, single source of truth

---

#### **3. Extract V4 Components → `combined_agent_worker.py`**

**From `tool_executor.py` & `tool_processor.py`:**
```python
- validate_tool_call() - Tool validation
- inject_credentials() - Credential injection
- process_tool_results() - Result processing
```

**Action:** Extract and add to `combined_agent_worker.py`  
**Why:** Unified worker should have all tool logic

---

## 📋 **RECOMMENDED CLEANUP ACTIONS**

### **Phase 1: Delete Obvious Duplicates (Immediate)**
```powershell
# Remove backup files
Remove-Item "AI_infrastructure\routes\thread_routes copy.py"
Remove-Item "AI_infrastructure\routes\automation_routes.py.backup"
Remove-Item "AI_infrastructure\threads\*.backup"

# Move to archive
Move-Item "AI_infrastructure\core\streaming_agent_worker.py" "AI_infrastructure\core\archived\"
```

### **Phase 2: Archive Obsolete Session Files (Low Risk)**
```powershell
# Archive unused session managers
Move-Item "AI_infrastructure\core\session_persistence.py" "AI_infrastructure\core\archived\"
Move-Item "AI_infrastructure\core\session_handler.py" "AI_infrastructure\core\archived\"
Move-Item "AI_infrastructure\core\session_database.py" "AI_infrastructure\core\archived\"
```

### **Phase 3: Extract & Consolidate (Requires Testing)**
1. Extract functions from `session_database.py` to `unified_session_manager.py`
2. Add conversation persistence to `unified_session_manager.py`
3. Update `agent_routes_v4.py` to load conversation history from DB
4. Test multi-turn conversations
5. Archive original files after migration

### **Phase 4: Frontend Cleanup (Low Priority)**
1. Complete migration from `message_renderer.js` to `UnifiedMessageRenderer.js`
2. Remove old `message_renderer.js` after migration
3. Test all message rendering scenarios

---

## 📊 **FINAL FILE COUNT**

### **Backend Core - Before:**
- Total: 28 files
- Active: 7 files
- Obsolete: 8 files
- Backups: 0 files
- Archive folder: 13 files (already archived)

### **Backend Core - After Cleanup:**
- Active: 7 files (keep)
- Archived: 21 files (move 8 more)

### **Backend Routes - Before:**
- Total: 30+ files
- Active: 18+ files
- Duplicates: 3 files

### **Backend Routes - After Cleanup:**
- Active: 18+ files (keep)
- Deleted: 3 duplicates

### **Frontend Modules - Before:**
- Total: 10+ modules
- Active: 10 modules
- Legacy: 1 module (message_renderer.js)

### **Frontend Modules - After Migration:**
- Active: 9 modules (after message_renderer migration)

---

## 🎯 **PRIORITY ACTIONS**

### **High Priority (Do First):**
1. ✅ Delete `.backup` files (safe, immediate)
2. ✅ Archive `streaming_agent_worker.py` (already merged)
3. ✅ Archive `session_persistence.py`, `session_handler.py` (not used)
4. 🔧 Extract conversation persistence from `session_database.py`
5. 🔧 Update `agent_routes_v4.py` to load history from DB

### **Medium Priority:**
1. Merge `agent_state_manager.py` into `unified_session_manager.py`
2. Complete frontend `UnifiedMessageRenderer` migration
3. Extract V4 tool functions to `combined_agent_worker.py`

### **Low Priority:**
1. Archive `session_orchestrator.py` (if Google Tasks not used)
2. Archive V4 components (`conversation_manager.py`, etc.) if sync mode not used
3. Clean up `core/archived/` folder (already has 13 old files)

---

## 📝 **TESTING CHECKLIST**

After cleanup, test these critical flows:

### **Backend:**
- [ ] Agent streaming works (`/api/agent/<id>/start`)
- [ ] Threads save to database
- [ ] Threads load from database
- [ ] Multi-turn conversations work (history persists)
- [ ] File uploads work
- [ ] OAuth authentication works
- [ ] Automation workflows execute
- [ ] Synergy sessions load

### **Frontend:**
- [ ] Prime panel sends messages
- [ ] Agent columns send messages
- [ ] Messages render correctly (markdown, code, tables)
- [ ] Thread sidebar loads
- [ ] Thread cards display
- [ ] Drag-and-drop works
- [ ] File attachments work

---

## 🎉 **BENEFITS OF CLEANUP**

1. **Reduced Confusion:** Clear which files are active vs obsolete
2. **Easier Maintenance:** Fewer files to update
3. **Better Performance:** No loading unused modules
4. **Clearer Architecture:** Single source of truth for sessions
5. **Easier Onboarding:** New developers see only active code
6. **Reduced Bugs:** No accidentally using wrong/old version

---

## 📚 **RELATED DOCUMENTATION**

- `SUPABASE_MIGRATION_AGENT_ROUTES_V4.md` - Supabase migration guide
- `SESSION_MANAGEMENT_ANALYSIS.md` - Session system comparison
- `CALCULATOR_INTEGRATION_COMPLETE.md` - Calculator tools integration
- `PROGRESSIVE_LOADING_SUCCESS.md` - Tool loading optimization

---

**Last Updated:** November 20, 2025  
**Maintained By:** GitHub Copilot (Claude Sonnet 4.5)
