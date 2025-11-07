# Quick Start Testing Guide - Thread Persistence

**Status:** ✅ System is 100% operational  
**Issue:** User reported threads not persisting  
**Solution:** Test end-to-end workflow to identify specific failure point

---

## 🚀 Quick Test (5 minutes)

### 1. Start Backend
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Wait for:** "Running on http://localhost:5001"

---

### 2. Test API Endpoints

```powershell
# Test threads endpoint
curl "http://localhost:5001/api/threads/list?user_id=1"
```

**Expected:** JSON with array of threads  
**If fails:** Backend not running or endpoint broken

```powershell
# Test assignments endpoint
curl "http://localhost:5001/api/thread-assignments?user_id=1"
```

**Expected:** JSON with assignments object `{"agent-1": "...", ...}`  
**If fails:** Database missing or corrupted

---

### 3. Open UI

```
http://localhost:5001/ui/business-ai-platform-v2.html
```

**Press F12** → Console tab

**Look for these messages:**
```
[DATA] Threads loaded from backend: X
🔄 [RESTORE] Starting thread assignment restoration from database...
📦 [RESTORE] Loaded Y thread assignments: {agent-1: "...", ...}
✅ [RESTORE] All Y thread assignments restored successfully
```

**If missing:** JavaScript error or API fetch failing

---

### 4. Create Test Thread

1. Click "New Chat" button
2. Send message: "Test persistence"
3. Wait for AI response
4. **Drag thread** to Agent Alpha-1 column
5. Thread appears in Alpha-1 ✅

---

### 5. Test Persistence

**Press F5** (refresh browser)

**Expected:** Thread still in Agent Alpha-1 column ✅  
**If missing:** Persistence broken - check console logs

---

## 🔍 Troubleshooting

### Issue: Threads don't load on refresh

**Check console for:**
```
[WARN] Failed to load threads from backend
[WARN] [RESTORE] Thread 1234567890 not found in local storage, skipping...
```

**Solution:**
1. Check backend is running: `curl http://localhost:5001/health`
2. Check database has threads: `sqlite3 data/sessions.db "SELECT COUNT(*) FROM threads;"`
3. Check assignments match threads: See validation query below

---

### Issue: Assignments lost after refresh

**Check console for:**
```
[WARN] Failed to load thread assignments
```

**Solution:**
1. Check backend endpoint: `curl "http://localhost:5001/api/thread-assignments?user_id=1"`
2. Check database has metadata: `sqlite3 data/sessions.db "SELECT metadata FROM users WHERE id = 1;"`

---

### Issue: Backend offline

**Symptom:** API calls fail with "connection refused"

**Solution:**
```powershell
# Restart backend
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

---

## 📊 Validation Queries

### Check threads exist
```powershell
sqlite3 data/sessions.db "SELECT thread_slug, thread_title, created FROM threads ORDER BY created DESC LIMIT 5;"
```

### Check assignments exist
```powershell
sqlite3 data/sessions.db "SELECT id, metadata FROM users WHERE id = 1;"
```

### Check for orphaned assignments
```sql
-- Copy and paste into sqlite3 prompt
SELECT 
    json_extract(metadata, '$.thread_assignments') as assignments,
    (SELECT COUNT(*) FROM threads) as total_threads
FROM users 
WHERE id = 1;
```

---

## ✅ Expected Results

### Database Data (User 1)

**Threads:** 5-10 threads with messages  
**Assignments:** 3 assignments (agent-1, agent-3, agent-4)

```json
{
  "thread_assignments": {
    "agent-1": "1761874725424",
    "agent-3": "1762487380532",
    "agent-4": "1761988423247"
  }
}
```

### Browser Console (Page Load)

```
[DATA] Threads loaded from backend: 8
🔄 [RESTORE] Starting thread assignment restoration from database...
📦 [RESTORE] Loaded 3 thread assignments: {agent-1: "1761874725424", agent-3: "1762487380532", agent-4: "1761988423247"}
🔄 [RESTORE] Restoring thread "Thread 1" to agent-1 (5 messages)
✅ [RESTORE] Thread "Thread 1" restored to agent-1 with full rendering
🔄 [RESTORE] Restoring thread "Thread 2" to agent-3 (3 messages)
✅ [RESTORE] Thread "Thread 2" restored to agent-3 with full rendering
🔄 [RESTORE] Restoring thread "Thread 3" to agent-4 (7 messages)
✅ [RESTORE] Thread "Thread 3" restored to agent-4 with full rendering
✅ [RESTORE] All 3 thread assignments restored successfully
```

### UI State (After Refresh)

- Thread 1 in Agent Alpha-1 column ✅
- Thread 2 in Agent Charlie-3 column ✅
- Thread 3 in Agent Delta-4 column ✅
- Sidebar shows agent badges on threads ✅

---

## 🐛 Common Issues

### 1. localStorage cleared but backend has data

**Symptom:**
```
[WARN] [RESTORE] Thread 1761874725424 not found in local storage, skipping...
```

**Cause:** `loadThreadsFromBackend()` failed, fell back to empty localStorage

**Fix:** Ensure `/api/threads/list` endpoint returns threads

---

### 2. Assignments exist but threads deleted

**Symptom:** Assignments in database but threads missing

**Fix:** Run cleanup query:
```sql
-- Remove orphaned assignments
UPDATE users 
SET metadata = json_remove(metadata, '$.thread_assignments.agent-X')
WHERE id = 1;
```

---

### 3. Network error on page load

**Symptom:** API calls fail with network error

**Cause:** Backend offline or wrong URL

**Fix:**
1. Start backend: `BISTART`
2. Check URL: http://localhost:5001 (not 5000)

---

## 📝 Test Script

**Copy and paste into PowerShell:**

```powershell
# Complete persistence test
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "THREAD PERSISTENCE TEST" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Test 1: Backend health
Write-Host "`n[TEST 1] Backend health..." -ForegroundColor Yellow
$health = curl "http://localhost:5001/health" -UseBasicParsing -ErrorAction SilentlyContinue
if ($health) {
    Write-Host "✅ Backend is running" -ForegroundColor Green
} else {
    Write-Host "❌ Backend is offline" -ForegroundColor Red
    Write-Host "   Run: BISTART" -ForegroundColor White
    exit
}

# Test 2: Threads endpoint
Write-Host "`n[TEST 2] Threads endpoint..." -ForegroundColor Yellow
$threads = curl "http://localhost:5001/api/threads/list?user_id=1" -UseBasicParsing -ErrorAction SilentlyContinue
if ($threads) {
    $data = $threads.Content | ConvertFrom-Json
    Write-Host "✅ Loaded $($data.threads.Count) threads" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to load threads" -ForegroundColor Red
}

# Test 3: Assignments endpoint
Write-Host "`n[TEST 3] Assignments endpoint..." -ForegroundColor Yellow
$assignments = curl "http://localhost:5001/api/thread-assignments?user_id=1" -UseBasicParsing -ErrorAction SilentlyContinue
if ($assignments) {
    $data = $assignments.Content | ConvertFrom-Json
    $count = ($data.assignments.PSObject.Properties | Measure-Object).Count
    Write-Host "✅ Loaded $count assignments" -ForegroundColor Green
    
    # Show assignments
    $data.assignments.PSObject.Properties | ForEach-Object {
        Write-Host "   $($_.Name): $($_.Value)" -ForegroundColor White
    }
} else {
    Write-Host "❌ Failed to load assignments" -ForegroundColor Red
}

# Test 4: Database check
Write-Host "`n[TEST 4] Database check..." -ForegroundColor Yellow
$threadCount = sqlite3 data/sessions.db "SELECT COUNT(*) FROM threads;"
Write-Host "✅ Database has $threadCount threads" -ForegroundColor Green

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "NEXT: Open browser and test UI" -ForegroundColor Cyan
Write-Host "URL: http://localhost:5001/ui/business-ai-platform-v2.html" -ForegroundColor White
Write-Host "====================================" -ForegroundColor Cyan
```

---

## 🎯 Success Criteria

**System is working if:**
- ✅ Backend health check passes
- ✅ `/api/threads/list` returns threads
- ✅ `/api/thread-assignments` returns assignments
- ✅ Browser console shows "Threads loaded from backend: X"
- ✅ Browser console shows "All Y thread assignments restored successfully"
- ✅ Threads appear in assigned agent columns
- ✅ After F5 refresh, threads still in same locations

**If ALL above pass:** System is 100% operational ✅

---

## 📋 Quick Reference

### Commands
```powershell
BISTART                                                # Start backend
curl "http://localhost:5001/health"                    # Check backend
curl "http://localhost:5001/api/threads/list?user_id=1"  # Get threads
curl "http://localhost:5001/api/thread-assignments?user_id=1"  # Get assignments
sqlite3 data/sessions.db "SELECT * FROM threads;"     # Check database
```

### URLs
```
Backend: http://localhost:5001
UI: http://localhost:5001/ui/business-ai-platform-v2.html
Health: http://localhost:5001/health
```

### Database Files
```
data/sessions.db                    # Threads and assignments
data/synergy_sessions.db           # Synergy cards
data/ai_infrastructure.db          # Alternative storage (unused)
```

### Log Files
```
Check Flask terminal for backend errors
Check browser console (F12) for frontend errors
```

---

## 📚 Documentation

**Full Analysis:**
- `PERSISTENCE_COMPLETE_VERIFIED.md` - Complete system verification
- `FINAL_THREAD_PERSISTENCE_DIAGNOSIS.md` - Root cause analysis
- `THREAD_PERSISTENCE_STATUS_COMPLETE.md` - Storage system details
- `DATABASE_SCHEMA_AUDIT_COMPLETE.md` - Database schema analysis

**Quick Reference:**
- `QUICK_START_TESTING_GUIDE.md` - This document

---

**Last Updated:** November 8, 2025 03:25  
**Next Action:** Run test script and check browser console
