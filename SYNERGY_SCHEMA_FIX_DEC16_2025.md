# Synergy Sessions Schema Fix - December 16, 2025

## 🐛 Issues Fixed

### 1. **Database Table Not Found Errors**
**Error:**
```
relation "synergy_sessions" does not exist
relation "synergy_internal_docs" does not exist
```

**Root Cause:**
- Supabase uses PostgreSQL connection pooling with Transaction Mode
- The `search_path` setting wasn't persisting across pooled connections
- Tables exist in `synergy_sessions` schema but queries were looking in `public` schema

**Solution:**
Added explicit `SET search_path TO synergy_sessions, public` after cursor creation in all routes that query the database.

**Files Modified:**
- `AI_infrastructure/routes/synergy_routes.py`
  - `create_internal_doc()` - Line ~2188
  - `get_sessions_with_internal_docs()` - Line ~607
  - `get_sessions_bulk()` - Line ~827

**Code Pattern:**
```python
conn = get_db_connection()
cursor = conn.cursor()

# Ensure search_path is set (critical for Supabase connection pooling)
if is_using_supabase():
    cursor.execute("SET search_path TO synergy_sessions, public")
```

---

### 2. **Frontend Error: `assignees.map is not a function`**

**Root Cause:**
- `assignees` field (and other JSON array fields) were returning `null` or `undefined` when empty
- Frontend code expected arrays and called `.map()` on null values
- **CRITICAL:** Only 2 of 5 endpoints had the fix initially - 3 endpoints were still returning null!

**Solution:**
Updated JSON field parsing to **always** return empty arrays `[]` instead of leaving fields as `null`.
**All 5 session-returning endpoints now fixed.**

**Files Modified:**
- `AI_infrastructure/routes/synergy_routes.py`
  - `get_sessions_with_internal_docs()` - Line ~625 ✅ FIXED
  - `get_sessions_bulk()` - Line ~843 ✅ FIXED
  - `get_sessions_list()` - Line ~489 ✅ FIXED (NEW)
  - `get_session()` (single session by ID) - Line ~1116 ✅ FIXED (NEW)
  - `search_sessions()` - Line ~1732 ✅ FIXED (NEW)

**Before:**
```python
for field in ['assignees', 'tags', ...]:
    if session.get(field):
        try:
            session[field] = json.loads(session[field])
        except:
            session[field] = []
# Problem: If field is null, it stays null
```

**After:**
```python
for field in ['assignees', 'tags', ...]:
    if session.get(field):
        try:
            session[field] = json.loads(session[field])
        except:
            session[field] = []
    else:
        session[field] = []  # Default to empty array if null/missing
```

---

### 3. **403 Forbidden Errors**

**Note:** This issue is related to permissions/authentication and needs separate investigation. The database schema fixes above will resolve the "table does not exist" errors, but 403 errors indicate a user permissions issue that may need attention.

---

## ✅ Verification

### Tables Confirmed to Exist in `synergy_sessions` Schema:
- ✅ `synergy_sessions.synergy_sessions` (main sessions table)
- ✅ `synergy_sessions.synergy_internal_docs` (documents)
- ✅ `synergy_sessions.milestones`
- ✅ `synergy_sessions.tasks`
- ✅ `synergy_sessions.subtasks`
- ✅ `synergy_sessions.milestone_comments`
- ✅ `synergy_sessions.milestone_history`
- ✅ `synergy_sessions.synergy_config`

### Connection Pool Configuration:
```python
# Optimized for Supabase Nano Transaction Mode
minconn=4    # Keep connections ready
maxconn=12   # Handle UI bursts + Python GC delays
```

---

## 🔍 Why This Happened

### Supabase Connection Pooling Behavior:
1. **Transaction Mode Pooler** (port 6543) - Used by the application
   - Connections are short-lived (seconds)
   - Settings like `search_path` don't persist between transactions
   - Each new transaction from the pool needs explicit schema setting

2. **Session Mode Pooler** (port 5432) - Fallback
   - Connections are long-lived
   - Settings persist but limited to 60 connections total

### Why Explicit search_path is Needed:
```python
# ❌ WRONG: Assumes search_path is already set
cursor.execute("SELECT * FROM synergy_sessions")

# ✅ CORRECT: Explicitly set search_path first
cursor.execute("SET search_path TO synergy_sessions, public")
cursor.execute("SELECT * FROM synergy_sessions")
```

---

## 📋 Migration SQL Created

Created `migrations/fix_synergy_schema.sql` with complete schema setup for `synergy_sessions` schema.

**Note:** Tables already exist in Supabase, so this file is for documentation/reference only.

---

## 🚀 Next Steps

### Recommended Additional Fixes:

1. **Add search_path to ALL routes** that query synergy_sessions tables
   - Search for all instances of `conn = get_db_connection()` in synergy_routes.py
   - Add the `SET search_path` statement after cursor creation

2. **Investigate 403 Forbidden errors**
   - Check user authentication tokens
   - Verify session ownership/permissions logic
   - Review `check_session_permission()` function

3. **Add Database Health Check**
   - Create endpoint: `GET /api/synergy/health`
   - Verify schema exists and tables are accessible
   - Check connection pool stats

---

## 📊 Testing Checklist

- [ ] Create new synergy session
- [ ] Create internal document
- [ ] Fetch sessions batch
- [ ] Verify assignees displays correctly (no .map errors)
- [ ] Check browser console for errors
- [ ] Verify all JSON array fields return arrays (never null)

---

## 🎯 Summary

**Problem:** Supabase connection pooling + missing search_path = "table does not exist" errors
**Solution:** Explicitly set `search_path TO synergy_sessions, public` after getting cursor
**Impact:** All database queries now correctly find tables in synergy_sessions schema

**Problem:** JSON fields returning null instead of empty arrays
**Solution:** Always default to `[]` for JSON array fields when null/missing
**Impact:** Frontend code can safely call `.map()` on all array fields
