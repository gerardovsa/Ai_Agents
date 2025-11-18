# Tool Use / Tool Result Error Fix Plan

## Problem Analysis

### Error Message
```
messages.1: `tool_use` ids were found without `tool_result` blocks immediately after: 
toolu_0135rN1EZs9wGcoZvuDcWV2Z, toolu_013ygPYg892UFEgYhNNJ3xcF, 
toolu_01Cdg4j2QTkxpP8ZPRyxijdd, toolu_01FKpB2PzUY8wF3nTeqwr4A5, 
toolu_01Hkc7nLL5bqhG9BeFCiwMiB, toolu_01MfBwhXmn8VkWrDppXtBGNV, 
toolu_01RC1GWRiwTUic7vxhcYHxc7, toolu_01TnxGkgTEBrMkRuv6HALaPM, 
toolu_01VzXE79kTtQtRsVnc788tpg.
Each `tool_use` block must have a corresponding `tool_result` block in the next message.
```

### Root Causes

1. **Incorrect Conversation Storage**
   - Frontend sends conversation with MIXED tool_use and tool_result blocks in assistant messages
   - Example from log:
     ```
     Message 1 (assistant): ['tool_use', 'tool_result', 'tool_use', 'tool_result', ...]
     ```
   - This violates Anthropic API rules: tool_result blocks CANNOT be in assistant messages

2. **Validation Extraction Issue**
   - Validation code DOES extract tool_results from assistant messages
   - BUT it doesn't verify ALL tool_use blocks have corresponding tool_results
   - Log shows:
     ```
     [Combined Worker] Message 1 (assistant) reordered:
       Before: ['tool_use', 'tool_result', 'tool_use', 'tool_result', ...]
       After:  ['tool_use', 'tool_use', 'tool_use', ...]  # Only 9 tool_use blocks
     [Combined Worker] Inserting 9 extracted tool_result blocks as user message
     ```
   - 9 tool_use blocks in assistant, 9 tool_results extracted
   - BUT API complains about 9 DIFFERENT tool_use IDs!

3. **ID Mismatch**
   - The tool_use IDs in the assistant message don't match the tool_result IDs extracted
   - API expected: toolu_0135rN1EZs9wGcoZvuDcWV2Z, ...
   - But validation log shows: ['toolu_01Hkc7nLL5bqhG9BeFCiwMiB', 'toolu_01VzXE79kTtQtRsVnc788tpg', ...]
   - **These are DIFFERENT tool_use IDs!**

### The REAL Problem

The conversation being loaded from database has:
```json
{
  "role": "assistant",
  "content": [
    {"type": "tool_use", "id": "toolu_0135rN1EZs9wGcoZvuDcWV2Z", ...},
    {"type": "tool_result", "tool_use_id": "toolu_OLD_123", ...},  // OLD result!
    {"type": "tool_use", "id": "toolu_013ygPYg892UFEgYhNNJ3xcF", ...},
    {"type": "tool_result", "tool_use_id": "toolu_OLD_456", ...},  // OLD result!
    ...
  ]
}
```

When validation extracts tool_results, it creates:
```json
// Assistant message (cleaned)
{
  "role": "assistant",
  "content": [
    {"type": "tool_use", "id": "toolu_0135rN1EZs9wGcoZvuDcWV2Z", ...},
    {"type": "tool_use", "id": "toolu_013ygPYg892UFEgYhNNJ3xcF", ...},
    ...
  ]
}

// User message (with extracted tool_results)
{
  "role": "user",
  "content": [
    {"type": "tool_result", "tool_use_id": "toolu_OLD_123", ...},  // WRONG ID!
    {"type": "tool_result", "tool_use_id": "toolu_OLD_456", ...},  // WRONG ID!
    ...
  ]
}
```

**Result**: API sees tool_use IDs that don't have matching tool_result IDs!

## Solution Strategy

### Phase 1: Immediate Fix (Combined Agent Worker Validation)

Update `validate_conversation_history()` to:

1. **Verify tool_use/tool_result ID matching**
   - When extracting tool_results from assistant message
   - Check that EACH tool_result.tool_use_id matches a tool_use.id
   - If mismatch detected, DISCARD the assistant message entirely

2. **Add comprehensive logging**
   - Log tool_use IDs found in assistant message
   - Log tool_result IDs found in extracted blocks
   - Log any mismatches

3. **Fail-safe behavior**
   - If validation detects ID mismatch, truncate conversation to BEFORE the bad message
   - This prevents API errors and allows conversation to continue

### Phase 2: Database Storage Fix (Prevent Root Cause)

Update how messages are saved:

1. **Frontend message saving** (`/api/threads/messages/save`)
   - Add validation BEFORE saving to database
   - Reject messages with tool_result blocks in assistant content
   - Log warnings about malformed messages

2. **Streaming worker message appending**
   - After each round, save the conversation properly:
     - Assistant message: tool_use blocks only (no tool_results)
     - Separate user message: tool_result blocks only
   - Never intermix them

### Phase 3: Cleanup Existing Data

Create a migration script to:
1. Query all saved threads
2. Find assistant messages with tool_result blocks
3. Split them into proper assistant + user message pairs
4. Update database

## Implementation Priority

**IMMEDIATE**: Phase 1 (Validation Fix) - Prevents API errors
**HIGH**: Phase 2 (Storage Fix) - Prevents new bad data
**MEDIUM**: Phase 3 (Cleanup) - Fixes existing bad data

## Files to Modify

1. `AI_infrastructure/core/combined_agent_worker.py`
   - Line 320-380: `validate_and_reorder_assistant_content()`
   - Add ID matching verification

2. `AI_infrastructure/routes/thread_routes copy.py`
   - Line 1240-1280: `save_messages()`
   - Add validation before saving

3. `AI_infrastructure/routes/agent_routes_v4.py`
   - Line 1270-1310: Thread auto-save in streaming endpoint
   - Ensure proper message structure

## Testing Plan

1. Create test conversation with tool_use/tool_result blocks
2. Save to database
3. Load and validate
4. Confirm no API errors
5. Verify IDs match correctly

## Success Criteria

- ✅ No more "tool_use ids were found without tool_result blocks" errors
- ✅ All tool_use IDs have matching tool_result IDs
- ✅ Conversations load correctly from database
- ✅ Agent responses save properly
- ✅ Multi-round streaming works without errors
