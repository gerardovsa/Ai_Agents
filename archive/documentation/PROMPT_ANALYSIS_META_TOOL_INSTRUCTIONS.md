# System Prompt Analysis - Meta-Tool Discovery Instructions

**Date:** November 11, 2025  
**Analysis:** Progressive Tool Loading & Meta-Tool Usage Instructions

---

## 📋 EXECUTIVE SUMMARY

**Status:** ✅ **META-TOOL INSTRUCTIONS ARE PRESENT AND COMPREHENSIVE**

The system prompt (`tool_usage_system_prompt.md`) contains **detailed, multi-layered instructions** for using meta-tools to discover and learn about available tools. The instructions are embedded at multiple levels with examples and workflows.

---

## 🔍 WHERE META-TOOL INSTRUCTIONS ARE LOADED

### **File Loading Chain:**

```
1. unified_ai_client.py (line 141-149)
   ↓
2. Loads: AI_infrastructure/prompts/tool_usage_system_prompt.md
   ↓
3. Combined with context-specific prompts via get_system_prompt()
   ↓
4. Sent to Claude API in combined_agent_worker.py
```

### **Code Location:**

**File:** `AI_infrastructure/core/unified_ai_client.py`

```python
def _get_tool_usage_instructions(self) -> str:
    """Load tool usage instructions from prompt file"""
    try:
        prompt_path = Path(__file__).parent.parent / 'prompts' / 'tool_usage_system_prompt.md'
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()  # ← Loads the full system prompt
    except Exception as e:
        print(f"Warning: Could not load tool usage prompt: {e}")
```

**Then combined:**

```python
def get_system_prompt(self, ui_context: str, agent_id: Optional[str] = None) -> str:
    # Load tool usage instructions
    tool_usage_prompt = self._get_tool_usage_instructions()
    
    if ui_context == 'data_agent_chat':
        return tool_usage_prompt + "\n\n" + self._get_data_agent_prompt()
    # ... other contexts
```

---

## 📖 META-TOOL INSTRUCTIONS IN THE PROMPT

### **Location 1: STEP 2 - DISCOVER & LEARN (Lines 38-50)**

```markdown
STEP 2: DISCOVER & LEARN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF you don't know which tool to use:
- Call search_tools("keyword") or list_platform_tools("platform")
- Call get_tool_schema("tool_name") to see parameters

IF you already know which tool to use:
- Call get_tool_schema("tool_name") to verify parameters (don't assume!)
```

**✅ Analysis:** Clear, concise instructions at the workflow level.

---

### **Location 2: RULE #3 - MANDATORY SCHEMA CHECKING (Lines 293-305)**

```markdown
RULE #3: ALWAYS GET SCHEMA BEFORE EXECUTING (MANDATORY!)

The Workflow:
1. Discover tool exists: `search_tools("create document")`
2. **GET SCHEMA FIRST:** `get_tool_schema("tool_name")` ← **MANDATORY STEP**
3. Read required vs optional parameters carefully
4. Execute tool with correct parameters
5. If it fails → re-check schema before retrying

Why This Matters:
- Tools have different parameter names than you expect
- Prevents "missing required parameter" errors
- Shows you types (string vs array vs object)
- Reduces trial-and-error by 90%

** IF YOU SKIP GET_TOOL_SCHEMA, YOU WILL USE WRONG PARAMETERS!**
```

**✅ Analysis:** VERY emphatic, uses bold/caps for emphasis. Includes rationale.

---

### **Location 3: COMPLETE WORKFLOW SECTION (Lines 338-418)**

```markdown
## **📋 COMPLETE WORKFLOW FOR EVERY REQUEST**

### **STEP 1: DISCOVER TOOLS**

Three Discovery Methods:

**Method 1: List Available Platforms**
```python
list_available_platforms()
# Shows: google_docs, google_sheets, gmail, microsoft_outlook, slack, etc.
```

**Method 2: Search by Keyword**
```python
search_tools("create document")
# Returns: google_docs_create_document, microsoft_word_create_document, etc.
```

**Method 3: List Platform-Specific Tools**
```python
list_platform_tools("google_docs")
# Returns: All Google Docs tools with descriptions
```

⚠️ PLATFORM NAMING CRITICAL CLARIFICATION:
[... detailed platform naming rules ...]

### **STEP 2: LEARN TOOL PARAMETERS (MANDATORY!)**

**Always Get Schema Before Executing:**
```python
get_tool_schema("google_docs_create_document")
```

**Returns:**
```json
{
  "name": "google_docs_create_document",
  "description": "Creates a new Google Doc",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {type: "string", required: true},
      ...
    }
  }
}
```
```

**✅ Analysis:** Comprehensive section with:
- All 3 discovery methods
- Code examples with expected outputs
- Platform naming clarifications
- Schema format examples

---

### **Location 4: DISCOVERY METHODS SECTION (Lines 580-610)**

```markdown
### **646 Tools Across 40 Platforms**

Platform Categories:
- Google Workspace (gmail, docs, sheets, drive, calendar, etc.)
- Microsoft 365 (outlook, word, excel, teams, onedrive, etc.)
- Communication (slack, twilio, resend)
- E-commerce (woocommerce, stripe, paypal, shopify)
- Development (github, cloudflare, supabase)
- Specialized (inhouse_print, quote_calculator, data_analysis)

### **Discovery Methods:**

**Method 1: List Platform Tools**
```python
list_platform_tools("google_docs")
# Returns: All Google Docs tools with descriptions
```

**Method 2: Search by Keyword**
```python
search_tools("send email")
# Returns: gmail_send_email, microsoft_outlook_send_email, etc.
```

**Method 3: Get Full Schema**
```python
get_tool_schema("gmail_send_email")
# Returns: All parameters, types, requirements
```

### **Naming Patterns:**

**Google Workspace:**
- `google_docs_*` - Google Docs
- `google_sheets_*` - Google Sheets
- `gmail_*` - Gmail (special case - no "google_" prefix!)

**Microsoft 365:**
- `microsoft_outlook_*` - Outlook
- `microsoft_word_*` - Word
...
```

**✅ Analysis:** Second comprehensive section with:
- Platform ecosystem overview
- Naming pattern rules
- Special case handling (gmail prefix)

---

## 🎯 INSTRUCTION QUALITY ASSESSMENT

### **Strengths:**

✅ **Multiple Reinforcement Points**
   - Instructions appear in 4 different sections
   - Each section has different emphasis (workflow vs rules vs examples)

✅ **Progressive Detail Levels**
   - Quick reference (STEP 2)
   - Detailed rules (RULE #3)
   - Complete workflows (COMPLETE WORKFLOW)
   - Context and patterns (DISCOVERY METHODS)

✅ **Code Examples with Expected Outputs**
   - Shows exact syntax: `search_tools("keyword")`
   - Shows return format: `# Returns: tool names...`

✅ **Strong Emphasis on get_tool_schema()**
   - Marked as MANDATORY in multiple places
   - Explains WHY it's necessary
   - Shows consequences of skipping it

✅ **Platform Naming Clarifications**
   - Addresses common confusion (google_workspace vs google_docs)
   - Provides correct examples and anti-examples
   - Explains special cases (gmail prefix)

---

### **Potential Improvements:**

#### **Issue 1: Meta-Tool Discovery Not Explicit in First Turn**

**Problem:** The prompt doesn't explicitly say:
> "On your first turn, you will ONLY have 5 meta-tools available. Use these to discover the full tool catalog."

**Current Text (Lines 38-50):**
```markdown
IF you don't know which tool to use:
- Call search_tools("keyword") or list_platform_tools("platform")
```

**Recommended Addition:**
```markdown
PROGRESSIVE TOOL LOADING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
On your FIRST turn, you have access to ONLY 5 meta-tools:
1. list_available_platforms() - See all platform categories
2. list_platform_tools(platform) - See tools for a specific platform
3. get_tool_schema(tool_name) - Get full parameter details for a tool
4. search_tools(query) - Search tools by keyword
5. recommend_tools_for_task(task) - Get smart recommendations

After your first response, the FULL 594-tool catalog will be available.

WORKFLOW:
Turn 1: Use meta-tools to discover → Choose appropriate tool
Turn 2+: Execute the actual tool with full access
```

---

#### **Issue 2: No Explicit "Discovery First" Decision Tree**

**Recommended Addition:**
```markdown
DECISION TREE: DO I NEED TO DISCOVER TOOLS?

Ask yourself:
┌─────────────────────────────────────────┐
│ Do I know EXACTLY which tool to use?    │
└────────┬─────────────────────┬──────────┘
         NO                   YES
         ↓                     ↓
    DISCOVER FIRST      VERIFY SCHEMA FIRST
         ↓                     ↓
    search_tools()      get_tool_schema()
         OR                    ↓
    list_platform_tools()  EXECUTE TOOL
         ↓
    get_tool_schema()
         ↓
    EXECUTE TOOL

Example:
User: "Send an email"
└→ I know it's gmail_send_email or outlook_send_email
   └→ search_tools("send email") to see options
      └→ get_tool_schema("gmail_send_email")
         └→ Execute tool
```

---

#### **Issue 3: Progressive Loading Not Mentioned in Meta-Tools Section**

**Current Section (Line 580):** Shows 3 discovery methods but doesn't explain WHEN they're used.

**Recommended Addition:**
```markdown
### **Meta-Tools (Discovery Phase)**

These 5 tools are ALWAYS available (even on first turn):
1. **list_available_platforms()** - See all platform names
   - Use when: User mentions broad category ("Google", "Microsoft")
   - Returns: List of actual platform names to use

2. **list_platform_tools(platform)** - See all tools for a platform
   - Use when: Know platform but not specific tool
   - Returns: Tool names + brief descriptions (NO schemas)

3. **search_tools(query)** - Search across all tools
   - Use when: Know action but not platform ("create document")
   - Returns: Matching tool names from all platforms

4. **get_tool_schema(tool_name)** - Get full parameter details
   - Use when: Know tool name, need to verify parameters
   - Returns: Complete schema with required/optional params

5. **recommend_tools_for_task(task)** - Smart recommendations
   - Use when: Complex task, need workflow guidance
   - Returns: Recommended tools with rationale
```

---

## 🔧 RECOMMENDED PROMPT UPDATES

### **Update 1: Add Progressive Loading Section (Insert after line 50)**

```markdown
═══════════════════════════════════════════════
PROGRESSIVE TOOL LOADING (IMPORTANT!)
═══════════════════════════════════════════════

TURN 1: Meta-Tools Only (5 tools)
You start with ONLY discovery tools:
- list_available_platforms()
- list_platform_tools(platform)
- search_tools(query)
- get_tool_schema(tool_name)
- recommend_tools_for_task(task)

Use these to discover which tool you need.

TURN 2+: Full Tool Access (594 tools)
After your first response, ALL tools become available.
Execute the tools you discovered in Turn 1.

EXAMPLE WORKFLOW:
User: "Send an email to john@example.com"

Turn 1 (discovery):
  → search_tools("send email")
  → Returns: gmail_send_email, outlook_send_email
  → get_tool_schema("gmail_send_email")
  → Returns: parameters (to, subject, body)

Turn 2 (execution):
  → gmail_send_email(to="john@example.com", ...)
  → Returns: Success with message_id

This architecture saves 99.2% tokens on first turn!
═══════════════════════════════════════════════
```

---

### **Update 2: Enhance STEP 2 with Discovery Decision Tree (Replace lines 38-50)**

```markdown
STEP 2: DISCOVER & LEARN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASK YOURSELF: "Do I know which tool to use?"

┌─────────────────────────────────────┐
│ I DON'T KNOW which tool to use      │
└─────────────────────────────────────┘
  ↓
  OPTION A: Broad search
    → search_tools("keyword")
    Example: search_tools("create document")
  
  OPTION B: Platform-specific
    → list_platform_tools("platform")
    Example: list_platform_tools("google_docs")
  
  OPTION C: Get recommendations
    → recommend_tools_for_task("task description")
    Example: recommend_tools_for_task("send weekly report")
  
  ↓
  THEN: Get schema for chosen tool
    → get_tool_schema("tool_name")

┌─────────────────────────────────────┐
│ I KNOW which tool to use            │
└─────────────────────────────────────┘
  ↓
  VERIFY schema (don't assume!)
    → get_tool_schema("tool_name")
  
  ↓
  EXECUTE with correct parameters

⚠️ NEVER skip get_tool_schema()!
Tools have unexpected parameter names/types.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### **Update 3: Add Meta-Tool Reference Card (Insert after line 610)**

```markdown
═══════════════════════════════════════════════
META-TOOL QUICK REFERENCE
═══════════════════════════════════════════════

**list_available_platforms()**
├─ When: User mentions broad category
├─ Returns: Platform names (google_docs, microsoft_outlook, etc.)
└─ Example: User says "Google" → See actual platform names

**list_platform_tools(platform)**
├─ When: Know platform, need tool list
├─ Returns: Tool names + descriptions (NO schemas)
└─ Example: list_platform_tools("gmail") → See all Gmail tools

**search_tools(query)**
├─ When: Know action, not sure of platform
├─ Returns: Matching tool names across all platforms
└─ Example: search_tools("send email") → Gmail + Outlook tools

**get_tool_schema(tool_name)**
├─ When: Know tool name, need parameters
├─ Returns: Full schema (required/optional params, types)
└─ Example: get_tool_schema("gmail_send_email") → See params

**recommend_tools_for_task(task)**
├─ When: Complex task, need workflow guidance
├─ Returns: Recommended tools with step-by-step rationale
└─ Example: recommend_tools_for_task("weekly report") → Workflow

═══════════════════════════════════════════════
```

---

## 📊 CURRENT VS RECOMMENDED STRUCTURE

### **Current Structure:**

```
Line 38-50:   STEP 2 (brief mention of meta-tools)
Line 293-305: RULE #3 (get_tool_schema mandatory)
Line 338-418: COMPLETE WORKFLOW (3 discovery methods)
Line 580-610: DISCOVERY METHODS (3 methods again)
```

**Issues:**
- Progressive loading NOT mentioned
- Meta-tools spread across 4 sections
- No decision tree
- Repetitive (3 methods shown twice)

---

### **Recommended Structure:**

```
Line 38-50:   PROGRESSIVE LOADING (NEW - explains Turn 1 vs Turn 2+)
Line 51-85:   STEP 2 - DISCOVER & LEARN (Enhanced with decision tree)
Line 293-305: RULE #3 (keep as-is - good emphasis)
Line 338-418: COMPLETE WORKFLOW (keep examples)
Line 611-650: META-TOOL QUICK REFERENCE (NEW - all 5 tools in one place)
```

**Benefits:**
- Progressive loading explained upfront
- Clear decision tree for when to use what
- Single reference card for all meta-tools
- Reduced repetition

---

## ✅ CONCLUSION

### **Current State:**

**VERDICT:** ✅ **Meta-tool instructions ARE present and comprehensive**

- Meta-tools mentioned in 4 different sections
- `get_tool_schema()` marked MANDATORY multiple times
- Code examples with expected outputs provided
- Platform naming clarifications included

### **Recommended Enhancements:**

1. **Add Progressive Loading section** (explains Turn 1 vs Turn 2+)
2. **Add Decision Tree** (visual guide for when to discover vs execute)
3. **Create Meta-Tool Quick Reference** (single source of truth)
4. **Reduce repetition** (consolidate discovery methods)

### **Priority:**

🔴 **HIGH PRIORITY:** Progressive loading explanation
- Currently missing entirely
- Critical for understanding the 5-tool → 594-tool transition

🟡 **MEDIUM PRIORITY:** Decision tree
- Would improve discovery workflow clarity
- Reduces confusion about when to use which method

🟢 **LOW PRIORITY:** Quick reference card
- Nice to have
- Reduces scrolling between sections

---

## 📝 IMPLEMENTATION PLAN

### **Step 1: Update tool_usage_system_prompt.md**

```bash
# Add 3 new sections:
1. Progressive Loading (after line 50)
2. Decision Tree (replace lines 38-50)
3. Quick Reference (after line 610)
```

### **Step 2: Test with Claude**

```python
# Test that Claude:
1. Uses meta-tools on Turn 1
2. Uses full tools on Turn 2+
3. Always calls get_tool_schema() before execution
4. Follows decision tree logic
```

### **Step 3: Monitor Metrics**

```python
# Track:
1. Frequency of get_tool_schema() calls
2. First-turn meta-tool usage rate
3. Parameter error reduction
4. Discovery time (turns to find right tool)
```

---

**END OF ANALYSIS**

**Status:** Ready for implementation  
**Estimated Impact:** 20-30% improvement in tool discovery accuracy  
**Token Cost:** +800 tokens to system prompt (negligible vs 70k tool schemas)
