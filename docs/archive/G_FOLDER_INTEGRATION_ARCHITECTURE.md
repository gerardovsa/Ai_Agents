# G_FOLDER Integration Architecture Diagram
**Visual representation of Option A: Module Plugin Enhancement**

---

## Current State (Before Integration)

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI_AGENTS SYSTEM                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              REGISTRY V3 (622 Tools)                       │ │
│  │                                                             │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐  │ │
│  │  │ Static Tools     │  │ Module Plugins (38 tools)    │  │ │
│  │  │ (584 tools)      │  │                               │  │ │
│  │  │                  │  │  • calculator (18)            │  │ │
│  │  │ • google_*       │  │  • query_library (2)          │  │ │
│  │  │ • microsoft_*    │  │  • salesforce (10)            │  │ │
│  │  │ • stripe_*       │  │  • stock-mgmt (8)             │  │ │
│  │  │ • gmail_*        │  │                               │  │ │
│  │  │ • tasks_*        │  │                               │  │ │
│  │  │ • etc.           │  │                               │  │ │
│  │  └──────────────────┘  └──────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▲                                   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │           AGENT WORKER (agent_worker.py)                  │  │
│  │                                                            │  │
│  │  • Progressive Loading (5 → 622 tools)                    │  │
│  │  • Tool Execution via registry.execute_tool()             │  │
│  │  • SSE Streaming                                           │  │
│  │  • Extended Thinking                                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              ▲                                   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │            FLASK ROUTES (agent_routes.py)                 │  │
│  │                                                            │  │
│  │  POST /api/agent/chat  → General AI agent                │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  G_FOLDER (STANDALONE)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  TOOL USE AGENT (tool_use_agent.py - 3,187 lines)         │ │
│  │                                                             │ │
│  │  • 15 Specialized Tools                                    │ │
│  │  • execute_sql (500+ lines schema docs)                    │ │
│  │  • calculate_quote (GOD + Shopify routing)                 │ │
│  │  • QueryLibrary (50+ queries)                              │ │
│  │  • Stock Management (SQLite)                               │ │
│  │  • Extended Thinking (10K budget)                          │ │
│  │  • System Prompt ("Viki the quote assistant")             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ▲                                   │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │         DATABASES                                          │  │
│  │                                                            │  │
│  │  • SQL Server (FredDEV) - Orders, JobTickets             │  │
│  │  • SQLite (stock_data.db) - Inventory, Jobs              │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

❌ PROBLEM: Two separate AI systems with no integration
```

---

## Target State (After Integration - Option A)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED AI_AGENTS SYSTEM                               │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                   REGISTRY V3 (637 Tools - ENHANCED)                     │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌───────────────────┐  ┌──────────────────────────┐ │ │
│  │  │ Static Tools │  │ Module Plugins    │  │ NEW: InHouse Tools       │ │ │
│  │  │ (584)        │  │ (38)              │  │ (15)                     │ │ │
│  │  │              │  │                   │  │                          │ │ │
│  │  │ • google_*   │  │ • calculator (18) │  │ • inhouse_get_calc_req  │ │ │
│  │  │ • microsoft_*│  │ • query_lib (2)   │  │ • inhouse_execute_sql   │ │ │
│  │  │ • stripe_*   │  │ • salesforce (10) │  │ • inhouse_calculate_quo│ │ │
│  │  │ • gmail_*    │  │ • stock-mgmt (8)  │  │ • inhouse_get_queries   │ │ │
│  │  │ • tasks_*    │  │                   │  │ • inhouse_query_library │ │ │
│  │  │ • etc.       │  │                   │  │ • inhouse_query_stocks  │ │ │
│  │  │              │  │                   │  │ • inhouse_stock_trans   │ │ │
│  │  │              │  │                   │  │ • inhouse_reorder_alert │ │ │
│  │  │              │  │                   │  │ • inhouse_update_stock  │ │ │
│  │  │              │  │                   │  │ • inhouse_get_pricing   │ │ │
│  │  │              │  │                   │  │ • inhouse_update_stock_r│ │ │
│  │  │              │  │                   │  │ • inhouse_update_job_rec│ │ │
│  │  │              │  │                   │  │ • inhouse_query_ai_jobs │ │ │
│  │  │              │  │                   │  │ • web_search (server)   │ │ │
│  │  └──────────────┘  └───────────────────┘  └──────────────────────────┘ │ │
│  │                                                                          │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │           NEW: InHouse Wrapper (inhouse_wrapper.py)              │   │ │
│  │  │                                                                   │   │ │
│  │  │  • Bridges registry_v3 → tool_use_agent.py                       │   │ │
│  │  │  • Singleton ToolUseAgent instance                               │   │ │
│  │  │  • Routes calls to agent._execute_client_tool()                  │   │ │
│  │  │  • Handles Decimal serialization                                 │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  │                              │                                           │ │
│  │                              ▼                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │          G_FOLDER Tool Use Agent (Reused as Library)             │   │ │
│  │  │                                                                   │   │ │
│  │  │  • ToolUseAgent class (3,187 lines)                              │   │ │
│  │  │  • _execute_client_tool() method                                 │   │ │
│  │  │  • Database connections (SQL Server + SQLite)                    │   │ │
│  │  │  • Calculator routing (GOD + Shopify)                            │   │ │
│  │  │  • QueryLibrary (50+ queries)                                    │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      ▲                                       │
│                                      │                                       │
│  ┌───────────────────────────────────┴────────────────────────────────────┐ │
│  │            ENHANCED AGENT WORKER (agent_worker.py)                     │ │
│  │                                                                         │ │
│  │  • Progressive Loading (5 → 637 tools)  ◄── 15 more tools!            │ │
│  │  • Tool Execution via registry.execute_tool()                          │ │
│  │  • NEW: Context-Aware System Prompt Routing                            │ │
│  │    - 'quote_agent' → G_FOLDER "Viki" prompt (3K+ lines)               │ │
│  │    - 'general' → data_agent_chat prompt                                │ │
│  │  • SSE Streaming (unchanged)                                            │ │
│  │  • Extended Thinking (unchanged)                                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      ▲                                       │
│                                      │                                       │
│  ┌───────────────────────────────────┴────────────────────────────────────┐ │
│  │              ENHANCED FLASK ROUTES (agent_routes.py)                   │ │
│  │                                                                         │ │
│  │  POST /api/agent/chat   → General AI (622 tools, data_agent prompt)   │ │
│  │  POST /api/agent/quote  → Quote AI (637 tools, Viki prompt)  ◄── NEW! │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘

✅ SOLUTION: Unified 637-tool system with context-aware routing
```

---

## Tool Execution Flow

### General Agent Request (Existing - Unchanged)

```
User: "Send email to john@example.com"
  │
  ▼
POST /api/agent/chat
  │
  ▼
agent_worker.run_simple_agent_worker(
  context='general'  ◄── Uses data_agent_chat prompt
)
  │
  ▼
Registry V3 (622 tools: 584 static + 38 plugins)
  │
  ▼
registry.execute_tool(tool_name='gmail_send_email', ...)
  │
  ▼
Google Workspace implementation
  │
  ▼
✅ Email sent via Gmail API
```

### Quote Agent Request (NEW - Enhanced)

```
User: "Quote for 1000 business cards, 350GSM satin, matt cello"
  │
  ▼
POST /api/agent/quote  ◄── NEW ROUTE
  │
  ▼
agent_worker.run_simple_agent_worker(
  context='quote_agent'  ◄── Uses G_FOLDER "Viki" prompt (3K+ lines)
)
  │
  ▼
Registry V3 (637 tools: 622 general + 15 inhouse)
  │
  ├─── Turn 1: inhouse_get_calculator_requirements('business_cards')
  │      │
  │      ▼
  │    inhouse_wrapper.inhouse_get_calculator_requirements()
  │      │
  │      ▼
  │    ToolUseAgent._execute_client_tool('get_calculator_requirements', ...)
  │      │
  │      ▼
  │    ComprehensiveQuoteCalculator.get_calculator_requirements()
  │      │
  │      ▼
  │    ✅ Returns: {quantity, stock_type, sides, celloglaze, artworks}
  │
  ├─── Turn 2: inhouse_execute_sql("SELECT TOP 10 ... FROM Orders ...")
  │      │
  │      ▼
  │    inhouse_wrapper.inhouse_execute_sql()
  │      │
  │      ▼
  │    ToolUseAgent._execute_client_tool('execute_sql', ...)
  │      │
  │      ▼
  │    InHousePrintDB.execute_query()  ◄── SQL Server FredDEV
  │      │
  │      ▼
  │    ✅ Returns: 10 historical orders with specifications
  │
  └─── Turn 3: inhouse_calculate_quote('business_cards', {...})
         │
         ▼
       inhouse_wrapper.inhouse_calculate_quote()
         │
         ▼
       ToolUseAgent._execute_client_tool('calculate_quote', ...)
         │
         ▼
       Routes to: calculate_business_cards() (Shopify exact pricing)
         │
         ▼
       ✅ Returns: {cost_ex_gst: 98.00, cost_inc_gst: 107.80, ...}
  
Final Response:
  "Based on your previous orders, I recommend our Premium Business Cards:
   - 350GSM Satin with Matt Celloglaze both sides
   - Professional feel that matches your brand standards
   - **Total: $107.80 (inc GST)**
   
   This pricing is consistent with your last order (variance: +2.3%)."
```

### Cross-Tool Usage (NEW - Synergy!)

```
User: "Quote for cards and email it to john@example.com"
  │
  ▼
POST /api/agent/quote
  │
  ▼
Registry V3 (637 tools available)
  │
  ├─── inhouse_calculate_quote('business_cards', ...)  ◄── InHouse tool
  │      │
  │      ▼
  │    ✅ Quote: $107.80
  │
  └─── gmail_send_email(to='john@...', subject='Quote', body='...')  ◄── General tool
         │
         ▼
       ✅ Email sent with quote details

🎉 SYNERGY: Quote agent can use Gmail, Calendar, Tasks, Drive, etc!
```

---

## Progressive Loading with InHouse Tools

### Turn 1 (First User Message)

```
User: "Quote for 1000 business cards"
  │
  ▼
agent_worker (Turn 1: len(conversation_history) == 0)
  │
  ▼
Send 5 meta-tools ONLY:
  • list_available_platforms
  • list_platform_tools
  • get_platform_guide
  • recommend_tools_for_task
  • get_workflow_steps

Token Cost: ~431 tokens (99.2% reduction)
```

### Turn 2+ (After Discovery)

```
AI: list_available_platforms()
  │
  ▼
Returns: ["google_workspace", "microsoft_365", "stripe", "inhouse_print", ...]
  │
  ▼
AI: list_platform_tools("inhouse_print")
  │
  ▼
Returns: ["inhouse_calculate_quote", "inhouse_execute_sql", ...]
  │
  ▼
agent_worker (Turn 2+: len(conversation_history) > 0)
  │
  ▼
Send ALL 637 tools:
  • 584 static tools
  • 38 module plugin tools
  • 15 inhouse tools  ◄── NEW!

Token Cost: ~80,000 tokens (but only after discovery)
```

**Cost Savings:**
- Without progressive loading: 80,000 tokens × $0.003/1K = $0.24 per request
- With progressive loading: 431 tokens × $0.003/1K = $0.0013 per first request
- **Savings:** 98.7% on first turn, $211/day with 1,000 daily requests

---

## Database Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    AI_AGENTS DATABASES                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite: ai_infrastructure.db (data/)                    │  │
│  │                                                           │  │
│  │  • users                                                  │  │
│  │  • user_platform_credentials  ◄── OAuth tokens            │  │
│  │  • sessions                                               │  │
│  │  • conversation_history                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    G_FOLDER DATABASES                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQL Server: FredDEV (Production)                        │  │
│  │                                                           │  │
│  │  • Orders (ClientName, OrderDate)                        │  │
│  │  • JobTickets (TicketNotes, QTY, Cost, Pages)           │  │
│  │  • PaperSize (SizeID, [Desc])  ◄── NO Width/Height!      │  │
│  │  • BindType (BindID, BindTypeDesc)                       │  │
│  │  • ColourStatus (ColourID, ColourDesc)  ◄── Urgency      │  │
│  │  • JobType, PaperType, GSM (Lookup tables)              │  │
│  │  • Quote_DigitalStocks (Production pricing)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite: stock_data.db (Inventory Management)            │  │
│  │                                                           │  │
│  │  • unified_stocks (Current levels, reorder points)       │  │
│  │  • transactions (Stock movements)                        │  │
│  │  • reorder_alerts (Critical/Warning alerts)              │  │
│  │  • extracted_jobs (219 AI-extracted jobs)               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

📌 ROUTING STRATEGY:
• Tools starting with 'inhouse_' → G_FOLDER databases
• All other tools → AI_agents databases
• No conflicts, clean separation
```

---

## File Structure After Integration

```
AI_agents/
├── AI_infrastructure/
│   ├── routes/
│   │   └── agent_routes.py
│   │       ├── /api/agent/chat  (existing - general agent)
│   │       └── /api/agent/quote  (NEW - quote agent)
│   └── core/
│       ├── agent_worker.py
│       │   └── run_simple_agent_worker(context='quote_agent')  ◄── ENHANCED
│       └── unified_ai_client.py (unchanged)
│
├── tools/
│   ├── registry_v3.py (unchanged)
│   ├── schemas/ (584 static tools - unchanged)
│   └── implementations/ (unchanged)
│
├── UI/external/modules/quote-calculator/
│   ├── schema/
│   │   ├── calculator_tools.json (18 existing)
│   │   ├── query_library_tools.json (2 existing)
│   │   └── inhouse_tools.json  ◄── NEW (15 tools)
│   │
│   ├── implementations/
│   │   ├── calculator_wrapper.py (existing)
│   │   ├── query_library_wrapper.py (existing)
│   │   └── inhouse_wrapper.py  ◄── NEW (bridges to tool_use_agent)
│   │
│   └── backend/
│       ├── tool_use_agent.py  ◄── REUSED AS LIBRARY (unchanged)
│       ├── god_calculators/ (unchanged)
│       ├── shopify_calculators/ (unchanged)
│       └── query_library.py (unchanged)
│
├── config/
│   └── database-config.json (unchanged)
│
├── data/
│   └── ai_infrastructure.db (unchanged)
│
└── G_FOLDER_INTEGRATION_PLAN.md  ◄── THIS DOCUMENT

In_House_SQL/  ◄── G_FOLDER project (unchanged)
├── UI/external/modules/quote-calculator/
│   └── backend/
│       ├── tool_use_agent.py (source of truth)
│       └── stock_data.db
└── stocks/
    └── stock_data.db
```

---

## Key Design Decisions

### Decision 1: Why Module Plugin Pattern?

**Options Considered:**
1. ✅ **Module Plugin (CHOSEN):** Add inhouse_tools.json + inhouse_wrapper.py
2. ❌ Standalone API: Keep G_FOLDER separate
3. ❌ Direct Integration: Modify registry_v3 core

**Why Module Plugin Won:**
- Leverages existing infrastructure (no core changes)
- Clean separation (only ADD files, don't modify)
- Rollback friendly (remove 2 files to undo)
- Progressive loading compatible (automatically included)

### Decision 2: Why Singleton ToolUseAgent?

**Problem:** Creating new ToolUseAgent instance per tool call is expensive
- Database connections (SQL Server + SQLite)
- Calculator initialization (6,277 lines of code)
- QueryLibrary loading (50+ queries)

**Solution:** Singleton pattern in `inhouse_wrapper.py`
```python
_agent_instance = None

def _get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ToolUseAgent(config_path)
    return _agent_instance
```

**Benefits:**
- One-time initialization cost
- Persistent database connections
- Shared state across tool calls
- Memory efficient

### Decision 3: Why Context-Aware Routing?

**Problem:** Different use cases need different system prompts
- Quote requests: Need "Viki the quote assistant" (3K+ lines with schema embedding)
- General requests: Need data_agent_chat prompt (concise)

**Solution:** Context parameter in `run_simple_agent_worker()`
```python
if context == 'quote_agent':
    system_prompt = VIKI_QUOTE_PROMPT  # G_FOLDER extensive prompt
else:
    system_prompt = ai_client.get_system_prompt('data_agent_chat')
```

**Benefits:**
- Same agent, different personality
- Appropriate context per request
- No duplicate infrastructure
- Easy to add more contexts later

### Decision 4: Why Prefix 'inhouse_'?

**Problem:** Potential tool name collisions
- G_FOLDER has `calculate_quote`
- Future modules might have similar names

**Solution:** Namespace all G_FOLDER tools with `inhouse_` prefix
```
calculate_quote        → inhouse_calculate_quote
execute_sql            → inhouse_execute_sql
get_available_queries  → inhouse_get_available_queries
```

**Benefits:**
- Zero collision risk
- Clear ownership (inhouse = InHouse Print specific)
- Easy to identify specialized tools
- Follows Python naming conventions

---

## Success Visualization

### Before Integration
```
User: "Quote for 1000 cards"
  │
  ▼
❌ Error: Tool 'calculate_quote' not found in registry
```

### After Integration
```
User: "Quote for 1000 cards"
  │
  ▼
✅ AI discovers inhouse_calculate_quote
  │
  ▼
✅ Executes via wrapper → ToolUseAgent
  │
  ▼
✅ Returns quote: $107.80 (inc GST)
  │
  ▼
✅ Response: "Based on your specifications (350GSM Satin, Matt Cello),
             I recommend Premium Business Cards at $107.80 inc GST.
             This matches your previous orders (variance: +2.3%)."
```

---

## Monitoring & Debugging

### Tool Execution Logs
```python
# inhouse_wrapper.py includes detailed logging

def inhouse_calculate_quote(product_type: str, parameters: dict, **kwargs):
    print(f"🔗 [InHouse Wrapper] calculate_quote called")
    print(f"   Product: {product_type}")
    print(f"   Params: {json.dumps(parameters, indent=2)}")
    
    agent = _get_agent()
    result = agent._execute_client_tool('calculate_quote', {...})
    
    print(f"✅ [InHouse Wrapper] Quote calculated: ${result.get('cost_inc_gst')}")
    return result
```

### Registry Verification
```python
# Verify integration worked
from tools.registry_v3 import get_registry

registry = get_registry()
print(f"Total tools: {len(registry.tools)}")  # Should be 637

inhouse_tools = [t for t in registry.tools if t.startswith('inhouse_')]
print(f"InHouse tools: {len(inhouse_tools)}")  # Should be 15
print(f"Tools: {sorted(inhouse_tools)}")
```

### Health Check Endpoint
```python
# NEW: /api/health/inhouse endpoint

@agent_routes.route('/api/health/inhouse', methods=['GET'])
def health_check_inhouse():
    """Verify InHouse tools are loaded and functional"""
    registry = get_registry()
    
    inhouse_tools = [t for t in registry.tools if t.startswith('inhouse_')]
    
    # Test singleton agent creation
    from UI.external.modules.quote_calculator.implementations import inhouse_wrapper
    agent = inhouse_wrapper._get_agent()
    
    return {
        'status': 'healthy',
        'total_tools': len(registry.tools),
        'inhouse_tools': len(inhouse_tools),
        'inhouse_tool_names': sorted(inhouse_tools),
        'agent_initialized': agent is not None,
        'databases': {
            'sql_server': agent.db.connection is not None,
            'sqlite': agent.stock_tools is not None
        }
    }
```

---

**Last Updated:** November 4, 2025  
**Status:** Architecture Complete - Visual Diagrams Created  
**Next:** Await user approval to proceed with Phase 1 implementation
