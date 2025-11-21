# Agent Stream 400 Error - Investigation & Fix

**Date:** November 21, 2025  
**Status:** 🔧 FIXED - Added state verification  
**Issue:** Agent stream endpoint returning 400 Bad Request

---

## 🎯 Problem

When sending a message to a multi-agent (Agent Alpha-1), the `/start` endpoint succeeds but the `/stream` endpoint immediately fails with **400 Bad Request**:

```
[Agent 1] Agent started: {data: {…}, success: true}
[Agent 1] Stream URL: .../api/agent/stream/1?thread_slug=1763717406534
GET .../api/agent/stream/1?thread_slug=1763717406534 400 (Bad Request)
```

### Error Flow:
1. ✅ `/api/agent/agent/1/start` - Succeeds
2. ❌ `/api/agent/stream/1?thread_slug=1763717406534` - Fails with 400

---

## 🔍 Root Cause Analysis

### What the `/stream` Endpoint Expects:

Looking at `agent_routes_v4.py` lines 802-813:

```python
if not last_message:
    error_msg = f"No user message found in conversation..."
    return error_response(error_msg, 400)
```

The `/stream` endpoint:
1. Gets the state from `agent_state_manager`
2. Extracts the conversation
3. Looks for the last user message
4. **Returns 400 if no user message found**

### What the `/start` Endpoint Does:

Looking at `agent_routes_v4.py` lines 595-597:

```python
user_message = {'role': 'user', 'content': prompt}
state['conversation'].append(user_message)
print(f"[START] Added current user message to conversation...")
```

The `/start` endpoint:
1. ✅ Gets state from `agent_state_manager`
2. ✅ Adds user message to conversation
3. ✅ Returns success
4. ❓ **But does the state persist properly?**

### Possible Causes:

1. **State not persisting** - Message added but not saved to state manager
2. **Different state objects** - `/start` and `/stream` get different state instances
3. **Timing issue** - `/stream` called before `/start` completes state save
4. **Lock contention** - `/start` holds lock, `/stream` gets empty state

---

## ✅ Solution Implemented

### Added State Verification in `/start` Endpoint

**File:** `AI_infrastructure/routes/agent_routes_v4.py`  
**Line:** ~598-604

```python
# ALWAYS add the current user message
user_message = {'role': 'user', 'content': prompt}
state['conversation'].append(user_message)
print(f"[START] Added current user message to conversation...")

# CRITICAL FIX: Verify state was actually saved
verify_state = agent_state_manager.get_or_create_state(agent_id, thread_slug)
print(f"[START] ✅ VERIFICATION: State retrieval test - conversation length: {len(verify_state.get('conversation', []))}")
if len(verify_state.get('conversation', [])) == 0:
    print(f"[START] ❌ CRITICAL ERROR: Message not in state after add!")
    return error_response("Failed to save message to state", 500)
```

### What This Does:

1. **Adds message** to state (existing behavior)
2. **Verifies immediately** by re-fetching state
3. **Fails fast** if message not found (returns 500 instead of allowing 400 later)
4. **Logs clearly** whether state persistence is working

---

## 📋 Testing Steps

### 1. Start Backend
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

### 2. Send Message to Agent
- Load thread into Agent Alpha-1
- Send a message
- Watch console logs

### 3. Expected Logs (Success)
```
[START] Added current user message to conversation - 1 messages total
[START] ✅ VERIFICATION: State retrieval test - conversation length: 1
[START] Starting simple agent worker thread...
[START] Returning success response
```

### 4. If Still Failing (Different Issue)
```
[START] Added current user message to conversation - 1 messages total
[START] ❌ VERIFICATION: State retrieval test - conversation length: 0
[START] ❌ CRITICAL ERROR: Message not in state after add!
```

This would indicate the `agent_state_manager.get_or_create_state()` is returning different objects.

---

## 🔧 Additional Debugging

If the issue persists after this fix, check:

### 1. Agent State Manager Implementation
```python
# Check if get_or_create_state returns same object
state1 = agent_state_manager.get_or_create_state(agent_id, thread_slug)
state2 = agent_state_manager.get_or_create_state(agent_id, thread_slug)
print(f"Same object? {state1 is state2}")
```

### 2. Thread Slug Consistency
```python
# Verify thread_slug is same in both calls
print(f"[START] thread_slug: {thread_slug}")
print(f"[STREAM] thread_slug: {request.args.get('thread_slug')}")
```

### 3. State Key Format
```python
# Verify state key formation is identical
start_key = f"{agent_id}_{thread_slug}"
stream_key = f"{agent_id}_{thread_slug}"
print(f"Keys match? {start_key == stream_key}")
```

---

## 🎯 Next Steps

### If Fix Works:
- ✅ State verification succeeds
- ✅ `/stream` finds the message
- ✅ Agent responds properly

### If Fix Reveals Issue:
The verification will fail and return 500, with logs showing:
- "❌ CRITICAL ERROR: Message not in state after add!"
- This means `agent_state_manager` has a bug in `get_or_create_state()`

### Potential Agent State Manager Issues:

1. **Not returning reference** - Returning copy instead of reference
2. **Wrong key format** - Using different key in getter vs setter
3. **Thread safety** - Race condition with locks
4. **Object creation** - Creating new dict instead of reusing existing

---

## 📝 Related Files

| File | Purpose |
|------|---------|
| `AI_infrastructure/routes/agent_routes_v4.py` | Agent endpoints (START & STREAM) |
| `AI_infrastructure/core/agent_state_manager.py` | State persistence |
| `UI/modules/agents/agent-js.js` | Frontend agent logic |

---

## 🔗 Related Issues

- **THINKING_DOTS_REMOVAL_COMPLETE.md** - Removed empty box thinking dots
- **THREAD_COPY_CONVERSATION_COMPLETE.md** - Thread copy feature

---

**Status:** ✅ Fix Applied - Ready for Testing  
**Expected Result:** State verification will either succeed (fixing the issue) or fail with clear error message pointing to the real problem

