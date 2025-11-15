# Tool Use Validation Fix - November 11, 2025

## Problem Summary

The combined agent worker was generating API errors from Anthropic:

```
Error code: 400 - 'tool_use' ids were found without 'tool_result' blocks immediately after
```

This occurred when assistant messages containing `tool_use` blocks were sent without corresponding `tool_result` blocks in the next user message.

## Root Causes Identified

### 1. **CRITICAL** - tool_result Blocks Stored in Assistant Messages
**Location:** Conversation history storage (upstream bug)

**Problem:**
The conversation history was being saved with tool_result blocks INSIDE assistant messages:

```python
# WRONG STRUCTURE (from actual error log):
{
    'role': 'assistant',
    'content': [
        {'type': 'thinking', ...},
        {'type': 'tool_use', 'id': 'toolu_01ABC', ...},
        {'type': 'tool_result', 'tool_use_id': 'toolu_01ABC', ...},  # ❌ WRONG!
        {'type': 'tool_use', 'id': 'toolu_01DEF', ...},
        {'type': 'tool_result', 'tool_use_id': 'toolu_01DEF', ...},  # ❌ WRONG!
        {'type': 'text', ...}
    ]
}
```

**Anthropic API Rule Violation:**
- tool_result blocks must ONLY appear in USER messages
- They must immediately follow the assistant message with tool_use blocks
- Having them in assistant messages causes 400 errors

**Solution:**
- **Extract** tool_result blocks from assistant messages during validation
- **Create** a new user message immediately after the assistant
- **Insert** extracted tool_result blocks in proper location
- This reconstructs the correct conversation structure automatically

### 2. Flawed `validate_user_content` Logic
**Location:** `AI_infrastructure/core/combined_agent_worker.py`, lines 126-189

**Problem:**
```python
# OLD CODE - BROKEN
for prev_msg in reversed(messages):
    if prev_msg.get('role') == 'assistant':
        prev_content = prev_msg.get('content', [])
        has_tool_use_before = any(
            b.get('type') == 'tool_use' for b in prev_content if isinstance(b, dict)
        )
        break  # Stop at first assistant message found
```

The function would:
- Look for the previous assistant message
- Check if it had tool_use blocks
- **Always break after first assistant**, even if it had NO tool_use blocks
- Result: `has_tool_use_before` could be `False` even when tool_use existed earlier
- This caused valid `tool_result` blocks to be incorrectly removed

**Solution:**
- Properly collect ALL `tool_use` IDs from the previous assistant message
- Validate each `tool_result` block matches a `tool_use_id`
- Remove only truly orphaned tool_result blocks

### 3. Missing Final Validation Before API Call
**Location:** `AI_infrastructure/core/combined_agent_worker.py`, lines 950-985

**Problem:**
- Conversation history was validated
- But no check ensured tool_use ↔ tool_result pairing
- Invalid message structures could still reach the API
- Caused 400 errors from Anthropic

**Solution:**
- Added comprehensive validation loop before API call
- Check EVERY assistant message with tool_use blocks
- Verify next message is user with matching tool_result blocks
- Remove invalid message pairs if mismatches found

### 4. Insufficient Debug Logging
**Problem:**
- Hard to diagnose conversation structure issues
- Couldn't see where tool_result blocks were getting lost

**Solution:**
- Added detailed logging BEFORE validation (show raw structure)
- Added detailed logging AFTER validation (show final structure)
- Added special checks for tool_use → tool_result pairing
- Shows missing tool_result IDs clearly

## Changes Made

### Change 1: **CRITICAL** - Extract and Move tool_result Blocks
**File:** `combined_agent_worker.py`, lines 29-123, 270-291

**New Feature:**
The `validate_and_reorder_assistant_content` function now:
1. **Extracts** tool_result blocks found in assistant messages
2. **Returns** them separately: `(validated_content, extracted_tool_results)`
3. **Logs** extraction with clear messages

The `validate_conversation_history` function then:
1. **Receives** extracted tool_result blocks
2. **Creates** a new user message immediately after assistant
3. **Inserts** extracted tool_result blocks in proper location
4. **Maintains** correct conversation structure

**Example:**
```python
# BEFORE (invalid):
[
    {'role': 'user', 'content': [...]},
    {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': 'A'},
        {'type': 'tool_result', 'tool_use_id': 'A'}  # ❌ WRONG PLACE!
    ]}
]

# AFTER (valid):
[
    {'role': 'user', 'content': [...]},
    {'role': 'assistant', 'content': [
        {'type': 'tool_use', 'id': 'A'}  # ✅ Only tool_use
    ]},
    {'role': 'user', 'content': [
        {'type': 'tool_result', 'tool_use_id': 'A'}  # ✅ In user message!
    ]}
]
```

### Change 2: Fixed `validate_user_content` Function
**File:** `combined_agent_worker.py`, lines 126-189

**Before:**
- Simple boolean check for tool_use existence
- No ID matching validation
- Could incorrectly remove valid tool_result blocks

**After:**
- Collects all tool_use IDs from previous assistant message
- Validates each tool_result has matching tool_use_id
- Only removes truly orphaned tool_result blocks
- Better error messages

### Change 3: Added Pre-API Validation
**File:** `combined_agent_worker.py`, lines 956-989

**New validation loop:**
```python
# Validate every tool_use has corresponding tool_result
for idx, msg in enumerate(messages):
    if msg.get('role') == 'assistant':
        tool_use_ids = [get tool_use IDs]
        
        if tool_use_ids:
            # Check next message is user with tool_result
            if idx + 1 < len(messages):
                next_msg = messages[idx + 1]
                if next_msg.get('role') == 'user':
                    tool_result_ids = [get tool_result IDs]
                    
                    missing_ids = set(tool_use_ids) - set(tool_result_ids)
                    if missing_ids:
                        # FIX: Remove invalid messages
                        messages = messages[:idx]
                        break
```

### Change 4: Enhanced Debug Logging
**File:** `combined_agent_worker.py`, lines 244-250, 308-339

**Added logging:**
- Shows conversation structure BEFORE validation
- Shows conversation structure AFTER validation
- Highlights tool_use blocks and their IDs
- Warns about missing tool_result blocks
- Shows which tool_result IDs are present in user messages

## Expected Behavior After Fix

### Valid Conversation Flow:
```
Message 0 (user): [text]
Message 1 (assistant): [thinking, tool_use(id=A), tool_use(id=B)]
Message 2 (user): [tool_result(tool_use_id=A), tool_result(tool_use_id=B)]
Message 3 (assistant): [text]
```

### Invalid Flow (Now Detected & Fixed):
```
Message 0 (user): [text]
Message 1 (assistant): [tool_use(id=A), tool_use(id=B)]
Message 2 (user): [tool_result(tool_use_id=A)]  ← MISSING B!
                  ^^^ DETECTED: Removed messages 1-2
```

### Console Output Example:
```
[Combined Worker] Validating 4 messages before Round 2...
[Combined Worker]   Message 0 (user): ['text']
[Combined Worker]   Message 1 (assistant): ['thinking', 'tool_use', 'tool_use']
[Combined Worker]   Message 2 (user): ['tool_result', 'tool_result']
[Combined Worker]   Message 3 (assistant): ['text']
[Combined Worker] Validated: 4 valid messages
[Combined Worker] Final conversation structure:
[Combined Worker]   Message 0 (user): ['text']
[Combined Worker]   Message 1 (assistant): ['thinking', 'tool_use', 'tool_use']
[Combined Worker]     → 2 tool_use blocks: ['toolu_01ABC', 'toolu_01DEF']
[Combined Worker]     → Next user message has 2 tool_result blocks
[Combined Worker]   Message 2 (user): ['tool_result', 'tool_result']
[Combined Worker]   Message 3 (assistant): ['text']
```

## Test Results

All 6 validation tests pass:
1. ✅ Valid conversation (tool_use → tool_result) - Preserved correctly
2. ✅ Orphaned tool_result - Removed correctly
3. ✅ Missing tool_result - Detected correctly
4. ✅ Duplicate assistant messages - Merged correctly
5. ✅ Thinking block ordering - Reordered correctly
6. ✅ **tool_result in assistant** - **Extracted and moved correctly** (NEW!)

**Test 6 Output:**
```
[Combined Worker] ⚠️ Extracting tool_result from assistant message (will be moved to user message)
[Combined Worker] ⚠️ Extracting tool_result from assistant message (will be moved to user message)
[Combined Worker] 🔧 Inserting 2 extracted tool_result blocks as user message
[Combined Worker] ✅ Validated: 3 valid messages
[Combined Worker]   Message 1 (assistant): ['thinking', 'tool_use', 'tool_use', 'text']
[Combined Worker]     → 2 tool_use blocks: ['toolu_01ABC', 'toolu_01DEF']
[Combined Worker]     → Next user message has 2 tool_result blocks
[Combined Worker]   Message 2 (user): ['tool_result', 'tool_result']
✅ PASS: tool_result blocks extracted and moved to user message
```

## Production Testing Recommendations

### Test 1: Simple Tool Execution
```powershell
CHAT "List my Gmail messages"
```

**Expected:**
- Request goes through successfully
- Tool executes and returns results
- No 400 errors

### Test 2: Multiple Tool Execution
```powershell
CHAT "List my Gmail messages and create a Google Doc"
```

**Expected:**
- Multiple tools execute in sequence
- All tool_result blocks match tool_use blocks
- No API errors

### Test 3: Multi-Round Conversation
```powershell
CHAT "Research the weather in Paris"
# (Claude uses tools)
CHAT "Now create a document about it"
# (Claude uses more tools)
```

**Expected:**
- Multiple rounds of tool execution
- Conversation history remains valid
- No orphaned tool_use blocks

## Files Modified

1. **combined_agent_worker.py** (4 major changes)
   - **CRITICAL**: Modified `validate_and_reorder_assistant_content` to extract tool_result blocks (lines 29-123)
   - Modified `validate_conversation_history` to insert extracted tool_results as user messages (lines 270-291)
   - Fixed `validate_user_content` function (lines 126-189)
   - Added pre-API validation (lines 1006-1042)
   - Enhanced debug logging (lines 244-250, 341-372)

2. **test_tool_use_validation.py** (1 change)
   - Added Test 6: tool_result extraction test (lines 180-240)

## Related Documentation

- `AGENT_FLOW_ANALYSIS.md` - Architecture analysis
- `PROGRESSIVE_LOADING_SUCCESS.md` - Tool discovery system
- `copilot-instructions.md` - Platform architecture

## Status

- Implementation: ✅ COMPLETE
- Unit Testing: ✅ COMPLETE (6/6 tests passing)
- Production Testing: ⏳ PENDING
- Deployment: ⏳ PENDING

## Next Steps

1. Test the fix with various tool execution scenarios
2. Monitor API error logs for 400 errors
3. Verify conversation history remains valid across multiple rounds
4. If successful, mark as production-ready

---

**Created:** November 11, 2025  
**Author:** GitHub Copilot  
**Issue:** Tool use validation causing 400 API errors  
**Resolution:** Fixed validation logic and added comprehensive checks
