# Test Device Lock with Browser

## Clear Cache & Test

1. **Open Chrome DevTools** (F12)

2. **Go to Console tab**

3. **Clear localStorage:**
```javascript
localStorage.clear();
console.log('✅ localStorage cleared');
```

4. **Refresh page** (F5 or Ctrl+R)

5. **Check console for:**
```
🔧 [DEV MODE] Setting up default test user for device lock testing...
✅ [DEV MODE] Auto-logged in as test user
```

6. **Verify no 401 errors:**
   - Should NOT see: `/api/auth/profile Failed to load resource: 401`
   - Should see: Thread list loading

7. **Test device lock:**
   - Click on a thread
   - Look for lock/unlock buttons (if frontend is integrated)
   - Orange border should appear when locked

## Expected Console Output

```
🔧 [DEV MODE] Setting up default test user for device lock testing...
✅ [DEV MODE] Auto-logged in as test user
🔍 [USER CHECK] Verifying user data from backend...
✅ [USER CHECK] User ID verified
[THREADS] Loading threads for user 1...
✅ [THREADS] Loaded X threads
```

## Test with 2 Browsers

**Browser A (Chrome):**
1. Open: http://localhost:5001/UI/business-ai-platform-v2.html
2. Console: `localStorage.clear(); location.reload();`
3. Should auto-login as user 1
4. Load a thread
5. (Future) Click "Lock to This Device"

**Browser B (Edge or Firefox):**
1. Open: http://localhost:5001/UI/business-ai-platform-v2.html
2. Console: `localStorage.clear(); location.reload();`
3. Should auto-login as same user 1 (different device)
4. Load same thread
5. (Future) Should see orange border + "Locked by [Device]" banner

## Troubleshooting

**Still seeing 401 errors?**
- Check backend terminal for: `🔧 [DEV MODE] Dev token detected`
- If not appearing, restart Flask: `Get-Process python | Stop-Process -Force; BISTART`

**Thread assignments error?**
- Fixed - now uses correct database (ai_infrastructure.db)
- Should no longer see 500 error

**Device lock not working?**
- Backend is ready (tested)
- Frontend integration still pending (JavaScript + CSS)
- See DEVICE_LOCK_IMPLEMENTATION_COMPLETE.md for integration steps
