# Synergy Real-Time WebSocket - Quick Start Guide

**Quick reference for testing and verifying the complete WebSocket integration.**

---

## ⚡ Quick Test (30 seconds)

### 1. Start the Server
```powershell
BISTART
```

Wait for:
```
✅ Flask app running on http://localhost:5001
✅ Socket.IO initialized
✅ 594 tools loaded
```

---

### 2. Open Two Browser Tabs
- Tab 1: http://localhost:5001
- Tab 2: http://localhost:5001

Login in both tabs, navigate to Synergy dashboard.

---

### 3. Test Real-Time Sync

**Test 1: Create Session**
- Tab 1: Click "+ New Session" button
- Tab 2: Watch for new card to appear instantly with animation
- ✅ Expected: Card slides in from top in Tab 2

**Test 2: Update Session**
- Tab 1: Edit any session (change title or priority)
- Tab 2: Watch for blue flash on the card
- ✅ Expected: Card updates in-place with background flash

**Test 3: Move Card (Kanban)**
- Tab 1: Drag card from "Backlog" to "In Progress"
- Tab 2: Watch card move between columns
- ✅ Expected: Card fades out, slides into new column

**Test 4: Delete Session**
- Tab 1: Delete any session
- Tab 2: Watch card disappear
- ✅ Expected: Card fades out and scales down

---

## 🔍 Verify Connection Status

**Look for connection indicator:**
- Top-right corner of Synergy dashboard
- 🟢 Green dot = Connected
- 🔴 Red dot = Disconnected
- 🟡 Yellow dot = Connecting

**Check browser console (F12):**
```
✅ [SYNERGY] Real-time WebSocket connected
🟢 [SYNERGY-WS] Connected
[SYNERGY-WS] Subscribed to synergy_board
```

---

## 📊 Verify Backend Logs

**Check Flask terminal output:**
```
[SYNERGY-WS] Client connected: <socket_id>
[SYNERGY-WS] Client subscribed to synergy_board
[SYNERGY-WS] Broadcasting: session_created
[SYNERGY-WS] Broadcasting: session_updated
```

---

## 🐛 Quick Troubleshooting

### WebSocket Not Connecting?

**Check 1: Socket.IO CDN Loaded**
```javascript
// Browser console (F12)
typeof io
// Expected: "function"
```

**Check 2: SynergyRealtime Loaded**
```javascript
// Browser console
typeof SynergyRealtime
// Expected: "object"
```

**Check 3: Flask Server Running**
```powershell
curl http://localhost:5001/health
# Expected: {"status": "healthy"}
```

---

### Events Not Broadcasting?

**Check Flask Logs:**
```powershell
# Should see emit calls in terminal:
[SYNERGY-WS] Broadcasting: session_updated
```

**Check Browser Console:**
```javascript
// Should see event handlers firing:
[REALTIME] Updating session card: sess_abc123
```

**Manual Test:**
```javascript
// Browser console
SynergyRealtime.socket.emit('ping', { test: true })
// Check Flask logs for ping received
```

---

## 🎯 Success Indicators

✅ **Connection Status:** Green dot visible in dashboard  
✅ **Console Logs:** Both frontend and backend logs show connection  
✅ **Real-Time Sync:** Changes in Tab 1 appear instantly in Tab 2  
✅ **Animations:** Smooth transitions (no instant jumps)  
✅ **Auto-Reconnect:** Recovers after server restart  

---

## 🔄 Test Auto-Reconnection

**Steps:**
1. Open Synergy dashboard (verify green connection status)
2. Stop Flask: `BISTOP`
3. Watch console: Should see "🔴 [SYNERGY-WS] Disconnected"
4. Watch status indicator: Should turn red
5. Restart Flask: `BISTART`
6. Watch console: Should see reconnection attempts (2s, 4s, 8s delays)
7. Verify green status when reconnected

**Expected Behavior:**
- Exponential backoff reconnection
- Max 10 attempts (then gives up)
- Automatic recovery when server available

---

## 📝 Files to Check

If issues occur, verify these files:

### Backend (Flask)
```
AI_infrastructure/flask_app.py (lines 361-520)
  - SocketIO initialization
  - WebSocket event handlers

AI_infrastructure/routes/synergy_routes.py
  - Line ~645: socketio.emit('session_created')
  - Line ~795: socketio.emit('session_updated')
  - Line ~845: socketio.emit('column_changed')
  - Line ~870: socketio.emit('session_deleted')
```

### Frontend (HTML/JS)
```
UI/business-ai-platform-v2.html
  - Line ~70: Socket.IO CDN script tag
  - Line ~72: synergy-realtime.js script tag
  - Line ~33390: SynergyRealtime.connect() in init()
  - Line ~15275: SynergyRealtime.disconnect() in switchTab()
  - Line ~34660: addCardRealtime() method
  - Line ~34710: updateCardRealtime() method
  - Line ~34820: removeCardRealtime() method

UI/js/synergy-realtime.js
  - Complete WebSocket manager (450+ lines)
  - Event handlers for all 4 event types
```

---

## 🚀 Quick Deploy to Render

**Prerequisites:**
- Git repository synced
- Render.com account configured
- Environment variables set:
  - `RENDER=true`
  - `SUPABASE_DB_URL` (Session Pooler URL)

**Deploy Steps:**
```bash
# Commit changes
git add .
git commit -m "Add Synergy real-time WebSocket integration"
git push origin main

# Render auto-deploys from main branch
# Wait 2-3 minutes for deployment

# Verify deployment
curl https://your-app.onrender.com/health
```

**Test on Render:**
1. Open dashboard: https://your-app.onrender.com
2. Open 2 browser tabs
3. Test real-time sync (same steps as local testing)

---

## 🎉 You're Done!

Real-time WebSocket sync is now fully integrated and ready for production.

**Next Steps:**
- Monitor WebSocket connections in production
- Track events per minute for performance
- Add user presence indicators (future enhancement)
- Implement collaborative editing (future enhancement)

---

**Last Updated:** January 24, 2025  
**Status:** ✅ Production Ready
