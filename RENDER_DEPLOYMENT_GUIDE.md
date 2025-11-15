# Render Deployment Guide - Supabase PostgreSQL Integration

**Date:** November 15, 2025  
**Purpose:** Deploy AI Agents platform with Supabase PostgreSQL backend  
**Related Documentation:** DATABASE_CONNECTIONS_UPDATE_COMPLETE.md, SUPABASE_TOOLS_COMPLETE.md

---

## Overview

This guide documents the environment variables and steps required to deploy the AI Agents platform to Render with Supabase PostgreSQL as the backend database.

## Architecture

- **Local Development:** SQLite databases in `data/` folder
- **Production (Render):** Supabase PostgreSQL with connection pooling
- **Database Connection:** Centralized via `AI_infrastructure/shared/database_utils.py`
- **Auto-Detection:** System automatically switches based on environment variables

## Required Environment Variables

### 1. Supabase Connection Variables

Add these to your Render service environment variables:

```bash
# Enable Supabase mode
USE_SUPABASE=true
RENDER=true

# Supabase connection details
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_SERVICE_KEY=[YOUR_SERVICE_KEY_HERE]

# Database connection string (connection pooler)
SUPABASE_DB_URL=postgresql://postgres.ryoicrdifiqhqpsnjmdo:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**Where to find these values:**
- `SUPABASE_URL`: Supabase Project Settings → API → Project URL
- `SUPABASE_SERVICE_KEY`: Supabase Project Settings → API → service_role key
- `SUPABASE_DB_URL`: Supabase Project Settings → Database → Connection Pooling → Connection string

### 2. Existing Render Variables (Keep These)

```bash
# Flask configuration
SECRET_KEY=[existing-value]
FLASK_ENV=production

# AI Provider API Keys
ANTHROPIC_API_KEY=[existing-value]
OPENAI_API_KEY=[existing-value]
DEEPSEEK_API_KEY_1=[existing-value]

# OAuth credentials
MICROSOFT_CLIENT_ID=[existing-value]
MICROSOFT_CLIENT_SECRET=[existing-value]
MICROSOFT_TENANT_ID=common

# Google OAuth (service account)
GOOGLE_SERVICE_ACCOUNT_JSON=[existing-value]

# Session management
SESSION_TYPE=filesystem
```

---

## Deployment Steps

### Step 1: Update Environment Variables in Render

1. Go to Render Dashboard: https://dashboard.render.com
2. Select your AI Agents service
3. Navigate to **Environment** tab
4. Add the Supabase variables listed above:
   - Click **Add Environment Variable**
   - Key: `USE_SUPABASE`, Value: `true`
   - Key: `RENDER`, Value: `true`
   - Key: `SUPABASE_URL`, Value: `https://ryoicrdifiqhqpsnjmdo.supabase.co`
   - Key: `SUPABASE_SERVICE_KEY`, Value: `[paste from Supabase]`
   - Key: `SUPABASE_DB_URL`, Value: `postgresql://postgres.ryoicrdifiqhqpsnjmdo:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`
5. Click **Save Changes**

### Step 2: Push Code to GitHub

```powershell
# Create v6 branch
git checkout -b v6

# Stage all updated files
git add AI_infrastructure/flask_app.py
git add AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py
git add google_workspace/oauth_credential_loader.py
git add AI_infrastructure/utils/email_alias_helpers.py
git add AI_infrastructure/utils/user_context_builder.py
git add AI_infrastructure/workspace/access_control.py
git add AI_infrastructure/workspace/slug_generator.py
git add AI_infrastructure/workspace/workspace_manager.py
git add tools/implementations/memory_tools.py
git add AI_infrastructure/shared/
git add DATABASE_CONNECTIONS_UPDATE_COMPLETE.md
git add RENDER_DEPLOYMENT_GUIDE.md

# Commit with comprehensive message
git commit -m "Update database connections for Supabase support

✅ Updated 9 critical files to use centralized get_database_connection()

HIGH PRIORITY (3 files):
- flask_app.py: Main Flask app database initialization
- microsoft_auth_routes_V2_FIXED.py: OAuth routes
- oauth_credential_loader.py: Google credentials loader

MEDIUM PRIORITY (6 files):
- email_alias_helpers.py: 6 occurrences updated
- user_context_builder.py: User context database queries
- access_control.py: Workspace RBAC system
- slug_generator.py: URL-safe slug generation
- workspace_manager.py: Workspace CRUD operations
- memory_tools.py: AI memory management

PATTERN APPLIED:
- Replace sqlite3.connect(db_path) with get_database_connection('schema_name')
- Add import: from shared.database_utils import get_database_connection
- Add row_factory check for SQLite compatibility

TESTING:
✅ Flask app starts successfully (281 tools loaded)
✅ All routes registered without errors
✅ All 9 files import successfully
✅ Database tables verified (16 tables in ai_infrastructure)

DEPLOYMENT:
- Supports both SQLite (local) and Supabase (production)
- Auto-detection via USE_SUPABASE environment variable
- Ready for Render deployment with Supabase PostgreSQL

Reference: DATABASE_CONNECTIONS_UPDATE_COMPLETE.md
Guide: RENDER_DEPLOYMENT_GUIDE.md"

# Push to GitHub
git push origin v6
```

### Step 3: Trigger Render Deployment

Render will automatically deploy when it detects the new commit on the v6 branch (if auto-deploy is enabled).

**Or manually trigger:**
1. Go to Render Dashboard → Your service
2. Click **Manual Deploy** button
3. Select branch: `v6`
4. Click **Deploy**

### Step 4: Monitor Deployment Logs

Watch for these success indicators:

```
✅ BUILD PHASE:
- Collecting dependencies...
- Installing Python packages...
- Build completed successfully

✅ START PHASE:
- Starting Flask application...
- Connected to Supabase PostgreSQL (Schema: ai_infrastructure)
- Tool Registry loaded - 281 tools available
- Database tables verified: 16 tables
- OAuth tokens schema up to date
- All routes registered successfully
- Running on http://0.0.0.0:5001

❌ ERROR INDICATORS TO WATCH FOR:
- "Database connection failed" - Check SUPABASE_DB_URL
- "Permission denied" - Check SUPABASE_SERVICE_KEY
- "Connection timeout" - Check Supabase connection pooling settings
- "sqlite3.connect() error" - Some file still using direct SQLite connection
```

---

## Verification Checklist

### 1. Test API Health Endpoint

```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "Supabase PostgreSQL",
  "tools": 281,
  "routes": 35
}
```

### 2. Test OAuth Login Flow

1. Navigate to: `https://your-app.onrender.com`
2. Click **Sign in with Google** or **Sign in with Microsoft**
3. Complete OAuth flow
4. Verify redirect to dashboard

**Check Supabase Dashboard:**
- Go to: https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo
- Navigate to **Table Editor** → `ai_infrastructure` schema → `users` table
- Verify new user row created
- Check `oauth_tokens` table for token entry

### 3. Test Thread Creation

```bash
curl -X POST https://your-app.onrender.com/api/threads/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Test Thread",
    "workspace_id": 1
  }'
```

**Verify in Supabase:**
- `threads` table should have new row
- Check `created_at` timestamp
- Verify `workspace_id` matches

### 4. Test Workspace Operations

```bash
# Create workspace
curl -X POST https://your-app.onrender.com/api/workspaces \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Test Workspace",
    "description": "Testing Supabase integration"
  }'
```

**Verify in Supabase:**
- `workspaces` table should have new row
- `workspace_members` table should have owner entry
- Check permissions in `workspace_access_control` table

### 5. Test AI Agent Chat

```bash
curl -X POST https://your-app.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Hello, what tools do you have?",
    "thread_id": "your-thread-id"
  }'
```

**Verify:**
- Agent responds with list of available tools
- Message saved to `messages` table in Supabase
- Thread `updated_at` timestamp updated

---

## Troubleshooting

### Issue: "Database connection failed"

**Symptom:** Logs show `psycopg2.OperationalError: could not connect to server`

**Solution:**
1. Verify `SUPABASE_DB_URL` is correct (should use port 6543 for pooler)
2. Check Supabase Project Settings → Database → Connection Pooling is enabled
3. Verify password in connection string matches Supabase database password
4. Check Supabase project is not paused (free tier pauses after inactivity)

### Issue: "Permission denied for schema"

**Symptom:** Logs show `permission denied for schema ai_infrastructure`

**Solution:**
1. Verify `SUPABASE_SERVICE_KEY` is the `service_role` key (NOT `anon` key)
2. Check Supabase SQL Editor and run:
   ```sql
   GRANT ALL PRIVILEGES ON SCHEMA ai_infrastructure TO postgres;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_infrastructure TO postgres;
   ```

### Issue: "sqlite3.connect() still being called"

**Symptom:** Logs show `sqlite3.connect('/app/data/ai_infrastructure.db')` even with `USE_SUPABASE=true`

**Solution:**
1. Check which file is making the call (look at traceback)
2. Verify file imports `get_database_connection` from `shared.database_utils`
3. Ensure file was included in v6 branch commit
4. Re-run verification script: `python data/show_database_structure_v2.py`

### Issue: "OAuth callback URL mismatch"

**Symptom:** OAuth login fails with "redirect_uri_mismatch" error

**Solution:**
1. Update OAuth redirect URIs in provider dashboards:
   - **Google:** https://console.cloud.google.com → APIs & Services → Credentials
     - Add: `https://your-app.onrender.com/api/auth/google/callback`
   - **Microsoft:** https://portal.azure.com → App Registrations → Authentication
     - Add: `https://your-app.onrender.com/api/auth/microsoft/callback`

### Issue: "Connection pool exhausted"

**Symptom:** Logs show `psycopg2.pool.PoolError: connection pool exhausted`

**Solution:**
1. Go to Supabase Dashboard → Project Settings → Database
2. Increase connection pool size (default is 15 for free tier)
3. Or optimize application to close connections properly:
   ```python
   conn = get_database_connection('ai_infrastructure')
   try:
       # Your queries here
   finally:
       conn.close()  # Always close connections
   ```

---

## Database Schema Management

### Current Schemas in Supabase

1. **ai_infrastructure** (16 tables)
   - users, oauth_tokens, sessions, threads, messages, workspaces, etc.

2. **sessions** (2 tables)
   - flask_sessions, active_sessions

3. **synergy_sessions** (2 tables)
   - synergy_sessions, synergy_internal_docs

4. **kanban_analytics** (5 tables)
   - kanban_cards, kanban_columns, time_tracking, etc.

5. **stock_data** (51 tables)
   - StockLevels, ClickCosts, ConsumableInventory, etc.

### Schema Migrations

If you need to add new tables or columns:

1. **Local Development:**
   ```python
   # Add migration in AI_infrastructure/migrations/
   # Test with SQLite first
   python AI_infrastructure/migrations/add_new_table.py
   ```

2. **Deploy to Supabase:**
   ```sql
   -- Run in Supabase SQL Editor
   -- https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/editor
   
   CREATE TABLE IF NOT EXISTS ai_infrastructure.new_table (
       id SERIAL PRIMARY KEY,
       name TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

3. **Verify Migration:**
   ```bash
   # Run verification script
   python data/show_database_structure_v2.py
   
   # Should show new table in both SQLite and Supabase
   ```

---

## Performance Optimization

### Connection Pooling

Supabase automatically provides connection pooling via PgBouncer (port 6543).

**Best Practices:**
- Always close connections after use
- Use context managers when possible:
  ```python
  with get_database_connection('ai_infrastructure') as conn:
      cursor = conn.cursor()
      # Your queries here
  # Connection automatically closed
  ```

### Query Optimization

- Use prepared statements for repeated queries
- Add indexes on frequently queried columns
- Use `EXPLAIN ANALYZE` in Supabase SQL Editor to optimize slow queries

### Monitoring

**Supabase Dashboard → Reports:**
- Monitor connection count
- Track slow queries
- Check database size
- View API usage

---

## Rollback Plan

If deployment fails, rollback to v5:

```bash
# On Render Dashboard
1. Go to your service → Deployments
2. Find previous successful deployment (v5)
3. Click "Redeploy"

# Or via Git
git checkout v5
git push origin v5 --force
```

**Then:**
1. Remove Supabase environment variables from Render
2. System will automatically fall back to SQLite mode
3. Investigate errors in deployment logs
4. Fix issues in v6 branch
5. Re-deploy when ready

---

## Success Criteria

✅ **All checks must pass before marking deployment successful:**

- [ ] Render deployment completes without errors
- [ ] Flask app starts and shows "Connected to Supabase PostgreSQL"
- [ ] Health endpoint returns 200 OK
- [ ] All 281 tools load successfully
- [ ] All 35 routes registered
- [ ] OAuth login works (Google + Microsoft)
- [ ] Thread creation saves to Supabase
- [ ] Workspace operations work correctly
- [ ] AI agent chat saves messages to database
- [ ] No sqlite3.connect() errors in logs
- [ ] Supabase Dashboard shows new data in tables

---

## Next Steps After Deployment

1. **Monitor Production Logs:**
   - Watch for database connection errors
   - Check response times
   - Monitor memory usage

2. **Performance Testing:**
   - Load test with multiple concurrent users
   - Verify connection pooling handles traffic
   - Check query performance in Supabase Reports

3. **User Acceptance Testing:**
   - Test all major features
   - Verify OAuth flows work smoothly
   - Check multi-workspace functionality
   - Test thread management and agent interactions

4. **Documentation Updates:**
   - Update API documentation with production URLs
   - Document any deployment-specific configurations
   - Add troubleshooting entries for production issues

---

## Support Resources

- **Supabase Documentation:** https://supabase.com/docs
- **Render Documentation:** https://render.com/docs
- **Internal Docs:**
  - `DATABASE_CONNECTIONS_UPDATE_COMPLETE.md` - This update's summary
  - `SUPABASE_TOOLS_COMPLETE.md` - Supabase integration guide
  - `SUPABASE_CLI_GUIDE.md` - CLI commands and usage
  - `SUPABASE_QUICK_REFERENCE.md` - Quick lookup guide

---

**Last Updated:** November 15, 2025  
**Version:** 1.0.0  
**Status:** Ready for Deployment
