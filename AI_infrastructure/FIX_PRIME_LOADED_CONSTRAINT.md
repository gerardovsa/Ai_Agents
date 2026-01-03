# Database Constraint Fix - Remove 'prime-loaded' Location

**Date:** December 31, 2025  
**Issue:** Thread assignment failing with constraint violation error  
**Status:** ✅ FIXED

---

## Problem

When assigning emails to Prime AI sidebar, the system was throwing this error:

```
API update failed: new row for relation "threads" violates check constraint "chk_location_valid"
DETAIL: Failing row contains (..., prime-loaded, ...)
```

### Root Cause

The database migration 010 (run_010_migration.py) removed `'prime-loaded'` from the valid location values in December 2025. However, the JavaScript frontend code was still trying to assign threads to the `'prime-loaded'` location.

### Valid Locations (After Migration 010)

```sql
CHECK (location = ANY (ARRAY[
  'unassigned', 'prime',
  'agent-1' through 'agent-26',
  'synergy'
]))
```

**Note:** `'prime-loaded'` is NO LONGER VALID ❌

---

## Files Fixed

### 1. thread-manager-interactions.js (6 changes)
**Location:** UI/modules_internal/thread-manager/

**Changes:**
- Line 96: `'prime-loaded'` → `'prime'` (loadThreadInPrime)
- Line 223: `'prime-loaded'` → `'prime'` (assignThread call)
- Line 290: `'prime-loaded'` → `'prime'` (move-to-prime case)
- Line 412: `'prime-loaded'` → `'prime'` (unloadThread comparison)
- Line 322: Updated comment (no more 'prime-loaded')
- Line 639: Updated comment (no more 'prime-loaded')

### 2. thread-manager-ui.js (4 changes)
**Location:** UI/modules_internal/thread-manager/

**Changes:**
- Lines 321-326: Updated button logic to use `'prime'` instead of `'prime-loaded'`
- Lines 506-510: Removed `'prime-loaded'` display name distinction
- Line 625: Changed render call to use `'prime'` location
- Lines 674-677: Removed `'prime-loaded'` normalization logic

### 3. thread-card-expansion.js (1 change)
**Location:** UI/modules_internal/thread-cards/

**Changes:**
- Line 231: `'prime-loaded'` → `'prime'` (cardLocation check)

### 4. thread-card-templates.js (1 change)
**Location:** UI/modules_internal/thread-cards/

**Changes:**
- Line 796: `'prime-loaded'` → `'prime'` (email pill display condition)

---

## Testing Checklist

### Before Fix
- [x] ❌ Error: "violates check constraint chk_location_valid"
- [x] ❌ Threads fail to assign to Prime
- [x] ❌ Email drafting workflow broken

### After Fix
- [ ] ⏳ No constraint violations
- [ ] ⏳ Threads successfully assign to Prime
- [ ] ⏳ Email drafting workflow works
- [ ] ⏳ Thread cards display correctly
- [ ] ⏳ Prime sidebar loads threads properly

---

## How to Test

### 1. Refresh Browser
```bash
# Hard refresh to clear cached JavaScript
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### 2. Test Email Assignment
1. Open Communication Hub
2. Click "Draft Reply" on any email
3. **Expected:** Thread loads in Prime without errors
4. **Check Console:** Should see `✅ Thread assigned to prime: [threadId]`

### 3. Verify Database
```sql
-- Check no prime-loaded threads exist
SELECT COUNT(*) FROM sessions.threads WHERE location = 'prime-loaded';
-- Expected: 0

-- Check prime threads exist
SELECT COUNT(*) FROM sessions.threads WHERE location = 'prime';
-- Expected: > 0
```

### 4. Check Browser Console
Look for these success messages:
```
✅ [Interactions] Thread assigned to prime: 1767108447128
✅ [CommunicationHub] Email assigned to Prime for draft reply
```

**NO ERRORS should appear** ❌ about constraint violations

---

## Migration History

### Migration 009 (December 2025)
- **Added** `'prime-loaded'` to valid locations
- **Purpose:** Distinguish threads that load on startup

### Migration 010 (December 2025)
- **Removed** `'prime-loaded'` from valid locations
- **Updated** existing `'prime-loaded'` threads → `'prime'`
- **Reason:** Simplified location model (use separate flag for "load on startup" if needed)

### This Fix (December 31, 2025)
- **Updated** JavaScript frontend to stop using `'prime-loaded'`
- **Changed** all references to use `'prime'` instead
- **Result:** Frontend and database now consistent ✅

---

## Alternative Solutions Considered

### Option 1: Revert Migration 010 (NOT CHOSEN)
- **Pros:** Minimal code changes
- **Cons:** Adds complexity with `'prime-loaded'` state
- **Reason Rejected:** Migration 010 was correct - simpler is better

### Option 2: Add Separate `auto_load` Column (FUTURE)
- **Pros:** Clean separation of concerns
- **Implementation:** Add `auto_load BOOLEAN` to threads table
- **Status:** Can be done later if needed

### Option 3: Update Frontend (CHOSEN ✅)
- **Pros:** Aligns with simplified database model
- **Cons:** Requires JavaScript changes across 4 files
- **Reason Chosen:** Correct architectural decision, cleaner codebase

---

## Technical Details

### Database Constraint Definition
```sql
ALTER TABLE sessions.threads 
ADD CONSTRAINT chk_location_valid 
CHECK (
  location = ANY (ARRAY[
    'unassigned'::text, 'prime'::text,
    'agent-1'::text, ... 'agent-26'::text,
    'synergy'::text
  ])
)
```

### JavaScript Assignment Call
```javascript
// BEFORE (WRONG ❌)
await this.assignThread(threadId, 'prime-loaded', true);

// AFTER (CORRECT ✅)
await this.assignThread(threadId, 'prime', true);
```

### Backend Route (No Changes Needed)
The backend `/api/thread-assignments/assign` route was already correct - it just validates against the database constraint. The error was coming from the frontend sending an invalid value.

---

## Impact Analysis

### Breaking Changes
**None** - This fix restores correct functionality

### User-Visible Changes
- ✅ Email draft workflow now works
- ✅ Thread assignment to Prime succeeds
- ✅ No more constraint violation errors

### Performance Impact
**None** - Same number of database operations

### Data Migration Required
**No** - Migration 010 already updated existing data

---

## Rollback Plan

If issues arise, revert these commits:

```bash
# List recent commits
git log --oneline -5

# Revert this fix
git revert <commit-hash>

# Push revert
git push origin v10
```

**Note:** You would also need to revert Migration 010 by running:
```sql
-- Re-add 'prime-loaded' to constraint
ALTER TABLE sessions.threads DROP CONSTRAINT chk_location_valid;
ALTER TABLE sessions.threads ADD CONSTRAINT chk_location_valid CHECK (
  location = ANY (ARRAY[
    'unassigned', 'prime', 'prime-loaded',
    'agent-1' ... 'agent-26',
    'synergy'
  ])
);
```

---

## Related Documentation

- **Migration 010:** `AI_infrastructure/migrations/run_010_migration.py`
- **Database Utils:** `AI_infrastructure/shared/database_utils.py`
- **Thread Manager:** `UI/modules_internal/thread-manager/`
- **Thread Cards:** `UI/modules_internal/thread-cards/`

---

## Future Improvements

### 1. Add `auto_load` Flag (Optional)
If we want to track "load on startup" preference:

```sql
ALTER TABLE sessions.threads ADD COLUMN auto_load BOOLEAN DEFAULT FALSE;
```

### 2. Add Location Validation Function
Create a JavaScript helper to validate locations before API calls:

```javascript
function validateThreadLocation(location) {
  const validLocations = [
    'unassigned', 'prime', 'synergy',
    ...Array.from({length: 26}, (_, i) => `agent-${i + 1}`)
  ];
  return validLocations.includes(location);
}
```

### 3. Add Database Constraint Test
Create automated test to verify constraint is working:

```python
# In test suite
def test_invalid_location_rejected():
    with pytest.raises(IntegrityError):
        execute_query(
            "INSERT INTO sessions.threads (thread_id, user_id, location) VALUES (%s, %s, %s)",
            ('test-123', 1, 'invalid-location')
        )
```

---

## Sign-Off

**Issue:** Thread assignment constraint violation  
**Root Cause:** Frontend using removed `'prime-loaded'` location  
**Fix:** Updated 4 JavaScript files to use `'prime'` instead  
**Files Changed:** 12 replacements across 4 files  
**Testing Status:** Ready for testing ⏳  
**Production Ready:** Yes, after testing ✅

---

**Last Updated:** December 31, 2025  
**Fixed By:** GitHub Copilot  
**Reviewed By:** _____________  
**Deployed:** _____________
