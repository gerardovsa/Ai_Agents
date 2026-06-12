# Quick Debug Reference - Thread History Badge Issue
**Date:** December 29, 2025

## 🚨 Quick Start

1. **Hard Refresh:** `Ctrl + Shift + R`
2. **Open Console:** `F12` → Console tab
3. **Click:** Thread History sidebar
4. **Look for:** 🔍 [DEBUG] messages

---

## 📊 Debug Output Cheat Sheet

### ✅ GOOD (Expected Output)
```
🔍 [DEBUG] Thread 1: {thread.location: "agent-1", currentLocation: "agent-1"}
🔍 [DEBUG] Final re-computed badge: {agentBadge.name: "Agent-1"}
```
**Result:** Badge should show "Agent-1"

### ❌ BAD (Database Issue)
```
🔍 [DEBUG] Thread 1: {thread.location: null, currentLocation: "unassigned"}
```
**Problem:** Backend not returning location  
**Fix:** Check database or thread_routes.py

### ❌ BAD (Cache Issue)
```
(No debug messages appear)
```
**Problem:** Old JavaScript still running  
**Fix:** Hard refresh or clear cache

### ⚠️ WARNING (Logic Issue)
```
🔍 [DEBUG] Re-computing badge in compactCard: {currentLocation: "agent-1"}
🔍 [DEBUG] Final re-computed badge: {agentBadge.name: "Unassigned"}
```
**Problem:** Re-computation logic broken  
**Fix:** Check badge computation code

---

## 🔍 What Each Debug Point Shows

| Point | File | What It Checks |
|-------|------|----------------|
| 1️⃣ | thread-manager-ui.js:180 | Thread data from backend |
| 2️⃣ | thread-manager-ui.js:208 | Parameters to renderThreadCard |
| 3️⃣ | thread-manager-ui.js:258 | Parameters to compactCard |
| 4️⃣ | thread-card-templates.js:163 | Badge re-computation start |
| 5️⃣ | thread-card-templates.js:197 | Badge re-computation result |

---

## 🎯 Quick Diagnosis

### See `thread.location: null`?
→ Backend/database issue - check thread_routes.py

### See correct location but wrong badge?
→ Template issue - check if agentBadge is used in HTML

### See no debug messages?
→ Cache issue - hard refresh browser

### See correct badge in logs but wrong on screen?
→ HTML rendering issue - inspect element in browser

---

## 📝 Quick Fixes

### Fix 1: Hard Refresh
```
Ctrl + Shift + R
```

### Fix 2: Clear Browser Cache
```
F12 → Application → Clear Storage → Clear site data
```

### Fix 3: Check Backend Response
```
F12 → Network → XHR → /api/threads/list → Preview tab
Look for "location" field in threads array
```

### Fix 4: Database Query
```sql
SELECT id, title, location FROM sessions.threads LIMIT 10;
```
If location is NULL → threads not assigned to agents

---

## ✅ Success Indicators

- [ ] Debug messages appear in console
- [ ] `thread.location` is NOT null
- [ ] `currentLocation` matches thread.location
- [ ] Badge re-computation runs (point 4 logs)
- [ ] Final badge shows correct agent name (point 5)
- [ ] Visual badge on screen matches logs

---

## 📞 If Still Broken

1. Share console output in chat
2. Share screenshot of Thread History
3. Share backend response from Network tab
4. Share database query result

---

**Files with Debug Logging:**
- `UI/modules_internal/thread-manager/thread-manager-ui.js`
- `UI/modules_internal/thread-cards/thread-card-templates.js`

**Remove Debug Later:**
Search for `// 🔍 DEBUG:` and delete those blocks
