# Tool Flow Visual Summary
**Quick Reference** - See COMPLETE_TOOL_FLOW_ARCHITECTURE_MAP.md for full details

---

## 🎯 ACTIVE TOOL FLOW (V4 Architecture)

```
USER SUBMITS MESSAGE
        ↓
┌───────────────────────────────────────┐
│ POST /api/agent/<id>/start           │
│ agent_routes_v4.py                    │
│ - Create session                      │
│ - Start background thread             │
│ - Return 200 OK immediately           │
└────────────────┬──────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│ BACKGROUND: agent_worker()           │
│ agent_worker.py (454-561)             │
│                                       │
│ PHASE 1: INITIALIZATION               │
│ ├─ Load registry_v3 (594 tools)      │
│ ├─ Get system prompt                 │
│ ├─ PROGRESSIVE TOOL LOADING:         │
│ │  ├─ Turn 1: 5 meta-tools           │
│ │  └─ Turn 2+: All 594 tools         │
│ ├─ Build conversation                │
│ ├─ Send to Claude API                │
│ └─ Put "init_complete" in Queue      │
└────────────────┬──────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│ GET /api/agent/stream/<id>            │
│ agent_routes_v4.py                    │
│ - Get session + Queue                 │
│ - Create StreamingAgentWorker         │
│ - Start SSE stream                    │
└────────────────┬──────────────────────┘
                 │
                 ▼
┌───────────────────────────────────────┐
│ StreamingAgentWorker.execute_...()   │
│ streaming_agent_worker.py (60-388)    │
│                                       │
│ PHASE 2: STREAMING & TOOLS            │
│                                       │
│ ┌─────────────────────────────────┐   │
│ │ ROUND 1                         │   │
│ ├─────────────────────────────────┤   │
│ │ 1. Stream thinking → SSE       │   │
│ │ 2. Stream text → SSE           │   │
│ │ 3. Stream tool_use → SSE       │   │
│ │ 4. Execute tools:              │   │
│ │    ├─ Inject credentials       │   │
│ │    ├─ registry.execute_tool()  │   │
│ │    └─ Stream result → SSE      │   │
│ │ 5. stop_reason?                │   │
│ │    ├─ "tool_use" → ROUND 2     │   │
│ │    └─ "end_turn" → Complete    │   │
│ └─────────────────────────────────┘   │
│                 │                     │
│                 ▼                     │
│ ┌─────────────────────────────────┐   │
│ │ ROUND 2+ (Recursive)            │   │
│ ├─────────────────────────────────┤   │
│ │ - Append tool results          │   │
│ │ - Recursive call               │   │
│ │ - Max 10 rounds                │   │
│ └─────────────────────────────────┘   │
└───────────────────────────────────────┘
```

---

## 📂 FILE STATUS: WHAT'S USED, WHAT'S NOT

### ✅ ACTIVE (Used by V4) - 8 Files

```
AI_infrastructure/core/
├── ✅ __init__.py                    → Package exports
├── ✅ agent_worker.py                → Initialization (POST /start)
├── ✅ streaming_agent_worker.py      → Streaming (GET /stream)
└── ✅ unified_session_manager.py     → Session management

AI_infrastructure/meta_tools/
├── ✅ platform_tools_lister.py       → List platforms/tools
├── ✅ platform_guide_provider.py     → Platform guides
├── ✅ workflow_instructor.py         → Workflow steps
└── ✅ smart_tool_instructor.py       → Tool recommendations
```

### ⚠️ LEGACY (Not Used) - 8 Files - CAN BE DELETED

```
AI_infrastructure/core/
├── ⚠️ unified_anthropic_client.py    → Replaced by streaming_agent_worker
├── ⚠️ unified_ai_client.py           → Multi-provider (not used)
├── ⚠️ conversation_manager.py        → Replaced by V4 split architecture
├── ⚠️ tool_executor.py               → Replaced by direct registry calls
├── ⚠️ tool_processor.py              → Replaced by inline processing
├── ⚠️ response_serializer.py         → Replaced by inline SSE formatting
├── ⚠️ session_handler.py             → Replaced by unified_session_manager
└── ⚠️ session_persistence.py         → Replaced by unified_session_manager
```

### 🔮 FUTURE (Not Yet Active) - 8 Files - KEEP FOR ROADMAP

```
AI_infrastructure/core/
├── 🔮 session_database.py            → Advanced features (docs, tasks)
├── 🔮 context_engine.py              → Knowledge graph
├── 🔮 context_aware_ai.py            → Context awareness
├── 🔮 event_triggers.py              → Event automation
├── 🔮 session_orchestrator.py        → Multi-agent handoffs
├── 🔮 sync_manager.py                → External sync
├── 🔮 task_card_manager.py           → Kanban UI
└── 🔮 agent_state_manager.py         → Stateful tracking
```

---

## 🛠️ TOOL REGISTRY: 594 TOOLS

### Progressive Loading Pattern

```
TURN 1: First Message
├─ Send: 5 meta-tools only
│  ├─ list_available_platforms
│  ├─ list_platform_tools
│  ├─ get_platform_guide
│  ├─ recommend_tools_for_task
│  └─ get_workflow_steps
└─ Purpose: Tool discovery (99.2% token savings)

TURN 2+: Follow-up Messages
├─ Send: ALL 594 tools
│  ├─ 330 Google Workspace tools
│  ├─ 150+ Microsoft 365 tools
│  ├─ 30+ WooCommerce tools
│  ├─ 9+ Stripe tools
│  ├─ 11+ Slack tools
│  └─ 64+ other platform tools
└─ Purpose: Full tool access
```

### Tool Execution Flow

```
Claude calls tool (e.g., gmail_send_email)
        ↓
┌───────────────────────────────────┐
│ credential_injector.py            │
│ - Query database for OAuth tokens │
│ - Add access_token to params      │
└────────────────┬──────────────────┘
                 ↓
┌───────────────────────────────────┐
│ registry_v3.py                    │
│ - Look up tool in 594 tools       │
│ - Get implementation              │
│ - Call function(**params)         │
└────────────────┬──────────────────┘
                 ↓
┌───────────────────────────────────┐
│ gmail.py (implementation)         │
│ - Extract credentials from kwargs │
│ - Build Google API client         │
│ - Execute Gmail API call          │
│ - Return structured result        │
└────────────────┬──────────────────┘
                 ↓
┌───────────────────────────────────┐
│ Stream result back to UI          │
│ SSE event: "tool_result"          │
└───────────────────────────────────┘
```

---

## 🔧 KEY FIXES APPLIED (October 31, 2025)

### Meta-Tools Import Fix

**Before:**
```
⚠️ WARNING: Failed to load meta_tools
⚠️ No module named 'AI_infrastructure.meta_tools'
```

**After:**
```
✅ INFO: 🔧 meta_tools: 5 functions loaded
✅ list_available_platforms - FOUND
✅ list_platform_tools - FOUND
✅ get_platform_guide - FOUND
✅ recommend_tools_for_task - FOUND
✅ get_workflow_steps - FOUND
```

**Changes:**
1. Fixed logger import (AI_infrastructure.utils.logger → logging)
2. Fixed class name (ToolRegistry → RegistryV3)
3. Fixed sys.path (added root directory)

---

## 📊 STATISTICS

### Code Distribution
- **Active:** 8 files, ~3,500 lines (Used by V4)
- **Legacy:** 8 files, ~6,000 lines (Can be deleted)
- **Future:** 8 files, ~3,000 lines (Keep for roadmap)
- **Total:** 24 files, ~12,500 lines

### Tool Distribution
- **Total Tools:** 594 tools
- **Meta-Tools:** 5 tools (discovery)
- **Platform Tools:** 589 tools (execution)
- **Token Savings:** 99.2% (first turn: 70,844 → 431 tokens)

### Import Chain (Active)
```
flask_app.py
    → agent_routes_v4.py
        → agent_worker.py → registry_v3 → meta_tools
        → streaming_agent_worker.py → registry_v3 → credential_injector
    → unified_session_manager.py
```

---

## 🎯 QUICK REFERENCE

### What Gets Called When

| User Action | Flask Route | Worker | Registry | Tools |
|-------------|-------------|--------|----------|-------|
| Submit message | POST /start | agent_worker | registry_v3 | 5 meta-tools |
| First response | GET /stream | streaming_agent_worker | registry_v3 | 5 meta-tools |
| Follow-up | GET /stream | streaming_agent_worker | registry_v3 | 594 tools |
| Tool call | (streaming) | streaming_agent_worker | registry_v3 → execute_tool() | Implementation |

### Key Files to Understand

1. **`agent_routes_v4.py`** - Entry points (POST /start, GET /stream)
2. **`agent_worker.py`** - Initialization + progressive loading
3. **`streaming_agent_worker.py`** - SSE streaming + multi-round tools
4. **`unified_session_manager.py`** - Session state management
5. **`registry_v3.py`** (tools/) - Tool registry (594 tools)

---

**For complete details, see:** `COMPLETE_TOOL_FLOW_ARCHITECTURE_MAP.md`
