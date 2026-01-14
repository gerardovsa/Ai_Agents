# Two Tables Explanation: `sessions` vs `synergy_sessions`

**Date:** November 9, 2025  
**Database:** synergy_sessions.db  
**Status:** Both tables are ACTIVE and serve different purposes

---

## Quick Answer

**WHY TWO TABLES?**
- `sessions` = **Legacy Kanban Board** (old system, 5 rows)
- `synergy_sessions` = **Synergy Dashboard** (current system, 15 rows)

They serve **different purposes** and are used by **different routes**.

---

## Field Comparison

### Common Fields (15 fields in both)
```
session_id, title, description, priority, status, kanban_column, 
due_date, created_at, assignees, tags, documents, links, 
next_steps, checklist, google_task_id
```

### UNIQUE to `sessions` (5 fields)
```
1. project_name          - Project name field
2. notes                 - General notes field
3. session_data          - Arbitrary data storage
4. updated_at            - Last update timestamp
5. google_calendar_event_id - Google Calendar integration
```

### UNIQUE to `synergy_sessions` (8 fields)
```
1. platforms_involved    - Array of platforms used (gmail, sheets, etc.)
2. thread_ids            - Array of linked AI conversation threads
3. assigned_agents       - Array of AI agents assigned to project
4. recent_activity       - Activity log/timeline
5. last_active          - Last activity timestamp
6. completed_at         - Completion timestamp
7. microsoft_todo_id    - Microsoft To-Do integration
8. google_calendar_id   - Google Calendar ID (different from event_id)
```

---

## Code Usage

### `sessions` table used by:
- **File:** `AI_infrastructure/routes/kanban_routes.py`
- **Purpose:** Legacy Kanban board (old system)
- **Rows:** 5 sessions
- **Features:**
  - Basic kanban board
  - Google Calendar event integration
  - Generic project/session tracking
  - No AI thread linking
  - No platform tracking

### `synergy_sessions` table used by:
- **File:** `AI_infrastructure/routes/synergy_routes.py`
- **Purpose:** Synergy Dashboard (current system)
- **Rows:** 15 sessions
- **Features:**
  - Advanced Kanban board
  - Multi-platform project tracking
  - AI thread linking (thread_ids)
  - Agent assignment (assigned_agents)
  - Activity timeline (recent_activity)
  - Platform awareness (platforms_involved)

---

## Key Differences

| Feature | sessions (Legacy) | synergy_sessions (Current) |
|---------|------------------|---------------------------|
| **Purpose** | Generic Kanban | Multi-platform AI projects |
| **AI Integration** | ❌ No threads | ✅ thread_ids |
| **Agent Tracking** | ❌ No | ✅ assigned_agents |
| **Platform Tracking** | ❌ No | ✅ platforms_involved |
| **Activity Log** | ❌ No | ✅ recent_activity |
| **Used by UI** | Old Kanban tab? | Synergy Dashboard tab |
| **Active Development** | ❌ Legacy | ✅ Current |

---

## Why Both Exist?

### Historical Context:
1. **`sessions` was created first** - Generic Kanban board for any project
2. **Synergy Dashboard needed more features**:
   - Track which platforms are involved (Gmail, Sheets, Docs, etc.)
   - Link AI conversation threads to projects
   - Track which AI agents are working on what
   - Maintain activity timeline
3. **Rather than migrate**, a new table was created with extended functionality
4. **Both coexist** - Legacy board still works, new Synergy is primary

### Design Decision:
- Creating a new table avoided breaking existing Kanban board
- Allowed adding specialized fields without cluttering legacy table
- Synergy-specific features (threads, agents, platforms) don't make sense in generic sessions
- Clean separation of concerns

---

## Database Stats

```
sessions table:         5 rows (20 fields)
synergy_sessions table: 15 rows (23 fields)
```

---

## Should We Consolidate?

### Arguments AGAINST consolidation:
1. ✅ **Different purposes** - Generic kanban vs multi-platform AI projects
2. ✅ **Both actively used** - 5 and 15 rows respectively
3. ✅ **Different features** - Synergy fields don't apply to generic sessions
4. ✅ **No conflict** - They don't overlap or interfere

### Arguments FOR consolidation:
1. ❌ Maintenance overhead - Two similar tables to maintain
2. ❌ User confusion - Which table for which purpose?
3. ❌ Code duplication - Similar CRUD operations in two route files

### Recommendation:
**KEEP BOTH for now**, but:
1. Document clearly which is for what
2. Consider deprecating `sessions` if legacy Kanban isn't used
3. If consolidating in future, migrate sessions → synergy_sessions with null values for extra fields

---

## Field Name Standardization

**Both tables use IDENTICAL field names for common fields:**
- ✅ `documents` (JSON array with {name, url, type})
- ✅ `next_steps` (JSON array)
- ✅ `checklist` (JSON array)
- ✅ `tags` (JSON array)
- ✅ All other 15 common fields match exactly

**This is GOOD** - means any consolidation would be straightforward.

---

## Related Files

### Backend Routes:
- `AI_infrastructure/routes/kanban_routes.py` - Uses `sessions` table
- `AI_infrastructure/routes/synergy_routes.py` - Uses `synergy_sessions` table

### Frontend:
- `UI/business-ai-platform-v2.html` - Synergy Dashboard (uses synergy_sessions)
- (Presumably another UI for legacy Kanban using sessions)

### Tools:
- `tools/schemas/synergy_tools.json` - Synergy tool schema (for synergy_sessions)

---

## Summary

**Both tables are legitimate and serve different purposes:**

- **`sessions`** = Legacy generic Kanban board (basic project tracking)
- **`synergy_sessions`** = Modern Synergy Dashboard (AI-powered multi-platform project tracking)

**The schema file correctly shows both** because both tables exist and are used.

**No bug, no error** - this is intentional architecture.

---

## Action Items

### Documentation:
- [x] Document purpose of each table ← THIS FILE
- [ ] Add comments to route files explaining table choice
- [ ] Update schema file with table purposes

### Future:
- [ ] Decide if legacy Kanban (sessions) should be deprecated
- [ ] If deprecating, migrate 5 rows from sessions → synergy_sessions
- [ ] If keeping, add UI documentation for which tab uses which table

---

**Status:** ✅ EXPLAINED - Two tables serve different purposes, both actively used
