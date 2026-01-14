# Tool Use Validation Fix - November 21, 2025

## Critical Bug Fixed: Orphaned tool_use Blocks Causing 400 Errors

### The Problem

**Error in Render Deployment:**
```
anthropic.BadRequestError: Error code: 400
'messages.1: `tool_use` ids were found without `tool_result` blocks immediately after: toolu_015LayFVLCjwa7vjE3ugjYjr. 
Each `tool_use` block must have a corresponding `tool_result` block in the next message.'
```

### Root Cause

**Location**: `combined_agent_worker.py` lines 1920-1980

The validation code had **INCORRECT LOGIC** that preserved broken messages when Extended Thinking was enabled:

```python
# OLD CODE (WRONG):
if missing_ids:
    if ai_thinking_enabled:
        # PRESERVING: Messages kept intact (thinking enabled)
        print("✅ PRESERVING: Messages kept intact")
        # ❌ BUG: This leaves orphaned tool_use blocks!
    else:
        # FIXING: Removing assistant+user messages
        messages = messages[:idx]
        break
```

**Why This Was Wrong:**
- Orphaned `tool_use` blocks **ALWAYS** cause 400 errors
- Anthropic API **REQUIRES** every `tool_use` to have a matching `tool_result`
- Thinking mode is **IRRELEVANT** to tool_use/tool_result pairing
- The code thought it was "preserving thinking blocks" but actually broke the conversation

### The Fix (Nov 21, 2025)

**Changed 3 locations** to **ALWAYS** fix orphaned tool_use blocks:

#### Fix 1: Missing tool_result blocks
```python
# NEW CODE (CORRECT):
missing_ids = set(tool_use_ids) - set(tool_result_ids)
if missing_ids:
    # CRITICAL FIX: ALWAYS remove orphaned tool_use blocks
    # Orphaned tool_use ALWAYS causes 400 errors - must fix regardless of thinking mode
    print(f"❌ ERROR: Assistant message {idx} has tool_use blocks without matching tool_result:")
    print(f"🔧 FIXING: Truncating conversation at message {idx} (thinking_enabled={ai_thinking_enabled})")
    messages = messages[:idx]
    break
```

#### Fix 2: Wrong message order (tool_use followed by non-user message)
```python
# NEW CODE (CORRECT):
else:
    # CRITICAL FIX: ALWAYS fix incorrect message order
    print(f"❌ ERROR: Assistant message {idx} has tool_use but next message is {next_msg.get('role')}, not user!")
    print(f"🔧 FIXING: Truncating conversation at message {idx}")
    messages = messages[:idx]
    break
```

#### Fix 3: Missing following message
```python
# NEW CODE (CORRECT):
else:
    # CRITICAL FIX: ALWAYS fix missing tool_result message
    print(f"❌ ERROR: Assistant message {idx} has tool_use but no following message!")
    print(f"🔧 FIXING: Truncating conversation at message {idx}")
    messages = messages[:idx]
    break
```

### What Changed

| Scenario | Old Behavior | New Behavior |
|----------|--------------|--------------|
| Orphaned tool_use + Thinking OFF | ✅ Truncate messages | ✅ Truncate messages |
| Orphaned tool_use + Thinking ON | ❌ PRESERVE (breaks API!) | ✅ Truncate messages |
| Wrong message order + Thinking OFF | ✅ Truncate messages | ✅ Truncate messages |
| Wrong message order + Thinking ON | ❌ PRESERVE (breaks API!) | ✅ Truncate messages |
| Missing tool_result + Thinking OFF | ✅ Truncate messages | ✅ Truncate messages |
| Missing tool_result + Thinking ON | ❌ PRESERVE (breaks API!) | ✅ Truncate messages |

### Why This Fixes Your Render Error

**Before:**
1. Agent uses tool → Creates `tool_use` block in assistant message
2. Tool execution fails or gets interrupted
3. No `tool_result` created in next user message
4. Validation sees orphaned `tool_use` + thinking enabled → **PRESERVES BROKEN MESSAGES**
5. Sends to Anthropic API → **400 ERROR**

**After:**
1. Agent uses tool → Creates `tool_use` block in assistant message
2. Tool execution fails or gets interrupted
3. No `tool_result` created in next user message
4. Validation sees orphaned `tool_use` → **TRUNCATES CONVERSATION** (removes broken messages)
5. Sends clean conversation to Anthropic API → **SUCCESS**

### Impact

✅ **Fixes 400 errors** in production (Render deployment)
✅ **Maintains Extended Thinking** functionality (thinking blocks preserved when valid)
✅ **No breaking changes** (only fixes broken conversations)
✅ **Works in all modes** (thinking enabled/disabled)

### Testing

**Before deploying to Render:**
```bash
# Test locally
BISTART

# Try to trigger the error:
# 1. Send a message that uses a tool
# 2. Interrupt before tool completes
# 3. Send another message
# Should now truncate conversation instead of 400 error
```

**What to look for in logs:**
```
❌ ERROR: Assistant message 1 has tool_use blocks without matching tool_result:
   tool_use IDs: ['toolu_015LayFVLCjwa7vjE3ugjYjr']
   tool_result IDs: []
   Missing: ['toolu_015LayFVLCjwa7vjE3ugjYjr']
🔧 FIXING: Truncating conversation at message 1 (thinking_enabled=True)
```

### Frontend Impact

**None** - This is a backend-only fix. The frontend changes we made (JSON parsing) are still correct and necessary.

### Deployment

**Files Modified:**
- `AI_infrastructure/core/combined_agent_worker.py` (lines 1938-1967)

**Deployment Steps:**
1. Commit changes: `git commit -m "fix: Always remove orphaned tool_use blocks (fixes 400 errors)"`
2. Push to v7 branch: `git push origin v7`
3. Deploy to Render
4. Test with a tool-using conversation
5. Verify no 400 errors in Render logs

### Related Issues

This fix also addresses:
- Tool execution timeouts leaving orphaned tool_use
- Network interruptions during tool calls
- Race conditions between tool_use and tool_result
- Conversation state corruption after errors

### Summary

**Before**: Thinking mode exempted messages from validation → 400 errors
**After**: All messages validated regardless of thinking mode → No 400 errors

The key insight: **Thinking blocks and tool_use/tool_result pairing are independent concerns**. Thinking blocks can exist alongside tools, but orphaned tool_use blocks are ALWAYS invalid, regardless of thinking mode.

---

**Status**: ✅ FIXED (Nov 21, 2025)
**Testing**: Ready for deployment
**Risk**: Low (only removes already-broken messages)
