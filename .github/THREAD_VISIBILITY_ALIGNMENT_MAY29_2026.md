# Thread Visibility Alignment Analysis — May 29, 2026

**Status:** 60% Complete (Creation ✅, Retrieval Partially ✅, Enforcement ⏳)

---

## Executive Summary

Thread visibility feature is partially implemented:

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema | ✅ Ready | migration 047: `visibility` column + `thread_members` table |
| Thread Creation | ✅ Fixed | POST endpoint accepts and stores visibility parameter |
| Thread Retrieval | ✅ Fixed | SELECT queries now include visibility column |
| Visibility Filtering | ⏳ TODO | list_threads() returns all threads without filtering |
| Access Enforcement | ⏳ TODO | No checks if user can see thread before returning data |
| Update Endpoint | ⏳ Missing | No PATCH /api/threads/<id>/visibility endpoint |
| Member Management | ⏳ Missing | thread_members table unused (no add/remove endpoints) |

---

## Database Schema Alignment

### ✅ Column: `sessions.threads.visibility`

**Definition** (migration 047):
```sql
ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'personal'
        CHECK (visibility IN ('personal', 'team', 'restricted'));
```

**Values:**
- `personal` — Owner only can see/access this thread
- `team` — All users in same `organisation_id` can see it
- `restricted` — Only owner + explicit members in `session.thread_members` table

**Database Status:** ✅ Present in Supabase

---

### ✅ Table: `sessions.thread_members`

**Definition** (migration 047):
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
```

**Purpose:** Store member list for `visibility='restricted'` threads

**Database Status:** ✅ Present in Supabase  
**Python Usage Status:** ❌ Completely Unused (no query code exists)

---

### ⚠️ Column: `sessions.threads.organisation_id`

**Why it matters:** For `visibility='team'` filtering

**Current Status:** ❌ May not exist in schema

**Verification Query:**
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_schema = 'sessions' 
  AND table_name = 'threads' 
  AND column_name = 'organisation_id';
```

**If missing:** Need to add via migration:
```sql
ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS organisation_id INTEGER
        REFERENCES ai_infrastructure.organisations(id) ON DELETE SET NULL;
```

---

## API Endpoint Status

### ✅ POST `/api/threads/create` — Fixed May 29

**What Changed:**
```python
# Line 387 in thread_routes.py — NOW CORRECT:
visibility = data.get('visibility', 'personal')  # Extract from request

# Stored in INSERT:
INSERT INTO sessions.threads (..., visibility) VALUES (..., %s)
```

**Test Case:**
```json
POST /api/threads/create
{
    "user_id": 12,
    "title": "Visualisation test 29th May",
    "visibility": "personal",
    "location": "agent-18",
    "tags": []
}
```

**Expected Response:**
```json
{
    "success": true,
    "thread": {
        "id": "1234567890",
        "title": "...",
        "visibility": "personal"
    }
}
```

**Status:** ✅ Fixed — Now accepts visibility parameter

---

### ✅ GET `/api/threads/list` — Partially Fixed May 29

**What Changed:**
```python
# SELECT now includes:
SELECT ..., t.visibility, t.organisation_id, ...

# Thread response now includes:
thread_data = {
    ...
    'visibility': row.get('visibility', 'personal'),
    'organisation_id': row.get('organisation_id'),
    ...
}
```

**Status:** ✅ Visibility field now returned

**⚠️ NOT Fixed:** Visibility filtering logic still missing

**What's STILL MISSING:**
```python
# This filtering logic does NOT exist yet:
if visibility == 'personal':
    # Only owner can see
    WHERE t.user_id = %s AND t.visibility = 'personal'
elif visibility == 'team':
    # All users in same org
    WHERE (t.user_id = %s OR (t.visibility = 'team' AND t.organisation_id = %s))
elif visibility == 'restricted':
    # Owner + explicit members
    WHERE (t.user_id = %s OR (t.visibility = 'restricted' AND 
           t.thread_slug IN (SELECT thread_id FROM sessions.thread_members WHERE user_id = %s)))
```

---

### ✅ GET `/api/threads/bulk-with-messages` — Partially Fixed May 29

**What Changed:**
```python
# SELECT now includes visibility and organisation_id in CTE
WITH assigned_threads AS (
    SELECT ..., t.visibility, t.organisation_id
    ...
)

# And in main SELECT:
SELECT ..., at.visibility, at.organisation_id, ...
```

**Status:** ✅ Visibility field now returned

**⚠️ NOT Fixed:** No visibility filtering (same as list_threads)

---

## Missing Endpoints & Features

### ❌ PATCH `/api/threads/<id>/visibility` — Not Implemented

**Purpose:** Change thread visibility after creation

**Design:**
```
PATCH /api/threads/1234567890/visibility
{
    "visibility": "team" | "personal" | "restricted"
}
```

**Access:** Owner only

**Implementation Needed:**
```python
@thread_bp.route('/<thread_id>/visibility', methods=['PATCH'])
def update_thread_visibility(thread_id):
    data = request.get_json()
    visibility = data.get('visibility')
    
    # Validate value
    if visibility not in ('personal', 'team', 'restricted'):
        return error_response('Invalid visibility', 400)
    
    # Update database
    with get_database_connection('sessions') as conn:
        with conn.cursor() as cursor:
            sql = "UPDATE sessions.threads SET visibility = %s WHERE thread_slug = %s AND user_id = %s"
            cursor.execute(sql, (visibility, thread_id, user_id))
            conn.commit()
    
    return success_response({'visibility': visibility})
```

---

### ❌ POST `/api/threads/<id>/members` — Not Implemented

**Purpose:** Add member to restricted thread

**Design:**
```
POST /api/threads/1234567890/members
{
    "user_id": 15,
    "can_write": true
}
```

**Access:** Owner only

**Implementation Needed:**
```python
@thread_bp.route('/<thread_id>/members', methods=['POST'])
def add_thread_member(thread_id):
    # Validate thread ownership
    # Validate target user exists
    # INSERT into session.thread_members
    # Return success
```

---

### ❌ DELETE `/api/threads/<id>/members/<user_id>` — Not Implemented

**Purpose:** Remove member from restricted thread

**Access:** Owner only

---

### ❌ GET `/api/threads/<id>/members` — Not Implemented

**Purpose:** List members of restricted thread

**Returns:**
```json
{
    "members": [
        {
            "user_id": 15,
            "username": "alice",
            "can_write": true,
            "added_by": 12,
            "added_at": "2026-05-29T12:00:00Z"
        }
    ]
}
```

---

## Visibility Filtering Logic — To Be Implemented

### Current Problem

`list_threads()` returns threads matching only `WHERE t.user_id = %s`, ignoring visibility:

```python
# CURRENT (WRONG):
cursor.execute("SELECT ... FROM sessions.threads WHERE user_id = %s", (user_id,))
# Returns: ALL threads owned by user (personal, team, restricted)
```

### Correct Logic (Needed)

For each thread returned, check visibility:

```python
def can_user_see_thread(thread, current_user_id, current_org_id):
    """
    Check if current user can see this thread based on visibility
    """
    if thread['visibility'] == 'personal':
        # Only owner can see
        return thread['user_id'] == current_user_id
    
    elif thread['visibility'] == 'team':
        # Owner OR same org
        return (thread['user_id'] == current_user_id or 
                thread['organisation_id'] == current_org_id)
    
    elif thread['visibility'] == 'restricted':
        # Owner OR explicit member
        if thread['user_id'] == current_user_id:
            return True
        
        # Check if user is in thread_members
        with get_database_connection('sessions') as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM sessions.thread_members WHERE thread_id = %s AND user_id = %s",
                    (thread['thread_slug'], current_user_id)
                )
                return cursor.fetchone() is not None
    
    return False
```

**Where to call:** In `list_threads()` after fetching rows, filter:
```python
threads = [t for t in threads if can_user_see_thread(t, user_id, current_org_id)]
```

---

## Frontend Alignment

### UI Shows These Options ✅

From screenshot: New thread dialog shows:
- ⭕ Personal (default, selected)
- ⭕ Team
- ⭕ Restricted

**Visibility Description:**
```
Personal = only you
Team = all org members
Restricted = invited members only
```

### Frontend Sends ✅

```javascript
// From thread-manager-crud.js
createThreadWithMetadata({
    title: 'Visualisation test 29th May',
    visibility: 'personal',  // ← Selected from radio button
    location: 'agent-18',
    tags: []
})
```

### Frontend Receives (What it needs)

```javascript
// Response should include:
{
    success: true,
    thread: {
        id: "...",
        visibility: "personal",  // ← Currently MISSING from response
        title: "...",
        created: "..."
    }
}
```

---

## Implementation Priority

### Tier 1 (Critical — Security)
1. ✅ DONE: Accept visibility in POST /create
2. ⏳ TODO: Filter visibility in GET /list
3. ⏳ TODO: Validate visibility before returning thread data

### Tier 2 (Important — User-Facing)
4. ⏳ TODO: PATCH endpoint for visibility updates
5. ⏳ TODO: Member management endpoints (restricted threads)

### Tier 3 (Nice-to-Have)
6. ⏳ TODO: RLS policies to enforce visibility at DB level
7. ⏳ TODO: Audit log for visibility changes

---

## Verification Checklist

- [x] Database schema has visibility column (migration 047)
- [x] Database schema has thread_members table (migration 047)
- [x] Thread creation accepts visibility parameter (POST /create)
- [x] Thread retrieval includes visibility field (GET /list, /bulk-with-messages)
- [ ] Thread retrieval filters by visibility (list_threads() WHERE clause)
- [ ] Access enforcement before returning data (can_user_see_thread check)
- [ ] PATCH endpoint to update visibility
- [ ] POST/DELETE endpoints for member management
- [ ] Frontend properly displays visibility in responses
- [ ] Frontend properly shows visibility status in thread list

---

## Files Modified (May 29, 2026)

| File | Change | Lines |
|------|--------|-------|
| `AI_infrastructure/routes/thread_routes.py` | Added visibility extraction in create_thread() | 387 |
| `AI_infrastructure/routes/thread_routes.py` | Added visibility to SELECT in list_threads() | 775–810 |
| `AI_infrastructure/routes/thread_routes.py` | Added visibility to response in list_threads() | 830–835 |
| `AI_infrastructure/routes/thread_routes.py` | Added visibility to CTE in bulk-with-messages() | 908–935 |

---

## Next Steps

1. **Immediate (Today):** Verify organisation_id column exists in threads table
2. **Short-term (Today):** Implement visibility filtering in list_threads()
3. **Short-term (Today):** Add access enforcement check
4. **Follow-up (Tomorrow):** Implement PATCH endpoint for visibility updates
5. **Follow-up (Tomorrow):** Implement member management endpoints

---

## Related Files

- **Database:** `AI_infrastructure/migrations/047_thread_visibility.sql`
- **Routes:** `AI_infrastructure/routes/thread_routes.py`
- **Frontend:** `UI/thread-manager-crud.js`, `UI/thread-manager-interactions.js`
- **Analysis:** `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`

