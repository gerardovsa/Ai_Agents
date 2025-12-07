# 🚀 Quick Start - AI Agents Platform

**⚠️ IMPORTANT**: Always access via `http://localhost:5001`, **NEVER** open HTML file directly!

---

## ✅ Correct Way to Start

### Step 1: Start Server
```powershell
cd "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure"
BISTART
```

**Wait for**:
```
 * Running on http://0.0.0.0:5001 (Press CTRL+C to quit)
✅ Server ready
```

### Step 2: Open Browser
Navigate to: **`http://localhost:5001`**

✅ This serves `UI/business-ai-platform-v2.html` correctly
✅ No CORS errors
✅ Service worker works
✅ All modules load properly

---

## ❌ Common Mistake

**DON'T** open the file directly:
```
file:///C:/Users/gpoli/GIT/AI_agents/UI/business-ai-platform-v2.html
```

**Why this fails**:
- ❌ CORS blocks ES6 module imports
- ❌ Service workers don't work
- ❌ `fetch()` calls fail
- ❌ Can't load external modules

**Error you'll see**:
```
Access to script at 'file:///.../module.js' from origin 'null' 
has been blocked by CORS policy
```

---

## 🔍 How to Tell Which You're Using

**Check browser address bar**:

✅ **Correct**: `http://localhost:5001`
```
Protocol: http:
Hostname: localhost
Port: 5001
```

❌ **Wrong**: `file:///C:/Users/gpoli/...`
```
Protocol: file:
Origin: null
```

---

## 🧪 Testing Phase 1 Optimization

Now that you know the correct way to access it:

### Step 1: Clear Cache
```javascript
// In browser console (F12):
localStorage.clear();
sessionStorage.clear();
caches.keys().then(names => names.forEach(name => caches.delete(name)));
```

### Step 2: Hard Refresh
`Ctrl + Shift + R` (hard reload)

### Step 3: Time It
- Open DevTools (F12)
- Go to Network tab
- Look at bottom: "Finish: X.XXs"
- Should see <1s to login screen

### Step 4: Check Console
You should see:
```
✅ LazyLoader initialized
✅ Lazy Loader Manifests loaded
📦 Available manifests: postAuth, synergy, automation, ...
```

**No CORS errors!**

---

## 📊 What You Should See

### Network Tab (Before Login):
```
Name                          Size      Time
================================================
business-ai-platform-v2.html  150 KB    0.2s
lazy-loader.js                12 KB     0.05s
lazy-loader-manifests.js      8 KB      0.05s
font-awesome/all.min.css      100 KB    0.1s
user_auth.js                  20 KB     0.05s
================================================
TOTAL                         ~280 KB   ~0.5s
```

### Console (Before Login):
```
✅ LazyLoader initialized
✅ Lazy Loader Manifests loaded
📦 Available manifests: postAuth, synergy, ...
[AUTH] Checking authentication status...
[AUTH] No active session - Showing login screen...
```

**No errors about CORS or file:// protocol!**

---

## 🐛 If You Still See CORS Errors

1. **Check URL bar**: Must be `http://localhost:5001`
2. **Restart server**: Sometimes port 5001 is blocked
3. **Check firewall**: Windows Defender may block localhost
4. **Try different port**: Edit server config if 5001 is in use

---

## ⚡ Quick Commands

### Start Server
```powershell
cd "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure"
BISTART
```

### Stop Server
```powershell
Stop-Process -Name "python" -ErrorAction SilentlyContinue
```

### Restart Server
```powershell
Stop-Process -Name "python" -ErrorAction SilentlyContinue
cd "C:\Users\gpoli\GIT\AI_agents\AI_infrastructure"
BISTART
```

---

## 📱 Bookmark This URL

Add to bookmarks: **`http://localhost:5001`**

This is your local development URL. Always use this!

---

## 🎯 Next: Test Phase 1

Once you're accessing via `http://localhost:5001`:

1. **Time login screen**: Should be <1 second (vs 5 seconds before)
2. **Check console**: No CORS errors
3. **Test OAuth**: Sign in with Google
4. **Time dashboard**: Should be ~2 seconds total

See `UI/PHASE_1_TESTING_GUIDE.md` for detailed testing instructions.

---

**Remember**: Server URL (`http://localhost:5001`), not file path! 🚀
