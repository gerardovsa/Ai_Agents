# SYNERGY TITLE + DESCRIPTION - QUICK START

**Status:** ✅ READY FOR DEPLOYMENT  
**Date:** December 11, 2025

---

## 🚀 DEPLOY IN 3 STEPS

### Step 1: Run Database Migration (5 min)
```bash
# Connect to Supabase
psql -h your-supabase-host -U postgres -d postgres

# Run migration
\i data/synergy_title_description_migration.sql

# Verify
SELECT COUNT(*) FROM synergy_sessions.milestones WHERE title IS NOT NULL;
```

### Step 2: Deploy Code (Auto - 2 min)
```bash
git add .
git commit -m "Add title+description support to Synergy"
git push origin main

# Render.com will auto-deploy from render.yaml
# Wait for build to complete (~2 minutes)
```

### Step 3: Test (5 min)
```python
# Quick smoke test
from tools.implementations.synergy import synergy_create_milestone

result = synergy_create_milestone(
    session_id="your_session_id",
    title="Test Milestone",
    description="Testing new title+description fields",
    tasks=[
        {
            "title": "Test Task",
            "description": "Task description here",
            "subtasks": [
                {
                    "title": "Test Subtask",
                    "description": "Subtask description"
                }
            ]
        }
    ]
)

print(f"✅ Success: {result['success']}")
print(f"📋 Milestone ID: {result['milestone_id']}")
```

---

## 📋 WHAT CHANGED

### NEW FORMAT (Use This):
```python
# ✅ RECOMMENDED: Use title + description
synergy_create_milestone(
    session_id="sess_123",
    title="Database Setup",  # Short name
    description="Set up PostgreSQL with initial schema",  # Full details
    tasks=[...]
)

synergy_create_task(
    milestone_id="ms_123",
    title="Configure backups",
    description="Set up daily S3 backups with monitoring",
    due_date="2025-12-20",
    subtasks=[...]
)

synergy_create_subtask(
    task_id="task_123",
    title="Test restore",
    description="Verify backup integrity with test restore",
    due_date="2025-12-18"
)
```

### OLD FORMAT (Still Works):
```python
# ⚠️ DEPRECATED: Old format still works for backward compatibility
synergy_create_milestone(
    session_id="sess_123",
    milestone_name="Database Setup",  # Old param name
    tasks=[...]
)

synergy_create_task(
    milestone_id="ms_123",
    task="Configure backups",  # Old param name
    subtasks=[...]
)
```

---

## ✨ NEW FEATURES

### All Levels Support:
- ✅ **Title**: Short name (required)
- ✅ **Description**: Full context (optional)
- ✅ **Due Date**: YYYY-MM-DD format
- ✅ **Priority**: low|medium|high|critical
- ✅ **Assigned To**: Person/team name
- ✅ **Checkbox**: Completed status

### Example with All Fields:
```python
{
    "title": "Deploy to production",
    "description": "Deploy all components with zero downtime\n\nAcceptance criteria:\n- All tests pass\n- Monitoring enabled\n- Rollback plan ready",
    "due_date": "2025-12-25",
    "priority": "critical",
    "assigned_to": "Platform Team",
    "estimated_hours": 8
}
```

---

## 📁 FILES CHANGED

1. ✅ **Database Schema**: `data/synergy_title_description_migration.sql` (NEW)
2. ✅ **Backend Routes**: `AI_infrastructure/routes/synergy_routes.py` (3 endpoints)
3. ✅ **Tool Implementation**: `tools/implementations/synergy.py` (3 functions)
4. ✅ **Tool Schemas**: `tools/schemas/synergy_tools.json` (3 definitions)
5. ✅ **Documentation**: `SYNERGY_TITLE_DESCRIPTION_ENHANCEMENT.md` (Complete guide)

---

## 🧪 QUICK TEST CHECKLIST

- [ ] Database migration completed successfully
- [ ] Backend deployment successful (check Render logs)
- [ ] Create milestone with new format works
- [ ] Create task with description works
- [ ] Create subtask with due_date works
- [ ] Old format (milestone_name) still works
- [ ] Dashboard displays title+description correctly

---

## 🔧 TROUBLESHOOTING

### Migration Fails?
```sql
-- Check if columns already exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name IN ('milestones', 'tasks', 'subtasks')
  AND column_name = 'title';

-- If exists, migration already ran
```

### Backend Errors?
```bash
# Check Render logs
render logs --tail 100

# Look for:
# - "column 'title' does not exist" → Run migration
# - "KeyError: 'title'" → Update tool code
```

### Tool Not Working?
```python
# Verify tool is loaded
from tools.implementations.synergy import synergy_create_milestone
import inspect

sig = inspect.signature(synergy_create_milestone)
print(sig.parameters.keys())
# Should include 'title' parameter
```

---

## 📞 SUPPORT

**Issue:** Database migration fails  
**Fix:** Check Supabase connection and run migration manually

**Issue:** Backend doesn't accept title field  
**Fix:** Verify code deployed - check git commit hash in Render

**Issue:** Old code breaks  
**Fix:** Shouldn't happen - backward compatible. Check error logs.

---

## ✅ SUCCESS CRITERIA

You're done when:
1. ✅ Migration shows all tables have `title` column
2. ✅ Backend accepts both `title` and legacy fields
3. ✅ New milestone creation works with title+description
4. ✅ Old code still works (backward compatible)
5. ✅ Dashboard shows title prominently with expandable description

---

**Ready to deploy!** Run Step 1 → Step 2 → Step 3 above.

Full documentation: `SYNERGY_TITLE_DESCRIPTION_ENHANCEMENT.md`
