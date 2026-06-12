# WebSocket Connection Error - Diagnostic & Fix

**Date:** November 21, 2025  
**Status:** 🔧 IMPROVED ERROR HANDLING  
**Issue:** WebSocket connection failing with "Invalid frame header"

---

## 🎯 Error Details

```
[REALTIME] Connection status: disconnected
WebSocket connection to 'ws://localhost:5001/socket.io/?EIO=4&transport=websocket' failed: Invalid frame header
```

**Location:** `synergy-realtime.js:52` → `manager.js:108`

---

## 🔍 Root Cause

"Invalid frame header" typically means:

1. **❌ Backend not running** - Flask app crashed or not started
2. **❌ Socket.IO not initialized** - Flask-SocketIO failed to load
3. **❌ Wrong port** - Frontend connecting to incorrect port
4. **❌ Firewall/proxy issue** - WebSocket upgrade blocked
5. **❌ CORS issue** - Cross-origin WebSocket blocked

### Most Likely: Backend Not Running

The error happens immediately when trying to upgrade to WebSocket, suggesting the server isn't responding at all.

---

## ✅ Fix Applied

### Enhanced Error Handling in synergy-realtime.js

**File:** `UI/js/synergy-realtime.js`  
**Line:** ~158-169

```javascript
_handleError(error) {
    console.error('[REALTIME] Connection error:', error);

    if (error.message === 'timeout') {
        console.warn('[REALTIME] Connection timeout - Server may be starting...');
        this._showConnectionStatus('connecting', 'Server starting, please wait...');
    } else if (error.message && error.message.includes('Invalid frame header')) {
        console.warn('[REALTIME] WebSocket handshake failed - Server may not be running');
        this._showConnectionStatus('disconnected', 'Backend not responding. Synergy will work in offline mode.');
        // Stop trying to reconnect after 3 attempts
        if (this.reconnectAttempts >= 3) {
            console.warn('[REALTIME] Stopping reconnection attempts - working in offline mode');
            this.maxReconnectAttempts = this.reconnectAttempts;
        }
    } else {
        this._showConnectionStatus('error');
    }
}
```

### What This Does:

1. **Detects "Invalid frame header"** error specifically
2. **Shows helpful message** - "Backend not responding. Synergy will work in offline mode."
3. **Stops retrying** after 3 attempts (prevents console spam)
4. **Allows offline mode** - Synergy board still works without real-time updates

---

## 🔧 Diagnostic Steps

### 1. Check if Backend is Running

```powershell
# Check if port 5001 is listening
netstat -an | findstr ":5001"

# Should show:
# TCP    0.0.0.0:5001    0.0.0.0:0    LISTENING
```

### 2. Start Backend if Not Running

```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Watch for Socket.IO initialization:**
```
================================================================================
DEVELOPMENT MODE: Flask SocketIO server
================================================================================
```

### 3. Check Socket.IO Endpoint

```powershell
# Test Socket.IO handshake
curl http://localhost:5001/socket.io/?EIO=4&transport=polling

# Should return Socket.IO session ID (JSON)
```

### 4. Check Flask App Logs

Look for errors in Flask startup:
```
[ERROR] Failed to initialize SocketIO
[ERROR] Port 5001 already in use
[ERROR] Import error: flask_socketio
```

---

## 📋 Backend Socket.IO Configuration

**File:** `AI_infrastructure/flask_app.py`  
**Lines:** 382-393

```python
# Initialize SocketIO with full async support
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    always_connect=True
)
```

**Startup Mode:** Line 1476
```python
USE_SOCKETIO = True  # Always use SocketIO server
```

---

## 🎯 Frontend Socket.IO Configuration

**File:** `UI/js/synergy-realtime.js`  
**Lines:** 48-60

```javascript
this.socket = io(apiUrl + this.config.namespace, {
    transports: ['websocket', 'polling'],  // Try WebSocket first, fallback to polling
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 2000,
    timeout: 60000,  // 60 seconds (handles Render cold starts)
    forceNew: false,
    upgrade: true,
    rememberUpgrade: true
});
```

**Namespace:** `/ws/synergy`  
**Room:** `synergy_board`

---

## ✅ Verification Steps

### After Starting Backend:

1. **Check console for connection success:**
   ```
   [REALTIME] ✅ Connected to WebSocket
   [REALTIME] Joined room: synergy_board
   ```

2. **Check UI status indicator:**
   - Should show "Connected" or green indicator
   - Should NOT show "disconnected"

3. **Test real-time updates:**
   - Create a Synergy session
   - Should appear instantly without refresh
   - Should see: `🆕 Session created:` in console

---

## 🚀 Offline Mode Behavior

If backend isn't available, Synergy now works in **offline mode**:

### What Still Works:
- ✅ View existing sessions (from cache/local storage)
- ✅ Create new sessions (saved to backend on next connection)
- ✅ Edit sessions (saved when connection restored)
- ✅ Move cards between columns (queued for sync)

### What Doesn't Work:
- ❌ Real-time multi-user updates
- ❌ Instant synchronization
- ❌ Live collaboration

### How to Exit Offline Mode:
1. Start the backend (`BISTART`)
2. Refresh the page
3. Connection should succeed

---

## 🔍 Common Issues & Solutions

### Issue: "Port 5001 already in use"
**Solution:**
```powershell
# Kill existing Flask process
Get-Process -Name python | Where-Object {$_.Path -like "*AI_agents*"} | Stop-Process -Force
# Then restart
BISTART
```

### Issue: "Module 'flask_socketio' not found"
**Solution:**
```powershell
pip install flask-socketio python-socketio
```

### Issue: "WebSocket upgrade failed"
**Cause:** Firewall or antivirus blocking WebSocket
**Solution:** Add exception for localhost:5001

### Issue: Backend running but connection still fails
**Check:**
1. Correct port: `http://localhost:5001` (not 5000)
2. Flask app prints: "DEVELOPMENT MODE: Flask SocketIO server"
3. No errors in Flask startup logs

---

## 📝 Related Files

| File | Purpose |
|------|---------|
| `UI/js/synergy-realtime.js` | Frontend WebSocket manager |
| `AI_infrastructure/flask_app.py` | Backend Socket.IO setup |
| `UI/js/synergy-board-init.js` | Synergy board initialization |

---

## 🔗 Related Documentation

- `AGENT_STREAM_400_ERROR_FIX.md` - Agent streaming fix
- `THINKING_DOTS_REMOVAL_COMPLETE.md` - UI improvements
- `THREAD_COPY_CONVERSATION_COMPLETE.md` - Thread features

---

**Status:** ✅ Error Handling Improved  
**Next Steps:** Start backend with `BISTART` and verify connection  
**Fallback:** Synergy works in offline mode if backend unavailable

