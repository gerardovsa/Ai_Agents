# Stream 400 Error - Root Cause Analysis

**Date:** November 17, 2025  
**Issue:** Stream endpoint returns 400 "No user message found" when chatting in existing threads  
**Status:** 🔴 CRITICAL - Identified root cause  

---

## Symptom

**Works:** Creating NEW thread and sending first message  
**Fails:** Loading EXISTING thread and sending new message

**Error Logs:**
```
[Stream 1] Session: 1763208281309
[Stream 1] Conversation length: 0
[Stream 1] All agent_ids in manager: ['1_1763208281309']
[Stream 1] Agent 1 NOT in state manager!  ← MISLEADING (it IS there, key format issue)
[Stream 1] Conversation is EMPTY - message not added by /start endpoint?
[Stream 1] ERROR: No user message found in conversation
GET /api/agent/stream/1?session_id=1763208281309 HTTP/1.1" 400
```

---

## Root Cause

### The Problem

When you load an **existing thread** and type a new message:

1. ✅ Thread loads from database into UI
2. ✅ UI displays conversation history  
3. ✅ You type new message and press Send
4. ❌ **UI calls `/stream` directly** WITHOUT calling `/start` first
5. ❌ Agent state manager has empty conversation (state created on-demand)
6. ❌ Stream endpoint can't find user message → 400 error

### Why New Threads Work

When you create a **new thread**:

1. ✅ UI calls `/threads/create` → creates empty thread
2. ✅ You type first message
3. ✅ **UI calls `/start`** → adds message to agent_state_manager
4. ✅ UI calls `/stream` → finds message → works!

### The Key Difference

**New thread flow:**
```
POST /threads/create → POST /agent/1/start → GET /agent/stream/1
                        (adds message)         (finds message)
```

**Existing thread flow:**
```
GET /threads/123 → GET /agent/stream/1
                   (NO /start call! No message added!)
```

---

## Evidence from Logs

### State Manager Key Format

```python
# agent_state_manager.py line 40
def _get_key(self, agent_id: str, session_id: str) -> str:
    return f"{agent_id}_{session_id}"
```

State is stored as `'1_1763208281309'`, not `'1'`.

Debug log shows:
```
All agent_ids in manager: ['1_1763208281309']  ← State EXISTS
Agent 1 NOT in state manager!  ← Misleading check (looking for '1', but key is '1_1763208281309')
```

The state **does exist**, but the debug logging checks for wrong key format.

### Conversation Empty

```
[Stream 1] Conversation length: 0
Conversation is EMPTY - message not added by /start endpoint?
```

This confirms: `/start` was NOT called before `/stream`.

---

## Solution Options

### Option 1: Fix UI to Always Call /start (RECOMMENDED)

**Change:** Modify UI JavaScript to call `/start` before `/stream` for ALL messages (new and existing threads)

**Files to modify:**
- `UI/business-ai-platform-v2.html` - sendChatMessage() function

**Pros:**
- Follows existing architecture
- No backend changes needed
- Consistent flow for all threads

**Cons:**
- UI change required
- Must test all chat scenarios

### Option 2: Make /stream Accept Empty Conversation

**Change:** Modify `/stream` endpoint to accept message in request body if conversation is empty

**Files to modify:**
- `AI_infrastructure/routes/agent_routes_v4.py` - stream_agent() function

**Pros:**
- Backward compatible
- Single fix point

**Cons:**
- Violates separation of concerns (/start adds messages, /stream processes them)
- Requires signature changes
- More complex error handling

### Option 3: Hybrid - /stream Falls Back to Database

**Change:** If conversation empty in agent_state_manager, load from database

**Files to modify:**
- `AI_infrastructure/routes/agent_routes_v4.py` - stream_agent() function

**Pros:**
- Handles both new and existing threads
- No UI changes needed

**Cons:**
- Database query on every stream (performance)
- Duplicates message loading logic
- State synchronization issues

---

## Recommended Fix (Option 1)

### UI Changes Needed

**File:** `UI/business-ai-platform-v2.html`

**Function:** `sendChatMessage()`

**Current behavior:**
```javascript
// Somewhere in sendChatMessage()
// Existing thread: Call /stream directly
const streamUrl = `/api/agent/stream/${agentId}?session_id=${sessionId}`;
```

**Required change:**
```javascript
// ALWAYS call /start first (for new AND existing threads)
const startResponse = await fetch(`/api/agent/${agentId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: userMessage,
        session_id: sessionId,
        thread_id: threadId,
        conversation_history: conversationHistory  // Important!
    })
});

// THEN call /stream
const streamUrl = `/api/agent/stream/${agentId}?session_id=${sessionId}`;
```

**Why this works:**
- `/start` adds message to agent_state_manager
- `/start` updates conversation history
- `/stream` finds message and processes it

---

## Testing Checklist

After implementing fix:

### Test 1: New Thread
1. Click "New Chat" in Prime
2. Type "Test message 1"
3. Press Send
4. **Expected:** Message sends, AI responds (NO 400 error)

### Test 2: Existing Thread
1. Load existing thread from history
2. Type "Test message 2"
3. Press Send
4. **Expected:** Message sends, AI responds (NO 400 error)

### Test 3: Thread with History
1. Load thread with 10+ messages
2. Type "Test message 3"
3. Press Send
4. **Expected:** Message sends, AI responds with context

### Test 4: Multi-Agent
1. Load thread in Agent-1
2. Move thread to Agent-2
3. Type "Test message 4"
4. Press Send
5. **Expected:** Message sends to Agent-2

---

## Debug Commands

### Check Agent State Manager

```python
# In agent_routes_v4.py, add temporary logging:
print(f"[DEBUG] All states: {agent_state_manager.states.keys()}")
print(f"[DEBUG] Looking for: {agent_id}_{session_id}")
state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
print(f"[DEBUG] State conversation length: {len(state.get('conversation', []))}")
```

### Check UI Network Tab

1. Open DevTools (F12) → Network tab
2. Filter: Fetch/XHR
3. Send message
4. **Check sequence:**
   - Should see: POST `/agent/1/start` → GET `/agent/stream/1`
   - Currently: Only GET `/agent/stream/1` (missing /start!)

### Check Render Logs

```
# Look for this sequence:
[START] Added current user message to conversation - X messages total
[Stream 1] Conversation length: X  ← Should match!
```

If conversation length is 0, /start wasn't called.

---

## Why Debug Logs Are Misleading

The log says:
```
Agent 1 NOT in state manager!
```

But this is **incorrect**. The state manager has key `'1_1763208281309'`, and the check is looking for `'1'`.

**The actual issue:** Conversation is empty because `/start` wasn't called.

**NOT the issue:** State manager key format (that's working correctly).

---

## Implementation Priority

🔴 **HIGH** - Blocking production use

**Estimated Time:** 30 minutes
- Find sendChatMessage() in UI
- Add /start call before /stream
- Test 4 scenarios above
- Deploy to Render

**Risk Level:** 🟢 LOW
- Backend unchanged (no risk)
- UI change is additive (always call /start)
- Easy to rollback if needed

---

## Related Files

- `UI/business-ai-platform-v2.html` - sendChatMessage() function (needs fix)
- `AI_infrastructure/routes/agent_routes_v4.py` - /start and /stream endpoints
- `AI_infrastructure/core/agent_state_manager.py` - State storage logic
- `RENDER_DEPLOYMENT_FIX.md` - Related deployment issues

---

**Next Step:** Locate `sendChatMessage()` in UI and add `/start` call before `/stream` for ALL message sends (not just new threads).
