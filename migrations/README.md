# Database Migrations - November 19, 2025

## Overview

This folder contains SQL migration scripts for deploying the thread isolation fixes and automation workflow integration to Supabase PostgreSQL.

## Files

### 1. `supabase_production_migration_nov19_2025.sql` ⭐ MAIN MIGRATION
**Purpose:** Deploy all database changes to production  
**Status:** Ready to run  
**Safety:** Includes `IF NOT EXISTS` clauses - safe to run multiple times  

**Changes:**
- ✅ Add `automation_slug` and `automation_title` columns
- ✅ Add `internal_doc_slug` and `internal_doc_title` columns  
- ✅ Create 6 performance indexes
- ✅ Add 4 data validation constraints
- ✅ Add column documentation comments
- ✅ Verify migration success

**Estimated Time:** ~30 seconds  
**Downtime Required:** None (online migration)

---

### 2. `verify_migration_nov19_2025.sql` 🔍 VERIFICATION
**Purpose:** Verify migration was successful  
**Run After:** Main migration script  

**Tests:**
1. ✅ Column existence (4 columns)
2. ✅ Index existence (6 indexes)  
3. ✅ Constraint existence (4 constraints)
4. ✅ Column comments (documentation)
5. ✅ Data integrity (no empty thread_slugs)
6. ✅ Performance metrics (index usage stats)

**Output:** Detailed pass/fail report

---

### 3. `rollback_nov19_2025.sql` ⚠️ EMERGENCY ROLLBACK
**Purpose:** Revert changes if issues occur  
**WARNING:** Will delete data in new columns!

**Use Only If:**
- Migration causes production errors
- Need to quickly restore previous state
- Issues found during deployment

**Before Running:** Backup database!

---

## Deployment Instructions

### Prerequisites

1. ✅ Supabase project access
2. ✅ PostgreSQL client (`psql`) or Supabase SQL Editor
3. ✅ Backup of sessions schema (recommended)
4. ✅ Backend code changes deployed (agent_routes_v4.py)

---

### Option A: Supabase Dashboard (Recommended)

**Step 1: Open SQL Editor**
1. Go to https://supabase.com
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "New query"

**Step 2: Run Migration**
1. Copy contents of `supabase_production_migration_nov19_2025.sql`
2. Paste into SQL editor
3. Click "Run" button
4. Wait for "Success" message (~30 seconds)

**Step 3: Verify Migration**
1. Click "New query"
2. Copy contents of `verify_migration_nov19_2025.sql`
3. Paste into SQL editor  
4. Click "Run" button
5. Check output - should see "✅ ALL TESTS PASSED"

**Step 4: Done!**
- Migration complete
- No restart required
- Changes active immediately

---

### Option B: psql Command Line

**Step 1: Connect to Supabase**
```bash
# Get connection string from Supabase dashboard (Settings > Database)
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"
```

**Step 2: Run Migration**
```sql
-- Run from psql prompt
\i migrations/supabase_production_migration_nov19_2025.sql
```

**Step 3: Verify**
```sql
\i migrations/verify_migration_nov19_2025.sql
```

**Step 4: Exit**
```sql
\q
```

---

## What Gets Changed

### New Columns Added

| Column | Type | Nullable | Default | Purpose |
|--------|------|----------|---------|---------|
| `automation_slug` | TEXT | YES | NULL | Links to published automation workflow |
| `automation_title` | TEXT | YES | NULL | Display name for automation (blue pill) |
| `internal_doc_slug` | TEXT | YES | NULL | Links to internal documentation |
| `internal_doc_title` | TEXT | YES | NULL | Display name for doc |

### Indexes Created

1. `idx_threads_automation_slug` - Fast automation lookups
2. `idx_threads_workflow_slug` - Fast workflow lookups
3. `idx_threads_internal_doc_slug` - Fast doc lookups
4. `idx_threads_synergy_card_id` - Fast synergy lookups
5. `idx_threads_user_thread` - User + thread composite
6. `idx_threads_thread_slug` - Thread isolation critical

### Constraints Added

1. `chk_thread_slug_not_empty` - Prevents empty thread_slugs
2. `chk_location_valid` - Enforces valid agent locations
3. `chk_workflow_slug_format` - Validates workflow-{id} format
4. `chk_automation_slug_format` - Validates automation-{id} format

---

## Post-Migration Checklist

After running migration, verify:

- [ ] All verification tests passed (run verify script)
- [ ] No production errors in logs
- [ ] Thread creation still works
- [ ] Messages send successfully
- [ ] Agent responses display correctly
- [ ] No cross-contamination between agents
- [ ] Workflow/automation pills display (if linked)

---

## Troubleshooting

### Issue: "relation does not exist"
**Cause:** Wrong schema name  
**Fix:** Ensure using `sessions.threads` not just `threads`

### Issue: "column already exists"
**Cause:** Migration run twice (not a problem!)  
**Fix:** Script uses `IF NOT EXISTS` - ignore message and continue

### Issue: "constraint already exists"
**Cause:** Migration run twice (not a problem!)  
**Fix:** Script uses `IF EXISTS` when dropping - safe to continue

### Issue: Migration takes too long
**Cause:** Large table size  
**Fix:** Run during low-traffic period, or contact Supabase support

---

## Rollback Procedure

**Only if critical issues occur!**

**Step 1: Backup First**
```sql
-- Export threads table
COPY sessions.threads TO '/tmp/threads_backup.csv' CSV HEADER;
```

**Step 2: Run Rollback**
```sql
\i migrations/rollback_nov19_2025.sql
```

**Step 3: Verify Rollback**
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'sessions' 
  AND table_name = 'threads'
  AND column_name IN ('automation_slug', 'automation_title');
-- Should return 0 rows
```

**Step 4: Restore Backend**
- Revert `agent_routes_v4.py` to previous version
- Restart Flask

---

## Performance Impact

### Before Migration
- Table size: ~X MB
- Index count: Y indexes
- Constraint count: Z constraints

### After Migration
- Table size: ~X MB (no data change)
- Index count: Y + 6 indexes
- Constraint count: Z + 4 constraints
- Query performance: **Improved** (new indexes)
- Insert performance: **Minimal impact** (<5ms)

### Index Storage Cost
- ~10-50 KB per index (depends on data)
- Total: ~60-300 KB for 6 indexes
- **Negligible** compared to performance gains

---

## Related Documentation

- `ALL_FIXES_COMPLETE_NOV19.md` - Complete fix documentation
- `THREAD_ISOLATION_FIX_COMPLETE_NOV19.md` - Thread isolation details
- `NAMEERROR_FIX_SUCCESS_NOV19.md` - NameError fix verification

---

## Support

**Issues?** Check:
1. Supabase logs (Dashboard > Logs)
2. Flask backend logs
3. Browser console (frontend errors)
4. Test scripts: `python test_complete_flow.py`

**Contact:** AI Agents Team  
**Created:** November 19, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
