# Deployment Checklist - November 19, 2025
**Thread Isolation & Automation Integration Release**

---

## 📋 Pre-Deployment Checks

### Backend Code Changes

- [ ] **Review all changes in `agent_routes_v4.py`:**
  - [ ] Line 716-728: thread_slug validation in stream endpoint
  - [ ] Line 515-535: thread_slug validation in start endpoint
  - [ ] Lines 773, 778, 781, 1117, 1260, 1329, 1405, 1422, 1442, 1449, 1464, 1479: session_id → thread_slug replacements
  - [ ] Line 1450-1468: Auto-save simplification

- [ ] **Run all test scripts locally:**
  ```powershell
  cd C:\Users\gpoli\GIT\AI_agents
  python test_complete_flow.py
  python test_raw_stream.py
  ```
  - [ ] All tests pass (100%)
  - [ ] No NameError in logs
  - [ ] No tuple index errors
  - [ ] Thread isolation verified

- [ ] **Check Flask startup:**
  ```powershell
  BISTART
  # Wait for "Running on http://localhost:5001"
  ```
  - [ ] No errors during startup
  - [ ] All 594 tools loaded
  - [ ] Health endpoint responds

---

## 🗄️ Database Migration

### Step 1: Backup Current Database

**CRITICAL:** Backup before any changes!

```sql
-- In Supabase SQL Editor or psql
-- Backup threads table
COPY sessions.threads TO '/tmp/threads_backup_nov19_2025.csv' CSV HEADER;

-- Or use Supabase Dashboard > Database > Backups
```

- [ ] Backup completed
- [ ] Backup file size verified (should be >0 bytes)
- [ ] Backup stored safely

---

### Step 2: Run Migration Script

**Location:** `migrations/supabase_production_migration_nov19_2025.sql`

**Supabase Dashboard Method:**
1. [ ] Open Supabase Dashboard
2. [ ] Go to SQL Editor
3. [ ] Create new query
4. [ ] Copy entire migration script
5. [ ] Click "Run"
6. [ ] Wait for success message (~30 seconds)
7. [ ] Check for any error messages

**psql Command Line Method:**
```bash
psql "your-connection-string"
\i migrations/supabase_production_migration_nov19_2025.sql
```

**Expected Output:**
```
ALTER TABLE
ALTER TABLE
CREATE INDEX
CREATE INDEX
...
NOTICE: ============================================================================
NOTICE: MIGRATION COMPLETE - November 19, 2025
NOTICE: ============================================================================
NOTICE: Columns verified: 4
NOTICE: Indexes created: 6
NOTICE: Constraints added: 4
NOTICE: Status: SUCCESS
```

- [ ] Migration completed without errors
- [ ] All expected NOTICE messages appeared
- [ ] No ERROR or FATAL messages

---

### Step 3: Verify Migration

**Location:** `migrations/verify_migration_nov19_2025.sql`

1. [ ] Run verification script
2. [ ] Check all tests passed:
   - [ ] ✅ TEST 1: Column Existence - PASS
   - [ ] ✅ TEST 2: Index Existence - PASS
   - [ ] ✅ TEST 3: Constraint Existence - PASS
   - [ ] ✅ TEST 4: Column Documentation - PASS
   - [ ] ✅ TEST 5: Data Integrity Checks - PASS
3. [ ] Review performance metrics
4. [ ] Note any warnings (non-critical)

---

## 🚀 Backend Deployment

### Step 1: Stop Current Flask

```powershell
# Find Flask process
Get-Process | Where-Object {$_.ProcessName -eq 'python' -and $_.CommandLine -like '*flask_app.py*'}

# Stop it
Stop-Process -Id [PID] -Force
```

- [ ] Flask process stopped
- [ ] No orphaned Python processes

---

### Step 2: Deploy Code Changes

**Git Commands:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Check current branch
git branch
# Should show: * v6

# Review changes
git status
git diff AI_infrastructure/routes/agent_routes_v4.py

# Commit changes
git add AI_infrastructure/routes/agent_routes_v4.py
git add migrations/
git add ALL_FIXES_COMPLETE_NOV19.md
git add DEPLOYMENT_CHECKLIST_NOV19.md

git commit -m "fix: Thread isolation and NameError fixes (Nov 19, 2025)

- Fixed 13 undefined session_id references (use thread_slug)
- Added thread_slug validation (empty/null checks)
- Simplified auto-save (removed tuple index error)
- Added database migration for automation columns
- All tests passing (thread isolation + stream responses)

Closes: Thread cross-contamination issue
Closes: NameError in stream endpoint
Closes: Auto-save tuple index error"

# Push to remote
git push origin v6
```

- [ ] Changes committed
- [ ] Commit message clear and descriptive
- [ ] Pushed to remote repository

---

### Step 3: Start Flask

```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
BISTART
```

**Wait for:**
```
Running on http://localhost:5001
* Restarting with stat
* Debugger is active!
```

- [ ] Flask started successfully
- [ ] No errors in startup logs
- [ ] Health endpoint responds: `http://localhost:5001/health`

---

## ✅ Post-Deployment Testing

### Test 1: Basic Health Check

```powershell
Invoke-WebRequest http://localhost:5001/health
```

**Expected:**
```json
{
  "status": "healthy",
  "app": "new_flask_app",
  "providers": ["anthropic", "deepseek", "openai"]
}
```

- [ ] Health check returns 200 OK
- [ ] All providers listed

---

### Test 2: Thread Creation

**Browser:** Open `http://localhost:5001`

1. [ ] Click "New Thread" in AI Prime
2. [ ] Thread created successfully
3. [ ] Thread appears in sidebar
4. [ ] No errors in console

---

### Test 3: Message Send & Response

1. [ ] Send message: "Hello, test message"
2. [ ] Wait for response
3. [ ] Check for:
   - [ ] Text response appears (not just thinking)
   - [ ] No NameError in backend logs
   - [ ] No "tuple indices" error
   - [ ] Response completes successfully

---

### Test 4: Thread Isolation

**Create threads in two different agents:**

1. [ ] Agent 1: Send "My name is Alice"
2. [ ] Agent 8: Send "My name is Bob"
3. [ ] Go back to Agent 1: Send "What is my name?"
4. [ ] Verify Agent 1 says "Alice" (not "Bob")
5. [ ] Check backend logs:
   - [ ] Different thread_slug values
   - [ ] No cross-contamination warnings

---

### Test 5: Auto-Save Verification

1. [ ] Send message to any agent
2. [ ] Wait for response to complete
3. [ ] Check backend logs for:
   - [ ] `✅ [Auto-Save] Thread updated: X_XXXX`
   - [ ] NO "tuple indices" error
   - [ ] NO "Could not determine thread location" error

---

### Test 6: Automation Workflow Integration

**If you have automation workflows:**

1. [ ] Link thread to automation workflow
2. [ ] Check thread header shows blue "Automation" pill
3. [ ] Verify automation_slug stored in database:
   ```sql
   SELECT thread_slug, automation_slug, automation_title 
   FROM sessions.threads 
   WHERE automation_slug IS NOT NULL 
   LIMIT 5;
   ```
4. [ ] Verify workflow context injected in messages

---

## 📊 Monitoring (First 24 Hours)

### Backend Logs to Watch

Monitor Flask logs for:

- [ ] **NameError:** Should be ZERO occurrences
  ```
  grep -i "nameerror" flask_logs.txt
  # Expected: No results
  ```

- [ ] **Tuple Index Error:** Should be ZERO occurrences
  ```
  grep -i "tuple indices" flask_logs.txt
  # Expected: No results
  ```

- [ ] **Thread Isolation:** Should see confirmation logs
  ```
  grep "Using thread_slug for isolation" flask_logs.txt
  # Expected: Many results
  ```

- [ ] **Auto-Save:** Should complete successfully
  ```
  grep "Auto-Save" flask_logs.txt
  # Expected: "Thread updated" messages, no errors
  ```

---

### Database Performance

Check query performance:

```sql
-- Index usage statistics
SELECT 
    indexname,
    idx_scan AS times_used,
    idx_tup_read AS tuples_read
FROM pg_stat_user_indexes
WHERE schemaname = 'sessions'
  AND tablename = 'threads'
  AND indexname LIKE 'idx_threads_%'
ORDER BY idx_scan DESC;
```

- [ ] New indexes being used (idx_scan > 0)
- [ ] No slow query warnings

---

### User Experience Metrics

Track:
- [ ] Response time (should be <2s)
- [ ] Error rate (should be <1%)
- [ ] Thread creation success rate (should be 100%)
- [ ] No user reports of cross-contamination

---

## 🚨 Rollback Plan

**If critical issues occur:**

### Option A: Quick Code Rollback

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Revert code changes
git revert HEAD

# Restart Flask
Stop-Process -Name python -Force
BISTART
```

### Option B: Database Rollback

**ONLY if database causing issues:**

```sql
\i migrations/rollback_nov19_2025.sql
```

**WARNING:** This deletes data in new columns!

### Rollback Triggers

Roll back if:
- ❌ NameError still occurring
- ❌ Thread cross-contamination detected
- ❌ Auto-save failures >10%
- ❌ Database performance degradation >20%
- ❌ User-facing errors increasing

---

## 📞 Support Contacts

**Issues?**

1. **Check logs first:**
   - Backend: Flask terminal output
   - Frontend: Browser console (F12)
   - Database: Supabase Dashboard > Logs

2. **Run diagnostics:**
   ```powershell
   python test_complete_flow.py
   ```

3. **Check documentation:**
   - `ALL_FIXES_COMPLETE_NOV19.md` - Full technical details
   - `migrations/README.md` - Database migration guide
   - `THREAD_ISOLATION_FIX_COMPLETE_NOV19.md` - Thread isolation

---

## ✅ Sign-Off

**Deployment completed by:** _________________  
**Date:** November 19, 2025  
**Time:** _________________

**Verification:**
- [ ] All pre-deployment checks passed
- [ ] Database migration successful
- [ ] Backend deployment successful
- [ ] All post-deployment tests passed
- [ ] Monitoring in place

**Status:** 
- [ ] ✅ PRODUCTION READY - All checks passed
- [ ] ⚠️ ISSUES FOUND - See notes below
- [ ] ❌ ROLLBACK REQUIRED - Critical issues

**Notes:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

**Deployment Guide Version:** 1.0  
**Last Updated:** November 19, 2025  
**Status:** Ready for Production Deployment
