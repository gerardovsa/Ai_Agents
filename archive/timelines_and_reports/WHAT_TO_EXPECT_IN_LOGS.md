# What To Expect In Flask Logs - November 25, 2025

## Overview
After the connection pool leak fix and logging enhancements, you should see clear markers for every operation showing SUCCESS, FAILURE, or SKIP status.

## Current Logging Status

### ✅ Fully Logged Functions
1. **autosave_thread** - Complete with entry/success/skip/error logging
2. **create_thread** - Entry logging added (more detail needed)

### ⏳ Partial Logging
- Most other functions have basic error handling but lack structured flow logging

## What You'll See When Testing

### Test 1: Create a New Thread
**Action:** Open UI, start new conversation

**Expected Logs:**
```
================================================================================
[THREAD CREATE] 📝 Creating new thread...
================================================================================
[THREAD CREATE] User ID: 14
[THREAD CREATE] Agent: prime
[THREAD CREATE] Title: New Chat
[POOL] Got connection from pool for 'sessions' (wait: 0.5ms)
[THREAD CREATE] ✅ SUCCESS: Thread created
[THREAD CREATE] Thread slug: thread_1732571234567
[THREAD CREATE] Title: New Chat
================================================================================
```

**What This Tells You:**
- ✅ Thread creation is working
- ✅ Connection pool is healthy (< 5ms wait time)
- ✅ No connection leaks (connection returned to pool)

---

### Test 2: Send Messages (Autosave Trigger)
**Action:** Send 5 messages in a conversation

**Expected Logs:**

**Message 1-4 (Skipped):**
```
================================================================================
[AUTOSAVE] 🔄 Checking autosave trigger...
================================================================================
[AUTOSAVE] Agent: prime, Session: abc123
[AUTOSAVE] Message count: 1
[AUTOSAVE] ⏭️  SKIPPED: Waiting for milestone (current: 1, next: 5)
================================================================================
```

**Message 5 (Saved):**
```
================================================================================
[AUTOSAVE] 🔄 Checking autosave trigger...
================================================================================
[AUTOSAVE] Agent: prime, Session: abc123
[AUTOSAVE] Message count: 5
[AUTOSAVE] 💾 Milestone reached (5 messages) - saving...
[POOL] Got connection from pool for 'sessions' (wait: 0.8ms)
[AUTOSAVE] ✅ SUCCESS: Thread auto-saved
[AUTOSAVE] Thread ID: prime_abc123
[AUTOSAVE] Messages: 5
================================================================================
```

**What This Tells You:**
- ✅ Autosave logic is working correctly
- ✅ Connection properly acquired and returned
- ✅ No more connection leaks from autosave

---

### Test 3: Load Existing Thread
**Action:** Refresh page or click on thread in sidebar

**Expected Logs (NOT YET IMPLEMENTED - TODO):**
```
================================================================================
[THREAD LOAD] 📂 Loading thread...
[THREAD LOAD] Thread slug: thread_123
================================================================================
[THREAD LOAD] User ID: 14
[POOL] Got connection from pool for 'sessions' (wait: 1.2ms)
[THREAD LOAD] ✅ Thread found in database
[THREAD LOAD] ✅ SUCCESS: Thread loaded
[THREAD LOAD] Messages: 12
================================================================================
```

---

### Test 4: List All Threads
**Action:** Open threads sidebar or dashboard

**Expected Logs (NOT YET IMPLEMENTED - TODO):**
```
================================================================================
[THREAD LIST] 📊 Listing threads...
================================================================================
[THREAD LIST] User ID: 14
[THREAD LIST] Filters: category=None, limit=50
[POOL] Got connection from pool for 'sessions' (wait: 0.9ms)
[THREAD LIST] Found 23 threads
[THREAD LIST] ✅ SUCCESS: Threads retrieved
================================================================================
```

---

## Connection Pool Health Indicators

### ✅ Healthy Pool
```
[POOL] Got connection from pool for 'ai_infrastructure' (wait: 0.5ms)
[POOL] Returned connection to pool for 'ai_infrastructure'
```
**Indicators:**
- Wait time < 5ms
- Connections acquired = connections returned
- No "LEAKED" warnings

---

### ⚠️  Pool Under Stress
```
[POOL] Got connection from pool for 'ai_infrastructure' (wait: 50ms)
[POOL] Pool usage: 2/2 connections in use
```
**Indicators:**
- Wait time 10-100ms (slow but working)
- All connections in use but being returned
- Consider increasing traffic handling

---

### ❌ Pool Exhausted (CRITICAL)
```
[POOL] ❌ CONNECTION POOL EXHAUSTED - LEAKED CONNECTIONS DETECTED
Schema: ai_infrastructure
Pool stats:
  Acquired: 9
  Returned: 7
  LEAKED: 2

SOLUTION:
  1. Check code for missing conn.close() calls
  2. Use context managers: with get_database_connection() as conn:
  3. Restart application to reset pool
```
**Indicators:**
- `Acquired > Returned` = Connections leaked
- All requests will fail until restart
- **ACTION REQUIRED:** Restart server immediately

---

## Error Scenarios To Test

### Test: Missing Required Field
**Action:** Try to create thread without user_id

**Expected Logs:**
```
================================================================================
[THREAD CREATE] 📝 Creating new thread...
================================================================================
[THREAD CREATE] User ID: None
[THREAD CREATE] ❌ FAILED: Missing user_id
================================================================================
```
**HTTP Response:** 400 Bad Request

---

### Test: Thread Not Found
**Action:** Try to load non-existent thread

**Expected Logs (TODO):**
```
================================================================================
[THREAD LOAD] 📂 Loading thread...
[THREAD LOAD] Thread slug: nonexistent_thread
================================================================================
[THREAD LOAD] User ID: 14
[POOL] Got connection from pool for 'sessions' (wait: 0.6ms)
[THREAD LOAD] ❌ FAILED: Thread not found in database
================================================================================
```
**HTTP Response:** 404 Not Found

---

### Test: Database Connection Error
**Action:** Simulate Supabase downtime

**Expected Logs:**
```
================================================================================
[THREAD CREATE] 📝 Creating new thread...
================================================================================
[THREAD CREATE] User ID: 14
[POOL] ❌ DB CONNECTION FAILED - UNEXPECTED ERROR
Database: sessions
Error Type: OperationalError
Error Message: could not connect to server
[THREAD CREATE] ❌ EXCEPTION: Database connection failed
Traceback (most recent call last):
  ...
================================================================================
```
**HTTP Response:** 500 Internal Server Error

---

## Monitoring Checklist

### Every Hour, Check For:
- [ ] ✅ SUCCESS count increasing (operations working)
- [ ] ❌ FAILED/EXCEPTION count = 0 or very low (< 1%)
- [ ] Connection pool wait times < 5ms (healthy pool)
- [ ] No "LEAKED" connection warnings
- [ ] No "EXHAUSTED" pool errors

### If You See Issues:
1. **High failure rate** → Check validation logic or client requests
2. **Long wait times** → Consider increasing pool size (carefully!)
3. **Leaked connections** → Find function missing `conn.close()` or `with` block
4. **Pool exhausted** → Restart server immediately

---

## Testing Script

```powershell
# Test 1: Create thread
curl -X POST http://localhost:5001/api/threads/create `
  -H "Content-Type: application/json" `
  -d '{"user_id": 14, "title": "Test Thread"}'

# Test 2: List threads  
curl http://localhost:5001/api/threads/list?user_id=14

# Test 3: Autosave (need active conversation)
# Open UI and send 5 messages - watch Flask logs

# Test 4: Connection pool health
curl http://localhost:5001/health
```

---

## Next Steps

1. **Restart Server** - Apply logging fixes
2. **Test Each Function** - Verify logs appear correctly
3. **Add Remaining Logging** - Complete functions not yet logged
4. **Monitor Production** - Watch for patterns

---

**Current Status:**
- ✅ Logging framework established
- ✅ Connection leak fixed in autosave_thread
- ⏳ Rolling out to remaining functions
- 🎯 Goal: 100% operation visibility

**Last Updated:** November 25, 2025
