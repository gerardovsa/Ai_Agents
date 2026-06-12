# Multi-User Sync Diagnostic Test

## Issue Report
User reports: "well it does not do the multi user sync"

## System Architecture (VERIFIED ✅)

### Backend Broadcasting (agent_routes_v4.py:1945-1965)
```python
def _broadcast_agent_thread_updated(event_payload):
    socketio_ext.emit(
        'agent_thread_updated',
        event_payload,
        room='command_center',  # ✅ Broadcasting to command_center room
        namespace='/ws/synergy'
    )
```

### Frontend Listener (agent-js.js:3626-3750)
```javascript
window.addEventListener('synergyrealtime:agent_thread_updated', async (evt) => {
    // ✅ Sophisticated listener exists
    // ✅ Loads messages from backend
    // ✅ Re-renders agent column
    // ✅ Deduplicates rapid updates (1500ms window)
});
```

### WebSocket Event Handler (synergy-realtime.js:286-298)
```javascript
_handleAgentThreadUpdated(data) {
    // ✅ Dispatches DOM event for modules to consume
    window.dispatchEvent(new CustomEvent('synergyrealtime:agent_thread_updated', {
        detail: data
    }));
}
```

### Room Join Logic (business-ai-platform-v2.html:24800)
```javascript
if (tabId === 'multi-agent') {
    SynergyRealtime.setPresenceContext({
        room: 'command_center',  // ✅ Joins command_center room
        badgeContainerId: 'command-center-active-users-badge',
        badgeCountId: 'command-center-active-users-count'
    });
}
```

## ✅ System Status: ALL COMPONENTS PRESENT

1. ✅ Backend broadcasts to `command_center` room
2. ✅ Frontend joins `command_center` room when opening multi-agent tab
3. ✅ WebSocket event handler dispatches to DOM
4. ✅ Sophisticated listener refreshes agent threads

## 🔍 Diagnostic Steps

### Test 1: Verify Room Join
**Open Browser Console:**
```javascript
// Check if WebSocket connected
SynergyRealtime.isConnected()
// Expected: true

// Check current room
SynergyRealtime.presenceContext.room
// Expected: 'command_center'
```

### Test 2: Verify Backend Broadcast
**Check Flask logs (AI_infrastructure/logs/flask_app.log):**
```
[STREAM] Broadcasting agent_thread_updated to command_center
```

### Test 3: Verify Frontend Receives Event
**Open Browser Console → Network Tab → WS → Messages:**
```json
{
  "type": "agent_thread_updated",
  "data": {
    "agent_id": "prime",
    "thread_slug": "thread_123",
    "message_count": 5
  }
}
```

### Test 4: Verify Listener Fires
**Open Browser Console:**
```javascript
// Should see log when message arrives:
[REALTIME] 🔄 Agent thread updated (Command Center): {...}
[REALTIME] ✅ Applying thread thread_123 to agent-1 ...
[REALTIME] 🔄 Refreshing agent-1 thread thread_123 (external update)
```

## 🐛 Potential Issues

### Issue 1: Users Not in Command Center Tab
**Symptom:** User on Home tab doesn't see updates
**Expected:** Multi-user sync ONLY works if both users are on Multi-Agent (Command Center) tab
**Solution:** Switch to Multi-Agent tab (tab with agent columns)

### Issue 2: WebSocket Not Connected
**Symptom:** `SynergyRealtime.isConnected()` returns false
**Fix:**
```javascript
await SynergyRealtime.connect()
```

### Issue 3: Room Not Joined
**Symptom:** `SynergyRealtime.presenceContext.room` is not 'command_center'
**Fix:**
```javascript
SynergyRealtime.setPresenceContext({
    room: 'command_center',
    badgeContainerId: 'command-center-active-users-badge',
    badgeCountId: 'command-center-active-users-count'
});
```

### Issue 4: Browser Cache
**Symptom:** Old code running (listener not installed)
**Fix:** Hard refresh (Ctrl+Shift+R) or clear cache

## 🧪 Manual Test Procedure

**Setup:**
1. Open **Browser A** (Chrome) → Login as User 1
2. Open **Browser B** (Firefox/Incognito) → Login as User 1 (same user)
3. Both browsers: Navigate to Multi-Agent tab (Command Center)

**Test Scenario:**
1. **Browser A:** Send message to Agent "Alpha-1"
2. **Browser B:** Should see message appear in Agent "Alpha-1" within 1-2 seconds

**Expected Behavior:**
- ✅ Browser B receives WebSocket event: `agent_thread_updated`
- ✅ Browser B fetches latest messages from backend
- ✅ Browser B re-renders Agent Alpha-1 column
- ✅ Browser B shows new message

**If Not Working:**
1. Check Browser B console for errors
2. Check Browser B Network → WS tab for WebSocket connection
3. Verify both browsers joined `command_center` room:
   ```javascript
   SynergyRealtime.presenceContext.room // Should be 'command_center'
   ```

## 📊 Monitoring Commands

**Check active WebSocket connections (Flask logs):**
```bash
grep "Connected to WebSocket" AI_infrastructure/logs/flask_app.log | tail -20
```

**Check broadcasts (Flask logs):**
```bash
grep "agent_thread_updated" AI_infrastructure/logs/flask_app.log | tail -20
```

**Check room subscriptions (Flask logs):**
```bash
grep "subscribed to room: command_center" AI_infrastructure/logs/flask_app.log | tail -20
```

## 🔧 Quick Fix (If Still Not Working)

Add enhanced logging to verify broadcasts are being sent:

**In browser console (both browsers):**
```javascript
// Enable verbose logging
SynergyRealtime.config.enableLogging = true;

// Listen for raw socket events
SynergyRealtime.socket.on('agent_thread_updated', (data) => {
    console.log('🔔 RAW SOCKET EVENT RECEIVED:', data);
});
```

## ✅ Success Criteria

When working correctly, you should see:

**Browser A (sender):**
```
[SEND] Sending message to agent-1
→ SSE stream starts
→ AI responds
→ Backend saves to database
→ Backend broadcasts: agent_thread_updated
```

**Browser B (receiver):**
```
🔔 RAW SOCKET EVENT RECEIVED: {agent_id: 'alpha', thread_slug: 'thread_123'}
[REALTIME] 🔄 Agent thread updated (Command Center): {...}
[REALTIME] 🔄 Refreshing agent-1 thread thread_123 (external update)
→ Fetches messages from backend
→ Re-renders agent column
→ Shows new message ✨
```

## 📝 Notes

- **Latency:** Expect 200-500ms delay (normal for WebSocket + database roundtrip)
- **Deduplication:** Rapid updates within 1500ms are deduplicated (prevents flicker)
- **Scope:** Only works for Command Center (Multi-Agent tab), not Prime
- **Persistence:** Messages persist in database (not ephemeral)

---

**Next Steps:** Run diagnostic tests and report which step fails.
