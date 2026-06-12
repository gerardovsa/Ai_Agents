# Meta-Tools Reference - EXACT Tools Available
**Last Updated:** January 19, 2026  
**Registry Version:** v3.0  
**Total Tools in System:** 1071 tools across all platforms

---

## 🎯 Purpose

Meta-tools help AI agents discover and use the 1071 available tools without sending all schemas upfront. This document lists the **EXACT** meta-tools that exist in production.

---

## ✅ AVAILABLE META-TOOLS (8 Tools)

### 1. `list_available_platforms()`
**Purpose:** List all platforms that have tools available

**Parameters:** None

**Returns:** List of platform names with tool counts

**Example:**
```python
list_available_platforms()
# Returns: {
#   "platforms": ["microsoft_excel", "gmail", "google_docs", ...],
#   "counts": {"microsoft_excel": 33, "gmail": 46, ...}
# }
```

**When to use:**
- Starting discovery process
- User mentions broad category like "Microsoft" or "Google"
- Need to see what integrations are available

---

### 2. `list_platform_tools(platform: str)`
**Purpose:** List tool names and descriptions for a specific platform (NO parameter schemas)

**Parameters:**
- `platform` (string, required): Platform name (e.g., 'microsoft_excel', 'gmail')

**Returns:** List of tool names with short descriptions

**Example:**
```python
list_platform_tools(platform='microsoft_excel')
# Returns: {
#   "tools": [
#     {"name": "microsoft_excel_create_workbook", "description": "..."},
#     {"name": "microsoft_excel_get_workbook", "description": "..."},
#     ...
#   ]
# }
```

**When to use:**
- After identifying platform from `list_available_platforms()`
- User wants to see what actions are available for a platform
- Before calling `get_tool_schema()` to get full details

---

### 3. `get_tool_schema(tool_name: str)`
**Purpose:** Get FULL parameter schema for ONE specific tool

**Parameters:**
- `tool_name` (string, required): Exact tool name (e.g., 'microsoft_excel_create_workbook')

**Returns:** Complete Anthropic-formatted tool schema with input_schema

**Example:**
```python
get_tool_schema(tool_name='microsoft_excel_create_workbook')
# Returns: {
#   "name": "microsoft_excel_create_workbook",
#   "description": "...",
#   "input_schema": {
#     "type": "object",
#     "properties": {...},
#     "required": [...]
#   }
# }
```

**When to use:**
- After discovering tool name from `list_platform_tools()` or `search_tools()`
- Before executing a tool to understand required parameters
- To validate what parameters are needed

**⚠️ CRITICAL:** You MUST pass `tool_name` parameter. Calling `get_tool_schema()` without parameters will fail.

---

### 4. `search_tools(query: str)`
**Purpose:** Search for tools by keyword or task across all platforms

**Parameters:**
- `query` (string, required): Search query (e.g., 'excel create', 'send email')

**Returns:** List of matching tools with relevance scores

**Example:**
```python
search_tools(query='excel create')
# Returns: {
#   "tools": [
#     {"name": "microsoft_excel_create_workbook", "score": 10, ...},
#     {"name": "google_sheets_create_spreadsheet", "score": 8, ...}
#   ]
# }
```

**When to use:**
- User asks for specific action (create, send, list, etc.)
- Don't know which platform has the tool
- Searching across multiple platforms simultaneously

---

### 5. `get_platform_guide(platform: str)`
**Purpose:** Get comprehensive guide for a specific platform

**Parameters:**
- `platform` (string, required): Platform name

**Returns:** Platform documentation with common workflows

**Example:**
```python
get_platform_guide(platform='microsoft_excel')
# Returns comprehensive guide with examples, workflows, tips
```

**When to use:**
- User is new to a platform
- Need examples of common workflows
- Understanding platform capabilities

---

### 6. `recommend_tools_for_task(task_description: str, user_platforms: list)`
**Purpose:** Get smart AI recommendations for which tools to use for a task

**Parameters:**
- `task_description` (string, required): Natural language description of task
- `user_platforms` (array, optional): List of platforms user has connected

**Returns:** Recommended tools and workflow

**Example:**
```python
recommend_tools_for_task(
    task_description='Send an email to john@example.com',
    user_platforms=['google_workspace']
)
# Returns recommendations for gmail_send_email
```

**When to use:**
- User provides vague task description
- Multiple ways to accomplish same goal
- Need workflow guidance

---

### 7. `get_workflow_steps(workflow_name: str)`
**Purpose:** Get step-by-step workflow for common tasks

**Parameters:**
- `workflow_name` (string, required): Workflow name (e.g., 'send_email', 'create_document')

**Returns:** Step-by-step instructions

**Example:**
```python
get_workflow_steps(workflow_name='send_email')
# Returns detailed step-by-step workflow
```

**When to use:**
- Need guidance for multi-step processes
- Understanding proper sequence of tool calls
- Learning best practices for common tasks

---

### 8. `execute_tool(tool_name: str, **params)`
**Purpose:** Execute ANY discovered tool by name (dynamic proxy for all 1071 tools)

**Parameters:**
- `tool_name` (string, required): Exact tool name to execute
- `**params`: All parameters required by the tool

**Returns:** Result from the executed tool

**Example:**
```python
execute_tool(
    tool_name='microsoft_excel_create_workbook',
    name='Sales Report 2026'
)
# Executes the tool and returns result
```

**When to use:**
- After discovering tool via `search_tools()` or `list_platform_tools()`
- After getting parameters via `get_tool_schema()`
- Ready to execute with all required parameters

**⚠️ CRITICAL:** You MUST pass `tool_name` parameter. Calling `execute_tool()` without tool_name will fail.

---

## 🔄 RECOMMENDED WORKFLOW

### Simple Discovery Workflow

```
1. list_available_platforms()
   ↓ See: ["microsoft_excel", "gmail", "google_docs", ...]
   
2. list_platform_tools(platform='microsoft_excel')
   ↓ See: ["microsoft_excel_create_workbook", "microsoft_excel_get_workbook", ...]
   
3. get_tool_schema(tool_name='microsoft_excel_create_workbook')
   ↓ See: {"name": ..., "description": ..., "input_schema": {...}}
   
4. execute_tool(tool_name='microsoft_excel_create_workbook', name='My Spreadsheet')
   ↓ Execute and get result
```

### Search-Based Workflow

```
1. search_tools(query='excel create')
   ↓ See: ["microsoft_excel_create_workbook", "google_sheets_create_spreadsheet", ...]
   
2. get_tool_schema(tool_name='microsoft_excel_create_workbook')
   ↓ See required parameters
   
3. execute_tool(tool_name='microsoft_excel_create_workbook', name='My Spreadsheet')
   ↓ Execute and get result
```

---

## ❌ COMMON MISTAKES

### Mistake 1: Calling without required parameters
```python
# ❌ WRONG
get_tool_schema()  # Missing tool_name parameter

# ✅ CORRECT
get_tool_schema(tool_name='microsoft_excel_create_workbook')
```

### Mistake 2: Guessing tool names instead of discovering
```python
# ❌ WRONG
execute_tool(tool_name='google_sheets_create_spreadsheet', name='My Sheet')
# Error: Tool not found (wrong name)

# ✅ CORRECT
search_tools(query='sheets create')
# See actual tool name: 'google_sheets_create_spreadsheet_v2'
execute_tool(tool_name='google_sheets_create_spreadsheet_v2', name='My Sheet')
```

### Mistake 3: Not using discovery tools before execution
```python
# ❌ WRONG - Guessing directly
execute_tool(tool_name='microsoft_word_create_document', title='Doc')

# ✅ CORRECT - Discover first
search_tools(query='word create')
# Returns actual tool names
get_tool_schema(tool_name='actual_tool_name_from_results')
# See parameters
execute_tool(tool_name='actual_tool_name_from_results', **params)
```

---

## 🚨 ERROR MESSAGES GUIDE

### "❌ MISSING PARAMETER: tool_name is required"

**Cause:** Called `get_tool_schema()` or `execute_tool()` without tool_name

**Fix:**
```python
# Use discovery tools to find exact tool name
search_tools(query='keyword')
# Then call with exact name
get_tool_schema(tool_name='exact_tool_name_from_search')
```

### "❌ TOOL NOT FOUND: 'tool_name' does not exist"

**Cause:** Guessed wrong tool name instead of using discovery tools

**Fix:**
```python
# DO NOT guess tool names
# Instead, use search_tools:
search_tools(query='relevant keyword')
# Use EXACT name from results
execute_tool(tool_name='exact_name_from_search_results', **params)
```

### "RestrictedPython not installed"

**Cause:** `python_exec` tools require RestrictedPython dependency

**Fix:**
```powershell
pip install RestrictedPython==7.4.0
```

---

## 📊 Registry Statistics

| Category | Count |
|----------|-------|
| Total Tools | 1071 |
| Total Platforms | ~50 |
| Meta-Tools | 8 |
| Microsoft 365 Tools | ~250 |
| Google Workspace Tools | ~350 |
| Quote Calculator Tools | ~80 |
| InHouse Print Tools | 11 |

---

## 🔧 Production Verification

To verify which meta-tools are registered in your environment:

```python
from tools.registry_v3 import RegistryV3

r = RegistryV3()

# List all meta-tools
meta_tools = [t for t in r.tools.keys() 
              if 'platform' in t.lower() or 
                 'schema' in t.lower() or 
                 'search_tools' == t or
                 'execute_tool' == t or
                 'recommend' in t.lower() or
                 'workflow' in t.lower()]

print("Available meta-tools:")
for tool in sorted(meta_tools):
    if tool in ['list_available_platforms', 'list_platform_tools', 
                'get_tool_schema', 'search_tools', 'get_platform_guide',
                'recommend_tools_for_task', 'get_workflow_steps', 'execute_tool']:
        print(f"  ✅ {tool}")
```

---

## 📝 Summary

**✅ DO:**
- Always use `tool_name` parameter with `get_tool_schema()` and `execute_tool()`
- Use discovery tools (`search_tools`, `list_platform_tools`) before executing
- Use EXACT tool names from discovery results
- Follow the recommended workflow: Discover → Get Schema → Execute

**❌ DON'T:**
- Call meta-tools without required parameters
- Guess tool names instead of using discovery
- Skip discovery step and jump directly to execution
- Assume tool names follow a pattern (they vary by platform)

---

**Remember:** These are the ONLY meta-tools available. If a tool is not listed here, it does NOT exist in production.
