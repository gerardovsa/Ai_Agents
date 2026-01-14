# 🗺️ AI TOOL DISCOVERY PATH - COMPLETE JOURNEY MAP

## What the AI Reads and When

This document traces the EXACT path the AI follows from startup to tool execution, showing every file read and every decision point.

---

## 📍 JOURNEY START: User Sends Message

**User Action:** Types message in chat and hits send  
**Location:** Browser → Flask endpoint `/api/v4/stream-agent`  
**File:** `AI_infrastructure/routes/agent_routes_v4.py`

---

## 🔄 PHASE 1: REQUEST INITIALIZATION (Lines 970-1000)

### What Happens:
```python
# Extract user info
user_id = request.json.get('user_id')
session_id = request.json.get('session_id')
user_message = request.json.get('message')
```

### Files Read:
1. **Database Query** (Line 985-1000):
   ```sql
   SELECT email FROM users WHERE id = %s
   ```
   - **Purpose:** Fetch user's email address
   - **Location:** `users` table in Supabase
   - **Result Stored In:** `user_email` variable

---

## 🔄 PHASE 2: USER CONTEXT CONSTRUCTION (Lines 1150-1330)

### 2.1 Weather Data (Lines 1150-1180)
**What AI Reads:**
- User's location (from database)
- Weather API response (if configured)
- **Result:** Temperature, condition, season

### 2.2 User Preferences (Lines 1190-1220)
**Database Query:**
```sql
SELECT * FROM user_preferences WHERE user_id = %s
```
**What AI Reads:**
- `nickname` - User's preferred name
- `preferred_platform` - Microsoft 365 or Google Workspace
- `communication_style` - professional/casual/friendly
- `detail_level` - brief/standard/detailed
- `preferred_tools` - JSON array of tool preferences
- `ai_memories` - JSON array of past interactions

### 2.3 Platform Detection (Lines 1240-1280)
**Decision Tree:**
```
IF user_prefs.preferred_platform == "microsoft_365":
    → Set mandatory_platform = "Microsoft 365 Suite"
    → Build instructions: "Use microsoft_outlook_*, microsoft_word_*, etc."
ELSE IF user_prefs.preferred_platform == "google_workspace":
    → Set mandatory_platform = "Google Workspace"
    → Build instructions: "Use gmail_*, google_docs_*, google_sheets_*, etc."
ELSE:
    → Set mandatory_platform = "Auto (Check Connected Platforms)"
```

### 2.4 Email Detection Rule (Line 1305)
**Special Case - InHouse Print Staff:**
```python
# FROM SYSTEM PROMPT (loaded later):
if email_address contains "_@inhouseprint.com.au":
    → MUST prioritize InHouse tools first
    → Use inhouse_get_domain_guide() before other tools
```

### 2.5 Final Context Block Built (Lines 1295-1330)
**What Gets Assembled:**
```
═══════════════════════════════════════════════════════════════
USER CONTEXT

User: [Nickname from DB]
User Email Address: [Email from DB - Line 1000]
Location: Sydney, NSW, Australia
Current Time: Monday, 16 Dec 2024 10:30 AM AEDT
Season: December (Summer)
Weather: 28°C (82°F), Sunny

MANDATORY PLATFORM USE: Microsoft 365 Suite

Additional Preferences (YOU MUST FOLLOW THESE):
- Communication Style: professional
- Detail Level: standard

Key Memories About This User:
- [Memory 1 from ai_memories JSON]
- [Memory 2 from ai_memories JSON]
═══════════════════════════════════════════════════════════════
```

---

## 🔄 PHASE 3: SYSTEM PROMPT LOADING (Line 204)

**File:** `AI_infrastructure/core/unified_ai_client.py`  
**Function:** `_get_tool_usage_instructions()`

### What Gets Read:
```python
prompt_path = Path(__file__).parent.parent / 'prompts' / 'tool_usage_system_prompt.md'
with open(prompt_path, 'r', encoding='utf-8') as f:
    return f.read()  # Returns 1,152 lines of instructions
```

**File Loaded:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

### What AI Learns Here:
1. **USER CONTEXT Template** (Lines 4-39):
   - How to interpret nickname, email, location, time, weather
   - **Email Detection Rule:** `if "_@inhouseprint.com.au" then prioritize InHouse tools`
   - Platform preferences (Microsoft vs Google)

2. **Identity & Role** (Lines 41-67):
   - "You are a powerful AI AGENT"
   - Cognitive process: THINK → PLAN → EXECUTE → VALIDATE → DELIVER

3. **Reality Check Rules** (Lines 69-95):
   - Decision tree for when to use tools vs respond directly
   - "Can I accomplish this WITHOUT calling tools?"

4. **Action Definitions** (Lines 97-150):
   - What requires tools (external data, creating resources, specialized calculations)
   - What doesn't require tools (explaining concepts, basic math)

5. **Tool Ecosystem Architecture** (Lines 152-280):
   - **4-Layer System:**
     - LAYER 1: Navigation tools (list_platform_tools, search_tools, **inhouse_get_domain_guide**)
     - LAYER 2: Guidance tools (platform_guide, inhouse_calculator_guide, etc.)
     - LAYER 3: Specification tools (get_tool_schema)
     - LAYER 4: Execution tools (execute_tool, direct tool calls)

6. **Platform Tool Discovery** (Lines 244-280):
   - **Microsoft 365:**
     - Email: `list_platform_tools("microsoft_outlook")`
     - Documents: `list_platform_tools("microsoft_word")`
     - Spreadsheets: `list_platform_tools("microsoft_excel")`
   - **Google Workspace:**
     - Email: `list_platform_tools("gmail")`
     - Documents: `list_platform_tools("google_docs")`
     - Spreadsheets: `list_platform_tools("google_sheets")`

7. **Execution Rules** (Lines 282-400):
   - RULE #1: Execute tools FIRST, then write response
   - RULE #2: ALWAYS get schema before executing
   - RULE #4: Report only what actually happened
   - RULE #5: Never end without suggesting next steps
   - RULE #6: Reference stated tools (memory technique)

8. **InHouse Print Trigger Keywords** (Lines 950-980):
   ```
   Watch for these keywords:
   - Quotes/Pricing: "quote", "calculate", "price", "cost"
   - Clients/Customers: "client", "customer", "ABC Company"
   - Orders/Jobs: "order", "job ticket", "printing history"
   - Database: "Fred", "database", "query", "look up"
   - Stock: "stock levels", "paper inventory"
   - Invoicing: "Xero", "invoice", "billing"
   ```

9. **InHouse Mandatory Workflow** (Lines 982-1050):
   ```python
   # ALWAYS START HERE:
   inhouse_get_domain_guide()
   # Returns which domain + next tool to call
   
   # TIER 2: Domain-specific guides
   inhouse_calculator_guide()  # Before calculating quotes
   inhouse_query_guide()       # Before SQL queries
   inhouse_database_guide()    # Before custom SQL (GET SCHEMA!)
   
   # TIER 3: Action tools
   calculate_business_cards()
   execute_query_library()
   inhouse_execute_query()
   ```

---

## 🔄 PHASE 4: TOOL REGISTRY INITIALIZATION (Happens on Server Startup)

**File:** `tools/registry_v3.py`  
**Triggered:** When Flask app starts (not per request)

### 4.1 Schema Loading (Lines 75-110)
**What Gets Read:**
```python
schemas_dir = self.tools_dir / "schemas"
schema_files = list(schemas_dir.glob("*.json"))  # ~90 JSON files
```

**Files Read:**
- `tools/schemas/gmail.json`
- `tools/schemas/microsoft_outlook.json`
- `tools/schemas/google_docs.json`
- `tools/schemas/calculator_tools.json`
- ... 86 more JSON schema files

**What Gets Loaded:**
- Tool names
- Descriptions
- **Short descriptions** (20-60 chars) ← KEY FOR DISCOVERY
- Input schemas (parameters, types, required fields)
- Platform tags

### 4.2 Implementation Loading (Lines 200-400)
**Google Workspace Tools (Lines 210-280):**
```python
# Load from google_workspace/
- google_workspace.gmail (46 functions)
- google_workspace.google_docs (47 functions)
- google_workspace.google_sheets (28 functions)
- google_workspace.google_drive (22 functions)
... etc
```

**Microsoft 365 Tools (Lines 290-350):**
```python
# Load from tools/implementations/
- microsoft_outlook_tools.py (30 functions)
- microsoft_excel_tools.py (33 functions)
- microsoft_word_tools.py (34 functions)
- microsoft_teams_tools.py (28 functions)
... etc
```

**InHouse Print Tools (Lines 600-700):**
```python
# Module Plugin System
[LOAD] Loading module: inhouse-print
  - inhouse_tools.json (11 tools)
  - inhouse_wrapper.py (11 implementations)
    - inhouse_get_domain_guide()
    - inhouse_calculator_guide()
    - inhouse_execute_sql()
    - inhouse_calculate_quote()
    ... etc

[LOAD] Loading module: quote-calculator
  - calculator_tools.json (31 tools)
  - query_library_tools.json (2 tools)
  - calculator_wrapper.py (33 implementations)
    - calculate_business_cards()
    - calculate_flyers_god()
    - get_available_queries()
    - execute_query_library()
    ... etc
```

**Final Registry State:**
- **1,032 tools loaded**
- **40+ platforms**
- **646+ accessible to AI** (some excluded for security)

---

## 🔄 PHASE 5: AI RECEIVES FIRST MESSAGE

**What AI Has at This Point:**
1. ✅ User context block (email, location, weather, platform, preferences)
2. ✅ System prompt (1,152 lines of instructions)
3. ✅ Tool registry reference (knows tools exist but hasn't seen them yet)
4. ✅ Meta-tools available (list_platform_tools, search_tools, get_tool_schema)

**What AI DOESN'T Have Yet:**
- ❌ List of specific tools (hasn't called discovery yet)
- ❌ Tool schemas (hasn't called get_tool_schema yet)
- ❌ Email content (hasn't called gmail_list_messages yet)
- ❌ Database records (hasn't queried Fred yet)

---

## 🔄 PHASE 6: TOOL DISCOVERY (First Time AI Needs a Tool)

### Example: User says "Send an email"

### 6.1 AI Reads System Prompt Section (Lines 244-280)
**Decision:**
```
User context says: MANDATORY PLATFORM USE: Microsoft 365 Suite
System prompt says: "Email: list_platform_tools('microsoft_outlook')"
→ AI decides to discover Outlook tools
```

### 6.2 AI Calls: `list_platform_tools("microsoft_outlook")`

**File Executed:** `tools/implementations/meta_tools.py`  
**Function:** `list_platform_tools()` (Lines 44-200)

**What This Function Does:**
```python
# Step 1: Load registry
from tools.registry_v3 import get_registry
registry = get_registry()  # Has all 1,032 tools in memory

# Step 2: Match platform
platform_lower = "microsoft_outlook"
tool_list = []

# Step 3: Find matching tools
for tool_name, tool in registry.tools.items():
    if tool_name.lower().startswith("microsoft_outlook_"):
        tool_list.append({
            "name": tool_name,
            "short_description": tool.get("short_description", tool.get("description", ""))
        })

# Step 4: Return results
return {
    "success": True,
    "platform": "microsoft_outlook",
    "tool_count": 30,
    "tools": tool_list  # List of 30 Outlook tools with SHORT descriptions
}
```

**What AI Receives (Example):**
```json
{
  "success": true,
  "platform": "microsoft_outlook",
  "tool_count": 30,
  "tools": [
    {
      "name": "microsoft_outlook_list_messages",
      "short_description": "List recent emails from inbox with filters"
    },
    {
      "name": "microsoft_outlook_read_message",
      "short_description": "Read full email content by message ID"
    },
    {
      "name": "microsoft_outlook_create_draft",
      "short_description": "Create draft email without sending"
    },
    ... 27 more tools
  ]
}
```

### 6.3 AI Writes to User (Memory Anchor)
**Following RULE #6 from system prompt:**
```
I found these Microsoft Outlook tools:
  1. microsoft_outlook_list_messages - List recent emails
  2. microsoft_outlook_read_message - Read full email content
  3. microsoft_outlook_create_draft - Create draft email
  4. microsoft_outlook_send_email - Send email (EXCLUDED for security)
  ... (showing first 10 of 30)

Which tool would you like me to use?
```

**Why This Matters:**
- AI creates **memory anchor** by numbering the list
- Can reference "#3 from above" later without re-discovering
- Saves tokens and reduces redundant tool calls

---

## 🔄 PHASE 7: TOOL SCHEMA RETRIEVAL (Before Execution)

### User says: "Use #3 to create a draft"

### 7.1 AI Reads System Prompt Rule #2 (Lines 290-320)
**Instruction:**
```
RULE #2: ALWAYS GET SCHEMA BEFORE EXECUTING (MANDATORY!)
1. Discover tool exists ✓ (already done)
2. GET SCHEMA FIRST: get_tool_schema("tool_name") ← MUST DO THIS
3. Read required vs optional parameters
4. Execute tool with correct parameters
```

### 7.2 AI Calls: `get_tool_schema("microsoft_outlook_create_draft")`

**File Executed:** `tools/implementations/meta_tools.py`  
**Function:** `get_tool_schema()` (Lines 850-900)

**What This Function Does:**
```python
# Step 1: Load registry
registry = get_registry()

# Step 2: Find tool
tool = registry.tools.get("microsoft_outlook_create_draft")

# Step 3: Return full schema
return {
    "success": True,
    "tool_name": "microsoft_outlook_create_draft",
    "description": "Create a draft email in Microsoft Outlook...",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient email address"
            },
            "subject": {
                "type": "string",
                "description": "Email subject line"
            },
            "body": {
                "type": "string",
                "description": "Email body content (plain text or HTML)"
            },
            "cc": {
                "type": "string",
                "description": "CC recipients (optional)"
            }
        },
        "required": ["to", "subject", "body"]  # ← AI LEARNS WHAT'S REQUIRED
    }
}
```

**What AI Learns:**
- ✅ Parameter names: `to`, `subject`, `body`, `cc`
- ✅ Required fields: `to`, `subject`, `body` (MUST provide these)
- ✅ Optional fields: `cc` (can omit)
- ✅ Data types: All strings
- ✅ Descriptions: What each parameter does

---

## 🔄 PHASE 8: TOOL EXECUTION

### 8.1 AI Constructs Tool Call
**Based on schema from Phase 7:**
```python
microsoft_outlook_create_draft(
    to="john@example.com",      # Required
    subject="Meeting Follow-up", # Required
    body="Hi John, ..."          # Required
    # cc omitted (optional)
)
```

### 8.2 Tool Execution Path
**File:** `tools/registry_v3.py`  
**Function:** `execute_tool()` (Lines 750-850)

```python
# Step 1: Find implementation
impl = registry.implementations.get("microsoft_outlook_create_draft")

# Step 2: Inject credentials
params = {
    "to": "john@example.com",
    "subject": "Meeting Follow-up",
    "body": "Hi John, ...",
    "_user_id": user_id,  # ← Injected automatically
    "_injected_credentials": {...}  # ← From database
}

# Step 3: Call actual implementation
result = impl(**params)

# Step 4: Return result
return {
    "success": True,
    "draft_id": "AAMkAGI1...",
    "message": "Draft created successfully"
}
```

### 8.3 AI Reads Result and Reports to User
**Following RULE #4 from system prompt (Lines 350-380):**
```
Actions Taken:

1. microsoft_outlook_create_draft
   - Resource: "Meeting Follow-up" email draft
   - Draft ID: AAMkAGI1... (ACTUAL ID from tool result)
   - URL: https://outlook.office.com/mail/... (ACTUAL URL)
   - Status: ✅ Success

Your draft has been created. Would you like to:
1. Edit the draft
2. Send the draft
3. Create another draft
4. End - I'm satisfied
```

---

## 🔄 SPECIAL PATH: INHOUSE PRINT WORKFLOW

### When User Email Contains "@inhouseprint.com.au"

### Phase 1: Email Detection (Line 6 of system prompt)
```python
# AI reads from USER CONTEXT:
User Email Address: gerardo@inhouseprint.com.au

# AI reads from system prompt line 6:
if "_@inhouseprint.com.au" in email_address:
    → MUST prioritize InHouse tools first
    → DO NOT use external systems until checking InHouse
```

### Phase 2: Trigger Keyword Detection (Lines 950-980)
**User says:** "Calculate a quote for 500 business cards"

**AI Reads Trigger Keywords:**
```
- "calculate" ← Matches "Quotes/Pricing" category
- "quote" ← Matches "Quotes/Pricing" category
- "business cards" ← Printing product
→ TRIGGER: InHouse Print operation detected
```

### Phase 3: Mandatory First Call (Lines 982-1000)
**AI MUST call:**
```python
inhouse_get_domain_guide()
```

**File Executed:** `UI/modules_external/inhouse-print/backend/inhouse_guide_wrapper.py`  
**Returns:**
```json
{
  "success": true,
  "domain": "calculator",
  "next_tool": "inhouse_calculator_guide",
  "reason": "User wants to calculate a quote - use calculator domain",
  "workflow": "1. Call inhouse_calculator_guide() 2. Call calculate_business_cards()"
}
```

### Phase 4: Domain-Specific Guide (Lines 1010-1030)
**AI calls:**
```python
inhouse_calculator_guide()
```

**Returns:**
```json
{
  "success": true,
  "available_calculators": [
    "calculate_business_cards",
    "calculate_flyers_god",
    "calculate_booklets",
    "calculate_letterheads_god",
    ... 27 more
  ],
  "recommended_calculator": "calculate_business_cards",
  "next_step": "Call get_tool_schema('calculate_business_cards')"
}
```

### Phase 5: Get Calculator Schema
**AI calls:**
```python
get_tool_schema("calculate_business_cards")
```

**Returns full parameter requirements:**
```json
{
  "required": ["quantity", "finish_size", "stock_type", "sides", "lamination"],
  "optional": ["spot_uv", "foiling", "edge_painting", ...]
}
```

### Phase 6: Execute Calculator
**AI calls:**
```python
calculate_business_cards(
    quantity=500,
    finish_size="90x55mm",
    stock_type="400gsm",
    sides="double",
    lamination="matt"
)
```

**Returns:**
```json
{
  "success": true,
  "quote_total": 245.50,
  "unit_price": 0.49,
  "breakdown": {
    "printing": 150.00,
    "stock": 50.00,
    "lamination": 45.50
  },
  "recommended_retail": 350.00
}
```

---

## 📊 COMPLETE READING ORDER SUMMARY

### Startup (Once per server start):
1. `tools/registry_v3.py` - Load registry
2. `tools/schemas/*.json` - Load all 90 schema files
3. `tools/implementations/*.py` - Load all implementation modules
4. `UI/modules_external/*/backend/*.py` - Load InHouse Print modules

### Per Request (Every user message):
1. `users` table - Fetch user email
2. `user_preferences` table - Fetch preferences, platform, style
3. `AI_infrastructure/prompts/tool_usage_system_prompt.md` - Load 1,152 line instructions
4. `AI_infrastructure/routes/agent_routes_v4.py` - Build USER CONTEXT block

### Tool Discovery (First time using platform):
1. `tools/implementations/meta_tools.py::list_platform_tools()` - Get tool list with short descriptions
2. AI writes numbered list to user (memory anchor)

### Tool Preparation (Before each execution):
1. `tools/implementations/meta_tools.py::get_tool_schema()` - Get parameter requirements
2. AI constructs correct parameters

### Tool Execution:
1. `tools/registry_v3.py::execute_tool()` - Route to implementation
2. `tools/implementations/[platform]_tools.py` - Execute actual tool
3. Return result to AI
4. AI reports to user with real IDs/URLs

---

## 🎯 KEY INSIGHTS

### Why Short Descriptions Matter:
- **Token Efficiency:** 20-60 chars vs 200+ chars
- **Discovery Speed:** AI can scan 50 tools in one response
- **Memory Anchoring:** Numbered lists with concise descriptions create reference points

### Why Email Detection Matters:
- **Routing Logic:** InHouse staff get specialized workflow
- **Tool Prioritization:** Check Fred database before external sources
- **Context Awareness:** AI knows user's business domain

### Why Get Schema First Matters:
- **Parameter Accuracy:** No guessing required/optional fields
- **Type Safety:** Knows if parameter is string/array/object
- **Error Prevention:** 90% fewer "missing parameter" errors

### Why USER CONTEXT Matters:
- **Platform Routing:** Microsoft vs Google tool selection
- **Personalization:** Nickname, communication style, detail level
- **Contextual Awareness:** Time, weather, season influence recommendations
- **Memory Continuity:** AI recalls past interactions and preferences

---

## 🔍 VISUAL FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ USER SENDS MESSAGE: "Calculate 500 business cards"             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: FETCH USER DATA                                       │
│ - Query users table (email)                                     │
│ - Query user_preferences (platform, style, memories)           │
│ - Build USER CONTEXT block                                     │
│   → User Email: gerardo@inhouseprint.com.au ✓                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: LOAD SYSTEM PROMPT                                    │
│ - Read tool_usage_system_prompt.md (1,152 lines)               │
│ - AI learns:                                                    │
│   → Email detection: @inhouseprint.com.au ✓                    │
│   → Trigger keywords: "calculate", "quote" ✓                   │
│   → Mandatory workflow: inhouse_get_domain_guide() first       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: KEYWORD MATCHING                                      │
│ - AI detects "calculate" + "quote" + "business cards"          │
│ - Matches InHouse trigger keywords                             │
│ - Decides: Use InHouse domain workflow                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: DOMAIN DISCOVERY (TIER 1)                             │
│ - AI calls: inhouse_get_domain_guide()                         │
│ - Returns: domain="calculator", next="inhouse_calculator_guide"│
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: CALCULATOR GUIDE (TIER 2)                             │
│ - AI calls: inhouse_calculator_guide()                         │
│ - Returns: 31 calculators, recommends "calculate_business_cards"│
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6: SCHEMA RETRIEVAL (TIER 3)                             │
│ - AI calls: get_tool_schema("calculate_business_cards")        │
│ - Returns: Required params (quantity, size, stock, sides, etc.)│
│ - AI learns what parameters are needed                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7: EXECUTION (TIER 4)                                    │
│ - AI calls: calculate_business_cards(quantity=500, ...)        │
│ - Returns: quote_total=$245.50, breakdown, recommendations     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8: REPORT TO USER                                        │
│ - AI shows: Quote total, breakdown, next steps                 │
│ - Offers: Create invoice, save quote, modify, end              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 FILES READ IN ORDER (Complete List)

### Server Startup:
1. `tools/registry_v3.py`
2. `tools/schemas/gmail.json`
3. `tools/schemas/microsoft_outlook.json`
4. `tools/schemas/google_docs.json`
5. ... (87 more JSON schemas)
6. `google_workspace/gmail/__init__.py`
7. `google_workspace/google_docs/__init__.py`
8. ... (10 more Google Workspace modules)
9. `tools/implementations/microsoft_outlook_tools.py`
10. `tools/implementations/microsoft_excel_tools.py`
11. ... (55 more implementation modules)
12. `UI/modules_external/inhouse-print/backend/inhouse_tools.json`
13. `UI/modules_external/inhouse-print/backend/inhouse_wrapper.py`
14. `UI/modules_external/quote-calculator/backend/calculator_tools.json`
15. `UI/modules_external/quote-calculator/backend/calculator_wrapper.py`

### Per User Request:
16. **Database:** `users` table → email column
17. **Database:** `user_preferences` table → all columns
18. `AI_infrastructure/prompts/tool_usage_system_prompt.md` (1,152 lines)
19. `AI_infrastructure/routes/agent_routes_v4.py` → Build USER CONTEXT
20. `AI_infrastructure/core/unified_ai_client.py` → Initialize Claude

### Tool Discovery:
21. `tools/implementations/meta_tools.py::list_platform_tools()`
22. `tools/implementations/meta_tools.py::search_tools()`
23. `tools/implementations/meta_tools.py::get_tool_schema()`

### InHouse Workflow:
24. `UI/modules_external/inhouse-print/backend/inhouse_guide_wrapper.py::inhouse_get_domain_guide()`
25. `UI/modules_external/inhouse-print/backend/inhouse_guide_wrapper.py::inhouse_calculator_guide()`
26. `UI/modules_external/quote-calculator/backend/calculator_wrapper.py::calculate_business_cards()`

---

## 🎓 LEARNING POINTS

### For AI:
- **Progressive Discovery:** Don't load all tools at once, discover as needed
- **Memory Anchoring:** Write numbered lists to create reference points
- **Schema First:** Always get schema before execution
- **Context Awareness:** User email, platform, and preferences guide tool selection

### For Developers:
- **Short Descriptions Critical:** Enable fast discovery and low token usage
- **User Context Block:** Provides personalization and routing logic
- **Email Detection:** Enables domain-specific workflows
- **4-Tier Architecture:** Guides AI from discovery → guidance → specification → execution

---

**END OF AI PATH MAP**
