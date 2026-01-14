# ThreadViewChoice Fix - Testing Guide

**Quick reference for testing the ThreadViewChoice modal fix**

---

## Quick Test Scenarios

### ✅ Test 1: Agent Thread (Modal Should Show)
```
1. Open thread menu
2. Find thread with agent badge (Agent 1, 2, or 3)
3. Click the thread
4. EXPECT: ThreadViewChoice modal appears
5. EXPECT: Two buttons: "View in Prime" and "Keep in Agent X"
```

**Why**: Prevents accidental removal from agent column

---

### ✅ Test 2: Prime Thread (No Modal)
```
1. Open thread menu
2. Find thread with "Prime" badge (or no agent)
3. Click the thread
4. EXPECT: NO modal shown
5. EXPECT: Thread loads directly in Prime panel
6. EXPECT: All messages render
7. EXPECT: Prime header shows 5-row thread-info
```

**Why**: Prime threads should load seamlessly without interruption

---

### ✅ Test 3: Modal Choices
```
SETUP: Click agent-assigned thread to show modal

Choice A: "View in Prime"
  → Thread moves from agent to Prime
  → Thread loads in Prime panel
  → Messages render
  → Agent column shows empty state

Choice B: "Keep in Agent X"
  → Thread stays in agent column
  → View switches to show agent
  → Thread visible in agent column
  → No changes to assignment
```

---

## Console Logs to Watch

### Agent Thread (Modal)
```javascript
📍 [getThreadLocation] Thread 1762192838469 location: agent-1
📍 [switchThread] Thread 1762192838469 is assigned to agent-1, showing modal
[ThreadViewChoice] Showing modal for thread: 1762192838469, agent: 1
```

### Prime Thread (Direct Load)
```javascript
📍 [getThreadLocation] Thread 1762192838470 location: Prime/unassigned
✅ [switchThread] Thread 1762192838470 location: null, loading in Prime
[loadThreadInPrime] Loading thread 1762192838470
[THREAD LOAD] Loading 5 messages from backend...
```

---

## Common Issues

### Issue: Modal shows for Prime thread
**Fix**: Check backend endpoint `/api/thread-assignments/location/<id>` returns `null`

### Issue: No messages render
**Fix**: Check `thread.message_count > 0` and backend loads messages

### Issue: Modal doesn't show for agent thread
**Fix**: Check backend returns `agent-1`, `agent-2`, or `agent-3`

---

## Browser Dev Tools Commands

```javascript
// Check current thread location (open console)
ThreadManager.getThreadLocation('YOUR_THREAD_ID').then(loc => console.log('Location:', loc));

// Force switch (bypass modal)
ThreadManager.switchThread('YOUR_THREAD_ID', true);

// Check thread data
console.log(ThreadManager.threads.find(t => t.id === 'YOUR_THREAD_ID'));

// Check backend directly
fetch('/api/thread-assignments/location/YOUR_THREAD_ID?user_id=1')
  .then(r => r.json())
  .then(d => console.log(d));
```

---

## Expected Behavior Summary

| Thread Location | Modal Shows? | Where Loads? | Message Render? |
|----------------|--------------|--------------|-----------------|
| `agent-1` | ✅ YES | User choice | ✅ YES |
| `agent-2` | ✅ YES | User choice | ✅ YES |
| `agent-3` | ✅ YES | User choice | ✅ YES |
| `prime` / `null` | ❌ NO | Prime (direct) | ✅ YES |
| Force switch | ❌ NO | Prime (direct) | ✅ YES |

---

## Success Criteria

✅ **All checks must pass:**

1. Agent threads show modal (prevents accidental removal)
2. Prime threads load directly (no interruption)
3. All messages render correctly
4. Prime header updates (5-row thread-info)
5. Agent columns stay in sync
6. No JavaScript errors in console
7. Backend location check works
8. Force switch bypasses modal

---

**Need Help?**
- Check console logs for 📍 emoji markers
- Verify backend endpoint: `/api/thread-assignments/location/<id>`
- Review `THREAD_VIEW_CHOICE_FIX_COMPLETE.md` for detailed info

**Last Updated**: January 2025
