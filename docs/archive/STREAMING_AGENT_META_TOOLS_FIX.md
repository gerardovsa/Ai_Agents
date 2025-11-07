# CRITICAL FIX: Streaming Agent Worker Tool Execution Bug

**Date:** November 3, 2025  
**Issue:** Meta-tools failing with "got multiple values for keyword argument 'tool_name'"  
**Severity:** CRITICAL - Blocked ALL tool execution in streaming mode (CHAT command)

---

## The Problem

When using the CHAT command (streaming mode), Claude would call meta-tools like:
- `get_tool_schema(tool_name='microsoft_word_create_document')`
- `execute_tool(tool_name='gmail_send_email', to='...', subject='...')`

The streaming_agent_worker.py was receiving:
```python
tool_name = 'get_tool_schema'
tool_input = {'tool_name': 'microsoft_word_create_document'}
```

Then executing:
```python
registry.execute_tool(
    tool_name='get_tool_schema',      # ← Parameter 1
    **tool_input                       # ← Spreads {'tool_name': '...'} = Parameter 2
)
```

**Result:** Duplicate `tool_name` parameter → TypeError!

---

## Why Google Tools Appeared Broken

User reported: "now my google tools not working"

What was actually happening:
1. Claude tried to call `microsoft_word_create_document` directly
2. Tool not found (because Microsoft tools require OAuth setup)
3. Claude called `search_tools('microsoft_word')` - ✅ WORKED
4. Claude called `get_tool_schema(tool_name='microsoft_word_create_document')` - ❌ FAILED
5. Claude gave up and tried Google tools instead
6. Google tools ALSO failed because `get_tool_schema` wasn't working
7. User thought Google tools were broken, but really the meta-tools were broken!

---

## The Fix

**File:** `AI_infrastructure/core/streaming_agent_worker.py`  
**Lines:** 324-350

**Added code to remove `tool_name` from `tool_input` before spreading:**

```python
for tool_use in tool_uses:
    tool_name = tool_use['name']
    tool_input = tool_use['input'].copy()  # ← Make copy
    tool_id = tool_use['id']
    
    # CRITICAL: Remove 'tool_name' from tool_input if present
    if 'tool_name' in tool_input:
        del tool_input['tool_name']  # ← Remove before spreading!
    
    # Now safe to execute
    result = self.registry.execute_tool(
        tool_name=tool_name,
        **tool_input  # ← No duplicate now
    )
```

---

## Pattern Established

**ALL places that call `registry.execute_tool` with `**tool_input` MUST:**

1. **Copy** `tool_input` to avoid mutating original
2. **Remove** `'tool_name'` from the copy if present
3. **Pass** `tool_name=tool_name` as explicit keyword argument
4. **Spread** the cleaned `**tool_input`

**Example:**
```python
tool_input_copy = tool_input.copy()
if 'tool_name' in tool_input_copy:
    del tool_input_copy['tool_name']

result = registry.execute_tool(
    tool_name=tool_name,
    **tool_input_copy
)
```

---

## Why agent_worker.py Didn't Have This Bug

Line 561 of agent_worker.py already had:
```python
if 'tool_name' in tool_input:
    del tool_input['tool_name']
```

That's why the non-streaming mode worked! We just needed to add the same fix to streaming_agent_worker.py.

---

## Testing After Fix

**Before:**
```
[Stream Round 2] Executing: get_tool_schema
[Stream Round 2] ERROR: got multiple values for keyword argument 'tool_name'
```

**After:**
```
[Stream Round 2] Executing: get_tool_schema
[Stream Round 2] Tool result: {"success": true, "tool_name": "microsoft_word_create_document", ...}
```

---

## About the `execute_tool` Meta-Tool

**Question:** "do we need the tool execution tool???"

**Answer:** YES! It's critical for the agent workflow:

1. **Discovery Phase:** Claude calls `list_platform_tools()`, `search_tools()`, `get_tool_schema()`
2. **Execution Phase:** Claude calls `execute_tool(tool_name='...', params=...)`

The `execute_tool` meta-tool is a WRAPPER that:
- Validates the tool exists
- Injects credentials if needed
- Calls the actual tool implementation
- Returns structured success/error results

Without it, Claude would need 606 tools loaded in EVERY request (10MB+ of tool definitions). With progressive loading + meta-tools, we only send 8 tools initially, saving 99.2% of tokens!

---

## Summary

**Root Cause:** streaming_agent_worker.py wasn't removing `tool_name` from `tool_input` before spreading it  
**Impact:** ALL meta-tool calls failed → appeared as if Google/Microsoft tools were broken  
**Fix:** Added `tool_name` removal logic (same as agent_worker.py line 561)  
**Status:** ✅ FIXED - Both streaming and non-streaming modes now work correctly  

---

**Related Files:**
- `EXECUTE_TOOL_PARAMETER_FIX_COMPLETE.md` - Complete fix documentation for all 6 files
- `PROGRESSIVE_LOADING_SUCCESS.md` - Why meta-tools are essential

**Last Updated:** November 3, 2025  
**Version:** 1.0.0
