# 🚀 Supabase Migration Guide

Complete guide to migrate AI Agents from SQLite + Render Persistent Disk to Supabase PostgreSQL.

## Why Supabase?

✅ **Beautiful Dashboard** - See all your data, run queries, manage tables visually  
✅ **Free Tier** - 500MB database, unlimited API requests  
✅ **Auto-scaling** - Handles growth automatically  
✅ **Real-time** - Built-in real-time subscriptions  
✅ **Backups** - Automatic daily backups  
✅ **Better than Render Disk** - No file copying issues, proper database  

## Cost Comparison

| Solution | Database Cost | App Cost | Total | Issues |
|----------|--------------|----------|-------|--------|
| **Current (SQLite + Disk)** | $2.50/mo (10GB disk) | $7/mo | **$9.50/mo** | 10 deployment failures |
| **Supabase Free** | $0/mo (500MB) | $7/mo | **$7/mo** | None - proper database |
| **Supabase Pro** | $25/mo (8GB) | $7/mo | **$32/mo** | None + more features |

**Savings: $2.50/month** with Supabase Free tier vs current setup!

---

## 📋 Phase 1: Create Supabase Project (5 minutes)

### Step 1: Sign Up / Log In
1. Go to https://supabase.com/dashboard
2. Sign up or log in (GitHub, Google, or email)

### Step 2: Create New Project
1. Click **"New Project"**
2. **Organization**: Create new or use existing
3. **Project Name**: `ai-agents-production`
4. **Database Password**: Generate strong password (save it!)
5. **Region**: **Singapore** (Southeast Asia) - closest to your Render deployment
6. **Pricing Plan**: **Free** (500MB database, unlimited API requests)
7. Click **"Create new project"** (takes 2-3 minutes)

### Step 3: Get Your Credentials

Once project is created, go to **Settings → Database**:

**You need 3 things:**

1. **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
2. **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (long string)
3. **Database URL**: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres`

**Save these in a text file** - you'll need them for migration!

---

## 📊 Phase 2: Run Migration (15 minutes)

### Step 1: Install Dependencies

```powershell
cd C:\Users\gpoli\GIT\AI_agents
pip install psycopg2-binary
```

### Step 2: Run Migration Script

```powershell
cd supabase_migration
python migrate_to_supabase.py
```

**You'll be prompted for:**
1. Supabase Project URL
2. Supabase Anon Key
3. Supabase Database URL (the full postgresql:// connection string)

**What it does:**
- ✅ Analyzes all 5 SQLite databases
- ✅ Creates PostgreSQL schemas (one per database)
- ✅ Converts SQLite types to PostgreSQL types
- ✅ Migrates all data (preserving relationships)
- ✅ Verifies row counts match
- ✅ Shows progress for each table

**Expected output:**
```
================================================================================
SUPABASE MIGRATION TOOL
SQLite → PostgreSQL Data Migration
================================================================================

Connecting to Supabase PostgreSQL...
✓ Connected successfully

================================================================================
PHASE 1: Analyzing SQLite Databases
================================================================================

Analyzing: ai_infrastructure.db
------------------------------------------------------------
  Table: users
    Columns: 8
    Rows: 5
  Table: user_platform_credentials
    Columns: 10
    Rows: 12
  ...
  Total tables: 15
  Total rows: 1,234

Analyzing: sessions.db
...

================================================================================
SUMMARY: 5 databases, 28 tables, 5,678 total rows
================================================================================

Proceed with migration? (yes/no): yes

================================================================================
PHASE 2: Creating PostgreSQL Schemas
================================================================================

Creating PostgreSQL schema for: ai_infrastructure
  ✓ Created table: ai_infrastructure.users
  ✓ Created table: ai_infrastructure.user_platform_credentials
  ...

================================================================================
PHASE 3: Migrating Data
================================================================================

Migrating data from: ai_infrastructure
  Migrating: users (5 rows)... ✓ (5 rows)
  Migrating: user_platform_credentials (12 rows)... ✓ (12 rows)
  ...

✓ Data migration complete

================================================================================
PHASE 4: Verification
================================================================================

Verifying migration: ai_infrastructure
  ✓ users: 5 rows (matches)
  ✓ user_platform_credentials: 12 rows (matches)
  ...

================================================================================
MIGRATION COMPLETE
================================================================================

✓ All data migrated and verified successfully!

Migrated: 28 tables, 5,678 rows

Next steps:
1. Update config.py to use PostgreSQL
2. Add Supabase credentials to Render env vars
3. Test the application

================================================================================
```

---

## 🔧 Phase 3: Update Application Code (10 minutes)

### Step 1: Update config.py

Update `AI_infrastructure/config.py` to support Supabase:

```python
# Add at top of file
import os
from pathlib import Path

# Determine database type based on environment
IS_PRODUCTION = os.getenv('RENDER') == 'true'
USE_SUPABASE = os.getenv('USE_SUPABASE') == 'true'

if USE_SUPABASE:
    # Supabase PostgreSQL configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    DATABASE_URL = os.getenv('SUPABASE_DB_URL')
    
    # Database configuration for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    print("🗄️ Using Supabase PostgreSQL database")
else:
    # SQLite configuration (development)
    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / 'data'
    
    DB_CONFIG_PATH = DATA_DIR / 'database-config.json'
    SESSION_DB_PATH = DATA_DIR / 'sessions.db'
    AI_INFRASTRUCTURE_DB_PATH = DATA_DIR / 'ai_infrastructure.db'
    
    print("🗄️ Using SQLite databases (development)")
```

### Step 2: Add Supabase Environment Variables to Render

Using the toolkit you created:

```powershell
cd C:\Users\gpoli\GIT\AI_agents\Render_backend
```

Create `add_supabase_env_vars.py`:

```python
import requests
import os

RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d47nfr2li9vc738s0uc0"

env_vars = {
    'USE_SUPABASE': 'true',
    'SUPABASE_URL': 'https://xxxxxxxxxxxxx.supabase.co',
    'SUPABASE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'SUPABASE_DB_URL': 'postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres'
}

headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Content-Type': 'application/json'
}

print("Adding Supabase environment variables to Render...\n")

for key, value in env_vars.items():
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars/{key}'
    response = requests.put(url, json={'value': value}, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✓ {key}")
    else:
        print(f"✗ {key}: {response.status_code}")

print("\n✓ Supabase environment variables added!")
```

**Fill in your actual Supabase credentials** then run:

```powershell
python add_supabase_env_vars.py
```

---

## 🚀 Phase 4: Deploy to Render (5 minutes)

### Step 1: Update render.yaml

Remove persistent disk configuration (no longer needed):

```yaml
services:
  - type: web
    name: ai-agents-backend-singapore
    runtime: docker
    region: singapore
    plan: starter
    branch: v3
    # REMOVE THIS SECTION (no longer needed):
    # disk:
    #   name: ai-agents-data
    #   mountPath: /data
    #   sizeGB: 10
    
    envVars:
      - key: RENDER
        value: true
      - key: USE_SUPABASE
        value: true
      # ... rest of env vars
```

### Step 2: Update Dockerfile

Remove database file copying (no longer needed):

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# No need to create /data or copy database files anymore!

# Expose port
EXPOSE 10000

# Start the app
CMD ["python", "AI_infrastructure/flask_app.py"]
```

### Step 3: Commit and Push

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Remove database files from tracking (no longer needed in git)
git rm -r --cached data/*.db
git rm -r --cached data/database-config.json

# Update .gitignore
echo "" >> .gitignore
echo "# SQLite databases (migrated to Supabase)" >> .gitignore
echo "data/*.db" >> .gitignore
echo "data/*.db-shm" >> .gitignore
echo "data/*.db-wal" >> .gitignore

# Commit changes
git add render.yaml Dockerfile .gitignore AI_infrastructure/config.py
git commit -m "Migrate to Supabase PostgreSQL - remove SQLite dependencies"

# Push to trigger deployment
git push origin v3
```

### Step 4: Monitor Deployment

```powershell
cd Render_backend
python render_toolkit.py monitor
```

**Expected result:**
- Build succeeds (no database file copying issues)
- Deployment succeeds
- Health check passes
- Application connects to Supabase

---

## 🎉 Phase 5: Verify and Celebrate (5 minutes)

### Step 1: Check Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **"Table Editor"** in sidebar
4. You should see your data organized by schemas:
   - `ai_infrastructure` schema (users, credentials, OAuth tokens)
   - `sessions` schema (Flask sessions)
   - `synergy_sessions` schema
   - `kanban_analytics` schema
   - `stock_data` schema

### Step 2: Test Application

```powershell
# Check service health
python render_toolkit.py health

# Expected output:
# ✓ Service is healthy
# ✓ Connected to Supabase PostgreSQL
```

### Step 3: Run a Test Query in Supabase

In Supabase Dashboard → SQL Editor:

```sql
-- Check user count
SELECT COUNT(*) FROM ai_infrastructure.users;

-- Check platform credentials
SELECT user_id, platform, updated_at 
FROM ai_infrastructure.user_platform_credentials 
ORDER BY updated_at DESC;

-- Check recent sessions
SELECT * FROM sessions.sessions 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## 🎊 Benefits You Get

### 1. Visual Database Management
- **Table Editor**: Edit data in a spreadsheet-like interface
- **SQL Editor**: Run queries with autocomplete and syntax highlighting
- **Schema Visualizer**: See relationships between tables
- **API Documentation**: Auto-generated API docs for your tables

### 2. Real-time Features (Bonus!)
- Subscribe to table changes in real-time
- Build live dashboards
- Instant updates without polling

### 3. Better Performance
- **Proper database engine** (not file-based SQLite)
- **Connection pooling** for concurrent users
- **Indexing** for faster queries
- **Query optimization** built-in

### 4. Professional DevOps
- **Automatic backups** - Daily backups, point-in-time recovery
- **Monitoring** - Query performance, connection stats
- **Logs** - See all database activity
- **Security** - Row-level security, SSL connections

### 5. No More Deployment Issues
- ❌ No more file copying errors
- ❌ No more .dockerignore problems
- ❌ No more persistent disk complexity
- ✅ Just a connection string - it works!

---

## 🆘 Troubleshooting

### Migration Script Fails

**Error: "psycopg2 not found"**
```powershell
pip install psycopg2-binary
```

**Error: "Connection refused"**
- Check your Supabase database URL
- Ensure you're using the connection string from Settings → Database
- Check firewall/network (Supabase uses port 5432)

**Error: "Schema already exists"**
- Safe to ignore - script will drop and recreate tables
- Or manually drop schemas in Supabase SQL Editor:
  ```sql
  DROP SCHEMA IF EXISTS ai_infrastructure CASCADE;
  DROP SCHEMA IF EXISTS sessions CASCADE;
  DROP SCHEMA IF EXISTS synergy_sessions CASCADE;
  DROP SCHEMA IF EXISTS kanban_analytics CASCADE;
  DROP SCHEMA IF EXISTS stock_data CASCADE;
  ```

### Application Fails to Connect

**Check environment variables:**
```powershell
python render_toolkit.py env
```

Should show:
- `USE_SUPABASE=true`
- `SUPABASE_URL=https://...`
- `SUPABASE_KEY=eyJ...`
- `SUPABASE_DB_URL=postgresql://...`

**Test connection manually:**
```python
import psycopg2
conn = psycopg2.connect('postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres')
print("✓ Connected!")
conn.close()
```

### Render Deployment Still Fails

**Clear Docker cache:**
1. Go to Render Dashboard → Service Settings
2. Click "Manual Deploy" → "Clear build cache & deploy"

**Check logs:**
```powershell
python render_toolkit.py monitor
```

Look for connection errors, missing environment variables, or import errors.

---

## 📚 Additional Resources

### Supabase Documentation
- **Getting Started**: https://supabase.com/docs/guides/getting-started
- **Database**: https://supabase.com/docs/guides/database
- **Python Client**: https://supabase.com/docs/reference/python/introduction

### PostgreSQL Documentation
- **Data Types**: https://www.postgresql.org/docs/current/datatype.html
- **SQL Commands**: https://www.postgresql.org/docs/current/sql-commands.html

### Render + Supabase
- **Best Practices**: https://render.com/docs/databases
- **Environment Variables**: https://render.com/docs/environment-variables

---

## 🎯 Summary

**Time investment:** ~45 minutes total  
**Cost savings:** $2.50/month (vs Render persistent disk)  
**Benefits:**
- ✅ Beautiful dashboard to manage data
- ✅ No more deployment issues
- ✅ Production-ready database
- ✅ Automatic backups
- ✅ Better performance
- ✅ Room to scale

**Next steps:**
1. Create Supabase project (5 min)
2. Run migration script (15 min)
3. Update config.py (10 min)
4. Add environment variables (5 min)
5. Deploy to Render (5 min)
6. Verify and celebrate! (5 min)

---

**Created:** November 9, 2025  
**Status:** Ready to use  
**Support:** Check TROUBLESHOOTING section or Supabase Discord
