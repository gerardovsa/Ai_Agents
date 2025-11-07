# InHouse Print AI Agent Flow - Complete Architecture

**Date:** November 5, 2025  
**Purpose:** Explain how AI discovers and uses InHouse Print tools  

---

## 🔄 Current Flow (How It Works Now)

### Option 1: Direct `/quote` Endpoint (Dedicated Route)

```
User Request → /api/agent/quote route → agent_worker(context='quote_agent')
                                              ↓
                                    Context routing logic
                                              ↓
                                    Loads 'viki_inhouse_agent' prompt
                                              ↓
                                    AI gets 200-line InHouse-specific instructions
                                              ↓
                                    AI sees 6 InHouse tools + knows SQL schema
                                              ↓
                                    AI responds with quote/SQL query
```

**Viki Prompt Contains:**
- 6 tool descriptions (meta-tools + action tools)
- SQL schema corrections (PaperSize, BindType, TicketNotes)
- Workflow guide (5 steps for quotes)
- Natural language mapping examples
- Communication style guide

**Pros:**
- ✅ Dedicated context for printing/quotes
- ✅ SQL schema knowledge embedded
- ✅ Workflow guidance specific to InHouse

**Cons:**
- ❌ Only works via `/quote` endpoint (not general chat)
- ❌ User must know to use `/quote` vs `/chat`
- ❌ General chat has NO knowledge of InHouse tools

---

### Option 2: General `/chat` Endpoint (Current Limitation)

```
User Request → /api/agent/chat route → agent_worker(context=None)
                                             ↓
                                   Uses 'data_agent_chat' prompt
                                             ↓
                       AI gets general tool instructions (959 lines)
                                             ↓
                       AI sees 630 tools (including 6 InHouse tools)
                                             ↓
                       BUT: NO InHouse-specific guidance!
                                             ↓
                       AI may NOT know when to use InHouse tools
```

**Current `data_agent_chat` (tool_usage_system_prompt.md):**
- Generic tool discovery process (list_available_platforms, search_tools)
- NO mention of InHouse Print
- NO SQL schema knowledge
- NO workflow for printing quotes

**Problem:**
- 🔴 AI doesn't know InHouse tools exist unless user mentions "InHouse" or "printing"
- 🔴 Even if AI finds tools, it doesn't know SQL schema quirks
- 🔴 No workflow guidance for quote requests

---

## 🎯 Proposed Solution: Hybrid Approach

### Strategy: Add InHouse Discovery to General Prompt

Update `tool_usage_system_prompt.md` with a **"Domain Expert System"** section:

```markdown
## DOMAIN EXPERT CONTEXTS

When user requests relate to specific domains, request specialized instructions:

### InHouse Print Domain (Quotes, Printing, Stock, SQL Queries)
**Triggers:** quote, print, business cards, flyers, stock levels, inventory, InHouse, paper, GSM
**Action:** 
1. Call `get_domain_instructions('inhouse_print')` to load Viki context
2. Follow Viki's SQL schema guidance and quote workflow
3. Use 6 InHouse tools: query catalog, execute SQL, calculator requirements, calculate quote, stock levels, reorder alerts

**Why:** InHouse Print has custom SQL schema (PaperSize has NO Width/Height, BindType uses BindTypeDesc) 
         and specific quote calculation workflows that require domain knowledge.
```

---

## 🛠️ Implementation Options

### Option A: Tool-Based Discovery (Recommended)

**Create new meta-tool:** `get_domain_instructions(domain_name: str)`

```python
def get_domain_instructions(domain_name: str) -> str:
    """
    Get specialized instructions for domain-specific operations
    
    Args:
        domain_name: 'inhouse_print', 'accounting', 'crm', etc.
    
    Returns:
        Specialized instructions text (appended to system prompt)
    """
    if domain_name == 'inhouse_print':
        return load_prompt('viki_inhouse_agent.txt')  # Return Viki instructions
    # Add other domains as needed
    return "No specialized instructions available"
```

**Flow:**
```
User: "Calculate quote for 1000 business cards"
  ↓
AI recognizes keywords: "quote", "business cards"
  ↓
AI calls: get_domain_instructions('inhouse_print')
  ↓
AI receives 200-line Viki instructions
  ↓
AI now knows: 6 tools, SQL schema, workflow
  ↓
AI executes quote workflow correctly
```

**Pros:**
- ✅ Works in general chat (no need for `/quote` endpoint)
- ✅ Just-in-time instruction loading
- ✅ Scalable to other domains (accounting, CRM, etc.)
- ✅ AI decides when to load instructions

**Cons:**
- ⚠️ Requires new tool implementation
- ⚠️ AI must recognize trigger keywords

---

### Option B: Prompt Keywords (Simpler, Less Flexible)

**Add to `tool_usage_system_prompt.md`:**

```markdown
## SPECIALIZED DOMAINS

### InHouse Print & Printing Quotes
**When user mentions:** quote, print, business cards, flyers, stock, inventory, paper, GSM, binding, InHouse

**Your capabilities:**
1. **Query Library** - Browse 64 pre-built SQL queries:
   - inhouse_get_query_library_catalog(category, limit)
   
2. **Custom SQL** - Execute SQL with schema knowledge:
   - inhouse_execute_sql(query)
   - IMPORTANT: PaperSize table has NO Width/Height columns! Use [Desc] field
   - IMPORTANT: BindType uses BindTypeDesc NOT BindName
   - IMPORTANT: TicketNotes is PRIMARY data source, not Ticket table
   
3. **Calculator Requirements** - Learn parameter options:
   - inhouse_get_calculator_requirements(product_type)
   
4. **Quote Calculation** - Calculate printing quotes:
   - inhouse_calculate_quote(product_type, parameters)
   
5. **Stock Management**:
   - inhouse_query_stock_levels(filters)
   - inhouse_get_reorder_alerts()

**Quote Workflow:**
1. Get calculator requirements first (learn params)
2. Gather context from SQL if needed (customer history)
3. Map natural language to parameters
4. Calculate quote
5. Check stock levels if relevant
```

**Pros:**
- ✅ Simple to implement (just update prompt)
- ✅ No new tools needed
- ✅ Works immediately

**Cons:**
- ❌ Prompt becomes longer (959 → 1100+ lines)
- ❌ Less flexible than tool-based discovery
- ❌ All instructions loaded even if not needed

---

### Option C: Keep Both Endpoints (Current + Improve)

**Enhance `/chat` endpoint with keyword detection:**

```python
@agent_routes_v4.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    message = data.get('message', '')
    
    # Detect InHouse Print keywords
    inhouse_keywords = ['quote', 'print', 'business card', 'flyer', 'stock', 
                        'inventory', 'paper', 'gsm', 'binding', 'inhouse']
    
    context = None
    if any(keyword in message.lower() for keyword in inhouse_keywords):
        context = 'quote_agent'  # Auto-route to Viki prompt
        print(f"🎯 Detected InHouse Print request - using Viki context")
    
    result = agent_worker(
        message=message,
        session_id=session_id,
        user_id=user_id,
        conversation_history=conversation_history,
        ai_client=ai_client,
        context=context  # Auto-route based on keywords
    )
```

**Pros:**
- ✅ Automatic context detection
- ✅ User doesn't need to choose endpoint
- ✅ Viki prompt only loaded when needed
- ✅ Simplest for users

**Cons:**
- ⚠️ Keyword detection may miss some cases
- ⚠️ May trigger false positives

---

## 📊 Comparison Table

| Approach | Complexity | Flexibility | User Experience | Token Efficiency |
|----------|------------|-------------|-----------------|------------------|
| **A: Tool-Based** | Medium | High | Good (auto-discovery) | High (just-in-time) |
| **B: Prompt Keywords** | Low | Low | Good (always available) | Low (always loaded) |
| **C: Keyword Detection** | Low | Medium | Excellent (transparent) | High (auto-route) |
| **Current (Dual Endpoints)** | Low | Low | Poor (must know endpoint) | High (dedicated) |

---

## 🎯 Recommended Implementation

**Hybrid: Option C + Tool for Complex Cases**

### Phase 1: Improve `/chat` with keyword detection (Option C)
```python
# In agent_routes_v4.py - /chat endpoint
inhouse_keywords = ['quote', 'print', 'printing', 'business card', 'flyer', 
                    'booklet', 'stock', 'inventory', 'paper', 'gsm', 
                    'binding', 'corflute', 'inhouse', 'calculate price']

context = 'quote_agent' if any(k in message.lower() for k in inhouse_keywords) else None
```

### Phase 2: Add brief mention in general prompt
```markdown
## SPECIALIZED TOOLS

**InHouse Print Tools** (6 tools for printing quotes & stock):
- If user asks about quotes, printing, stock levels → You'll automatically get InHouse context
- Tools: query_library, execute_sql, calculator_requirements, calculate_quote, stock_levels, reorder_alerts
```

### Phase 3: (Future) Add domain instruction tool for other domains
```python
# Later: For accounting, CRM, etc.
get_domain_instructions('accounting')  # Load accounting-specific context
get_domain_instructions('crm')  # Load CRM-specific context
```

---

## 📝 Current File Locations

**System Prompts:**
- General: `AI_infrastructure/prompts/tool_usage_system_prompt.md` (959 lines)
- Viki (InHouse): `AI_infrastructure/prompts/viki_inhouse_agent.txt` (200 lines)

**Routing Logic:**
- Agent Worker: `AI_infrastructure/core/agent_worker.py` (line ~309) ✅ NOW FIXED
- Chat Route: `AI_infrastructure/routes/agent_routes_v4.py` (line ~100)
- Quote Route: `AI_infrastructure/routes/agent_routes_v4.py` (line ~1064)

**Tools:**
- 6 InHouse tools in `UI/external/modules/inhouse-print/schema/inhouse_tools.json`
- Wrapper: `UI/external/modules/inhouse-print/implementations/inhouse_wrapper.py`

---

## 🚀 Next Steps

**Immediate (Do Now):**
1. ✅ Add context routing back to agent_worker.py (DONE)
2. Add keyword detection to `/chat` route (5 minutes)
3. Test: "Calculate quote for 1000 business cards" in general chat

**Short-term (This Week):**
1. Add brief InHouse mention to general prompt (2 minutes)
2. Document flow for users
3. Add more trigger keywords based on usage

**Long-term (Future):**
1. Create `get_domain_instructions()` tool for other domains
2. Build domain registry system
3. Add domain auto-detection ML model

---

**Status:** Context routing FIXED ✅  
**Next:** Add keyword detection to `/chat` route  
**Impact:** InHouse tools will work in general chat seamlessly
