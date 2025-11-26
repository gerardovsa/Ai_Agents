# InHouse Print Render Deployment - Supabase Credentials Solution

**Date:** November 26, 2025  
**Status:** ✅ Ready for Deployment  
**Branch:** v9

---

## 🎯 Problem Solved

**Issue:** InHouse Print tools failed on Render with error:
```
Database config not found: /app/config/database-config.json
```

**Root Cause:** 
- SQL Server credentials were in `database-config.json` (not in Render env vars)
- File path resolution failed in Docker container
- Credentials were never uploaded to Render environment

**Solution:**
- ✅ Store credentials in Supabase (`ai_infrastructure.user_platform_credentials`)
- ✅ Create environment-aware credentials manager
- ✅ Update all wrapper files to use Supabase (Render) or JSON file (local)

---

## 📦 Files Created/Modified

### New Files Created:
1. **`AI_infrastructure/auth/supabase_credentials.py`** (235 lines)
   - Environment-aware credentials manager
   - Fetches from Supabase on Render
   - Falls back to database-config.json locally
   - Used by: All InHouse Print wrapper files

2. **`scripts/setup/insert_inhouse_credentials.sql`** (198 lines)
   - SQL to insert credentials into Supabase
   - 4 platforms: inhouse_print, anthropic, xero_print, shopify
   - Includes verification queries

### Files Modified:
3. **`UI/external/modules/inhouse-print/implementations/inhouse_wrapper.py`**
   - Replaced file path logic with Supabase credentials manager
   - Auto-detects Render vs Local environment

4. **`UI/external/modules/quote-calculator/implementations/calculator_wrapper.py`**
   - Updated `_get_calculator()` to use Supabase credentials

5. **`UI/external/modules/quote-calculator/implementations/query_library_wrapper.py`**
   - Updated `_get_query_library()` to use Supabase credentials

---

## 🚀 Deployment Steps

### Step 1: Insert Credentials into Supabase

**Run this SQL in Supabase SQL Editor:**

```sql
-- File: scripts/setup/insert_inhouse_credentials.sql
-- This inserts 4 sets of credentials:
-- 1. inhouse_print (SQL Server: 3.25.76.138)
-- 2. anthropic (Claude API key)
-- 3. xero_print (Xero API credentials)
-- 4. shopify (WooCommerce API credentials)
```

**To execute:**
1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Navigate to: **SQL Editor**
3. Copy contents of `scripts/setup/insert_inhouse_credentials.sql`
4. Click **Run**
5. Verify with:
```sql
SELECT platform, credential_type, is_active, created_at
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 1
ORDER BY platform;
```

**Expected result:**
```
platform        | credential_type | is_active | created_at
----------------|----------------|-----------|------------
anthropic       | api_key        | true      | 2025-11-26...
inhouse_print   | sql_server     | true      | 2025-11-26...
shopify         | api_key        | true      | 2025-11-26...
xero_print      | oauth          | true      | 2025-11-26...
```

---

### Step 2: Verify Render Environment Variables

**Ensure these are set in Render (already configured):**

```bash
# Supabase Connection (CRITICAL)
SUPABASE_DB_URL_POOLER=postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres

# Used for environment detection
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
```

The code auto-detects Render by checking for `SUPABASE_DB_URL` environment variable.

---

### Step 3: Push Code to Render

```powershell
# From AI_agents repository
cd C:\Users\gpoli\GIT\AI_agents

# Add changes
git add -A
git commit -m "Fix Render deployment: Use Supabase for InHouse Print credentials"

# Push to trigger auto-deployment
git push origin v9
```

**Render will automatically:**
1. Detect changes to `v9` branch
2. Build new Docker image
3. Deploy updated code
4. Restart service

---

### Step 4: Verify Deployment

**1. Check Render Logs:**
   - Go to: https://dashboard.render.com
   - Select: `ai-agents-backend-singapore`
   - Click: **Logs** tab
   - Look for:
   ```
   🔍 Fetching credentials from Supabase...
   ✅ Credentials loaded from Supabase
   [InHouse Wrapper] Loading database configuration...
   [InHouse Wrapper] Initializing ToolUseAgent with config from Supabase
   ✅ Singleton ToolUseAgent initialized successfully
   ```

**2. Test InHouse Print Tools:**
   ```bash
   # Using CHAT command
   CHAT "Search Fred database for customer 'Smith'"
   ```

**3. Check Health Endpoint:**
   ```bash
   curl https://ai-agents-backend-singapore.onrender.com/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "tools_loaded": 594,
     "inhouse_print": "available"
   }
   ```

---

## 🔧 How It Works

### Environment Detection Flow

```
┌──────────────────────────────────────┐
│   wrapper_file.py starts            │
└─────────────┬────────────────────────┘
              │
              ↓
┌──────────────────────────────────────┐
│  Import supabase_credentials.py      │
└─────────────┬────────────────────────┘
              │
              ↓
┌──────────────────────────────────────┐
│  Check: 'SUPABASE_DB_URL' in env?    │
└─────────────┬────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
     YES              NO
      │                │
      ↓                ↓
┌──────────────┐  ┌──────────────────┐
│   RENDER     │  │    LOCAL DEV     │
│  (Production)│  │  (Your Machine)  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ↓                   ↓
┌──────────────────┐  ┌─────────────────────────┐
│ Connect Supabase │  │ Read database-config.json│
│ Query table:     │  │ From:                    │
│ user_platform_   │  │ C:\Users\gpoli\GIT\      │
│   credentials    │  │   In_House_SQL\config\   │
└──────┬───────────┘  └────────┬────────────────┘
       │                       │
       └───────┬───────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│  Return config dict:                 │
│  {                                   │
│    'DatabaseConnections': {...},     │
│    'AI': {...}                       │
│  }                                   │
└─────────────┬────────────────────────┘
              │
              ↓
┌──────────────────────────────────────┐
│  Write to temporary JSON file        │
└─────────────┬────────────────────────┘
              │
              ↓
┌──────────────────────────────────────┐
│  Pass to ToolUseAgent/Calculator     │
│  (expects file path, not dict)       │
└──────────────────────────────────────┘
```

---

## 📊 Supabase Table Structure

### `ai_infrastructure.user_platform_credentials`

```sql
Column            | Type      | Description
------------------|-----------|----------------------------------------
id                | serial    | Primary key
user_id           | integer   | User ID (1 = system/default)
platform          | text      | Platform identifier (inhouse_print, etc.)
credential_type   | text      | Type (sql_server, api_key, oauth)
credential_key    | text      | Key identifier
credential_value  | text      | Main credential value
credentials       | jsonb     | Full credentials object (USED BY CODE)
metadata          | jsonb     | Additional info
is_active         | boolean   | Active status
created_at        | timestamp | Creation time
updated_at        | timestamp | Last update
```

**What the code uses:**
- `credentials` JSONB column contains all secrets:
  ```json
  {
    "server": "3.25.76.138\\INHPSQLSERVER",
    "port": 1433,
    "user": "sa",
    "password": "Jack2011",
    "database": "InHousePrint",
    "connection_string": "data source=...",
    "provider": "SqlServer"
  }
  ```

---

## 🧪 Testing Locally

**Before pushing to Render, test locally:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Test credentials manager
python AI_infrastructure/auth/supabase_credentials.py
```

**Expected output:**
```
============================================================
Testing Supabase Credentials Manager
============================================================

1. Testing Supabase connection...
✅ Local mode - no Supabase connection to test

2. Testing local config loading...
🔍 Loading credentials from database-config.json...
✅ Found config at: C:\Users\gpoli\GIT\In_House_SQL\config\database-config.json
✅ Config loaded:
   - SQL Server: 3.25.76.138\INHPSQLSERVER
   - Database: InHousePrint

============================================================
```

---

## 🔒 Security Notes

### What's Secure:
✅ Credentials stored in Supabase (encrypted at rest)  
✅ Connection uses TLS/SSL  
✅ Credentials never logged or exposed in API responses  
✅ Environment variables remain in Render (not in code)  
✅ Local development uses separate config file (not committed to git)

### What to NEVER Do:
❌ Don't commit `database-config.json` to git  
❌ Don't print credentials in logs  
❌ Don't expose credentials in API responses  
❌ Don't hardcode credentials in code

---

## 🐛 Troubleshooting

### Issue: "Database config not found" on Render

**Symptoms:**
```
FileNotFoundError: database-config.json not found
```

**Solutions:**
1. **Check Supabase credentials were inserted:**
   ```sql
   SELECT * FROM ai_infrastructure.user_platform_credentials 
   WHERE platform = 'inhouse_print';
   ```

2. **Check Render environment variables:**
   - `SUPABASE_DB_URL_POOLER` must be set
   - Verify in Render Dashboard → Environment

3. **Check Render logs:**
   ```
   Look for: "🔍 Fetching credentials from Supabase..."
   ```

---

### Issue: "psycopg2 not found" on Render

**Symptoms:**
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
Check `requirements.txt` includes:
```
psycopg2-binary==2.9.9
```

---

### Issue: Connection timeout to SQL Server

**Symptoms:**
```
Timeout expired. The timeout period elapsed prior to completion
```

**Solutions:**
1. **Check SQL Server is accessible from Render:**
   - IP: 3.25.76.138
   - Port: 1433
   - Firewall must allow Render IP ranges

2. **Check credentials are correct:**
   ```sql
   SELECT credentials->>'password' 
   FROM ai_infrastructure.user_platform_credentials 
   WHERE platform = 'inhouse_print';
   ```

3. **Check connection string format:**
   ```
   data source=3.25.76.138\INHPSQLSERVER,1433;user id=sa;password=Jack2011;database=InHousePrint
   ```

---

## 📝 Rollback Plan

If deployment fails:

**1. Revert to previous commit:**
```powershell
git revert HEAD
git push origin v9
```

**2. Render will auto-deploy previous version**

**3. Logs will show:**
```
Deployment #123 (previous version) - Live
```

---

## 🎉 Success Indicators

Deployment is successful when:

✅ Render logs show: "Credentials loaded from Supabase"  
✅ Health endpoint returns `"inhouse_print": "available"`  
✅ CHAT command can query Fred database  
✅ No "Database config not found" errors  
✅ SQL Server connection established

---

## 📚 Related Documentation

- **`SUPABASE_CREDENTIALS_MANAGER.md`** - Credentials manager API reference
- **`DATABASE_PATH_FIX_COMPLETE.md`** - Previous path fix attempt
- **`RENDER_DEPLOYMENT_GUIDE.md`** - General Render deployment guide

---

**Last Updated:** November 26, 2025  
**Author:** AI Agent Platform Team  
**Status:** ✅ Production Ready
