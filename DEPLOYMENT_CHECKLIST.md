# Supabase Fix - Deployment Checklist

## Pre-Deployment

- [ ] **Review changes**
  ```bash
  git status
  git diff AI_infrastructure/shared/database_utils.py
  git diff AI_infrastructure/auth/user_auth.py
  ```

- [ ] **Run local tests** (if needed)
  ```bash
  python test_database_placeholders.py
  python check_all_schema_references.py
  ```

## Step 1: SQL Cleanup in Supabase (5 min)

- [ ] Go to **Supabase Dashboard** → SQL Editor
- [ ] Open file: `cleanup_duplicate_tables.sql`
- [ ] **Run entire script**
- [ ] Verify output shows 3 tables dropped:
  - [ ] sessions.users ✅
  - [ ] sessions.workspaces ✅
  - [ ] sessions.thread_assignments ✅

## Step 2: Deploy to Render (3 min)

- [ ] **Commit changes**
  ```bash
  cd C:\Users\gpoli\GIT\AI_agents
  git add .
  git commit -m "Fix: Supabase schema consolidation + placeholder conversion"
  ```

- [ ] **Push to Render**
  ```bash
  git push origin v6
  ```

- [ ] **Monitor deployment**
  - Go to Render Dashboard
  - Watch deployment logs
  - Wait for "✅ Live" status (~2-3 minutes)

## Step 3: Test Authentication (5 min)

- [ ] **Test Login**
  - Go to your app URL
  - Login with printing@inhouseprint.com.au
  - Should succeed (no 401 errors)

- [ ] **Check Profile**
  - View profile page
  - Email should show: `printing@inhouseprint.com.au`
  - NOT: `user_14@ai-platform.local`

- [ ] **Create New Thread**
  - Click "New Chat"
  - Add title: "Test Thread Nov 17"
  - Should create successfully
  - NO "parameter $1" error

- [ ] **Send Message**
  - Type a message in thread
  - Should save correctly
  - Check thread list refreshes

## Step 4: Check Render Logs (2 min)

- [ ] **Open Render Logs**
  - Render Dashboard → Logs tab

- [ ] **Verify successful operations:**
  ```
  ✅ [DB] Connected to Supabase PostgreSQL
  ✅ Total sessions in DB: 527 (not 0!)
  ✅ Token found in sessions.user_sessions
  ✅ User 14 sessions: 152
  ✅ Token verification SUCCESS
  ```

- [ ] **Check for errors:**
  - NO "relation does not exist" errors
  - NO "parameter $1" errors
  - NO "0 sessions in DB" messages

## Step 5: Extended Testing (5 min)

- [ ] **Test OAuth** (if you use it)
  - Google OAuth login
  - Microsoft OAuth login
  - Verify sessions created

- [ ] **Test Synergy** (if you use it)
  - Create synergy session
  - Link threads
  - Verify data saves

- [ ] **Test Thread Operations**
  - List threads
  - View thread details
  - Edit thread
  - Archive thread

## Final Cleanup (After 24-48 hours)

- [ ] **Verify everything stable**
  - No authentication issues
  - No database errors
  - User data correct

- [ ] **Drop old user_sessions table**
  ```sql
  -- Run in Supabase SQL Editor
  DROP TABLE ai_infrastructure.user_sessions;
  ```

- [ ] **Verify final state**
  ```sql
  SELECT table_schema, table_name, 
         (SELECT COUNT(*) FROM information_schema.columns 
          WHERE table_schema = t.table_schema 
          AND table_name = t.table_name) as columns
  FROM information_schema.tables t
  WHERE table_schema IN ('ai_infrastructure', 'sessions')
  ORDER BY table_schema, table_name;
  ```

## Success Criteria

✅ All boxes checked above  
✅ No errors in Render logs  
✅ Authentication works  
✅ Profile shows correct email  
✅ Thread/message operations work  
✅ 527 sessions found (not 0)  

## Rollback (If Needed)

If critical issues occur:

1. **Revert code**
   ```bash
   git revert HEAD
   git push origin v6
   ```

2. **Restore sessions.users** (if email issues)
   ```sql
   -- Supabase SQL Editor
   CREATE TABLE sessions.users AS 
   SELECT * FROM ai_infrastructure.users WHERE id IN (12, 13, 14);
   ```

3. **Contact support** with Render logs

---

## Quick Status Check

**Current Status:** All fixes implemented, ready to deploy

**Next Action:** Run SQL cleanup in Supabase, then deploy

**Estimated Time:** 15 minutes total

**Risk Level:** Low (all changes tested, migrations complete)

---

**Ready to proceed!** 🚀
