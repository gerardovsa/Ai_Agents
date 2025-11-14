# Bug Fix: NameError - 'tool_use_ids' is not defined

**Date:** November 14, 2025  
**File:** `AI_infrastructure/core/combined_agent_worker.py`  
**Status:** ✅ FIXED AND TESTED

## Problem Description

The validation function `validate_conversation_history()` in `combined_agent_worker.py` was throwing a `NameError` when processing conversation history:

```
NameError: name 'tool_use_ids' is not defined. Did you mean: 'tool_use_blocks'?
```

This error occurred at line 468 during the validation of assistant messages with tool_use blocks.

## Root Cause

The code was trying to check for missing tool results by comparing `tool_use_ids` and `tool_result_ids`, but these variables were never defined:

```python
# Line 468 - BEFORE FIX (BROKEN)
missing_ids = set(tool_use_ids) - set(tool_result_ids)  # ❌ Variables not defined!
```

The loop extracted tool information but didn't collect the IDs into lists for comparison.

## Solution

Added proper variable initialization and population in the validation loop:

### Changes Made (Lines 418-438)

**Line 418:** Added `tool_use_ids = []` initialization
```python
tool_info = []
tool_use_ids = []  # FIX: Define variable before use
```

**Line 423:** Added ID collection in the loop
```python
tool_id = tool_block.get('id', 'no-id')
tool_use_ids.append(tool_id)  # FIX: Collect tool IDs
```

**Line 438:** Added `tool_result_ids` extraction
```python
tool_result_ids = [b.get('tool_use_id') for b in tool_result_blocks]  # FIX: Define variable before use
```

### Complete Fixed Code Block

```python
# Extract tool names and IDs
tool_info = []
tool_use_ids = []  # FIX: Define variable before use
for tool_block in tool_use_blocks:
    try:
        tool_name = tool_block.get('name', 'unknown')
        tool_id = tool_block.get('id', 'no-id')
        tool_use_ids.append(tool_id)  # FIX: Collect tool IDs
        # Count tokens in tool input (approximate)
        tool_input_str = str(tool_block.get('input', {}))
        token_count = len(tool_input_str) // 4
        tool_info.append(f"{tool_name}[{token_count}t]")
    except Exception:
        tool_info.append(f"unknown[?t]")

# ... later in code ...

# Check if next message is user with tool_result
if next_msg.get('role') == 'user':
    next_content = next_msg.get('content', [])
    tool_result_blocks = [b for b in next_content if isinstance(b, dict) and b.get('type') == 'tool_result']
    tool_result_ids = [b.get('tool_use_id') for b in tool_result_blocks]  # FIX: Define variable before use
    
    # ... validation logic ...
    
    # Check for missing tool_results (NOW WORKS!)
    missing_ids = set(tool_use_ids) - set(tool_result_ids)
    if missing_ids:
        print(f"[Combined Worker]     ⚠️ MISSING tool_result for IDs: {list(missing_ids)[:3]}{'...' if len(missing_ids) > 3 else ''}")
```

## Verification

### Syntax Check
```powershell
python -m py_compile AI_infrastructure/core/combined_agent_worker.py
# ✅ No errors
```

### Test Results
Created `test_tool_use_ids_fix.py` with 3 test cases:

1. **Test 1:** Valid conversation with matching tool_use/tool_result  
   ✅ PASS - Validated 3 messages without error

2. **Test 2:** Missing tool_result (should detect but not crash)  
   ✅ PASS - Validated 2 messages, detected missing tool_result gracefully

3. **Test 3:** Multiple tool_use blocks with matching results  
   ✅ PASS - Validated 3 messages with multiple tools

**All tests passed successfully!**

## Impact

- **Before:** Server crashed with NameError when validating conversations with tool_use blocks
- **After:** Validation works correctly and gracefully detects missing tool_results
- **Side Effects:** None - purely additive fix

## Related Code

The same variable pattern is used correctly in other parts of the file:
- Lines 185-196: Earlier validation logic (already correct)
- Lines 1276-1290: Later validation in execute_streaming_request (already correct)

Only the logging/debug section (lines 418-468) was missing the variable definitions.

## Deployment

- File auto-reloads with Flask's debug mode
- No restart required
- No database changes needed
- No API changes

## Testing Recommendations

1. Run the test script: `python test_tool_use_ids_fix.py`
2. Test in UI by sending messages that use tools (e.g., "List Gmail messages")
3. Monitor Flask logs for validation messages - should show no NameError

---

**Fix Author:** GitHub Copilot (Claude Sonnet 4.5)  
**Verified By:** Automated test suite (3/3 tests passing)  
**Status:** Production ready ✅
