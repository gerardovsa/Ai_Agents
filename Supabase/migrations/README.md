# Supabase Migration System

**Purpose:** Track and apply database schema changes to Supabase (PostgreSQL)

---

## 📁 Migration File Structure

```
Supabase/migrations/
├── README.md (this file)
├── 001_baseline_schema.sql         ← Current schema (Nov 2025)
├── 002_add_thread_sharing.sql      ← Already applied
├── 003_future_feature.sql          ← Template for new changes
└── migration_log.md                ← Change history
```

---

## 🚀 How to Use

### Creating a New Migration

1. **Copy the template:**
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents\Supabase\migrations
   Copy-Item 000_migration_template.sql 004_my_new_feature.sql
   ```

2. **Edit the migration:**
   - Add your SQL changes (CREATE TABLE, ALTER TABLE, etc.)
   - Document what and why you're changing
   - Include both UP (apply) and DOWN (rollback) sections

3. **Test locally first:**
   ```powershell
   # Test on local SQLite first
   sqlite3 data/sessions.db < migrations/004_my_new_feature.sql
   ```

4. **Apply to Supabase:**
   ```powershell
   python apply_migration.py 004_my_new_feature.sql
   ```

---

## 📋 Migration Naming Convention

```
[NUMBER]_[DESCRIPTION].sql

Examples:
001_baseline_schema.sql           # Initial schema
002_add_thread_sharing.sql        # Thread sharing feature
003_add_workspaces.sql            # Workspace system
004_optimize_indexes.sql          # Performance improvements
005_add_user_preferences.sql      # User settings
```

**Rules:**
- ✅ Number sequentially (001, 002, 003...)
- ✅ Use descriptive names (what it does)
- ✅ Use underscores for spaces
- ✅ Keep it short and clear

---

## 🔄 Migration Workflow

### Local Development → Supabase

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Develop Locally (SQLite)                       │
├─────────────────────────────────────────────────────────┤
│ 1. Test changes on local SQLite database               │
│ 2. Verify everything works                             │
│ 3. Write migration SQL file                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Create Migration File                          │
├─────────────────────────────────────────────────────────┤
│ 1. Copy template: 000_migration_template.sql           │
│ 2. Name: 004_my_feature.sql                            │
│ 3. Add SQL commands                                     │
│ 4. Document changes                                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Apply to Supabase                              │
├─────────────────────────────────────────────────────────┤
│ python apply_migration.py 004_my_feature.sql           │
│                                                         │
│ ✓ Connects to Supabase                                 │
│ ✓ Executes SQL                                          │
│ ✓ Records in migration_history table                   │
│ ✓ Updates migration_log.md                             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Commit to Git                                  │
├─────────────────────────────────────────────────────────┤
│ git add Supabase/migrations/004_my_feature.sql         │
│ git commit -m "Add: My new feature migration"          │
│ git push                                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Migration Template

See `000_migration_template.sql` for the standard template.

**Key sections:**
1. **Header** - What, why, when, who
2. **UP** - Commands to apply the change
3. **DOWN** - Commands to rollback the change
4. **Verification** - How to test it worked

---

## 📊 Migration History Tracking

Every migration is recorded in two places:

### 1. Database Table: `migration_history`
```sql
SELECT * FROM migration_history ORDER BY applied_at DESC;
```

**Shows:**
- Migration number
- Description
- Applied timestamp
- Applied by (user)
- Status (success/failed)

### 2. File: `migration_log.md`
```markdown
## Migration 004 - My New Feature
- **Date:** 2025-11-10
- **Author:** Developer Name
- **Status:** Applied ✅
- **Changes:** Added new table for feature X
```

---

## ⚠️ Important Rules

### DO ✅
- ✅ Test on local SQLite first
- ✅ Write both UP and DOWN migrations
- ✅ Number migrations sequentially
- ✅ Document what and why
- ✅ Commit migrations to Git
- ✅ Run migrations one at a time
- ✅ Backup before major changes

### DON'T ❌
- ❌ Skip migration numbers (001, 002, 004 ← missing 003!)
- ❌ Edit old migrations (create new one instead)
- ❌ Apply migrations directly in Supabase UI (use script)
- ❌ Test on production first (local → supabase)
- ❌ Forget to commit migration files

---

## 🔧 Common Migration Types

### Add New Table
```sql
-- UP
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DOWN
DROP TABLE IF EXISTS new_table;
```

### Add Column
```sql
-- UP
ALTER TABLE threads 
ADD COLUMN IF NOT EXISTS new_field TEXT;

-- DOWN
ALTER TABLE threads 
DROP COLUMN IF EXISTS new_field;
```

### Create Index
```sql
-- UP
CREATE INDEX IF NOT EXISTS idx_threads_user 
ON threads(user_id);

-- DOWN
DROP INDEX IF EXISTS idx_threads_user;
```

### Modify Column
```sql
-- UP
ALTER TABLE threads 
ALTER COLUMN title SET DEFAULT 'New Default';

-- DOWN
ALTER TABLE threads 
ALTER COLUMN title SET DEFAULT 'Untitled Thread';
```

---

## 🚨 Rollback Procedure

If a migration breaks something:

1. **Check migration history:**
   ```sql
   SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;
   ```

2. **Run the DOWN section:**
   ```powershell
   python rollback_migration.py 004_my_feature.sql
   ```

3. **Verify rollback:**
   ```powershell
   python Supabase/supabase_toolkit.py summary
   ```

4. **Fix the migration file**

5. **Re-apply:**
   ```powershell
   python apply_migration.py 004_my_feature_fixed.sql
   ```

---

## 📚 Tools

### apply_migration.py
```powershell
# Apply a migration to Supabase
python Supabase/apply_migration.py migrations/004_my_feature.sql
```

### rollback_migration.py
```powershell
# Rollback a migration from Supabase
python Supabase/rollback_migration.py migrations/004_my_feature.sql
```

### show_migrations.py
```powershell
# Show all applied migrations
python Supabase/show_migrations.py
```

---

## 🎯 Quick Commands

```powershell
# Show current schema
python Supabase/supabase_toolkit.py summary

# Test connection
python Supabase/supabase_toolkit.py test

# Show migration history
python Supabase/show_migrations.py

# Apply new migration
python Supabase/apply_migration.py migrations/004_my_feature.sql

# Rollback migration
python Supabase/rollback_migration.py migrations/004_my_feature.sql
```

---

## 📝 Example: Adding a Feature

**Scenario:** Add "favorites" feature to threads

**Step 1: Create migration file**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\Supabase\migrations
Copy-Item 000_migration_template.sql 005_add_thread_favorites.sql
```

**Step 2: Edit `005_add_thread_favorites.sql`**
```sql
-- Migration: Add Thread Favorites Feature
-- Date: 2025-11-10
-- Author: You

-- UP (Apply changes)
CREATE TABLE IF NOT EXISTS thread_favorites (
    id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(thread_id, user_id)
);

CREATE INDEX idx_favorites_user ON thread_favorites(user_id);
CREATE INDEX idx_favorites_thread ON thread_favorites(thread_id);

-- DOWN (Rollback)
DROP TABLE IF EXISTS thread_favorites;
```

**Step 3: Apply to Supabase**
```powershell
python Supabase/apply_migration.py migrations/005_add_thread_favorites.sql
```

**Step 4: Commit to Git**
```powershell
git add Supabase/migrations/005_add_thread_favorites.sql
git commit -m "Add: Thread favorites migration"
git push
```

---

## 🔍 Troubleshooting

### Error: "Migration already applied"
```
Solution: Check migration_history table, migration already exists
```

### Error: "Connection failed"
```
Solution: Check SUPABASE_URL in .env.master
```

### Error: "Permission denied"
```
Solution: Use SUPABASE_SERVICE_ROLE_SECRET (not anon key)
```

### Migration partially applied
```
Solution: Wrap in transaction:
BEGIN;
-- Your migration here
COMMIT;
```

---

## 📖 Further Reading

- [Supabase Migrations Docs](https://supabase.com/docs/guides/database/migrations)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [Migration Best Practices](https://www.postgresql.org/docs/current/ddl-basics.html)

---

**Last Updated:** November 10, 2025  
**Status:** Ready for use ✅  
**Your Supabase:** ryoicrdifiqhqpsnjmdo.supabase.co
