# 🚀 Supabase Migration - Complete Guide

**Date:** November 15, 2025  
**Estimated Time:** 30 minutes  
**Database Size:** ~10-50MB (all databases combined)

---

## 📋 Prerequisites

- Supabase account (free): https://supabase.com
- Python 3.8+ with pip
- Local databases in `data/` folder
- Render deployment configured

---

## Step 1: Create Supabase Project (5 minutes)

### 1.1 Sign up / Log in
- Go to: https://supabase.com/dashboard
- Click "New Project"

### 1.2 Project Configuration
```
Project Name: ai-agents-production
Database Password: [GENERATE STRONG PASSWORD - SAVE THIS!]
Region: Singapore (ap-southeast-1)  ← Closest to Render Singapore
Pricing Plan: Free ($0/month)
  - 500MB Database
  - 8GB Storage  
  - 2GB Bandwidth/day
  - 50,000 Monthly Active Users
```

### 1.3 Wait for Provisioning
- Takes 2-3 minutes
- Don't close the browser tab

### 1.4 Get Your Credentials

**A. API Credentials**  
Dashboard → Project Settings → API

```bash
# Copy these values:
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (very long)
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  (very long, KEEP SECRET)
```

**B. Database Connection String**  
Dashboard → Project Settings → Database → Connection String → URI

```bash
# Should look like:
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres

# Replace [YOUR-PASSWORD] with the password from step 1.2
```

---

## Step 2: Install Dependencies (2 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Install required packages
pip install psycopg2-binary supabase-py python-dotenv

# Verify installation
python -c "import psycopg2, supabase; print('Dependencies OK')"
```

---

## Step 3: Configure Environment Variables (3 minutes)

### 3.1 Create `.env` file (if it doesn't exist)

```powershell
# Create .env in AI_agents root
New-Item -Path ".env" -ItemType File -Force
```

### 3.2 Add Supabase credentials to `.env`

Open `.env` and add:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-anon-key...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-service-key...
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
USE_SUPABASE=true

# Legacy SQLite (keep as backup)
USE_SQLITE=false
```

**⚠️ IMPORTANT:** Replace:
- `xxxxxxxxxxxxx` with your project ID
- `YOUR_PASSWORD` with your database password
- Full anon key and service key

---

## Step 4: Test Connection (2 minutes)

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Test Supabase connectivity
python Supabase/test_supabase_connection.py
```

**Expected output:**
```
Testing Supabase Connection

Step 1: Checking environment variables...
 SUPABASE_URL: https://xxxxx.supabase.co
 SUPABASE_KEY: eyJhbGciOiJIUzI1NiIs...

Step 2: Initializing Supabase client...
 Client initialized successfully

Step 3: Testing connectivity...
 Connected to Supabase PostgreSQL
 Database version: PostgreSQL 15.x

SUCCESS! Connection working correctly
```

**If it fails:**
- Check `.env` file has correct credentials
- Verify no typos in connection string
- Confirm Supabase project is fully provisioned

---

## Step 5: Run Migration (15 minutes)

### 5.1 Start Migration

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Run migration script
python Supabase/migrate_to_supabase.py
```

### 5.2 Migration Process

The script will:
1. Connect to Supabase PostgreSQL
2. Analyze local SQLite databases
3. Create tables with PostgreSQL-compatible schema
4. Migrate data in batches (1000 rows at a time)
5. Verify data integrity

**Databases migrated:**
- ✅ `ai_infrastructure.db` → users, OAuth tokens, platform credentials
- ✅ `sessions.db` → threads, messages, saved threads
- ✅ `synergy_sessions.db` → synergy projects, internal docs
- ✅ `kanban_analytics.db` → kanban analytics data
- ✅ `stock_data.db` → InHousePrint inventory

### 5.3 Monitor Progress

```
========================================
SUPABASE MIGRATION TOOL
========================================

[1/5] Migrating ai_infrastructure.db...
  Table: users (3 rows)
   100% |████████████████████| 3/3 rows migrated
  Table: user_platform_credentials (12 rows)
   100% |████████████████████| 12/12 rows migrated
  
[2/5] Migrating sessions.db...
  Table: threads (82 rows)
   100% |████████████████████| 82/82 rows migrated
  Table: messages (219 rows)
   100% |████████████████████| 219/219 rows migrated

[3/5] Migrating synergy_sessions.db...
  Table: synergy_sessions (5 rows)
   100% |████████████████████| 5/5 rows migrated
  Table: synergy_internal_docs (12 rows)
   100% |████████████████████| 12/12 rows migrated

[4/5] Migrating kanban_analytics.db...
  Skipped (no tables found)

[5/5] Migrating stock_data.db...
  Table: stock_levels (1,245 rows)
   100% |████████████████████| 1245/1245 rows migrated

========================================
MIGRATION COMPLETE!
========================================

Total tables migrated: 15
Total rows migrated: 1,582
Time elapsed: 8 minutes 34 seconds

Databases backed up to: data/backups/2025-11-15_173045/
```

### 5.4 Verify in Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Click your project → "Table Editor"
3. Verify tables exist:
   - `users` (should have 3 rows)
   - `threads` (should have 82 rows)
   - `synergy_sessions` (should have your projects)
   - `stock_levels` (should have inventory data)

---

## Step 6: Update Render Environment (5 minutes)

### 6.1 Add Environment Variables to Render

1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add these variables:

```bash
SUPABASE_URL = https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_URL = postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
USE_SUPABASE = true
```

### 6.2 Save and Deploy

1. Click **"Save Changes"**
2. Render will automatically redeploy (2-3 minutes)
3. Monitor deploy logs for errors

---

## Step 7: Verify Deployment (3 minutes)

### 7.1 Test Backend

```powershell
# Test health endpoint
curl https://ai-agents-backend-singapore.onrender.com/

# Expected response:
{
  "status": "healthy",
  "app": "new_flask_app",
  "database": "supabase",
  "providers": ["anthropic", "openai", "deepseek"]
}
```

### 7.2 Test Authentication

1. Go to your frontend: https://your-app.com
2. Try logging in with OAuth
3. Verify profile loads
4. Check threads load correctly
5. Test Synergy Suite functionality

### 7.3 Check Supabase Logs

Dashboard → Logs → API Logs

Look for:
- SELECT queries from your app
- INSERT/UPDATE operations
- No errors or warnings

---

## 🎉 Migration Complete!

Your AI Agents platform is now running on Supabase PostgreSQL!

### ✅ What You Gained:

**Before (SQLite on Render):**
- ❌ 1GB storage limit
- ❌ No automatic backups
- ❌ Manual database uploads
- ❌ WAL mode issues
- ❌ No concurrent writes

**After (PostgreSQL on Supabase):**
- ✅ 8GB storage (8x more!)
- ✅ Automatic daily backups (7-day retention)
- ✅ No manual uploads needed
- ✅ True RDBMS with ACID compliance
- ✅ Concurrent connections
- ✅ Real-time subscriptions available
- ✅ Built-in auth (if needed later)
- ✅ Point-in-time recovery

---

## 📊 Post-Migration Checklist

- [ ] All tables visible in Supabase Table Editor
- [ ] Row counts match local databases
- [ ] OAuth authentication working
- [ ] Threads loading correctly
- [ ] Synergy Suite functional
- [ ] InHousePrint stock data accessible
- [ ] No errors in Render logs
- [ ] No errors in Supabase logs
- [ ] Backup local SQLite files (keep in `data/` folder)

---

## 🔧 Troubleshooting

### Issue: Migration script fails with "connection refused"

**Solution:**
```powershell
# Check firewall/VPN isn't blocking port 5432
# Verify connection string is correct
# Try connecting with psql:
psql "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
```

### Issue: "no such table" errors on Render

**Solution:**
```bash
# Render environment variables not set
# Go to Render Dashboard → Environment
# Verify all 4 variables are present:
#   - SUPABASE_URL
#   - SUPABASE_KEY  
#   - SUPABASE_DB_URL
#   - USE_SUPABASE=true
```

### Issue: 401 Unauthorized from Supabase

**Solution:**
```bash
# Wrong API key or expired token
# Regenerate anon key:
# Dashboard → Project Settings → API → Reset anon key
# Update .env and Render environment
```

### Issue: Data missing after migration

**Solution:**
```powershell
# Re-run migration for specific database:
python Supabase/migrate_to_supabase.py --database sessions

# Or rollback and retry:
python Supabase/migrate_to_supabase.py --rollback
python Supabase/migrate_to_supabase.py
```

---

## 🔄 Rollback Plan (If Needed)

If something goes wrong, you can rollback:

```powershell
# 1. Stop using Supabase
# Edit .env:
USE_SUPABASE=false
USE_SQLITE=true

# 2. Update Render environment
# Dashboard → Environment
# Change: USE_SUPABASE=false

# 3. Upload SQLite databases to Render
# (See RENDER_DATABASE_UPLOAD_INSTRUCTIONS.md)

# 4. Redeploy
git push origin v5
```

---

## 📚 Additional Resources

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **psycopg2 Docs:** https://www.psycopg.org/docs/
- **Migration Script:** `Supabase/migrate_to_supabase.py`
- **Connection Test:** `Supabase/test_supabase_connection.py`

---

## 🆘 Need Help?

**Check migration logs:**
```powershell
# View detailed logs
cat Supabase/migration.log

# Check Render logs
# Dashboard → Logs tab
```

**Contact Support:**
- Supabase Discord: https://discord.supabase.com
- Render Support: support@render.com

---

**Last Updated:** November 15, 2025  
**Migration Version:** 2.0  
**Status:** Production Ready ✅
