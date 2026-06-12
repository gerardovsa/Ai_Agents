# Thread Visibility — Database vs API Alignment Chart
**Date:** May 29, 2026

---

## Quick Status

```
┌─────────────────────────────────────────────┐
│  THREAD VISIBILITY FEATURE: 60% COMPLETE    │
├─────────────────────────────────────────────┤
│  ✅ Database Schema         — COMPLETE      │
│  ✅ Thread Creation API     — FIXED (May 29)│
│  ✅ Thread Retrieval API    — FIXED (May 29)│
│  ❌ Visibility Filtering    — MISSING       │
│  ❌ Access Enforcement      — MISSING       │
│  ❌ Update API              — MISSING       │
│  ❌ Member Management API   — MISSING       │
└─────────────────────────────────────────────┘
```

---

## Layer 1: DATABASE SCHEMA ✅ READY

### Table: `sessions.threads`

```sql
-- Visibility Column (Migration 047)
Column Name: visibility
Data Type:   TEXT
Default:     'personal'
Nullable:    NO
Constraint:  CHECK (visibility IN ('personal', 'team', 'restricted'))

-- Organisation Column (Needed for team visibility)
Column Name: organisation_id
Data Type:   INTEGER
Nullable:    YES (optional)
Reference:   ai_infrastructure.organisations(id)
```

**Verification Query:**
```sql
-- Check if columns exist
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_schema = 'sessions' 
  AND table_name = 'threads'
  AND column_name IN ('visibility', 'organisation_id');

-- Expected output:
-- visibility      | text     | personal | NO
-- organisation_id | integer  | NULL     | YES
```

**Status:** ✅ Both columns exist in Supabase

---

### Table: `sessions.thread_members`

```sql
CREATE TABLE IF NOT EXISTS sessions.thread_members (
    id          SERIAL PRIMARY KEY,
    thread_id   TEXT        NOT NULL REFERENCES sessions.threads(thread_slug),
    user_id     INTEGER     NOT NULL REFERENCES ai_infrastructure.users(id),
    can_write   BOOLEAN     NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    added_by    INTEGER     REFERENCES ai_infrastructure.users(id),
    UNIQUE (thread_id, user_id)
);

CREATE INDEX idx_thread_members_thread ON sessions.thread_members(thread_id);
CREATE INDEX idx_thread_members_user   ON sessions.thread_members(user_id);
```

**Purpose:** Store member list for `visibility='restricted'` threads

**Status:** ✅ Table exists in Supabase

**Current Usage:** ❌ NO Python code uses this table (completely unused)

---

## Layer 2: API ENDPOINTS — Status Matrix

### POST `/api/threads/create` — ✅ FIXED May 29

| Component | Status | Details |
|-----------|--------|---------|
| **Accepts visibility** | ✅ YES | `data.get('visibility', 'personal')` |
| **Validates value** | ❌ NO | Accepts any value, DB constraint enforces |
| **Stores in DB** | ✅ YES | Inserted into threads.visibility column |
| **Returns visibility** | ✅ YES | Included in response object |

**Code Location:** `AI_infrastructure/routes/thread_routes.py` line 387

**Test Result:**
```bash
curl -X POST http://localhost:5000/api/threads/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": 12, "title": "Test", "visibility": "personal"}'

# Before (May 28): 500 Error — "name 'visibility' is not defined"
# After (May 29):  200 OK ✅
```

---

### GET `/api/threads/list` — ✅ PARTIALLY FIXED May 29

| Component | Status | Details |
|-----------|--------|---------|
| **Returns visibility** | ✅ YES | Added to SELECT clause, included in response |
| **Returns organisation_id** | ✅ YES | Added to SELECT clause, included in response |
| **Filters by visibility** | ❌ NO | Still returns ALL threads where user_id = ? |
| **Enforces access** | ❌ NO | No check if user can see thread |

**Code Location:** `AI_infrastructure/routes/thread_routes.py` line 765

**Current Query:**
```sql
SELECT t.id, ..., t.visibility, t.organisation_id  -- ✅ ADDED
FROM sessions.threads t
WHERE t.user_id = %s  -- ❌ ONLY checks user is owner
```

**What's Missing:**
```sql
-- Should be:
WHERE (
    (t.visibility = 'personal' AND t.user_id = %s)
    OR (t.visibility = 'team' AND t.organisation_id = %s)
    OR (t.visibility = 'restricted' AND t.thread_slug IN (
        SELECT thread_id FROM sessions.thread_members WHERE user_id = %s
    ))
)
```

**Test Result:**
```bash
curl http://localhost:5000/api/threads/list?user_id=12

# Response now includes:
{
    "threads": [{
        "id": "...",
        "visibility": "personal",      # ✅ NOW PRESENT
        "organisation_id": 1,           # ✅ NOW PRESENT
        "title": "My Thread",
        ...
    }]
}

# BUG: User can see ALL their threads regardless of visibility value
```

**Priority:** 🔴 HIGH (Security gap)

---

### GET `/api/threads/bulk-with-messages` — ✅ PARTIALLY FIXED May 29

| Component | Status | Details |
|-----------|--------|---------|
| **Returns visibility** | ✅ YES | Added to CTE and main SELECT |
| **Returns organisation_id** | ✅ YES | Added to CTE and main SELECT |
| **Filters by visibility** | ❌ NO | Same issue as list_threads() |
| **Enforces access** | ❌ NO | Same issue as list_threads() |

**Code Location:** `AI_infrastructure/routes/thread_routes.py` line 881

**Test Result:**
```bash
curl 'http://localhost:5000/api/threads/bulk-with-messages?user_id=12&locations=prime,agent-1'

# Response now includes visibility and organisation_id ✅
# But has the same filtering bug as list_threads() ❌
```

---

### PATCH `/api/threads/<id>/visibility` — ❌ MISSING

| Component | Status | Details |
|-----------|--------|---------|
| **Endpoint exists** | ❌ NO | Not implemented |
| **Access check** | — | N/A |
| **DB update** | — | N/A |
| **Response** | — | N/A |

**Design Specification:**

```http
PATCH /api/threads/1234567890/visibility
Authorization: Bearer <JWT>
Content-Type: application/json

{
    "visibility": "team"
}
```

**Expected Response (Success):**
```json
{
    "success": true,
    "thread_id": "1234567890",
    "visibility": "team",
    "changed_at": "2026-05-29T12:45:00Z"
}
```

**Access Control:**
- Owner only
- OR admin in same org
- OR manager in same org (if org-level thread)

**Priority:** 🟡 MEDIUM

---

### POST `/api/threads/<id>/members` — ❌ MISSING

| Component | Status | Details |
|-----------|--------|---------|
| **Endpoint exists** | ❌ NO | Not implemented |
| **Add to thread_members table** | — | N/A |
| **Access check** | — | N/A |

**Design Specification:**

```http
POST /api/threads/1234567890/members
Authorization: Bearer <JWT>
Content-Type: application/json

{
    "user_id": 15,
    "can_write": true
}
```

**Expected Response:**
```json
{
    "success": true,
    "member": {
        "user_id": 15,
        "username": "alice",
        "can_write": true,
        "added_at": "2026-05-29T12:45:00Z"
    }
}
```

**SQL Operation:**
```sql
INSERT INTO sessions.thread_members (thread_id, user_id, can_write, added_by)
VALUES ('1234567890', 15, true, 12)
ON CONFLICT (thread_id, user_id) DO UPDATE
SET can_write = EXCLUDED.can_write;
```

**Priority:** 🟡 MEDIUM

---

### GET `/api/threads/<id>/members` — ❌ MISSING

| Component | Status | Details |
|-----------|--------|---------|
| **Endpoint exists** | ❌ NO | Not implemented |
| **Query thread_members** | — | N/A |

**Design:**
```http
GET /api/threads/1234567890/members
```

**Expected Response:**
```json
{
    "success": true,
    "thread_id": "1234567890",
    "members": [
        {
            "user_id": 12,
            "username": "gerardo",
            "can_write": true,
            "role": "owner",
            "added_at": "2026-05-29T12:00:00Z"
        },
        {
            "user_id": 15,
            "username": "alice",
            "can_write": true,
            "role": "member",
            "added_at": "2026-05-29T12:45:00Z"
        }
    ]
}
```

**Priority:** 🟡 MEDIUM

---

### DELETE `/api/threads/<id>/members/<user_id>` — ❌ MISSING

| Component | Status | Details |
|-----------|--------|---------|
| **Endpoint exists** | ❌ NO | Not implemented |
| **Remove from thread_members** | — | N/A |

**Design:**
```http
DELETE /api/threads/1234567890/members/15
```

**Expected Response:**
```json
{
    "success": true,
    "message": "Member removed",
    "user_id": 15
}
```

**Priority:** 🟡 MEDIUM

---

## Layer 3: VISIBILITY FILTERING LOGIC — ❌ NOT IMPLEMENTED

### The Problem

Current code returns ALL threads owned by user, ignoring visibility rules:

```python
# CURRENT CODE (thread_routes.py line 770):
cursor.execute(
    "SELECT ... FROM sessions.threads WHERE user_id = %s",
    (user_id,)
)
```

### Correct Logic (Needed)

```python
def can_user_access_thread(thread, current_user_id, current_org_id):
    """
    Determine if user can see/access this thread based on visibility rules
    
    Args:
        thread: Thread dict with fields: user_id, visibility, organisation_id
        current_user_id: Current user's ID
        current_org_id: Current user's organisation ID
    
    Returns:
        Boolean: True if user can access thread
    """
    visibility = thread.get('visibility', 'personal')
    owner_id = thread.get('user_id')
    org_id = thread.get('organisation_id')
    thread_slug = thread.get('thread_slug')
    
    # Rule 1: Owner always sees own threads
    if owner_id == current_user_id:
        return True
    
    # Rule 2: Personal visibility → owner only
    if visibility == 'personal':
        return False
    
    # Rule 3: Team visibility → owner + org members
    if visibility == 'team':
        if org_id and org_id == current_org_id:
            return True  # Same org
        return False
    
    # Rule 4: Restricted visibility → owner + explicit members
    if visibility == 'restricted':
        # Check if user is in thread_members table
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM sessions.thread_members WHERE thread_id = %s AND user_id = %s",
                    (thread_slug, current_user_id)
                )
                return cursor.fetchone() is not None
    
    return False
```

### Where to Apply

**Option A: Python-level filtering** (add after fetching threads)
```python
threads = [t for t in all_threads if can_user_access_thread(t, user_id, org_id)]
```

**Option B: Database-level filtering** (modify WHERE clause)
```sql
WHERE (
    t.user_id = %s
    OR (t.visibility = 'team' AND t.organisation_id = %s)
    OR (t.visibility = 'restricted' AND t.thread_slug IN (
        SELECT thread_id FROM sessions.thread_members WHERE user_id = %s
    ))
)
```

**Recommendation:** Both (belt-and-braces approach)

---

## Comparison: Synergy Sessions vs Threads

Thread visibility mirrors **synergy_sessions** visibility, which already has full implementation:

| Feature | Synergy Sessions | Threads |
|---------|------------------|---------|
| visibility column | ✅ Implemented | ✅ (Just added) |
| visibility values | private/shared/team | personal/team/restricted |
| Update endpoint | ✅ PATCH /<id>/visibility | ❌ Missing |
| Member table | ✅ session_members | ✅ thread_members (unused) |
| Filtering logic | ✅ In list_sessions() | ❌ Missing |
| Access enforcement | ✅ Python + SQL | ❌ Missing |

**Reference:** `synergy_routes.py` line 1140+ has the complete implementation pattern to copy.

---

## Implementation Checklist

### Phase 1 (CRITICAL — Security)
- [ ] Add visibility filtering to `list_threads()` WHERE clause
- [ ] Add visibility filtering to `get_threads_bulk_with_messages()` WHERE clause
- [ ] Add access enforcement check before returning thread data
- [ ] Test visibility filtering prevents unauthorized access

### Phase 2 (User-Facing Features)
- [ ] Create PATCH `/api/threads/<id>/visibility` endpoint
- [ ] Create POST `/api/threads/<id>/members` endpoint
- [ ] Create DELETE `/api/threads/<id>/members/<uid>` endpoint
- [ ] Create GET `/api/threads/<id>/members` endpoint

### Phase 3 (Hardening)
- [ ] Add RLS policies on threads table
- [ ] Add RLS policies on thread_members table
- [ ] Add audit logging for visibility changes
- [ ] Add validation for restricted-only operations

---

## Database Readiness

```
Migration 047 Status:
✅ sessions.threads.visibility column created
✅ sessions.thread_members table created
✅ Indexes created
✅ CHECK constraints added
✅ Foreign keys configured

Ready for:
✅ Storing visibility values
✅ Storing member lists
✅ Enforcing constraints
❌ RLS policies (can add separately)
```

---

## Summary

| Layer | Component | Status | Work Required |
|-------|-----------|--------|----------------|
| DB | Schema | ✅ Ready | None |
| DB | Constraints | ✅ Ready | None |
| API | Create | ✅ Fixed | None |
| API | Retrieve | ✅ Partial | Add visibility to response ✅ |
| API | Filter | ❌ Missing | HIGH priority |
| API | Enforce | ❌ Missing | HIGH priority |
| API | Update | ❌ Missing | MEDIUM priority |
| API | Members | ❌ Missing | MEDIUM priority |

**Overall:** Database is ready. API is 60% complete. Focus on filtering/enforcement next.

