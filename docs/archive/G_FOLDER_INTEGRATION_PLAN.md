# G_FOLDER Tool Use Agent Integration Plan
**Date:** November 4, 2025  
**Status:** Architecture Analysis Complete - Ready for Implementation  
**Integration Target:** AI_agents V2_clean branch

---

## Executive Summary

The G_FOLDER `tool_use_agent.py` (3,187 lines) implements a sophisticated Tool Use API with:
- **15 specialized tools** (14 client + 1 server)
- **Extended Thinking** with interleaved thinking capability
- **Comprehensive database schema knowledge** embedded in tool descriptions
- **Real-time streaming** with SSE event capture
- **Multi-calculator routing** (GOD database-driven + Shopify hardcoded)
- **QueryLibrary** with 50+ pre-built SQL queries

**Current State:**
- ✅ G_FOLDER system fully functional as standalone module
- ✅ AI_agents has 622 tools from registry_v3 (general purpose)
- ✅ Progressive tool loading system active (5 meta-tools → full tools)
- ⚠️ G_FOLDER calculator tools NOT integrated with main AI agent

**Integration Goal:**
Merge G_FOLDER's specialized InHouse Print tools into AI_agents' 622-tool ecosystem while preserving both systems' strengths.

---

## Architecture Analysis

### 1. Current AI_agents Tool System

**Registry V3 Architecture:**
```
AI_agents/
├── tools/
│   ├── registry_v3.py (Central tool registry)
│   ├── schemas/ (Static tool definitions - 584 tools)
│   └── implementations/ (Python tool implementations)
└── UI/external/modules/ (Plugin system)
    ├── quote-calculator/ (18 calculator tools)
    │   ├── schema/ (calculator_tools.json, query_library_tools.json)
    │   ├── implementations/ (calculator_wrapper.py, query_library_wrapper.py)
    │   └── backend/ (GOD calculators, Shopify calculators, tool_use_agent.py)
    └── [other modules]/
```

**Tool Loading Flow:**
1. Registry V3 loads from `tools/schemas/` (584 static tools)
2. Module plugin loader discovers `UI/external/modules/*/schema/` folders
3. Loads ALL `*_wrapper.py` files from `implementations/`
4. **Total:** 622 tools (584 static + 38 module plugins)

**Progressive Loading (October 2025):**
- **Turn 1:** Send 5 meta-tools only (99.2% token reduction)
- **Turn 2+:** Send all 622 tools after discovery
- **Implementation:** `agent_worker.py` lines 236-258

### 2. G_FOLDER Tool Use Agent Architecture

**Standalone System:**
```
In_House_SQL/UI/external/modules/quote-calculator/backend/
└── tool_use_agent.py (3,187 lines)
    ├── ToolUseAgent class
    ├── 15 tool definitions (_get_tool_definitions)
    ├── Client tool execution (_execute_client_tool)
    ├── Server tool handling (web_search)
    ├── SSE streaming (process_request)
    └── Event capture system
```

**15 Specialized Tools:**

| Tool | Type | Purpose |
|------|------|---------|
| `get_calculator_requirements` | Client | Parameter guidance for each calculator |
| `execute_sql` | Client | SQL queries with 500+ lines of schema docs |
| `calculate_quote` | Client | Routes to GOD/Shopify calculators |
| `get_available_queries` | Client | List 50+ QueryLibrary queries |
| `get_query_from_library` | Client | Execute pre-built parameterized queries |
| `query_stock_levels` | Client | Inventory management (SQLite) |
| `get_stock_transactions` | Client | Stock movement history |
| `get_reorder_alerts` | Client | Stock shortage alerts |
| `update_stock_level` | Client | ⚠️ WRITE - Update inventory |
| `get_production_pricing` | Client | SQL Server pricing data |
| `update_stock_record` | Client | ⚠️ WRITE - Modify unified_stocks |
| `update_job_record` | Client | ⚠️ WRITE - Modify extracted_jobs |
| `query_ai_extracted_jobs` | Client | Query 219 AI-extracted jobs (SQLite) |
| `web_search` | Server | Anthropic-executed web search |

**Key Features:**
- **Database Schema Embedding:** `execute_sql` tool contains 500+ lines of corrections
  - PaperSize reality: NO Width/Height columns
  - BindType structure: Uses BindTypeDesc, not [Desc]
  - ColourStatus purpose: Urgency, NOT print color
  - TicketNotes as PRIMARY source of truth
- **Calculator Routing:** Intelligent routing between GOD (database) and Shopify (hardcoded)
- **Extended Thinking:** 10,000 token budget with interleaved thinking
- **System Prompt:** Complete InHouse Print assistant personality

### 3. Integration Challenges

**Challenge 1: Dual Tool Execution Paths**
- AI_agents uses `registry_v3.execute_tool(tool_name=...)`
- G_FOLDER uses `self._execute_client_tool(tool_name, tool_input)`
- **Solution:** Wrapper pattern - Map G_FOLDER tools to registry implementations

**Challenge 2: Database Connections**
- G_FOLDER connects to InHousePrintDB (SQL Server FredDEV)
- AI_agents uses ai_infrastructure.db (SQLite)
- **Solution:** Keep separate database connections, route by tool name

**Challenge 3: System Prompt Conflicts**
- G_FOLDER has "Viki the AI quote assistant" prompt (extensive)
- AI_agents has `data_agent_chat` prompt (general purpose)
- **Solution:** Context-aware prompt routing (quote context vs general context)

**Challenge 4: Progressive Loading Compatibility**
- Current system sends 5 meta-tools turn 1, 622 tools turn 2
- G_FOLDER tools add 15 more specialized tools
- **Solution:** Include G_FOLDER tools in progressive loading system

**Challenge 5: Tool Name Collisions**
- G_FOLDER `calculate_quote` vs potential registry tools
- **Solution:** Prefix G_FOLDER tools: `inhouse_calculate_quote`

---

## Integration Strategy

### Option A: Module Plugin Enhancement (RECOMMENDED)

**Approach:** Enhance existing quote-calculator module to expose G_FOLDER tools through registry_v3

**Architecture:**
```
UI/external/modules/quote-calculator/
├── schema/
│   ├── calculator_tools.json (18 existing calculator tools)
│   ├── query_library_tools.json (2 existing meta-tools)
│   └── inhouse_tools.json (NEW - 15 G_FOLDER tools)
├── implementations/
│   ├── calculator_wrapper.py (existing)
│   ├── query_library_wrapper.py (existing)
│   └── inhouse_wrapper.py (NEW - bridges to tool_use_agent.py)
└── backend/
    ├── tool_use_agent.py (existing - becomes library)
    └── [GOD calculators, Shopify calculators, etc.]
```

**Implementation Steps:**

**Step 1: Create `inhouse_tools.json` Schema**
```json
{
  "platform": "inhouse_print",
  "description": "InHouse Print specialized quote and database tools",
  "tools": [
    {
      "name": "inhouse_get_calculator_requirements",
      "description": "Get parameter requirements for InHouse Print calculators...",
      "parameters": { "product_type": {"type": "string", ...} }
    },
    {
      "name": "inhouse_execute_sql",
      "description": "Execute SQL with embedded schema knowledge (500+ lines)...",
      "parameters": { "query": {"type": "string", ...} }
    },
    // ... 13 more tools
  ]
}
```

**Step 2: Create `inhouse_wrapper.py` Implementation**
```python
"""
InHouse Print Tools Wrapper
Bridges registry_v3 to tool_use_agent.py

This wrapper creates a singleton ToolUseAgent instance and routes
tool calls from the registry to the agent's execution methods.
"""

import sys
import os

# Import ToolUseAgent
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)
from tool_use_agent import ToolUseAgent

# Singleton agent instance
_agent_instance = None

def _get_agent():
    """Get or create singleton ToolUseAgent instance"""
    global _agent_instance
    if _agent_instance is None:
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', '..', 
            'config', 'database-config.json'
        )
        _agent_instance = ToolUseAgent(config_path)
    return _agent_instance


def inhouse_get_calculator_requirements(product_type: str, **kwargs):
    """Wrapper for get_calculator_requirements"""
    agent = _get_agent()
    return agent._execute_client_tool(
        'get_calculator_requirements',
        {'product_type': product_type}
    )


def inhouse_execute_sql(query: str, **kwargs):
    """Wrapper for execute_sql"""
    agent = _get_agent()
    return agent._execute_client_tool(
        'execute_sql',
        {'query': query}
    )


def inhouse_calculate_quote(product_type: str, parameters: dict, **kwargs):
    """Wrapper for calculate_quote"""
    agent = _get_agent()
    return agent._execute_client_tool(
        'calculate_quote',
        {'product_type': product_type, 'parameters': parameters}
    )


# ... 12 more wrapper functions
```

**Step 3: Update `agent_worker.py` for Context-Aware Routing**
```python
def run_simple_agent_worker(
    agent_id: str,
    prompt: str,
    lock: threading.Lock,
    session_id: str,
    queue: Queue,
    conversation_history: Optional[List[Dict]] = None,
    ai_client = None,
    user_id: int = 1,
    context: str = 'general'  # NEW: quote_agent vs general
):
    """Enhanced with context-aware system prompt routing"""
    
    # Load registry (now includes 637 tools: 622 general + 15 inhouse)
    from tools import registry_v3
    registry = registry_v3.get_registry()
    
    # Context-aware system prompt selection
    if context == 'quote_agent':
        # Use G_FOLDER's comprehensive quote agent prompt
        system_prompt = """You are Viki, an AI quote assistant for InHouse Print...
        [Full 3,000+ line G_FOLDER system prompt with database schema embedding]
        """
    else:
        # Use general data agent prompt
        system_prompt = ai_client.get_system_prompt('data_agent_chat')
    
    # Progressive loading (same as before)
    tools = _get_progressive_tools(conversation_history, registry)
    
    # Execute with context
    response = ai_client.create_message(
        messages=messages,
        system=system_prompt,  # Context-specific prompt
        tools=tools,
        enable_thinking=True,
        enable_web_search=(context == 'quote_agent')  # Web search for quotes
    )
```

**Step 4: Add Quote Agent Route**
```python
# AI_infrastructure/routes/agent_routes.py

@agent_routes.route('/api/agent/quote', methods=['POST'])
def quote_agent():
    """
    InHouse Print quote agent with specialized tools
    Uses G_FOLDER system prompt and inhouse_* tools
    """
    data = request.json
    prompt = data.get('message', '')
    user_id = data.get('user_id', 1)
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Create SSE queue
    queue = Queue()
    lock = threading.Lock()
    
    # Launch worker with quote_agent context
    thread = threading.Thread(
        target=run_simple_agent_worker,
        args=(
            'quote_agent',  # agent_id
            prompt,
            lock,
            session_id,
            queue,
            None,  # conversation_history
            unified_ai_client,
            user_id,
            'quote_agent'  # CONTEXT - triggers G_FOLDER prompt
        )
    )
    thread.start()
    
    # Stream SSE events
    return Response(
        stream_with_context(_stream_events(queue, session_id)),
        mimetype='text/event-stream'
    )
```

**Pros:**
- ✅ Minimal code duplication
- ✅ Preserves G_FOLDER's specialized knowledge
- ✅ Leverages existing module plugin system
- ✅ Context-aware routing (quote vs general)
- ✅ Progressive loading compatible (637 tools total)

**Cons:**
- ⚠️ Adds 15 tools to progressive loading system (minor overhead)
- ⚠️ Requires careful system prompt management

---

### Option B: Standalone Quote Agent API (Alternative)

**Approach:** Keep G_FOLDER as separate API endpoint, don't integrate with registry

**Architecture:**
```
AI_infrastructure/
├── routes/
│   ├── agent_routes.py (general AI agent - 622 tools)
│   └── quote_agent_routes.py (NEW - InHouse Print quotes only)
└── core/
    └── quote_agent_worker.py (NEW - dedicated worker)

UI/external/modules/quote-calculator/
└── backend/
    └── tool_use_agent.py (unchanged - standalone)
```

**Pros:**
- ✅ Zero changes to existing AI agent
- ✅ G_FOLDER remains independent
- ✅ Clean separation of concerns

**Cons:**
- ❌ Duplicate AI infrastructure (2 separate agents)
- ❌ No cross-tool usage (can't use general tools in quotes)
- ❌ Harder to maintain (2 codebases)

---

## Recommended Implementation: Option A

**Why Option A:**
1. **Unified Experience:** Users get 637 tools in one agent (622 general + 15 specialized)
2. **Cross-Tool Synergy:** Quote agent can use Gmail, Calendar, Tasks, etc.
3. **Maintainability:** Single AI infrastructure to maintain
4. **Progressive Loading:** Existing optimization applies to all tools
5. **Context Awareness:** Same agent, different personality by context

**Implementation Phases:**

### Phase 1: Schema Creation (1-2 hours)
- Create `inhouse_tools.json` with 15 tool definitions
- Copy descriptions from `tool_use_agent.py` `_get_tool_definitions()`
- Add `inhouse_` prefix to all tool names
- Test schema loads in registry_v3

### Phase 2: Wrapper Implementation (2-3 hours)
- Create `inhouse_wrapper.py` with 15 wrapper functions
- Implement singleton ToolUseAgent pattern
- Route calls to `agent._execute_client_tool()`
- Handle Decimal serialization (already solved in G_FOLDER)
- Test wrapper functions individually

### Phase 3: System Prompt Integration (1-2 hours)
- Extract G_FOLDER system prompt to separate file
- Add context parameter to `run_simple_agent_worker()`
- Implement prompt routing logic
- Test with sample quote requests

### Phase 4: Route Creation (1 hour)
- Add `/api/agent/quote` route
- Wire up quote agent worker with context
- Test SSE streaming
- Validate tool execution

### Phase 5: Testing & Validation (2-3 hours)
- Test all 15 inhouse_* tools execute correctly
- Verify database connections work
- Check progressive loading includes new tools
- Validate system prompt switching
- Test cross-tool usage (quote + gmail)

**Total Estimated Time:** 7-11 hours

---

## Testing Plan

### Unit Tests
```python
# test_inhouse_wrapper.py

def test_inhouse_get_calculator_requirements():
    """Test calculator requirements wrapper"""
    result = inhouse_get_calculator_requirements('business_cards')
    assert result['success'] == True
    assert 'quantity' in result['requirements']

def test_inhouse_execute_sql():
    """Test SQL execution wrapper"""
    result = inhouse_execute_sql(
        "SELECT TOP 5 ClientName FROM Orders"
    )
    assert result['success'] == True
    assert 'data' in result

def test_inhouse_calculate_quote():
    """Test quote calculation wrapper"""
    result = inhouse_calculate_quote(
        'business_cards',
        {'quantity': 500, 'stock_type': 'satin_350gsm'}
    )
    assert result['success'] == True
    assert 'cost_inc_gst' in result
```

### Integration Tests
```python
# test_quote_agent_integration.py

def test_registry_loads_inhouse_tools():
    """Verify registry includes 15 inhouse tools"""
    registry = get_registry()
    inhouse_tools = [t for t in registry.tools if t.startswith('inhouse_')]
    assert len(inhouse_tools) == 15

def test_progressive_loading_includes_inhouse():
    """Verify progressive loading works with 637 tools"""
    # Turn 1: 5 meta-tools
    tools_turn1 = _get_progressive_tools([], registry)
    assert len(tools_turn1) == 5
    
    # Turn 2: 637 tools (622 general + 15 inhouse)
    history = [{'role': 'user', 'content': 'test'}]
    tools_turn2 = _get_progressive_tools(history, registry)
    assert len(tools_turn2) == 637

def test_context_routing():
    """Test system prompt switches by context"""
    # Quote context
    prompt_quote = _get_system_prompt('quote_agent')
    assert 'Viki' in prompt_quote
    assert 'InHouse Print' in prompt_quote
    
    # General context
    prompt_general = _get_system_prompt('general')
    assert 'data_agent_chat' in prompt_general
```

### End-to-End Tests
```bash
# Test quote request
curl -X POST http://localhost:5001/api/agent/quote \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quote for 1000 business cards, 350GSM satin, matt cello both sides",
    "user_id": 1
  }'

# Expected: SSE stream with tool_use events for:
# 1. inhouse_get_calculator_requirements
# 2. inhouse_execute_sql (search history)
# 3. inhouse_calculate_quote
# 4. Final response with quote
```

---

## Rollback Plan

**If Integration Fails:**

1. **Immediate Rollback:** Remove `inhouse_tools.json` and `inhouse_wrapper.py`
2. **Registry Refresh:** Restart Flask to reload without inhouse tools
3. **Route Disable:** Comment out `/api/agent/quote` route
4. **Fallback:** G_FOLDER system continues working standalone

**Risk Mitigation:**
- Keep G_FOLDER system unchanged (backend/tool_use_agent.py)
- Only ADD new files (schema, wrapper, route)
- No modifications to existing registry_v3 core
- Context parameter optional (defaults to 'general')

---

## Success Metrics

**Integration Complete When:**
- ✅ Registry shows 637 tools (622 + 15 inhouse)
- ✅ `/api/agent/quote` endpoint responds with SSE stream
- ✅ Tool execution events appear in UI
- ✅ Quotes calculated correctly (match G_FOLDER standalone)
- ✅ System prompt switches based on context
- ✅ Progressive loading includes inhouse tools
- ✅ Cross-tool usage works (quote + gmail)

**Performance Targets:**
- First token latency: <2s (same as current)
- Tool execution time: <5s per tool (unchanged)
- Progressive loading turn 1: <500 tokens (5 meta-tools only)
- Progressive loading turn 2: <80,000 tokens (637 tools)

---

## Documentation Updates

**Files to Create/Update:**

1. `G_FOLDER_INTEGRATION_COMPLETE.md` (this document + results)
2. `UI/external/modules/quote-calculator/README.md` (update architecture)
3. `tools/README.md` (document inhouse_* tools)
4. `AI_infrastructure/routes/README.md` (document /api/agent/quote)
5. `.github/copilot-instructions.md` (add inhouse tools section)

---

## Next Steps

**Ready to Proceed?**

1. **Confirm Strategy:** Option A (Module Plugin Enhancement)
2. **Create Branch:** `feature/g-folder-integration`
3. **Implement Phase 1:** Create `inhouse_tools.json` schema
4. **Test Incrementally:** Verify each phase before moving forward
5. **Deploy:** Merge to V2_clean after all tests pass

**Timeline:**
- **Day 1:** Phases 1-2 (schema + wrapper)
- **Day 2:** Phases 3-4 (system prompt + route)
- **Day 3:** Phase 5 (testing + validation)

**Ready to start?** 🚀

---

**Last Updated:** November 4, 2025  
**Status:** Architecture Complete - Awaiting User Approval  
**Estimated Completion:** 3 days (7-11 hours of work)
