# Manual Thread Isolation Test

## What Was Fixed

✅ **Backend Changes:**
- Added validation: `session_id` MUST equal `thread_slug`
- If mismatch detected, backend forces `session_id = thread_slug`
- All state keys now use `{agent_id}_{thread_slug}`

✅ **Frontend Changes:**
- `sendAgentMessage()` now uses `thread.id` (thread_slug) as `session_id`
- Both `session_id` and `thread_slug` sent to backend (with same value)
- SSE stream connections use `thread_slug` query parameter
- `loadThreadIntoAgent()` syncs `MultiAgent.sessions[agentId] = thread.id`

## Manual Testing Steps

### Test 1: Two Agents, Different Threads

1. **Open Business AI Platform:** http://localhost:5001

2. **Create Thread A for Agent 1:**
   - Click on **Agent 1** column
   - Click "New Thread" button
   - Title: "Thread A - Testing Agent 1"
   - Send message: "Hello from Agent 1"
   - ✅ **Expected:** Response appears in Agent 1 column

3. **Create Thread B for Agent 8 (Delta):**
   - Click on **Agent 8** column
   - Click "New Thread" button
   - Title: "Thread B - Testing Agent 8"
   - Send message: "Hello from Agent 8"
   - ✅ **Expected:** Response appears in Agent 8 column

4. **Verify Isolation:**
   - Switch back to Agent 1 → Thread A
   - ✅ **Expected:** Shows only "Hello from Agent 1" and its response
   - ❌ **FAIL if:** Shows "Hello from Agent 8" or Agent 8's response
   
   - Switch to Agent 8 → Thread B
   - ✅ **Expected:** Shows only "Hello from Agent 8" and its response
   - ❌ **FAIL if:** Shows "Hello from Agent 1" or Agent 1's response

### Test 2: Multiple Threads in Same Agent

1. **In Agent 1, create Thread C:**
   - Click "New Thread"
   - Title: "Thread C"
   - Send: "Message for Thread C"
   
2. **In Agent 1, create Thread D:**
   - Click "New Thread"
   - Title: "Thread D"
   - Send: "Message for Thread D"

3. **Verify Each Thread Shows Only Its Messages:**
   - Switch to Thread C → Should show only "Message for Thread C"
   - Switch to Thread D → Should show only "Message for Thread D"
   - ❌ **FAIL if:** Messages from Thread C appear in Thread D or vice versa

### Test 3: Moving Threads Between Locations

1. **Create thread in Agent 1:**
   - Send message: "Original message in Agent 1"

2. **Drag thread to Agent 8:**
   - Drag the thread card from Agent 1's area to Agent 8's area
   - ✅ **Expected:** Thread moves to Agent 8 column
   - ✅ **Expected:** Messages remain intact

3. **Send new message in Agent 8:**
   - In the moved thread, send: "New message in Agent 8"
   - ✅ **Expected:** Response appears in Agent 8 (not Agent 1)
   - ✅ **Expected:** Both old and new messages visible

### Test 4: Prime Chat Isolation

1. **In AI Prime, start a conversation:**
   - Send: "Hello Prime AI"
   - ✅ **Expected:** Response appears in Prime chat area

2. **In Agent 1, start a conversation:**
   - Send: "Hello Agent 1"
   - ✅ **Expected:** Response appears in Agent 1 column

3. **Verify No Cross-Contamination:**
   - Check Prime chat → Should NOT show Agent 1's messages
   - Check Agent 1 → Should NOT show Prime's messages

## Backend Logs to Watch

Open Terminal and run:
```powershell
BISTART
```

**Look for these log patterns:**

### ✅ SUCCESS Patterns:
```
[START] Thread slug: 1763479637070
[START] Session ID: 1763479637070 (✅ SYNCED)
[START] ✅ Using thread_slug for isolation: 17634796370...
[START] State key: 1_1763479637070 (using thread_slug for isolation)
```

### ❌ ERROR Patterns (Would indicate issues):
```
[START] ❌ THREAD ISOLATION ERROR:
  - session_id: 12345
  - thread_slug: 67890
  - MISMATCH DETECTED - This causes cross-contamination!
[START] 🔧 FORCING session_id = thread_slug for isolation
```

**If you see the ERROR pattern:** The frontend is still sending mismatched IDs. Check browser console for errors.

## Browser Console Logs

Press **F12** → Console tab

**Look for these patterns:**

### ✅ SUCCESS:
```javascript
[Agent Agent 1] Thread slug: 1763479637070
[Agent Agent 1] Session ID: 1763479637070 (✅ SYNCED)
[Agent Agent 1] 🔧 Syncing session_id with thread_slug: 1763479637070
[Stream] Connecting with thread_slug: 1763479637070
```

### ❌ MISMATCH (Would indicate frontend issue):
```javascript
[Agent Agent 1] Session ID: 17634796 (❌ MISMATCH!)
```

## Troubleshooting

### If Contamination Still Occurs:

1. **Clear Browser Cache:**
   ```
   Ctrl+Shift+Delete → Clear cache → Reload page
   ```

2. **Check Backend State Keys:**
   - Backend logs show: `All state keys in manager: ['1_1763479637070', '8_1763479326677']`
   - Each agent should have unique thread_slug in the key

3. **Verify Thread Slugs:**
   - Open browser DevTools → Application → IndexedDB → ThreadManager
   - Check `thread.id` values - should be unique timestamps like "1763479637070"

4. **Check Database:**
   ```sql
   SELECT id, thread_slug, name, location
   FROM sessions.threads
   WHERE user_id = 14
   ORDER BY created_at DESC;
   ```
   - `thread_slug` should match what's in logs
   - `location` should match agent assignment (e.g., "agent-1", "agent-8")

### If SSE Streams Fail:

Check that stream URLs use `thread_slug`:
```javascript
// CORRECT:
/api/agent/stream/1?thread_slug=1763479637070

// WRONG (old way):
/api/agent/stream/1?session_id=12345
```

## Success Criteria

✅ **Test passes if:**
1. Agent 1's responses appear ONLY in Agent 1 column
2. Agent 8's responses appear ONLY in Agent 8 column
3. Prime's responses appear ONLY in Prime chat area
4. Each thread shows ONLY its own messages
5. Moving threads between agents preserves messages
6. Backend logs show `session_id === thread_slug`
7. No "THREAD ISOLATION ERROR" messages in logs

❌ **Test fails if:**
1. Agent 8's response appears in Agent 1's chat (or vice versa)
2. Messages from one thread appear in another thread
3. Backend logs show "MISMATCH DETECTED"
4. Any cross-contamination between Prime and Agents

## Next Steps After Successful Test

1. **Deploy to Render:** Changes are already pushed (commit 57145cf)
2. **Test on Production:** Repeat tests on https://ai-agents-backend-singapore.onrender.com
3. **Monitor Logs:** Watch Render logs for any isolation errors
4. **User Acceptance:** Have users test multi-agent workflows

---

**Status:** Ready for testing  
**Commit:** 57145cf  
**Date:** November 19, 2025  
**Critical Fix:** session_id === thread_slug enforcement throughout stack
