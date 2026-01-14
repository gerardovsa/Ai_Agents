# Complete Schema Consolidation Plan

**Date:** November 17, 2025  
**Issue:** Duplicate tables across schemas causing query confusion  
**Status:** 🔴 CRITICAL - Data integrity issues found

## Summary of Issues

| Table | ai_infrastructure | sessions | Issue | Priority |
|-------|-------------------|----------|-------|----------|
| `user_sessions` | 527 rows | 527 rows | ✅ MIGRATED - Need cleanup | Medium |
| `users` | 7 rows (REAL) | 3 rows (DUMMY) | 🔴 DATA CONFLICT | **CRITICAL** |
| `thread_assignments` | 0 rows | 0 rows | Both empty | Low |
| `workspaces` | 4 rows | 0 rows | sessions empty | Low |

## Critical Issue: users Table Data Conflict

### ai_infrastructure.users (7 users - CORRECT DATA):
```
ID 1:  user_1 (user_1@ai-platform.local)
ID 3:  inhouse (inhouse@vetsuccessacademy.com)
ID 5:  google_test (google_test@example.com)
ID 6:  microsoft_test (microsoft_test@example.com)
ID 12: gerardo (gerardo@vetsuccessacademy.com)
ID 13: Gerardo (Gerardo@minivetguide.onmicrosoft.com)
ID 14: printing (printing@inhouseprint.com.au) ← YOUR ACCOUNT
```

### sessions.users (3 users - DUMMY/TEST DATA):
```
ID 12: user_12 (user_12@ai-platform.local) ← WRONG EMAIL!
ID 13: user_13 (user_13@ai-platform.local) ← WRONG EMAIL!
ID 14: user_14 (user_14@ai-platform.local) ← WRONG EMAIL (yours!)
```

**Problem:** Users 12, 13, 14 have **different email addresses** in each schema!

## Root Cause Analysis

1. **Historical migration incomplete** - Some tables copied, others not
2. **sessions schema created** but not all data migrated
3. **Dummy data** added to sessions.users for testing
4. **Real data** remains in ai_infrastructure schema

## Current Code Behavior

### Queries Using ai_infrastructure:
- `user_auth.py` - Login/auth queries `ai_infrastructure.users` ✅
- All user management routes use `ai_infrastructure` connection ✅
- OAuth flows query `ai_infrastructure.users` ✅

### Queries Using sessions:
- `thread_routes.py` - Connects to `sessions` for threads/messages
- If these routes query `users` unqualified → queries `sessions.users` ❌

## Fix Strategy

### Phase 1: Immediate Fixes (CRITICAL - Do First)

1. **Drop sessions.users** (dummy data, causes conflicts)
   ```sql
   DROP TABLE sessions.users;
   ```

2. **Drop sessions.workspaces** (empty, unused)
   ```sql
   DROP TABLE sessions.workspaces;
   ```

3. **Drop sessions.thread_assignments** (empty, duplicate)
   ```sql
   DROP TABLE sessions.thread_assignments;
   ```

### Phase 2: Code Updates (Prevent Future Issues)

Update any code connecting to `sessions` that queries `users`, `workspaces`, or `thread_assignments` to use schema-qualified names:

```python
# WRONG (when connected to sessions schema):
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
# This queries sessions.users (dummy data!)

# CORRECT:
cursor.execute("SELECT * FROM ai_infrastructure.users WHERE id = %s", (user_id,))
# This queries ai_infrastructure.users (real data)
```

###Phase 3: Cleanup (After Verification)

After 24-48 hours of successful operation:

```sql
-- Clean up old user_sessions duplicate
DROP TABLE ai_infrastructure.user_sessions;
-- (data already migrated to sessions.user_sessions)
```

## Detailed Fix Script

```sql
-- Run in Supabase SQL Editor

-- 1. Verify data before dropping
SELECT 'ai_infrastructure.users' as source, COUNT(*) as count 
FROM ai_infrastructure.users
UNION ALL
SELECT 'sessions.users' as source, COUNT(*) as count 
FROM sessions.users;

-- Expected: 7 rows in ai_infrastructure, 3 in sessions

-- 2. Drop duplicate/dummy tables in sessions schema
DROP TABLE IF EXISTS sessions.users;
DROP TABLE IF EXISTS sessions.workspaces;
DROP TABLE IF EXISTS sessions.thread_assignments;

-- 3. Verify drops
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'sessions'
ORDER BY table_name;

-- Should NOT show: users, workspaces, thread_assignments
```

## Schema Organization (Final State)

### ai_infrastructure Schema (User & System Data)
```
✅ users (7 rows - ONLY copy)
✅ user_sessions (527 rows - will be dropped after verification)
✅ user_preferences
✅ user_platform_credentials  
✅ oauth_tokens
✅ workspaces (4 rows - ONLY copy)
✅ thread_assignments (0 rows - ONLY copy)
✅ prompt_library
✅ scheduled_tasks
✅ device_registry
```

### sessions Schema (Session & Conversation Data)
```
✅ user_sessions (527 rows - migrated, KEEP)
✅ threads (83 rows)
✅ messages (219 rows)
✅ saved_threads (28 rows)
✅ sessions (0 rows)
✅ api_sessions (0 rows)
✅ thread_shares (0 rows)
✅ thread_users (0 rows)
❌ users (DROP - dummy data)
❌ workspaces (DROP - empty)
❌ thread_assignments (DROP - empty duplicate)
```

### synergy_sessions Schema (Synergy Feature Data)
```
✅ synergy_sessions (15 rows)
✅ synergy_internal_docs (16 rows)
```

## Testing Checklist

After running fixes:

- [ ] Login works (queries ai_infrastructure.users)
- [ ] Profile shows correct email (printing@inhouseprint.com.au, not user_14@...)
- [ ] Thread creation works
- [ ] Message saving works
- [ ] Synergy features work
- [ ] OAuth flows work
- [ ] No "relation does not exist" errors

## Potential Breaking Changes

### Routes That Connect to sessions AND Query users:

These might break if they query `users` without schema qualification:

```bash
# Find potential issues:
grep -r "get_database_connection('sessions')" AI_infrastructure/routes/ | \
  xargs grep -l "FROM users"
```

**If found, update to:**
```python
# Change FROM:
cursor.execute("SELECT * FROM users WHERE id = %s")

# Change TO:
cursor.execute("SELECT * FROM ai_infrastructure.users WHERE id = %s")
```

## SQL Cleanup Script (Run After Testing)

```sql
-- ONLY run this after 24-48 hours of successful operation

-- Final cleanup: Drop old user_sessions from ai_infrastructure
DROP TABLE IF EXISTS ai_infrastructure.user_sessions;

-- Verify final state
SELECT 
    table_schema,
    table_name,
    (SELECT COUNT(*) 
     FROM information_schema.columns 
     WHERE table_schema = t.table_schema 
     AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema IN ('ai_infrastructure', 'sessions', 'synergy_sessions')
ORDER BY table_schema, table_name;
```

## Summary

**Priority 1 (CRITICAL - Do Now):**
1. Drop `sessions.users` (dummy data conflict)
2. Drop `sessions.workspaces` (empty duplicate)
3. Drop `sessions.thread_assignments` (empty duplicate)

**Priority 2 (Important - After Testing):**
1. Verify all routes use correct schema qualifications
2. Test authentication and user queries
3. Monitor for "relation does not exist" errors

**Priority 3 (Cleanup - After 24-48 hours):**
1. Drop `ai_infrastructure.user_sessions` (migrated data)

**Expected Result:**
- ✅ No duplicate tables
- ✅ No data conflicts
- ✅ All queries use correct schemas
- ✅ Authentication works correctly
- ✅ User emails display correctly

---

**Files Created:**
- `check_all_schema_references.py` - Schema audit tool
- `analyze_duplicate_tables.py` - Duplicate analysis
- `COMPLETE_SCHEMA_CONSOLIDATION_PLAN.md` - This document

**Next Action:** Run SQL cleanup script in Supabase
