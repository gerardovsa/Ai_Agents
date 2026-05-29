# Thread Visibility Endpoints & Functions Analysis — May 29, 2026

**Date**: May 29, 2026  
**Scope**: Complete audit of thread visibility implementation across routes, migrations, and codebase  
**Status**: Partially implemented — Storage and schema complete, enforcement missing

---

## Executive Summary

Thread visibility infrastructure is **50% complete**:

✅ **DONE:**
- Database schema (visibility column, thread_members table)
- Thread creation with visibility parameter
- Basic storage and retrieval

❌ **MISSING:**
- Endpoint to update/change visibility after creation
- Filtering logic that respects visibility on reads
- Member management for restricted threads
- Access control enforcement (no verification caller can see thread)
- Thread_members table is completely unused

---

## 1. Database Layer

### Migration 047: Thread Visibility
**File**: `AI_infrastructure/migrations/047_thread_visibility.sql`

#### Visibility Column
```sql
ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'personal'
        CHECK (visibility IN ('personal', 'team', 'restricted'));
```

**Enum values:**
- `personal` — Only thread creator can see/access
- `team` — All organization members can see/access
- `restricted` — Only explicit members (in thread_members) can see/access

#### Thread Members Table
```sql
CREATE TABLE IF NOT EXISTS sessions.thread_members (
    id          SERIAL PRIMARY KEY,
    thread_id   TEXT        NOT NULL REFERENCES sessions.threads(thread_slug) ON DELETE CASCADE,
    user_id     INTEGER     NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    can_write   BOOLEAN     NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    added_by    INTEGER     REFERENCES ai_infrastructure.users(id),
    UNIQUE (thread_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_thread_members_thread ON sessions.thread_members(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_members_user   ON sessions.thread_members(user_id);
```

**Purpose**: Tracks explicit members for `visibility='restricted'` threads.  
**Status**: Created but **completely unused** in any code.

---

## 2. Routes & Endpoints Analysis

### 2.1 Thread Routes File Structure

**File**: `AI_infrastructure/routes/thread_routes.py`  
**Blueprint prefix**: `/api/threads`  
**Total endpoints**: 25+

#### Currently Implemented

| Endpoint | Method | Line | Purpose | Visibility Handling |
|----------|--------|------|---------|---------------------|
| `/create` | POST | 410 | Create new thread | ✅ Accepts & stores `visibility` param (line 387) |
| `/list` | GET | 826 | List user's threads | ❌ Does NOT filter by visibility |
| `/load/<thread_id>` | GET | 1486 | Get single thread | ⚠️ Loads but no access check |
| `/<thread_id>/update` | PATCH | 1651 | Update thread metadata | ❌ No visibility update |
| `/bulk-with-messages` | GET | 968 | Bulk load threads | ❌ No visibility filtering |
| `/search` | GET | 1217 | Search threads | ❌ No visibility filtering |

**More endpoints**: `/assigned`, `/save`, `/upsert`, `/delete`, `/stats`, `/autosave`, `/mark-read`, `/details`, etc.  
**Visibility handling in all**: **NONE** (no filtering, no enforcement, no member checks)

#### Missing Endpoints

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/<thread_id>/visibility` | PATCH | Update thread visibility after creation | HIGH |
| `/<thread_id>/members` | GET | List members of restricted thread | HIGH |
| `/<thread_id>/members` | POST | Add user to restricted thread | HIGH |
| `/<thread_id>/members/<user_id>` | DELETE | Remove user from restricted thread | HIGH |

### 2.2 Thread Sharing Routes

**File**: `AI_infrastructure/routes/thread_sharing_routes.py`  
**Purpose**: Share threads with specific users

**Current endpoints:**
- `POST /api/threads/<thread_slug>/share` — Share thread
- `POST /api/threads/<thread_slug>/share-email` — Share via email
- `POST /api/thread-shares/accept/<token>` — Accept share
- `DELETE /api/threads/<thread_slug>/share/<user_id>` — Revoke share
- `GET /api/threads/<thread_slug>/collaborators` — List who thread is shared with
- `GET /api/my-shared-threads` — List threads shared with current user

**Visibility awareness**: ⚠️ Limited
- Focuses on explicit sharing (collaborators)
- Doesn't enforce visibility='team' auto-sharing
- Doesn't leverage thread_members table

### 2.3 Thread Assignment Routes

**File**: `AI_infrastructure/routes/thread_assignment_routes.py`  
**Purpose**: Assign threads to locations (Prime/Alpha/Bravo/Charlie)

**Current endpoints**:
- POST/GET `/api/thread-assignments` — Manage assignments
- POST `/api/thread-assignments/assign` — Assign thread
- DELETE `/api/thread-assignments/clear/<location>` — Clear location

**Visibility awareness**: ❌ None
- No filtering by visibility
- No access control before assignment

---

## 3. Visibility Filtering & Enforcement: Current State

### 3.1 List Threads Function
**File**: `AI_infrastructure/routes/thread_routes.py` (line 765)  
**Function**: `list_threads()`

**Current query:**
```sql
SELECT 
    t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at,
    t.metadata, t.location, t.tags, t.synergy_card_id, ...
    (SELECT COUNT(*) FROM sessions.messages WHERE thread_id = t.id) as message_count,
    ...
FROM sessions.threads t
WHERE t.user_id = %s
ORDER BY t.updated_at DESC
LIMIT %s
```

**Issues:**
1. ❌ **Does NOT select** `visibility` column
2. ❌ **Does NOT filter** by visibility rules
3. ❌ **Returns ALL threads** regardless of visibility setting
4. ❌ **No access control** — doesn't check if caller can see thread

**Correct behavior should be:**
```sql
-- Only include threads where:
-- 1. visibility='personal' AND user_id = current_user (owner)
-- 2. visibility='team' AND current_user is in same org as thread
-- 3. visibility='restricted' AND current_user is in thread_members
WHERE (
    (t.visibility = 'personal' AND t.user_id = %s)
    OR (t.visibility = 'team' AND t.organisation_id = %s)
    OR (t.visibility = 'restricted' AND EXISTS (
        SELECT 1 FROM sessions.thread_members tm
        WHERE tm.thread_id = t.thread_slug AND tm.user_id = %s
    ))
)
```

### 3.2 Thread Loading Function
**File**: `AI_infrastructure/routes/thread_routes.py` (line 1486)  
**Function**: `load_thread(thread_id)`

**Current behavior:**
- Loads thread by ID/slug with no visibility check
- Returns thread data regardless of caller's visibility access

**Missing logic:**
- Verify caller has access based on visibility + membership
- Return 403 if caller cannot see this thread

### 3.3 Other GET Operations
- `/bulk-with-messages` — No filtering
- `/search` — No filtering
- `/details` — No visibility check
- All assume user_id ownership = access permission

---

## 4. Thread Members Table Usage

### Current State
**Table exists**: ✅ `sessions.thread_members`  
**Used anywhere**: ❌ No references in any Python code

```bash
# Search results:
$ find AI_infrastructure -name "*.py" -exec grep -l "thread_members" {} \;
# Returns: NOTHING
```

### What Should Use It
1. **Membership verification** — "Does user_id have access to thread_id?"
2. **Member listing** — "Who is allowed to see thread_id?"
3. **Access control** — "Check thread_members before returning thread data"
4. **Member management** — "Add/remove users from restricted threads"

**All of these are currently missing.**

---

## 5. Visibility Implementation Map

### What Exists
```
┌─────────────────────────────────┐
│   sessions.threads              │
│  ├─ id (INT)                    │
│  ├─ thread_slug (TEXT)          │
│  ├─ user_id (INT)               │
│  ├─ visibility (TEXT) ✅        │
│  └─ ...                         │
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│   sessions.thread_members       │
│  ├─ thread_id (TEXT FK)         │
│  ├─ user_id (INT FK)            │
│  ├─ can_write (BOOL)            │
│  └─ added_at (TSTAMPZ)          │
└─────────────────────────────────┘
```

### What's Missing: Enforcement Layer
```
API Request
    ↓
[❌ MISSING: Check g.user_id, g.organisation_id, g.jwt_version_valid]
    ↓
Get thread with visibility check
    ├─ personal: user_id = g.user_id
    ├─ team: organisation_id = g.organisation_id
    └─ restricted: user_id in thread_members
    ↓
Return thread (or 403 if no access)
```

---

## 6. Comparison: Synergy Implementation

Synergy sessions (similar concept) have **visibility update endpoints**:

**File**: `AI_infrastructure/routes/synergy_routes.py`  
**Endpoint**: `PATCH /<session_id>/visibility`  
**Line**: 1140+

```python
@synergy_bp.route('/<session_id>/visibility', methods=['PATCH'])
def update_session_visibility(session_id):
    """Update the visibility field of a session (private / shared / team)."""
    # Implementation exists for synergy
    # UPDATE synergy_sessions SET visibility = %s, last_active = %s WHERE session_id = %s
```

**Threads need equivalent.**

---

## 7. Implementation Gaps Summary

### Tier 1: Critical (Blocks visibility feature)
- [ ] PATCH endpoint to update thread visibility
- [ ] Visibility filtering in list_threads()
- [ ] Visibility filtering in load_thread()
- [ ] Visibility enforcement in all GET endpoints

### Tier 2: Important (Enables restricted threads)
- [ ] POST/DELETE endpoints for thread_members management
- [ ] GET endpoint to list members of a thread
- [ ] Access verification before returning thread data
- [ ] Membership check in restricted visibility filtering

### Tier 3: Enhancement
- [ ] Visibility change audit log
- [ ] Member role tracking (can_write flag usage)
- [ ] Bulk member operations
- [ ] Member invitation system (for restricted threads)

---

## 8. Code Locations to Modify

| Task | File | Line/Function | Type |
|------|------|---------------|------|
| Add visibility filtering | thread_routes.py | `list_threads()` ~765 | Modify WHERE clause |
| Add visibility check on load | thread_routes.py | `load_thread()` ~1486 | Add access check |
| Create update endpoint | thread_routes.py | (new) | Add new @route |
| Member management endpoints | thread_routes.py | (new) | Add 3 @routes |
| Access control helper | thread_routes.py | (new) | Add utility function |
| Org ID on threads | — | ✅ Already exists (migration 029) | — |

---

## 9. Required Implementation Order

```
Phase 1: Core Enforcement (This week)
├─ Add can_access_thread(user_id, thread_id) helper function
├─ Modify list_threads() to filter by visibility
├─ Modify load_thread() to check visibility
└─ Add PATCH /<thread_id>/visibility endpoint

Phase 2: Member Management (Next)
├─ POST /<thread_id>/members - add member
├─ DELETE /<thread_id>/members/<user_id> - remove
├─ GET /<thread_id>/members - list
└─ Visibility filter in thread_sharing_routes

Phase 3: Validation & Audit (Polish)
├─ Audit log for visibility changes
├─ Membership audit
└─ Documentation
```

---

## 10. Testing Checklist

### Visibility='personal' Tests
- [ ] Only creator can see in list
- [ ] Creator can load thread
- [ ] Other users get 403
- [ ] Visibility cannot be changed to team/restricted

### Visibility='team' Tests
- [ ] All org members can see in list
- [ ] All org members can load thread
- [ ] Non-org members get 403
- [ ] Visibility can be changed to personal/restricted

### Visibility='restricted' Tests
- [ ] Only explicit members can see
- [ ] Only explicit members can load
- [ ] Non-members get 403 even in same org
- [ ] Can add/remove members
- [ ] can_write flag is respected

---

## 11. API Design Proposal

### New Endpoints

#### Update Thread Visibility
```
PATCH /api/threads/<thread_id>/visibility
Request:
{
    "visibility": "restricted"  // "personal" | "team" | "restricted"
}
Response:
{
    "success": true,
    "thread_id": "...",
    "visibility": "restricted",
    "updated_at": "..."
}
```

#### Add Member to Thread
```
POST /api/threads/<thread_id>/members
Request:
{
    "user_id": 42,
    "can_write": true
}
Response:
{
    "success": true,
    "user_id": 42,
    "can_write": true,
    "added_at": "..."
}
```

#### Remove Member from Thread
```
DELETE /api/threads/<thread_id>/members/<user_id>
Response:
{
    "success": true,
    "user_id": 42,
    "removed_at": "..."
}
```

#### List Members of Thread
```
GET /api/threads/<thread_id>/members
Response:
{
    "success": true,
    "thread_id": "...",
    "visibility": "restricted",
    "members": [
        {
            "user_id": 42,
            "username": "john",
            "can_write": true,
            "added_at": "...",
            "added_by": 12
        }
    ]
}
```

---

## 12. File Structure Reference

```
AI_infrastructure/
├── routes/
│   ├── thread_routes.py              ← Main thread endpoints
│   ├── thread_sharing_routes.py      ← Sharing (needs visibility awareness)
│   ├── thread_assignment_routes.py   ← Location assignments (no visibility)
│   └── ...
├── migrations/
│   ├── 047_thread_visibility.sql     ← Schema: visibility column + thread_members table
│   ├── 029_org_id_on_threads.sql     ← Organisation context for team visibility
│   └── ...
└── shared/
    └── database_utils.py             ← execute_query() helper
```

---

## Conclusion

Thread visibility is **architecturally sound** (good schema design) but **operationally incomplete** (no filtering or enforcement). The infrastructure supports all three visibility modes, but the application never actually uses visibility settings to restrict access.

**Priority: HIGH** — This is a security gap. Threads marked 'personal' are visible to all users because there's no filtering.

**Effort: MEDIUM** — 30-40 hours to implement Tier 1 + Tier 2, assuming the helper functions are well-designed.
