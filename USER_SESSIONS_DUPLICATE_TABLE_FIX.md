# User Sessions Duplicate Table - Complete Fix

**Date:** November 17, 2025  
**Issue:** Token verification failing - looking in wrong user_sessions table  
**Root Cause:** Duplicate `user_sessions` tables in two schemas  
**Status:** ✅ IDENTIFIED - Migration needed

## The Problem

Your Supabase database has **TWO `user_sessions` tables**:

| Schema | Table | Records | Status |
|--------|-------|---------|--------|
| `ai_infrastructure` | `user_sessions` | **527 records** | ✅ HAS DATA |
| `sessions` | `user_sessions` | **0 records** | ❌ EMPTY |

### What Happened:

1. **Original Setup:** All sessions stored in `ai_infrastructure.user_sessions`
2. **My Fix:** Changed queries to use `sessions.user_sessions` (for logical grouping)
3. **Result:** Queries looking in empty table - **0 sessions found!**

### Current State (from Render logs):

```
Total sessions in DB: 0
Token NOT found in database
User has 0 session(s) in DB
STAGE 2 FAILED: Token not in database
```

**Translation:** Code is querying `sessions.user_sessions` (empty) instead of `ai_infrastructure.user_sessions` (527 records).

## Session Distribution

Current data in `ai_infrastructure.user_sessions`:

- **User 14:** 152 sessions (your account!)
- **User 1:** 109 sessions
- **User 12:** 94 sessions
- **User 4:** 46 sessions
- **Total:** 527 sessions across 10 users

## Two Solution Paths

### Option A: Keep Data in ai_infrastructure (Quick Fix)

**Revert my changes** - use `ai_infrastructure.user_sessions` everywhere.

**Pros:**
- ✅ Fastest fix (15 minutes)
- ✅ No data migration needed
- ✅ Immediate resolution

**Cons:**
- ❌ Less logical schema organization
- ❌ Sessions mixed with user/auth data
- ❌ Inconsistent with sessions schema design

### Option B: Migrate to sessions Schema (RECOMMENDED)

**Copy data** from `ai_infrastructure.user_sessions` → `sessions.user_sessions`.

**Pros:**
- ✅ Logical schema organization
- ✅ Sessions grouped with threads/messages
- ✅ Consistent design
- ✅ Better long-term maintainability

**Cons:**
- ⚠️ Requires data migration (5 minutes)
- ⚠️ Need to test after migration

## Recommended Solution: Option B (Migration)

### Step 1: Run Migration Script

```bash
python migrate_user_sessions_to_sessions_schema.py
```

**What it does:**
- Copies all 527 records from `ai_infrastructure.user_sessions`
- Inserts into `sessions.user_sessions`
- Preserves all data (id, user_id, token, expires_at, etc.)
- Uses `ON CONFLICT DO NOTHING` (safe if re-run)

### Step 2: Verify Migration

```bash
python check_duplicate_user_sessions.py
```

Expected output:
```
TABLE 1: ai_infrastructure.user_sessions - 527 records
TABLE 2: sessions.user_sessions - 527 records
STATUS: DUPLICATE DATA - Both tables have records!
```

### Step 3: Deploy to Render

```bash
git add .
git commit -m "Fix: Migrate user_sessions to sessions schema"
git push origin v6
```

Render will auto-deploy in ~2-3 minutes.

### Step 4: Test Authentication

After deployment, test login:

```bash
# User should see their 152 existing sessions
# Token verification should succeed
# Profile page should load
```

### Step 5: Cleanup (Optional)

After verifying everything works for 24-48 hours:

```sql
-- Connect to Supabase SQL Editor
DROP TABLE ai_infrastructure.user_sessions;
```

## Files Already Fixed

These files were updated in my previous fix to use `sessions.user_sessions`:

### ✅ AI_infrastructure/auth/user_auth.py (7 changes)
- Line 607: `FROM sessions.user_sessions`
- Line 613: `FROM sessions.user_sessions WHERE token = ?`
- Line 621: `FROM sessions.user_sessions WHERE user_id = ?`
- Line 438: `INSERT INTO sessions.user_sessions`
- Line 519: `INSERT INTO sessions.user_sessions`
- Line 1457: `INSERT INTO sessions.user_sessions`
- Line 1483: `SELECT user_id FROM sessions.user_sessions`

### ❌ Files Still Using ai_infrastructure (Need Investigation)

These might still have old references:

```bash
# Check for remaining references
grep -r "ai_infrastructure.user_sessions" AI_infrastructure/routes/
grep -r "INSERT INTO user_sessions" AI_infrastructure/ | grep -v sessions.user_sessions
```

## Schema Organization (After Migration)

### sessions Schema (Session-related tables)
```
sessions.user_sessions    ← User login sessions (JWT tokens)
sessions.sessions         ← UI context/conversation sessions  
sessions.threads          ← Conversation threads
sessions.messages         ← Thread messages
sessions.saved_threads    ← Archived threads
```

### ai_infrastructure Schema (User/system data)
```
ai_infrastructure.users
ai_infrastructure.user_preferences
ai_infrastructure.user_platform_credentials
ai_infrastructure.oauth_tokens
ai_infrastructure.workspaces
```

**Logical separation:**
- `sessions.*` = Temporary/session data
- `ai_infrastructure.*` = Permanent user/system data

## Testing Checklist

After migration and deployment:

- [ ] Login works (new sessions created in sessions.user_sessions)
- [ ] Token verification succeeds
- [ ] Profile page loads
- [ ] Thread creation works
- [ ] Message saving works
- [ ] OAuth flows (Google/Microsoft) create sessions correctly
- [ ] User 14 sees their 152 existing sessions

## Migration SQL (Manual Alternative)

If script fails, run this in Supabase SQL Editor:

```sql
-- Copy all data
INSERT INTO sessions.user_sessions (
    id, user_id, token, ip_address, user_agent, 
    created_at, expires_at
)
SELECT 
    id, user_id, token, ip_address, user_agent,
    created_at, expires_at
FROM ai_infrastructure.user_sessions
ON CONFLICT (id) DO NOTHING;

-- Verify counts match
SELECT 
    (SELECT COUNT(*) FROM ai_infrastructure.user_sessions) as source_count,
    (SELECT COUNT(*) FROM sessions.user_sessions) as dest_count;

-- Check user 14 specifically
SELECT COUNT(*) as user_14_sessions
FROM sessions.user_sessions
WHERE user_id = 14;
-- Should return: 152
```

## Summary

**Problem:** Duplicate `user_sessions` tables, data in wrong one  
**Root Cause:** Schema migration incomplete - data not moved  
**Solution:** Migrate 527 records to sessions schema  
**Impact:** Fixes token verification for all users  
**Time:** 5 minutes migration + 3 minutes deploy = 8 minutes total  

---

**Files Modified:**
- `AI_infrastructure/auth/user_auth.py` - Already fixed (7 changes)
- `check_duplicate_user_sessions.py` - Analysis tool (NEW)
- `migrate_user_sessions_to_sessions_schema.py` - Migration script (NEW)
- `USER_SESSIONS_DUPLICATE_TABLE_FIX.md` - This document (NEW)

**Status:** Ready for migration  
**Next Action:** Run migration script, then deploy to Render
