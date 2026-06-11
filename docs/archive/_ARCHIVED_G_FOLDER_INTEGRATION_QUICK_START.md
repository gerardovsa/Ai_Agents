# G_FOLDER Integration Quick Start Guide
**TL;DR - Executive Summary for Fast Implementation**

---

## What Are We Doing?

**Integrating G_FOLDER's specialized InHouse Print tools into AI_agents' 622-tool ecosystem.**

**Result:** One unified AI agent with 637 tools (622 general + 15 InHouse Print specialized)

---

## Why This Integration?

### Current Problem
- AI_agents: 622 general tools (Gmail, Tasks, Calendar, etc.) ✅
- G_FOLDER: 15 specialized quote tools (Calculator, SQL, Inventory) ✅
- **BUT:** Two separate systems, no integration ❌

### After Integration
- **One agent** with 637 tools
- **Cross-tool synergy:** "Quote for cards AND email it to john@example.com"
- **Context-aware routing:** Quote context → Viki prompt, General context → data_agent prompt
- **Progressive loading:** 5 tools turn 1 → 637 tools turn 2+

---

## Integration Strategy: Module Plugin Enhancement

**Add 2 new files to existing quote-calculator module:**

1. **`inhouse_tools.json`** (Schema - 15 tool definitions)
2. **`inhouse_wrapper.py`** (Implementation - bridges to tool_use_agent.py)

**Modify 1 existing file:**
- **`agent_worker.py`** (Add context-aware system prompt routing)

**Add 1 new route:**
- **`/api/agent/quote`** (Quote agent endpoint with Viki prompt)

**Total Changes:** 3 new files + 1 modified file = **4 files to implement**

---

## Implementation Checklist

### Phase 1: Schema Creation (1-2 hours)
```bash
# Create inhouse_tools.json with 15 tool definitions
cd c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\schema
# Create file with 15 tools: inhouse_get_calculator_requirements, inhouse_execute_sql, etc.
```

**Test:**
```python
from tools.registry_v3 import get_registry
registry = get_registry()
print(f"Total: {len(registry.tools)}")  # Should be 637 (622 + 15)
inhouse = [t for t in registry.tools if t.startswith('inhouse_')]
print(f"InHouse: {len(inhouse)}")  # Should be 15
```

### Phase 2: Wrapper Implementation (2-3 hours)
```bash
# Create inhouse_wrapper.py with 15 wrapper functions
cd c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\implementations
# Implement singleton ToolUseAgent pattern + 15 wrapper functions
```

**Test:**
```python
from UI.external.modules.quote_calculator.implementations import inhouse_wrapper
agent = inhouse_wrapper._get_agent()
result = inhouse_wrapper.inhouse_get_calculator_requirements('business_cards')
print(result)  # Should show calculator parameters
```

### Phase 3: System Prompt Integration (1-2 hours)
```bash
# Modify agent_worker.py to add context-aware routing
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core
# Add context parameter and prompt routing logic
```

**Test:**
```python
# In agent_worker.py
system_prompt = _get_system_prompt(context='quote_agent')
print(len(system_prompt))  # Should be ~3000+ chars (Viki prompt)

system_prompt = _get_system_prompt(context='general')
print(len(system_prompt))  # Should be ~500-800 chars (data_agent prompt)
```

### Phase 4: Route Creation (1 hour)
```bash
# Add /api/agent/quote route
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes
# Add quote agent route to agent_routes.py
```

**Test:**
```bash
# Start Flask
BISTART

# Test quote endpoint
curl -X POST http://localhost:5001/api/agent/quote \
  -H "Content-Type: application/json" \
  -d '{"message": "Quote for 1000 business cards", "user_id": 1}'

# Should return SSE stream with tool_use events
```

### Phase 5: End-to-End Testing (2-3 hours)
```bash
# Test all 15 inhouse_* tools
# Test system prompt switching
# Test progressive loading includes new tools
# Test cross-tool usage (quote + gmail)
```

---

## File Locations Reference

### New Files to Create

**1. Schema File:**
```
c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\schema\inhouse_tools.json
```

**2. Wrapper File:**
```
c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\implementations\inhouse_wrapper.py
```

### Files to Modify

**1. Agent Worker:**
```
c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\core\agent_worker.py
```
- Add `context` parameter to `run_simple_agent_worker()`
- Add system prompt routing logic

**2. Agent Routes:**
```
c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\agent_routes.py
```
- Add `/api/agent/quote` endpoint

---

## 15 InHouse Tools to Implement

| Tool Name | Wrapper Function | Purpose |
|-----------|------------------|---------|
| `inhouse_get_calculator_requirements` | `inhouse_get_calculator_requirements(product_type)` | Parameter guidance |
| `inhouse_execute_sql` | `inhouse_execute_sql(query)` | SQL with schema docs |
| `inhouse_calculate_quote` | `inhouse_calculate_quote(product_type, parameters)` | Quote calculation |
| `inhouse_get_available_queries` | `inhouse_get_available_queries(category)` | List QueryLibrary |
| `inhouse_get_query_from_library` | `inhouse_get_query_from_library(query_name, parameters)` | Execute query |
| `inhouse_query_stock_levels` | `inhouse_query_stock_levels(filters)` | Inventory query |
| `inhouse_get_stock_transactions` | `inhouse_get_stock_transactions(stock_id, limit)` | Stock history |
| `inhouse_get_reorder_alerts` | `inhouse_get_reorder_alerts()` | Stock alerts |
| `inhouse_update_stock_level` | `inhouse_update_stock_level(stock_id, new_level, reason)` | Update inventory |
| `inhouse_get_production_pricing` | `inhouse_get_production_pricing(filters)` | SQL Server pricing |
| `inhouse_update_stock_record` | `inhouse_update_stock_record(stock_id, updates, reason)` | Modify stock |
| `inhouse_update_job_record` | `inhouse_update_job_record(ticket_id, updates, reason)` | Modify job |
| `inhouse_query_ai_extracted_jobs` | `inhouse_query_ai_extracted_jobs(sql_query)` | Query 219 jobs |
| `inhouse_web_search` | (Server tool - Anthropic executes) | Web search |

**Total:** 13 client tools + 1 server tool + 1 meta-tool wrapper = 15 tools

---

## Wrapper Template

```python
"""
InHouse Print Tools Wrapper
Bridges registry_v3 to tool_use_agent.py
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
            os.path.dirname(__file__), '..', '..', '..', '..', 
            'config', 'database-config.json'
        )
        _agent_instance = ToolUseAgent(config_path)
    return _agent_instance

def inhouse_get_calculator_requirements(product_type: str, **kwargs):
    """Get calculator parameter requirements"""
    agent = _get_agent()
    return agent._execute_client_tool(
        'get_calculator_requirements',
        {'product_type': product_type}
    )

def inhouse_execute_sql(query: str, **kwargs):
    """Execute SQL with embedded schema knowledge"""
    agent = _get_agent()
    return agent._execute_client_tool(
        'execute_sql',
        {'query': query}
    )

# ... 11 more wrapper functions
```

---

## Context-Aware Routing Pattern

```python
# In agent_worker.py

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
    
    # Load registry
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
        enable_web_search=(context == 'quote_agent')
    )
```

---

## Testing Commands

### Registry Verification
```python
python -c "from tools.registry_v3 import get_registry; r = get_registry(); print(f'Total: {len(r.tools)}'); inhouse = [t for t in r.tools if t.startswith(\'inhouse_\')]; print(f'InHouse: {len(inhouse)}, Tools: {sorted(inhouse)}')"
```

**Expected Output:**
```
Total: 637
InHouse: 15, Tools: ['inhouse_calculate_quote', 'inhouse_execute_sql', ...]
```

### Wrapper Test
```python
python -c "from UI.external.modules.quote_calculator.implementations.inhouse_wrapper import _get_agent, inhouse_get_calculator_requirements; agent = _get_agent(); print('Agent initialized:', agent is not None); result = inhouse_get_calculator_requirements('business_cards'); print('Result:', result['success'])"
```

**Expected Output:**
```
Agent initialized: True
Result: True
```

### Quote API Test
```bash
curl -X POST http://localhost:5001/api/agent/quote \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quote for 1000 business cards, 350GSM satin, matt cello both sides",
    "user_id": 1
  }'
```

**Expected Output:**
```
data: {"type":"thinking_block","content":"Analyzing quote request..."}
data: {"type":"tool_use","tool_name":"inhouse_get_calculator_requirements"}
data: {"type":"tool_result","tool_name":"inhouse_get_calculator_requirements","success":true}
data: {"type":"tool_use","tool_name":"inhouse_calculate_quote"}
data: {"type":"tool_result","tool_name":"inhouse_calculate_quote","success":true}
data: {"type":"content_delta","text":"Based on your specifications..."}
data: {"type":"complete"}
```

---

## Rollback Plan

**If something breaks:**

1. **Remove Schema:**
   ```bash
   rm c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\schema\inhouse_tools.json
   ```

2. **Remove Wrapper:**
   ```bash
   rm c:\Users\gpoli\GIT\AI_agents\UI\external\modules\quote-calculator\implementations\inhouse_wrapper.py
   ```

3. **Revert agent_worker.py:**
   ```bash
   git checkout agent_worker.py
   ```

4. **Restart Flask:**
   ```bash
   Stop-Process -Name python -Force
   BISTART
   ```

**System returns to 622 tools (no InHouse tools).**

---

## Success Criteria

**Integration complete when:**
- ✅ Registry shows 637 tools (622 + 15)
- ✅ `/api/agent/quote` endpoint works
- ✅ Quote calculations match G_FOLDER standalone
- ✅ System prompt switches by context
- ✅ Progressive loading includes inhouse tools
- ✅ Cross-tool usage works (quote + gmail)

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Schema | 1-2 hours | 2 hours |
| Phase 2: Wrapper | 2-3 hours | 5 hours |
| Phase 3: System Prompt | 1-2 hours | 7 hours |
| Phase 4: Route | 1 hour | 8 hours |
| Phase 5: Testing | 2-3 hours | 11 hours |
| **TOTAL** | **7-11 hours** | **~2 days** |

---

## Key Decisions Reference

**Q: Why not integrate G_FOLDER directly into registry core?**  
A: Module plugin pattern is safer - only ADD files, no core changes, easy rollback.

**Q: Why singleton ToolUseAgent?**  
A: Database connections are expensive. One instance shared across all tool calls.

**Q: Why prefix 'inhouse_'?**  
A: Avoids tool name collisions, clear namespace, follows conventions.

**Q: Why context-aware routing?**  
A: Different use cases need different system prompts. Quote needs Viki's 3K+ line prompt with schema embedding.

**Q: Why keep G_FOLDER tool_use_agent.py unchanged?**  
A: Reuse as library. Wrapper bridges to it. Zero duplication, minimal changes.

---

## Next Steps

1. ✅ Read `G_FOLDER_INTEGRATION_PLAN.md` (architecture details)
2. ✅ Read `G_FOLDER_INTEGRATION_ARCHITECTURE.md` (visual diagrams)
3. ✅ Read this Quick Start Guide
4. 🔲 Approve strategy
5. 🔲 Create feature branch: `feature/g-folder-integration`
6. 🔲 Implement Phase 1: `inhouse_tools.json`
7. 🔲 Implement Phase 2: `inhouse_wrapper.py`
8. 🔲 Implement Phase 3: Context routing in `agent_worker.py`
9. 🔲 Implement Phase 4: `/api/agent/quote` route
10. 🔲 Implement Phase 5: Full testing suite
11. 🔲 Merge to V2_clean

**Ready to start Phase 1?** 🚀

---

**Last Updated:** November 4, 2025  
**Status:** Quick Start Guide Complete  
**Next:** Await user approval to begin implementation
