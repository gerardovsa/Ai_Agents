# 🔄 Duplicate Request Handling Analysis - December 4, 2025

## 🎯 Issue Discovered

**Question from User:**
> "What if the user sends a message but then there was an error of some kind and the response was not returned, and then they send the same message again because they want that answer -- how does this deduplication detection work? How does the system handle this... as the second request being triggered was because the first failed... not because the first is still running..."

---

## 🔍 Current System Behavior

### **CRITICAL FINDING: NO DUPLICATE DETECTION EXISTS! ⚠️**

After comprehensive code archaeology analysis, I discovered:

### 1. **Lock Mechanism (Threading)**
**File**: `AI_infrastructure/core/agent_state_manager.py`

```python
def get_lock(self, agent_id: str, thread_id: str) -> threading.Lock:
    """Get execution lock for agent (thread safety)"""
    key = self._get_key(agent_id, thread_id)
    
    with self._state_lock:
        if key not in self.locks:
            self.locks[key] = threading.Lock()
        
        return self.locks[key]
```

**What it does:**
- Creates a `threading.Lock` per agent+thread combination
- Lock is acquired in `agent_routes_v4.py` line 678: `lock.acquire()`
- Lock is released in `combined_agent_worker.py` line 1869: `lock.release()` (in finally block)

**What it SHOULD prevent:**
- Two threads processing the same agent+thread simultaneously

**What it ACTUALLY prevents:**
- **NOTHING in your scenario!** ❌

---

### 2. **Status Tracking**
**File**: `AI_infrastructure/core/agent_state_manager.py`

```python
def update_status(self, agent_id: str, thread_id: str, status: str):
    """Update agent status (idle, running, error)"""
    state = self.get_state(agent_id, thread_id)
    if state:
        state['status'] = status
        state['last_activity'] = datetime.now()
```

**Status values used:**
- `'idle'` - Agent not processing
- `'processing'` - Agent currently working
- `'error'` - Agent encountered error

**Set in**: `agent_routes_v4.py` line 676:
```python
agent_state_manager.update_status(agent_id, thread_slug, 'processing')
```

**Problem**: Status is NEVER checked before accepting new request! ⚠️

---

## 🚨 The Problem: Your Exact Scenario

### Scenario Walkthrough:

1. **User sends message:** "check the xero functions"
2. **Backend receives request** → Sets status to 'processing' → Acquires lock → Spawns worker thread
3. **Worker thread starts** → Calls `calculate_flyers_god` → Database hangs (150s with no timeout)
4. **SSE stream breaks** → Browser shows `ERR_INCOMPLETE_CHUNKED_ENCODING`
5. **Worker thread STILL RUNNING** (blocked on database call, lock still held)
6. **User thinks it failed** → Sends same message again: "check the xero functions"
7. **Backend receives second request** → **NO CHECK** if first request still running!
8. **Backend tries to acquire lock** → **BLOCKS** waiting for first request to release lock
9. **Second request hangs** waiting for first request (which is hung on database)
10. **User frustrated** → Sends third request → Same problem!

### Result:
- **Multiple requests pile up** waiting for same lock
- **All requests hung** on same database timeout
- **No feedback to user** that first request is still running
- **After 150s** first request fails → Releases lock → Second request starts → Same problem!

---

## 🔧 Current Issues

### Issue 1: No Status Check Before Processing
**File**: `agent_routes_v4.py` - `/agent/<agent_id>/start` endpoint

**Current code** (line 670-678):
```python
lock = agent_state_manager.get_lock(agent_id, thread_slug)
queue = agent_state_manager.get_queue(agent_id, thread_slug)
agent_state_manager.update_status(agent_id, thread_slug, 'processing')

lock.acquire()  # ← BLOCKS if already held!
```

**Missing**:
```python
# Check if already processing
current_state = agent_state_manager.get_state(agent_id, thread_slug)
if current_state and current_state['status'] == 'processing':
    return error_response("Agent is already processing your previous request. Please wait.", 409)
```

---

### Issue 2: Lock Not Released on Error
**File**: `combined_agent_worker.py` - `run_simple_agent_worker()`

**Current code** (line 1867-1870):
```python
finally:
    try:
        lock.release()
    except:
        pass  # ← Swallows all errors!
```

**Problem**:
- If lock was never acquired (edge case), `release()` raises `RuntimeError`
- If lock was already released (double-release), `release()` raises `RuntimeError`
- Empty `except:` swallows these errors silently

**Better approach**:
```python
finally:
    try:
        if lock.locked():  # Check if lock is actually held
            lock.release()
    except RuntimeError as e:
        print(f"[LOCK ERROR] Failed to release lock: {e}")
```

---

### Issue 3: Status Never Set to 'error' on Failure
**File**: `combined_agent_worker.py`

**Current code** (line 1861-1866):
```python
except Exception as e:
    print(f"{log_prefix} Error: {e}")
    import traceback
    traceback.print_exc()
    queue.put({'type': 'error', 'error': str(e)})
    # ← Status stays 'processing'!
```

**Missing**:
```python
except Exception as e:
    print(f"{log_prefix} Error: {e}")
    import traceback
    traceback.print_exc()
    queue.put({'type': 'error', 'error': str(e)})
    
    # CRITICAL: Update status to 'error' so new requests aren't blocked
    from core.agent_state_manager import agent_state_manager
    agent_state_manager.update_status(agent_id, session_id, 'error')
```

---

### Issue 4: No Timeout on Lock Acquisition
**File**: `agent_routes_v4.py`

**Current code** (line 678):
```python
lock.acquire()  # ← Blocks FOREVER if lock held
```

**Problem**: If first request hung, second request waits FOREVER

**Better approach**:
```python
if not lock.acquire(timeout=5):  # Wait max 5 seconds
    return error_response(
        "Agent is currently processing another request. Please wait and try again.",
        409
    )
```

---

## 📋 Complete Fix Implementation

### Fix 1: Add Status Check Before Processing
**File**: `AI_infrastructure/routes/agent_routes_v4.py` (after line 673)

```python
# STEP 6: CHECK IF ALREADY PROCESSING
# ============================================
print(f"\n[START] 🔍 STEP 6: Checking if agent already processing...")

current_state = agent_state_manager.get_state(agent_id, thread_slug)
if current_state and current_state.get('status') == 'processing':
    print(f"[START] ⚠️ Agent already processing request for thread {thread_slug}")
    return error_response(
        "Your previous message is still being processed. Please wait for the response before sending another message.",
        409  # HTTP 409 Conflict
    )

print(f"[START] ✅ Agent available - proceeding with request")

# STEP 7: START AI WORKER THREAD
# ============================================
print(f"\n[START] 🤖 STEP 7: Starting AI worker thread...")
```

### Fix 2: Add Timeout to Lock Acquisition
**File**: `AI_infrastructure/routes/agent_routes_v4.py` (replace line 678)

```python
# Acquire lock with timeout (prevents infinite waiting)
lock_acquired = lock.acquire(timeout=5.0)
if not lock_acquired:
    print(f"[START] ❌ Failed to acquire lock - agent still processing previous request")
    agent_state_manager.update_status(agent_id, thread_slug, 'idle')  # Reset status
    return error_response(
        "Agent is currently busy processing another request. Please try again in a few seconds.",
        409
    )

print(f"[START] 🔒 Lock acquired successfully")
```

### Fix 3: Update Status to 'error' on Failure
**File**: `AI_infrastructure/core/combined_agent_worker.py` (in except block, line 1864)

```python
except Exception as e:
    print(f"{log_prefix} Error: {e}")
    import traceback
    traceback.print_exc()
    queue.put({'type': 'error', 'error': str(e)})
    
    # CRITICAL: Update status so future requests aren't blocked
    from core.agent_state_manager import agent_state_manager
    agent_state_manager.update_status(agent_id, session_id, 'error')
```

### Fix 4: Better Lock Release with Status Reset
**File**: `AI_infrastructure/core/combined_agent_worker.py` (replace finally block, line 1867)

```python
finally:
    # Reset status to idle (allow new requests)
    from core.agent_state_manager import agent_state_manager
    agent_state_manager.update_status(agent_id, session_id, 'idle')
    
    # Release lock safely
    try:
        if lock.locked():
            lock.release()
            print(f"{log_prefix} 🔓 Lock released")
        else:
            print(f"{log_prefix} ⚠️ Lock was not held (already released)")
    except RuntimeError as e:
        print(f"{log_prefix} ❌ Failed to release lock: {e}")
```

---

## 🎯 Expected Behavior After Fixes

### Scenario 1: User Sends Duplicate While First Request Processing
1. **User sends message 1** → Status set to 'processing', lock acquired
2. **Worker thread starts** → Processing message
3. **User sends message 2 (duplicate)** → Status check sees 'processing'
4. **Backend returns 409 error** → "Your previous message is still being processed"
5. **Frontend shows message** → "Please wait for your previous message to complete"
6. **First request completes** → Status set to 'idle', lock released
7. **User can now send message 2** → Works normally

### Scenario 2: First Request Fails (Error)
1. **User sends message 1** → Status set to 'processing', lock acquired
2. **Worker thread encounters error** → Catches exception
3. **Status updated to 'error'** → Lock released in finally block
4. **User sends message 2** → Status check sees 'error' (not 'processing')
5. **Backend accepts request** → Resets status to 'processing'
6. **Message 2 processed normally**

### Scenario 3: First Request Hangs (Timeout)
1. **User sends message 1** → Status set to 'processing', lock acquired
2. **Worker thread hangs on database** (150s timeout)
3. **User sends message 2** → Tries to acquire lock with 5s timeout
4. **Lock acquisition times out** → Returns 409 error
5. **Backend returns** → "Agent is currently busy, try again in a few seconds"
6. **After 150s** → First request fails, lock released, status set to 'error'
7. **User sends message 3** → Works normally

---

## 🔬 Testing Strategy

### Test 1: Duplicate Request While Processing
```bash
# Terminal 1
curl -X POST http://localhost:5000/agent/1/start \
  -H "Content-Type: application/json" \
  -d '{"thread_slug": "test-thread", "message": "test message"}'

# Terminal 2 (send IMMEDIATELY)
curl -X POST http://localhost:5000/agent/1/start \
  -H "Content-Type: application/json" \
  -d '{"thread_slug": "test-thread", "message": "test message"}'
```

**Expected**: Second request returns 409 with "already processing" message

### Test 2: Request After Error
```python
# Simulate error in worker
def test_error_recovery():
    # Send request that will fail
    response1 = send_message("trigger database error")
    assert response1.status == 500
    
    # Send second request immediately
    response2 = send_message("normal message")
    assert response2.status == 200  # Should work!
```

### Test 3: Lock Timeout
```python
# Simulate hanging worker
def test_lock_timeout():
    # Send request that hangs (database timeout)
    send_message("calculate_flyers_god with bad DB")
    
    # Wait 2 seconds, send duplicate
    time.sleep(2)
    response = send_message("same message")
    
    # Should get 409 (not hang forever)
    assert response.status == 409
    assert "busy" in response.json()['error'].lower()
```

---

## 📊 Impact Summary

### Current Issues Found:
1. ❌ No status check → Multiple requests pile up waiting for lock
2. ❌ No lock timeout → Second request waits forever if first hung
3. ❌ Status never set to 'error' → Future requests think agent still processing
4. ❌ Silent lock release errors → Hard to debug lock issues

### After Fixes:
1. ✅ Status check → Immediate 409 response if already processing
2. ✅ Lock timeout (5s) → Quick feedback if agent busy
3. ✅ Status updated to 'error' → Future requests know first one failed
4. ✅ Better lock release → Clear logging of lock issues

### User Experience:
- **Before**: Duplicate requests hang indefinitely, no feedback
- **After**: Immediate feedback "still processing, please wait" with 409 status

---

## 🚀 Recommended Actions

### Priority 1 (Critical - Implement Now):
1. Add status check before processing (Fix 1)
2. Add lock timeout (Fix 2)
3. Update status to 'error' on failure (Fix 3)

### Priority 2 (Important - Implement This Week):
4. Better lock release with status reset (Fix 4)
5. Add frontend handling for 409 responses
6. Add retry logic with exponential backoff

### Priority 3 (Nice to Have):
7. Add request deduplication by message hash
8. Add request queue with max length
9. Add user notification when request completes

---

**Document Version**: 1.0  
**Date**: December 4, 2025  
**Author**: AI Code Archeology Agent  
**Status**: Analysis Complete - Awaiting Implementation

