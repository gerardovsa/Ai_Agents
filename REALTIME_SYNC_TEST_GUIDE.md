# Real-time Message Sync - Quick Test Guide

## 🚀 Quick Test (2 Browsers)

### Setup
1. Open **Chrome** → Login as your user
2. Open **Firefox** (or Chrome Incognito) → Login as same user

### Test 1: Agent Column Sync
1. **Chrome**: Send "Hello from Chrome" to **Agent Alpha**
2. **Firefox**: Should see message appear instantly in Agent Alpha
3. **Firefox**: Reply "Hello from Firefox"
4. **Chrome**: Should see reply appear instantly

### Test 2: Prime AI Sync
1. **Chrome**: Send message in **Prime AI** chat
2. **Firefox**: Switch to Prime AI → Should see message
3. **Firefox**: Reply in Prime AI
4. **Chrome**: Should see reply instantly

### Test 3: Console Verification
Press F12 in both browsers and look for:
```
✅ [Realtime Init] Messages subscription active
📊 [Realtime Init] Active subscriptions: 8
```

When message arrives:
```
🔔 [Messages] New message received
📍 [Messages] Thread location: agent-1
🎨 [Messages] Rendering message in #agent-messages-1
✅ [Messages] Message rendered successfully
```

## 🎯 What Should Happen

### ✅ Success Indicators
- [ ] Message appears in other browser **within 1 second**
- [ ] Notification shows "New message in [Agent Name]"
- [ ] Green "live" badge appears on agent header
- [ ] Message has correct timestamp
- [ ] No duplicate messages
- [ ] Auto-scrolls to new message

### ❌ If It's Not Working

**1. Check subscriptions:**
```javascript
console.log(window.RealtimeSubscriptionsInit?.getActiveSubscriptions?.());
// Should include 'messages'
```

**2. Check session token:**
```javascript
console.log(localStorage.getItem('session_token'));
// Should show: session_1735987200000_abc123xyz
```

**3. Force reload:**
```
Ctrl+Shift+R (hard refresh both browsers)
```

**4. Check Flask logs:**
```
Look for: [MESSAGE SAVE] Session: session_xxxxx
```

## 🎨 Visual Indicators

### Live Viewer Badge
When you send a message in Browser 1, Browser 2 should show:
```
[Agent Alpha Header]  🟢 1 live
```
- Green pulsing dot
- Number of other sessions
- "live" label
- Disappears after 30 seconds

### Column Highlight
Agent column should have subtle green glow when others are viewing

## 🔧 Troubleshooting Commands

### Clear Session Token (if duplicates appear)
```javascript
localStorage.removeItem('session_token');
location.reload();
```

### Force Re-subscribe
```javascript
window.RealtimeSubscriptionsInit.unsubscribeAll();
await window.RealtimeSubscriptionsInit.initializeAllSubscriptions();
```

### Check Message Count
```javascript
// In browser console
const threadId = window.ThreadManager?.currentThreadId;
const messages = window.MessageStore?.getMessages(threadId);
console.log(`Thread ${threadId} has ${messages?.length} messages`);
```

## 📱 Mobile Testing

1. Desktop: Send message to Agent Alpha
2. Mobile (logged in same user): Open Agent Alpha
3. Message should appear instantly on mobile
4. Reply from mobile
5. Desktop should see reply

## 🎯 Expected Console Output (Full Flow)

### Browser 1 (Sender):
```
[Agent Alpha] User message rendered
📡 [Agent Alpha] Broadcasted user message to other sessions
🔔 [Messages] New message received: {...}
✅ [Messages] Message from this session, skipping (already rendered)
```

### Browser 2 (Receiver):
```
🔔 [Messages] New message received: {...}
📍 [Messages] Thread location: agent-1
📍 [Messages] Target: Alpha
📥 [Messages] Message from another session, rendering...
🎨 [Messages] Rendering message in #agent-messages-1
✅ [Messages] Message rendered successfully
ℹ️ [Notification] New message in Alpha
```

## ✅ Success Checklist

After testing, verify:
- [ ] Messages sync across browsers (**< 1 second**)
- [ ] No duplicate messages
- [ ] Notifications appear for other sessions' messages
- [ ] Live viewer badge appears/disappears correctly
- [ ] Works in both agent columns AND Prime AI
- [ ] Auto-scrolls to new messages
- [ ] Session token persists after page reload
- [ ] Console shows 8 active subscriptions

## 🎉 If All Tests Pass

The real-time message synchronization is working correctly! You now have:
- ✅ Cross-session message sync
- ✅ Cross-device collaboration
- ✅ Live presence indicators
- ✅ Instant notifications
- ✅ Duplicate prevention

---

**Test Duration:** ~5 minutes  
**Required:** 2 browsers (or 1 browser + 1 mobile device)  
**User:** Any user account (test with same user in both sessions)
