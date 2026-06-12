# ✅ Supabase Migration Checklist

Use this checklist to track your progress through the migration.

## Prerequisites
- [ ] AI Agent backend is running locally (BISTART)
- [ ] You have access to Render dashboard
- [ ] You have access to create Supabase account
- [ ] Git repository is clean (no uncommitted changes)

---

## Phase 1: Supabase Setup (10 minutes)

### Create Supabase Project
- [ ] Go to https://supabase.com/dashboard
- [ ] Sign up / Log in
- [ ] Click "New Project"
- [ ] Fill in details:
  - [ ] Organization: (create new or use existing)
  - [ ] Project name: `ai-agents-production`
  - [ ] Database password: (generate and save securely)
  - [ ] Region: **Singapore** (Southeast Asia)
  - [ ] Plan: **Free** (500MB database)
- [ ] Click "Create new project" (wait 2-3 minutes)

### Get Credentials
- [ ] Go to Settings → Database
- [ ] Copy and save these 3 items:
  - [ ] **Project URL**: `https://xxxxx.supabase.co`
  - [ ] **Anon Key**: `eyJhbGci...` (long JWT token)
  - [ ] **Connection String**: `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

**💡 TIP:** Save these in a text file - you'll use them multiple times!

---

## Phase 2: Install Dependencies (2 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents
pip install psycopg2-binary
```

- [ ] psycopg2-binary installed successfully
- [ ] No error messages

---

## Phase 3: Run Migration (15 minutes)

### Backup Current Databases (Safety First!)
```powershell
cd data
cp ai_infrastructure.db ai_infrastructure.db.backup
cp sessions.db sessions.db.backup
cp synergy_sessions.db synergy_sessions.db.backup
cp kanban_analytics.db kanban_analytics.db.backup
cp stock_data.db stock_data.db.backup
```

- [ ] All database files backed up

### Run Migration Script
```powershell
cd ..\supabase_migration
python migrate_to_supabase.py
```

- [ ] Script started successfully
- [ ] Entered Supabase Project URL
- [ ] Entered Supabase Anon Key
- [ ] Entered Supabase Database URL (connection string)
- [ ] Connection to PostgreSQL successful
- [ ] Phase 1: Analysis completed (shows tables and row counts)
- [ ] Typed "yes" to confirm migration
- [ ] Phase 2: Schema creation completed (all tables created)
- [ ] Phase 3: Data migration completed (all rows migrated)
- [ ] Phase 4: Verification completed (all counts match)
- [ ] Migration completed successfully

**Expected Output:**
```
✓ All data migrated and verified successfully!

Migrated: 28 tables, 5,678 rows
```

---

## Phase 4: Verify in Supabase Dashboard (5 minutes)

### Check Tables
- [ ] Go to Supabase Dashboard → Table Editor
- [ ] See schemas in left sidebar:
  - [ ] `ai_infrastructure` (users, credentials, OAuth tokens)
  - [ ] `sessions` (Flask sessions)
  - [ ] `synergy_sessions` (Synergy data)
  - [ ] `kanban_analytics` (Analytics)
  - [ ] `stock_data` (Stock management)

### Run Test Queries
Go to SQL Editor and run:

```sql
-- Check user count
SELECT COUNT(*) FROM ai_infrastructure.users;
```
- [ ] Query executed successfully
- [ ] Shows expected number of users

```sql
-- Check credentials
SELECT user_id, platform, updated_at 
FROM ai_infrastructure.user_platform_credentials 
ORDER BY updated_at DESC 
LIMIT 5;
```
- [ ] Query executed successfully
- [ ] Shows your platform credentials

---

## Phase 5: Update Application (10 minutes)

### Update Config
```powershell
cd C:\Users\gpoli\GIT\AI_agents\supabase_migration
python update_config_for_supabase.py
```

- [ ] Script ran successfully
- [ ] Backup created (config.py.backup)
- [ ] Config.py updated with Supabase support

**Or manually update** `AI_infrastructure/config.py`:
- [ ] Added Supabase configuration code
- [ ] Added USE_SUPABASE environment check
- [ ] Maintained SQLite support for local dev

### Add Environment Variables to Render
```powershell
cd ..\Render_backend
python add_supabase_env_vars.py
```

- [ ] Entered Supabase Project URL
- [ ] Entered Supabase Anon Key  
- [ ] Entered Supabase Database URL
- [ ] Script completed successfully
- [ ] All 4 variables added:
  - [ ] `USE_SUPABASE=true`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `SUPABASE_DB_URL`

---

## Phase 6: Update Deployment Files (5 minutes)

### Update render.yaml
```powershell
cd ..
code render.yaml
```

Remove persistent disk section:
- [ ] Removed `disk:` configuration block
- [ ] Removed `mountPath: /data`
- [ ] Removed `sizeGB: 10`
- [ ] Saved file

### Update Dockerfile
```powershell
code Dockerfile
```

Simplify to:
- [ ] Removed `/data` directory creation
- [ ] Removed database file copying (RUN commands)
- [ ] Removed startup.sh references
- [ ] Changed CMD to: `CMD ["python", "AI_infrastructure/flask_app.py"]`
- [ ] Saved file

### Update .gitignore
```powershell
code .gitignore
```

- [ ] Added `data/*.db` (SQLite databases)
- [ ] Added `data/*.db-shm` (SQLite shared memory)
- [ ] Added `data/*.db-wal` (SQLite write-ahead log)
- [ ] Saved file

---

## Phase 7: Commit and Deploy (10 minutes)

### Remove Database Files from Git
```powershell
git rm --cached data/*.db
git rm --cached data/database-config.json
```

- [ ] Database files removed from tracking
- [ ] No errors

### Commit Changes
```powershell
git add .
git status
```

**Review changes:**
- [ ] Modified: render.yaml (disk removed)
- [ ] Modified: Dockerfile (simplified)
- [ ] Modified: .gitignore (databases excluded)
- [ ] Modified: AI_infrastructure/config.py (Supabase support)
- [ ] Deleted: data/*.db (from tracking)

```powershell
git commit -m "Migrate to Supabase PostgreSQL - remove SQLite dependencies"
```

- [ ] Commit created successfully

### Push and Deploy
```powershell
git push origin v3
```

- [ ] Push successful
- [ ] Render deployment triggered

### Monitor Deployment
```powershell
cd Render_backend
python render_toolkit.py monitor
```

**Watch for:**
- [ ] Build started
- [ ] Build completed (no database file errors)
- [ ] Deployment started
- [ ] Deployment completed
- [ ] Service live
- [ ] Health check passed

**Expected final status:**
```
Service Status: [ACTIVE] not_suspended
Latest Deploy:  [SUCCESS] live
Health Status:  [HEALTHY]
```

---

## Phase 8: Test and Verify (10 minutes)

### Check Service Health
```powershell
python render_toolkit.py health
```

- [ ] Service is healthy
- [ ] Returns 200 OK
- [ ] No connection errors

### Test Application
- [ ] Open: https://ai-agents-backend-singapore.onrender.com/health
- [ ] Returns: `{"status": "ok"}`
- [ ] No errors in browser console

### Run Test Conversation
```powershell
cd ..
CHAT "test connection to database"
```

- [ ] AI responds successfully
- [ ] No database connection errors
- [ ] Response shows Supabase connection

### Check Logs in Supabase
- [ ] Go to Supabase Dashboard → Logs
- [ ] See connection logs
- [ ] See query logs
- [ ] No errors

---

## Phase 9: Cleanup (5 minutes)

### Remove Old Render Disk (Optional - Save $2.50/month)
- [ ] Go to Render Dashboard
- [ ] Navigate to service settings
- [ ] Find disk section
- [ ] Delete `ai-agents-data` disk
- [ ] Confirm deletion

**⚠️ WARNING:** Only do this AFTER confirming Supabase works!

### Local Cleanup
```powershell
cd C:\Users\gpoli\GIT\AI_agents\data
```

Keep backups, optionally remove originals:
- [ ] Verified Supabase has all data
- [ ] Optionally removed `.db` files (kept `.backup` files)

---

## 🎉 Success Criteria

### Deployment
- ✅ Render deployment succeeded
- ✅ No build errors
- ✅ Service is live and healthy
- ✅ Health endpoint returns 200 OK

### Database
- ✅ All tables visible in Supabase dashboard
- ✅ Row counts match original SQLite databases
- ✅ Can run queries in SQL Editor
- ✅ Application connects successfully

### Application
- ✅ AI agent responds to queries
- ✅ No database connection errors
- ✅ OAuth credentials work
- ✅ Sessions persist correctly

### Cost
- ✅ Render plan: $7/month (was $9.50 with disk)
- ✅ Supabase: $0/month (Free tier)
- ✅ **Total: $7/month** (saved $2.50/month)

---

## 📊 Migration Statistics

Track your migration:

| Metric | Count |
|--------|-------|
| Databases migrated | ___ / 5 |
| Tables migrated | ___ / 28 |
| Rows migrated | ___ |
| Migration time | ___ minutes |
| Deployment time | ___ minutes |
| Total time | ___ minutes |

---

## 🆘 Troubleshooting

### If Migration Fails
- [ ] Check Supabase credentials are correct
- [ ] Verify network connectivity
- [ ] Check firewall allows port 5432
- [ ] Review error messages in console
- [ ] See SUPABASE_SETUP_GUIDE.md troubleshooting section

### If Deployment Fails
- [ ] Check environment variables in Render: `python render_toolkit.py env`
- [ ] Verify Dockerfile changes saved
- [ ] Clear build cache in Render dashboard
- [ ] Check logs: `python render_toolkit.py monitor`

### If Application Can't Connect
- [ ] Verify `USE_SUPABASE=true` in Render env vars
- [ ] Check Supabase database URL is correct
- [ ] Test connection manually with psycopg2
- [ ] Check Supabase dashboard for connection logs

---

## 📚 Resources

- **Complete Guide**: `SUPABASE_SETUP_GUIDE.md`
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Render Dashboard**: https://dashboard.render.com
- **Toolkit Commands**: `python render_toolkit.py --help`

---

## ✅ Final Checklist

- [ ] Migration completed successfully
- [ ] All data verified in Supabase
- [ ] Application deployed to Render
- [ ] Service is healthy and responsive
- [ ] Tests passing
- [ ] Old persistent disk removed (optional)
- [ ] Documentation updated
- [ ] Team notified of migration

**🎊 CONGRATULATIONS! You've successfully migrated to Supabase!**

---

**Created:** November 9, 2025  
**Last Updated:** November 9, 2025  
**Status:** Ready to use
