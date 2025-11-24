# Supabase Connection Manager - Quick Reference

## 🚀 Quick Commands

### Check Connection Status
```javascript
SupabaseConnectionManager.getState()
// Returns: {state, isOnline, channels, lastActivity, idleTime}
```

### Verify Single Client
```javascript
console.log('Same client?', 
    SupabaseConnectionManager.client === window.SUPABASE_CLIENT
); // Should be: true
```

### Force Reconnect
```javascript
SupabaseConnectionManager.disconnect();
await SupabaseConnectionManager.init();
```

### Backend Pool Stats
```python
from AI_infrastructure.shared.database_utils import log_pool_usage
log_pool_usage()
```

---

## ✅ Expected Console Output (Healthy)

```
✅ [SUPABASE] Config ready for connection manager
🔷 [Supabase] Initializing connection manager...
🔷 [Supabase] Creating new client...
✅ [Supabase] Realtime connection established
✅ [Supabase] Health monitoring started (30s idle threshold)
✅ [Supabase] Client created and aliases set
✅ [ThreadCardRealtime] Initialized with connection manager
✅ [Assignment] Realtime active with connection manager
```

---

## ❌ Warning Signs (Problems)

### Multiple Clients Warning
```
⚠️ Multiple GoTrueClient instances detected
```
**Fix:** Clear cache, hard reload (Ctrl+Shift+R)

### Channel Errors
```
❌ [ThreadCardRealtime] Channel error: CHANNEL_ERROR
```
**Fix:** Check network, verify connection manager loaded

### 500 Backend Errors
```
500 Internal Server Error: too many clients
```
**Fix:** Check for leaked connections, restart Flask

---

## 🔍 Debugging Checklist

- [ ] Clear browser cache (`localStorage.clear(); sessionStorage.clear()`)
- [ ] Hard reload page (Ctrl+Shift+R)
- [ ] Check DevTools → Console for warnings
- [ ] Check DevTools → Network → WS tab (should see 1 connection)
- [ ] Verify `SupabaseConnectionManager` exists
- [ ] Verify single client instance
- [ ] Check backend pool stats (Python)
- [ ] Test network reconnection (toggle offline/online)

---

## 📊 Health Check

### Good Signs ✅
- One WebSocket connection
- No "Multiple GoTrueClient" warnings
- Connection state: 'connected'
- Leaked connections: 0
- Health checks only when idle >30s

### Bad Signs ❌
- Multiple WebSocket attempts
- "Multiple GoTrueClient" warnings
- Connection state: 'failed'
- Leaked connections > 0
- Health checks every second

---

## 🛠️ Common Fixes

### Problem: No realtime updates
```javascript
// Check subscriptions
console.log('Channels:', SupabaseConnectionManager.channels.size);
// Should be: 2 or more

// Force reconnect
SupabaseConnectionManager.disconnect();
await SupabaseConnectionManager.init();
```

### Problem: Connection keeps failing
```javascript
// Check config
console.log('URL:', window.SUPABASE_URL);
console.log('Key:', window.SUPABASE_ANON_KEY ? 'Set' : 'Missing');

// Check network
console.log('Online:', navigator.onLine);
```

### Problem: Backend errors
```python
# Check for leaks
from AI_infrastructure.shared.database_utils import log_pool_usage
log_pool_usage()

# Look for: "Leaked connections: N" where N > 0
# Fix: Search for missing conn.close() calls
```

---

## 📝 Key Files

**Frontend:**
- `UI/js/supabase-connection-manager.js` - Main manager
- `UI/business-ai-platform-v2.html` - Config loading

**Backend:**
- `AI_infrastructure/shared/database_utils.py` - Connection pool

**Docs:**
- `SUPABASE_FIX_FINAL_SUMMARY_NOV24.md` - Complete guide
- `SUPABASE_CONNECTION_FIX_COMPLETE_NOV24.md` - Implementation details

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| WebSocket connections | 1 |
| Client instances | 1 |
| "Multiple GoTrueClient" warnings | 0 |
| CHANNEL_ERROR count | 0 |
| Backend 500 errors | 0 |
| Leaked connections | 0 |
| Page load time | <1s |

---

## 📞 Quick Test

```javascript
// Paste this in console:
(async () => {
    console.log('=== Supabase Health Check ===');
    
    // 1. Check manager
    console.log('1. Manager exists:', !!window.SupabaseConnectionManager);
    
    // 2. Check state
    const state = SupabaseConnectionManager?.getState();
    console.log('2. State:', state?.state);
    
    // 3. Check client
    const sameClient = SupabaseConnectionManager?.client === window.SUPABASE_CLIENT;
    console.log('3. Single client:', sameClient);
    
    // 4. Check channels
    const channels = SupabaseConnectionManager?.channels?.size;
    console.log('4. Channels:', channels);
    
    // 5. Overall
    const healthy = state?.state === 'connected' && sameClient && channels >= 2;
    console.log('\n✅ Result:', healthy ? 'HEALTHY' : 'NEEDS ATTENTION');
})();
```

Expected output:
```
=== Supabase Health Check ===
1. Manager exists: true
2. State: connected
3. Single client: true
4. Channels: 2
✅ Result: HEALTHY
```

---

**Last Updated:** November 24, 2025  
**Status:** Production Ready
