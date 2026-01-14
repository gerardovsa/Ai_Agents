# Create Comprehensive Synergy Example - Quick Guide

## What This Does

Creates a **complete demo synergy card** showing ALL available features:
- 8 next steps with 30 subtasks
- 5 checklist items with 13 subtasks
- 5 external resource links
- 3 internal documents (richtext + spreadsheet)
- 10 activity log entries
- Tags, priorities, due dates, assigned agents

## How to Run

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python scripts\setup\create_comprehensive_synergy_example.py
```

## Expected Output

```
Using database: C:\Users\gpoli\GIT\AI_agents\data\synergy_sessions.db
Created synergy session: sess_comprehensive_example_2025
Added 8 next steps with sub-checklists
Added 5 checklist items with subtasks
Added 5 external resource links
Added 10 activity log entries
Created 3 internal documents

SUCCESS! Comprehensive example synergy card created!

Session ID: sess_comprehensive_example_2025
Title: Complete Project Management Example

Features included:
  - 8 next steps with sub-checklists
  - 5 checklist items with subtasks
  - 5 external resource links
  - 10 activity log entries
  - 3 internal documents
  - Tags, priorities, due dates
  - Assigned agents
  - Rich markdown description

Refresh your Synergy board to see it!
```

## How to View

1. Open `business-ai-platform-v2.html` in browser
2. Click synergy toggle button (LEFT side)
3. Look for "Complete Project Management Example" card
4. Click to expand and explore all features

## What's Included

### Session Details
- **Title:** Complete Project Management Example
- **Session ID:** sess_comprehensive_example_2025
- **Priority:** High
- **Status:** Active
- **Column:** In Progress
- **Due Date:** 14 days from creation
- **Tags:** example, demo, comprehensive, reference, tutorial
- **Agents:** Primary AI Agent, Secondary AI Agent, Research Agent

### Next Steps (8)
1. ✅ Complete project requirements documentation (4 subtasks - DONE)
2. ✅ Set up development environment (3 subtasks - DONE)
3. ⏳ Implement core backend API (5 subtasks - 2/5 done)
4. ⏳ Design frontend UI (4 subtasks - 0/4 done)
5. ⏳ Integration testing (4 subtasks - 0/4 done)
6. ⏳ Documentation prep (4 subtasks - 0/4 done)
7. ⏳ Production deployment (3 subtasks - 0/3 done)
8. ⏳ Post-launch optimization (3 subtasks - 0/3 done)

### Checklist Items (5)
1. ✅ Code review completed (3 subtasks - ALL done)
2. ✅ All tests passing (3 subtasks - ALL done)
3. ⏳ Documentation up to date (3 subtasks - 1/3 done)
4. ⏳ Performance benchmarks met (3 subtasks - 1/3 done)
5. ⏳ Security requirements satisfied (4 subtasks - 2/4 done)

### External Links (5)
- Project Requirements Document (Google Docs)
- Design Mockups (Figma)
- Project Timeline (Google Sheets)
- GitHub Repository
- API Documentation

### Internal Documents (3)
- **Technical Architecture Document** (Rich Text)
- **API Endpoints Specification** (Spreadsheet with 5 endpoints)
- **Meeting Notes - Sprint Planning** (Rich Text)

### Activity Log (10 entries)
- Timestamped entries from 7 days ago to 2 hours ago
- Shows progression: creation → requirements → design → development → testing

## Database Location

**Target:** `data/synergy_sessions.db`

**Tables:**
- `synergy_sessions` - Main session data
- `synergy_internal_docs` - Internal documents

## Use Cases

1. **Reference:** See how to structure complex projects
2. **Testing:** Test UI with realistic data
3. **Demo:** Show clients all synergy features
4. **Template:** Copy structure for new projects
5. **Development:** Test new features with rich data

## Cleanup

To remove the example:

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python -c "import sqlite3; conn = sqlite3.connect('data/synergy_sessions.db'); cursor = conn.cursor(); cursor.execute('DELETE FROM synergy_sessions WHERE session_id = \"sess_comprehensive_example_2025\"'); cursor.execute('DELETE FROM synergy_internal_docs WHERE session_id = \"sess_comprehensive_example_2025\"'); conn.commit(); print('Example removed')"
```

## Troubleshooting

### Error: "no such table: synergy_sessions"
**Solution:** The synergy database hasn't been initialized. Start the Flask app first:
```powershell
BISTART
```
Then run the script.

### Error: Database locked
**Solution:** Close any open connections to synergy_sessions.db and try again.

### Can't see the card in UI
**Solution:** 
1. Refresh your browser (Ctrl+F5)
2. Click the synergy toggle button on the LEFT side
3. Check that the card appears in the "In Progress" column

## Notes

- Script is idempotent (safe to run multiple times)
- Uses `INSERT OR REPLACE` to prevent duplicates
- All timestamps are ISO format
- JSON fields properly serialized
- Foreign key constraints respected

## Related Files

- `create_comprehensive_synergy_example.py` - This script (432 lines)
- `SYNERGY_SIDEBAR_AND_EXAMPLE_COMPLETE.md` - Full documentation
- `UI/business-ai-platform-v2.html` - Main UI file
- `AI_infrastructure/routes/synergy_routes.py` - API endpoints

---

**Created:** December 2024  
**Status:** Production Ready  
**Purpose:** Demo Data Creation
