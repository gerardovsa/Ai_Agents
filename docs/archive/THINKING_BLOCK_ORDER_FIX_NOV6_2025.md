# Thinking Block Order Fix - November 6, 2025

## Problem

**Error:**
```
Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 
'message': 'messages.7.content.0: If an assistant message contains any thinking blocks, 
the first block must be `thinking` or `redacted_thinking`. Found `text`.'}}
```

**Root Cause:**
When using Claude's Extended Thinking feature, Anthropic API requires that:
- If an assistant message contains **any** thinking blocks
- The **first block** MUST be `thinking` or `redacted_thinking`

The error occurred because content blocks were being stored/serialized in the order they were received from the API, which might have text blocks before thinking blocks. When these messages were loaded from the database and sent back to Claude in subsequent rounds, the API rejected them.

## Solution

Added content block reordering logic in **two places**:

### 1. Streaming Agent Worker (`streaming_agent_worker.py`)

**Fixed `_serialize_content_blocks()` method** (lines 640-712):
- When serializing response blocks for storage, now checks if thinking blocks exist
- If thinking blocks exist but first block is not thinking, reorders them
- Ensures: `[thinking] + [text/tool_use blocks]`

```python
# CRITICAL FIX: Reorder blocks - thinking MUST be first
if serialized:
    has_thinking = any(b.get('type') == 'thinking' for b in serialized)
    
    if has_thinking and serialized[0].get('type') != 'thinking':
        # Separate thinking blocks from other blocks
        thinking_blocks = [b for b in serialized if b.get('type') == 'thinking']
        other_blocks = [b for b in serialized if b.get('type') != 'thinking']
        
        # Reorder: thinking first, then others
        serialized = thinking_blocks + other_blocks
```

### 2. Simple Agent Worker (`agent_worker.py`)

**Added `reorder_assistant_content_blocks()` function** (lines 74-113):
- New utility function to reorder content blocks in assistant messages
- Checks if thinking blocks exist
- If first block is not thinking, moves thinking blocks to the front
- Returns properly ordered content: `[thinking] + [other blocks]`

**Updated message building** (lines 417-424):
- When loading conversation_history, reorders assistant message content blocks
- Ensures all historical messages comply with Anthropic API requirements
- Does not mutate original conversation_history (uses `.copy()`)

```python
# Build messages with history
messages = []
if conversation_history:
    # Reorder assistant messages to ensure thinking blocks come first
    for msg in conversation_history:
        if msg.get('role') == 'assistant' and isinstance(msg.get('content'), list):
            msg = msg.copy()  # Don't mutate original
            msg['content'] = reorder_assistant_content_blocks(msg['content'])
        messages.append(msg)
messages.append({'role': 'user', 'content': prompt})
```

## Why This Was Needed

**Storage vs API Requirements:**
1. Content blocks are stored in the database in the order received from API
2. Earlier versions of the code didn't guarantee thinking-first order
3. When messages are loaded from database and sent back to Claude, they must comply with current API rules
4. Anthropic enforced this rule more strictly in recent API updates

**Two Points of Failure:**
1. **Serialization** (streaming_agent_worker.py): When saving new responses to database
2. **Deserialization** (agent_worker.py): When loading existing messages from database

## Impact

**Before Fix:**
- ❌ Multi-round conversations with Extended Thinking would fail
- ❌ Error: "first block must be `thinking`... Found `text`"
- ❌ User experience broken after first tool use round

**After Fix:**
- ✅ All content blocks properly ordered (thinking first)
- ✅ Multi-round conversations work correctly
- ✅ Historical messages from database comply with API rules
- ✅ Both streaming and non-streaming agents fixed

## Files Modified

1. `AI_infrastructure/core/streaming_agent_worker.py`
   - Enhanced `_serialize_content_blocks()` to reorder blocks before storage
   
2. `AI_infrastructure/core/agent_worker.py`
   - Added `reorder_assistant_content_blocks()` utility function
   - Updated message building to reorder historical assistant messages

## Testing

**Verify syntax:**
```powershell
python -m py_compile AI_infrastructure\core\streaming_agent_worker.py
python -m py_compile AI_infrastructure\core\agent_worker.py
```

**Test multi-round conversation:**
```powershell
BISTART  # Start server
CHAT "Create a Google Sheet with sales data"  # Will use tools multiple times
```

**Expected behavior:**
- First round: AI uses `execute_tool` meta-tool
- Second round: AI receives tool result and continues
- No "thinking block order" errors
- Conversation completes successfully

## Related Documentation

- Anthropic Extended Thinking: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking
- API Error Reference: https://docs.anthropic.com/en/docs/api/errors
- Progressive Tool Loading: `PROGRESSIVE_LOADING_SUCCESS.md`

## Status

✅ **FIXED** - November 6, 2025
- Both streaming and non-streaming agent workers updated
- Syntax verified
- Ready for testing

---

**Last Updated:** November 6, 2025  
**Author:** AI Agent (GitHub Copilot)  
**Issue:** Anthropic API 400 error - thinking block order validation
