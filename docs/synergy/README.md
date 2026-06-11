# SYNERGY DASHBOARD DOCUMENTATION

**Last Updated:** November 9, 2025 (historical) / June 11, 2026 (row 46 link updates)
**Status:** Historical Index ✅ (see update notes below)

---

> **Update (June 11, 2026, archive-cleanup row 46):** The "Complete Reference" and
> "UI Fixes Summary" files referenced below were moved to the top-level
> `docs/archive/kanban/_ARCHIVED_*.md` namespace (they were dated Nov 9, 2025
> snapshot docs, not durable canonical references). Only the **Card Structure**
> doc remains as a current reference.

## QUICK LINKS

📖 **Start Here:**
- [Card Structure](./SYNERGY_CARD_STRUCTURE_DOCUMENTATION.md) - Field reference and data formats (current reference)

🔧 **For Developers:**
- Frontend: `UI/business-ai-platform-v2-fixed.html` (25,871 lines)
- Backend: `AI_infrastructure/routes/synergy_routes.py`
- Threads: `AI_infrastructure/routes/thread_routes.py`
- Tools: `tools/schemas/synergy_tools.json`

📦 **Archived Documentation:**
- Archived files now consolidated at: `docs/archive/kanban/_ARCHIVED_SYNERGY_*.md`
  (the in-tree `docs/synergy/archive/` subdir was retired during the June 2026 cleanup)

---

## WHAT IS SYNERGY?

Synergy Dashboard is a visual Kanban-style project management system for tracking multi-platform AI agent projects. It provides:

- **Visual Tracking:** 4-column Kanban board (Backlog → In Progress → Review → Done)
- **Multi-Platform:** Integrates Google Workspace, Microsoft 365, Slack, Stripe, etc.
- **Persistent Context:** Projects survive across conversations
- **Rich Metadata:** Documents, links, checklists, notes, activity logs, thread linking

---

## RECENT UPDATES

### November 9, 2025 - Version 2.0 ✅

Fixed 11 critical UI display issues:
1. ✅ Documents display (clickable links + type badges)
2. ✅ Links display (always visible + field handling)
3. ✅ Checklist display (field variations + subtasks)
4. ✅ Next steps consistency
5. ✅ Linked threads (created backend endpoint)
6. ✅ Notes field display
7. ✅ Activity log structure
8. ✅ Session ID click-to-copy
9. ✅ Checkbox event handling
10. ✅ Smooth card transitions
11. ✅ Edit mode flow

**Impact:** 100% data visibility, professional UX, robust field handling

(See archived [UI Fixes Summary](../../archive/kanban/_ARCHIVED_SYNERGY_UI_FIXES_SUMMARY_NOV9_2025.md) for the full Nov 9 details — this section is now historical.)

---

## DOCUMENTATION STRUCTURE

### Core Documentation (docs/synergy/)

**Main References:**
- `SYNERGY_CARD_STRUCTURE_DOCUMENTATION.md` - Field reference (current canonical)
  - 30 database fields
  - JSON array structures
  - Field name variations
  - Data format examples

> The previous "Complete Reference" (Nov 9, 2025) and "UI Fixes Summary"
> (Nov 9, 2025) docs were moved to `docs/archive/kanban/_ARCHIVED_*.md` during
> the June 2026 cleanup. They are 7+ months out of date.

### Archived Documentation

Previous documentation versions (now at `docs/archive/kanban/_ARCHIVED_SYNERGY_*.md`):
- `_ARCHIVED_SYNERGY_DISPLAY_FIX_COMPLETE.md` - Earlier fixes
- `_ARCHIVED_SYNERGY_HTML_DB_VERIFICATION_COMPLETE.md` - Database verification
- `_ARCHIVED_SYNERGY_THREAD_LINKING_ANALYSIS.md` - Thread linking analysis
- `_ARCHIVED_SYNERGY_THREAD_INTEGRATION_COMPLETE.md` - Thread integration guide
- `_ARCHIVED_SYNERGY_COMPLETE_REFERENCE_NOV9_2025.md` - Nov 9 master doc (archived)
- `_ARCHIVED_SYNERGY_UI_FIXES_SUMMARY_NOV9_2025.md` - Nov 9 UI fixes summary (archived)

---

## GETTING STARTED

### For AI Agents

**1. Use the Smart Tool:**
```javascript
const result = await synergy_smart_project_tracker({
    title: "Customer Onboarding System",
    platforms_involved: ["gmail", "forms", "sheets"],
    next_steps: [
        "Create welcome email",
        "Create signup form",
        "Create tracking sheet"
    ],
    priority: "high"
});

const sessionId = result.session_id;
```

**2. Update After Creating Resources:**
```javascript
// CRITICAL: Fetch first
const session = await synergy_get_session({ session_id: sessionId });

// Then update with ALL documents
await synergy_update_session({
    session_id: sessionId,
    documents: [
        ...session.documents,  // Keep existing
        { name: "Email Template", url: emailUrl, type: "email" }
    ]
});
```

**3. Get Guidance:**
```javascript
await synergy_agent_instructions('quickstart');  // Step-by-step guide
await synergy_agent_instructions('troubleshooting');  // Common issues
```

### For Users

**Access Dashboard:**
1. Navigate to AI Agents platform
2. Click "Synergy" tab in sidebar
3. View Kanban board with all projects

**Card Actions:**
- **Click card** - Expand to see full details
- **Drag card** - Move between columns
- **Pop out** - Open in separate window
- **Edit** - Modify all fields
- **Resume** - Continue in AI chat

---

## KEY FEATURES

### Data Display (Nov 9 Fixes)
- ✅ **Documents:** Clickable links with type-specific icons and badges
- ✅ **Links:** Always visible, handles field variations
- ✅ **Checklist:** Displays tasks and subtasks correctly
- ✅ **Next Steps:** Handles all field name variations
- ✅ **Linked Threads:** Shows real thread data with agent info
- ✅ **Notes:** Always visible with empty state
- ✅ **Activity Log:** Structured format with icons and timestamps
- ✅ **Session ID:** Click-to-copy with toast notification

### User Experience
- ✅ **Smooth Transitions:** 0.3s animations with cubic-bezier easing
- ✅ **Event Handling:** Checkboxes work without side effects
- ✅ **Edit Flow:** Returns to popout after save
- ✅ **Visual Feedback:** Hover effects, toast notifications

### Backend
- ✅ **REST API:** Full CRUD operations
- ✅ **Thread Integration:** Link threads to projects
- ✅ **Real-time Updates:** WebSocket support (when enabled)

---

## DATABASE SCHEMA

### synergy_sessions Table (30 columns)

**Core Fields:**
- `session_id` - Unique identifier
- `title` - Project title
- `description` - Detailed description
- `project_name` - Grouping name

**Status & Priority:**
- `status` - active, paused, completed, archived
- `priority` - low, medium, high, critical
- `kanban_column` - backlog, in_progress, review, done

**JSON Arrays:**
- `documents` - [{name, url, type, created_at}]
- `links` - [{title/name, url, type}]
- `tags` - ["tag1", "tag2"]
- `next_steps` - [string] or [{description, completed, due_date, sub_checklist}]
- `checklist` - [{task/item, completed, subtasks}]
- `assignees` - ["User 1", "User 2"]
- `thread_ids` - ["thread_123", "thread_456"]
- `assigned_agents` - ["agent1", "agent2"]
- `recent_activity` - [{description, type, timestamp, user}]

(Schema details from archived [Complete Reference](../../archive/kanban/_ARCHIVED_SYNERGY_COMPLETE_REFERENCE_NOV9_2025.md) — full schema in the current `SYNERGY_CARD_STRUCTURE_DOCUMENTATION.md`.)

---

## API ENDPOINTS

### Main Operations
- `POST /api/synergy/create` - Create session
- `GET /api/synergy/list` - List all sessions
- `GET /api/synergy/<session_id>` - Get single session
- `PUT /api/synergy/<session_id>` - Update session
- `DELETE /api/synergy/<session_id>` - Delete session

### New (Nov 9, 2025)
- `POST /api/threads/details` - Get thread data for multiple IDs

(Full API docs in the archived [Complete Reference](../../archive/kanban/_ARCHIVED_SYNERGY_COMPLETE_REFERENCE_NOV9_2025.md).)

---

## TROUBLESHOOTING

### Common Issues

**Documents disappear after update:**
- ❌ Cause: Updating without fetching existing data
- ✅ Solution: Always call `synergy_get_session()` first

**Links not showing:**
- ✅ FIXED (Nov 9): Section now always visible

**Checklist items missing:**
- ✅ FIXED (Nov 9): Handles both `task` and `item` fields

**Threads spinner never stops:**
- ✅ FIXED (Nov 9): Created `/api/threads/details` endpoint

**Checkbox collapses card:**
- ✅ FIXED (Nov 9): Added `stopPropagation()`

**Edit from popout closes popout:**
- ✅ FIXED (Nov 9): Added source tracking

---

## TESTING

### Test Files
- `test_synergy_ui_fixes.py` - UI fixes verification
- `test_flask_routes.py` - Backend routes check
- `test_end_to_end_synergy.py` - Full workflow test

### Manual Testing
All items verified ✅:
- Documents display correctly
- Links section visible
- Checklist with subtasks
- Next steps display
- Threads load data
- Notes field visible
- Activity log structured
- Session ID copies
- Checkboxes work
- Transitions smooth
- Edit flow correct

---

## VERSION HISTORY

**Version 2.0 - November 9, 2025:**
- Fixed 11 critical UI display issues
- Added `/api/threads/details` backend endpoint
- Enhanced UX with smooth transitions and click-to-copy
- Resolved all field name inconsistencies
- Improved edit mode flow with source tracking

**Version 1.5 - October 2025:**
- Thread linking functionality
- Multiple backend integrations
- WebSocket support (disabled)

**Version 1.0 - September 2025:**
- Initial Synergy Dashboard release
- Basic Kanban functionality
- CRUD operations

---

## FILE LOCATIONS

### Documentation
- Card Structure (current canonical): `docs/synergy/SYNERGY_CARD_STRUCTURE_DOCUMENTATION.md`
- Archive (historical, June 2026 consolidated): `docs/archive/kanban/_ARCHIVED_SYNERGY_*.md`

### Code
- Frontend: `UI/business-ai-platform-v2-fixed.html`
- Backend Routes: `AI_infrastructure/routes/synergy_routes.py`
- Thread Routes: `AI_infrastructure/routes/thread_routes.py`
- Kanban Routes: `AI_infrastructure/routes/kanban_routes.py`
- Tool Schema: `tools/schemas/synergy_tools.json`
- Tool Implementation: `tools/implementations/synergy.py`

### Database
- Synergy Sessions: `data/synergy_sessions.db`
- Threads: `data/sessions.db`

---

## SUPPORT

**For Issues:**
1. Check the archived [Complete Reference](../../archive/kanban/_ARCHIVED_SYNERGY_COMPLETE_REFERENCE_NOV9_2025.md) (historical)
2. Review the archived [UI Fixes Summary](../../archive/kanban/_ARCHIVED_SYNERGY_UI_FIXES_SUMMARY_NOV9_2025.md) (historical)
3. Use `synergy_agent_instructions('troubleshooting')` tool (current)
4. Check frontend console for errors
5. Verify backend logs in Flask output

**For Questions:**
- Use `synergy_agent_instructions('overview')` for general info
- Use `synergy_agent_instructions('quickstart')` for getting started
- Use `synergy_agent_instructions('workflow')` for complete patterns

---

## MAINTENANCE

**Regular Tasks:**
- Monitor error rates
- Check database growth
- Review user feedback
- Test new integrations
- Update documentation

**Next Review:** December 2025

---

**Documentation Index Maintained By:** GitHub Copilot AI Assistant  
**Last Updated:** November 9, 2025  
**Status:** Production Ready ✅
