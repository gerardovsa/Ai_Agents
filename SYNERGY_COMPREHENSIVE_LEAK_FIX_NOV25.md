# Synergy Routes - Comprehensive Connection Leak Fix
**Date**: November 25, 2025  
**Status**: IN PROGRESS (7/22 functions fixed)

## Executive Summary

Found **22 functions** in `synergy_routes.py` with manual `conn.close()` calls inside try blocks. These are potential connection leaks waiting to happen.

**Fixed So Far**: 7 functions (commits 8bd391d, 8a44e88)  
**Remaining**: 15 functions  
**Priority**: HIGH - Production stability

---

## Fixed Functions (7 total)

### Batch 0 - Critical UI Blockers (Commit 8bd391d)
1. ✅ **get_sessions_with_internal_docs()** - Line 389: Sidebar batch load
2. ✅ **get_linked_threads()** - Line 1833: Session expansion in sidebar

### Batch 1 - Core Session Operations (Commit 8a44e88)
3. ✅ **init_database()** - Line 213: Database initialization
4. ✅ **list_sessions()** - Line 293: Session filtering
5. ✅ **get_sessions_simple()** - Line 352: Thread linking dropdown
6. ✅ **get_sessions_bulk()** - Line 606: Bulk session fetch
7. ✅ **create_session()** - Line 654: Session creation

---

## Remaining Functions (15 total)

### HIGH PRIORITY - Active UI Endpoints

8. ⚠️ **get_session()** - Line 790: Get single session with internal docs  
   - **Risk**: Medium - Used when clicking session card  
   - **Leaks**: 2x conn.close() calls (lines 800, 919)  
   - **Impact**: Card details won't load

9. ⚠️ **update_session()** - Line 936: Update session fields  
   - **Risk**: HIGH - Used frequently during editing  
   - **Leaks**: 1x conn.close() (line 1018)  
   - **Impact**: Edits fail, connection leaks

10. ⚠️ **update_column()** - Line 1050: Move cards between kanban columns  
    - **Risk**: HIGH - Drag-and-drop feature  
    - **Leaks**: 1x conn.close() (line 1089)  
    - **Impact**: Drag-drop breaks

11. ⚠️ **delete_session()** - Line 1121: Delete session  
    - **Risk**: Medium - Less frequent  
    - **Leaks**: 1x conn.close() (line 1129)  
    - **Impact**: Can't delete sessions

12. ⚠️ **link_thread_to_synergy()** - Line 1157: Link thread to session  
    - **Risk**: HIGH - Core feature  
    - **Leaks**: 2x conn.close() (lines 1183, 1212)  
    - **Impact**: Thread linking fails

13. ⚠️ **update_card_position()** - Line 1227: Reorder cards  
    - **Risk**: Medium - Position tracking  
    - **Leaks**: 1x conn.close() (line 1250)  
    - **Impact**: Card ordering breaks

14. ⚠️ **update_multiple_positions()** - Line 1263: Batch position update  
    - **Risk**: Medium - Bulk operations  
    - **Leaks**: 1x conn.close() (line 1290)  
    - **Impact**: Bulk moves fail

15. ⚠️ **unlink_thread_from_synergy()** - Line 1302: Unlink thread  
    - **Risk**: Medium - Cleanup operation  
    - **Leaks**: 2x conn.close() (lines 1326, 1355)  
    - **Impact**: Can't unlink threads

### MEDIUM PRIORITY - Internal Docs CRUD

16. ⚠️ **create_internal_doc()** - Line 1374: Create document  
    - **Leaks**: 2x conn.close() (lines 1437, 1450)

17. ⚠️ **get_internal_doc()** - Line 1472: Get document  
    - **Leaks**: 1x conn.close() (line 1502)

18. ⚠️ **update_internal_doc()** - Line 1534: Update document  
    - **Leaks**: 2x conn.close() (lines 1568, 1598)

19. ⚠️ **delete_internal_doc()** - Line 1617: Delete document  
    - **Leaks**: 2x conn.close() (lines 1634, 1638)

20. ⚠️ **list_all_internal_docs()** - Line 1654: List all docs  
    - **Leaks**: 1x conn.close() (line 1687)

21. ⚠️ **list_internal_docs()** - Line 1714: List session docs  
    - **Leaks**: 1x conn.close() (line 1750)

22. ⚠️ **link_existing_document()** - Line 1781: Link existing doc  
    - **Leaks**: 2x conn.close() (lines 1820, 1824)

### LOW PRIORITY - Milestones (Feature Not Widely Used Yet)

23-35. **Milestone Functions** - Lines 2140-3400  
   - create_milestone, create_milestone_task, create_task_subtask
   - complete_subtask, complete_task, complete_milestone
   - get_milestone_progress, get_session_milestones
   - update_task, update_subtask, block_task
   - update_milestone_documents, update_milestone_links, update_milestone_field
   - All have manual conn.close() in try blocks

---

## Fix Pattern (Standard)

```python
def my_function():
    """Function docstring"""
    conn = None  # ← Initialize before try
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ... all database operations ...
        
        return jsonify({...})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if conn:  # ← Check if created
            conn.close()  # ← ALWAYS executes
```

---

## Why This Matters

**Connection Pool Configuration** (from database_utils.py):
```python
maxconn=2  # Only 2 connections per schema
```

**With 15 unfixed functions**:
- Each leak reduces available connections by 1
- Pool exhausted after 2 concurrent requests
- Users see 500 errors: "Connection pool exhausted"
- Requires Flask restart to recover

---

## Recommended Fix Strategy

### Phase 1 - HIGH PRIORITY (Complete This ASAP) ✅
- Fix functions 8-15 (8 functions)
- These are actively used by UI
- Prevents most connection leaks

### Phase 2 - MEDIUM PRIORITY
- Fix functions 16-22 (7 functions)
- Internal docs less frequently used
- But still important for stability

### Phase 3 - LOW PRIORITY
- Fix milestone functions (13+ functions)
- Feature not widely adopted yet
- Can defer if time-limited

---

## Testing Plan

After each batch of fixes:
1. Restart Flask (`BISTART`)
2. Open UI in browser
3. Test affected features:
   - Open Synergy sidebar ✅
   - Expand session cards
   - Edit session titles
   - Drag-drop cards between columns
   - Link/unlink threads
   - Create/edit internal docs
4. Monitor connection pool stats (should show 0 leaks)

---

## Prevention - Long Term

### Code Review Checklist
- [ ] Never use `conn.close()` inside try blocks
- [ ] Always use `try/finally` pattern
- [ ] Initialize `conn = None` before try
- [ ] Test exception paths (they're where leaks hide!)

### Automated Detection
Create pre-commit hook:
```bash
# Check for conn.close() inside try blocks
grep -n "conn.close()" routes/*.py | while read line; do
    # Check if in try block without finally
    # (Requires more sophisticated parsing)
    echo "WARNING: Manual conn.close() found: $line"
done
```

---

## Files Changed

- **AI_infrastructure/routes/synergy_routes.py**
  - Total lines: 3,424
  - Functions modified: 7/22 (32%)
  - Lines changed: ~100
  - Commits: 8bd391d, 8a44e88

---

## Next Actions

1. **IMMEDIATE**: Fix functions 8-15 (HIGH PRIORITY batch)
2. **TODAY**: Fix functions 16-22 (MEDIUM PRIORITY batch)
3. **THIS WEEK**: Fix milestone functions (LOW PRIORITY)
4. **ONGOING**: Monitor connection pool stats
5. **FUTURE**: Implement automated leak detection

---

**Last Updated**: November 25, 2025  
**Engineer**: AI Agent (GitHub Copilot)  
**Status**: 7/22 functions fixed (32% complete)  
**Next**: Fix get_session(), update_session(), update_column() (functions 8-10)
