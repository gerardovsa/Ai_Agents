# Render.com Environment Variable Update

**Date:** November 21, 2025  
**Purpose:** Add dual-URL Supabase configuration + backward compatibility

---

## 🎯 REQUIRED CHANGES

### Add This Variable (1 new variable):

```bash
SUPABASE_DB_URL=postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
```

**Why:** Provides backward compatibility for 18 standalone scripts that haven't been migrated to the dual-URL system yet.

---

## ✅ COMPLETE ENVIRONMENT VARIABLE LIST

**Copy-paste this into Render.com Environment tab:**

```bash
# AI Provider Keys
ANTHROPIC_API_KEY=<your-anthropic-key-from-env-master>
DEEPSEEK_API_KEY_1=<your-deepseek-key-from-env-master>
OPENAI_API_KEY=<your-openai-key-from-env-master>

# Google OAuth & Cloud
GOOGLE_APPLICATION_CREDENTIALS=/data/your-service-account-file.json
GOOGLE_CLOUD_PROJECT=your-project-name
GOOGLE_OAUTH_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=<your-client-secret>
GOOGLE_OAUTH_REDIRECT_URI=https://your-app.onrender.com/oauth2callback
GOOGLE_REDIRECT_URI=https://your-app.onrender.com/api/auth/google/callback
SERVICE_ACCOUNT_EMAIL=your-service-account@appspot.gserviceaccount.com

# Microsoft OAuth
MICROSOFT_CLIENT_ID=<your-microsoft-client-id>
MICROSOFT_CLIENT_SECRET=<your-microsoft-client-secret>
MICROSOFT_REDIRECT_URI=https://your-app.onrender.com/api/auth/microsoft/callback
MICROSOFT_TENANT_ID=common

# Security Keys
JWT_SECRET=<your-jwt-secret-from-env-master>
SECRET_KEY=<your-secret-key-from-env-master>

# Supabase API Keys
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>
SUPABASE_URL=https://your-project-id.supabase.co

# Supabase Database Connection - DUAL URL SYSTEM
# PRIMARY: Transaction Mode Pooler (port 6543) - Flask uses this (auto-closes connections)
SUPABASE_DB_URL_POOLER=postgresql://postgres.your-project:your-password@aws-0-region.pooler.supabase.com:6543/postgres

# FALLBACK: Session Mode Pooler (port 5432) - Backup if Transaction Mode fails
SUPABASE_DB_URL_SESSION=postgresql://postgres.your-project:your-password@aws-0-region.pooler.supabase.com:5432/postgres

# LEGACY: Backward compatibility for standalone scripts (NEW - ADD THIS)
SUPABASE_DB_URL=postgresql://postgres.your-project:your-password@aws-0-region.pooler.supabase.com:6543/postgres

# Legacy flag
USE_SUPABASE=true
```

---

## 📝 STEP-BY-STEP INSTRUCTIONS

### 1. Go to Render Dashboard
- Open: https://dashboard.render.com/
- Select: **ai-agents-backend-singapore** service

### 2. Navigate to Environment
- Click: **Environment** tab (left sidebar)
- Scroll down to environment variables section

### 3. Add New Variable
Click **Add Environment Variable** button and add:

```
Key: SUPABASE_DB_URL
Value: postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
```

### 4. Verify Existing Variables
Confirm these already exist (they should from your list):
- ✅ SUPABASE_DB_URL_POOLER
- ✅ SUPABASE_DB_URL_SESSION

### 5. Save Changes
- Click **Save Changes** button at bottom
- Render will auto-deploy (~2 minutes)

### 6. Monitor Deployment
Watch the **Logs** tab for:
```
 [POOL] Using Transaction Mode (port 6543) for 'sessions'
 [POOL] Created connection pool for 'sessions' (1-2 connections)
 [POOL] Total pools: 1
 [POOL] Total potential connections: 2 (Supabase Nano limit: 60)
```

**Success indicators:**
- ✅ No "SUPABASE_DB_URL not set" errors
- ✅ No "connection pool exhausted" errors
- ✅ Sees " [POOL] Using Transaction Mode (port 6543)"

---

## 🔍 WHAT THIS DOES

### Current State (Before Change):
```
SUPABASE_DB_URL_POOLER ✅ (Flask uses this - Transaction Mode)
SUPABASE_DB_URL_SESSION ✅ (Fallback - Session Mode)
SUPABASE_DB_URL ❌ (Missing - causes 18 scripts to fail)
```

### After Change:
```
SUPABASE_DB_URL_POOLER ✅ (PRIMARY - Flask core infrastructure)
SUPABASE_DB_URL_SESSION ✅ (FALLBACK - If 6543 fails)
SUPABASE_DB_URL ✅ (LEGACY - Backward compatibility)
```

### Why 3 URLs?

1. **SUPABASE_DB_URL_POOLER (port 6543)**
   - Used by: Flask core (database_utils.py)
   - Mode: Transaction Mode
   - Behavior: Auto-closes connections after each transaction
   - Benefit: Prevents pool exhaustion on Free Tier

2. **SUPABASE_DB_URL_SESSION (port 5432)**
   - Used by: Flask core (automatic fallback)
   - Mode: Session Mode
   - Behavior: Keeps connections open
   - Use case: If Transaction Mode fails

3. **SUPABASE_DB_URL (port 6543)** ← **NEW**
   - Used by: 18 standalone scripts (legacy)
   - Mode: Same as POOLER (Transaction Mode)
   - Purpose: Backward compatibility while scripts are migrated
   - Scripts: create_scheduler_tables.py, test_pool_and_schema.py, etc.

---

## ✅ VERIFICATION CHECKLIST

After deployment completes:

### 1. Check Render Logs
```bash
# Should see:
 [POOL] Using Transaction Mode (port 6543) for 'sessions'
 [POOL] Created connection pool
 [POOL] Total potential connections: X (Supabase Nano limit: 60)

# Should NOT see:
❌ "SUPABASE_DB_URL not set"
❌ "connection pool exhausted"
❌ Any database connection errors
```

### 2. Test Pool Health Endpoint
```bash
curl https://ai-agents-backend-singapore.onrender.com/api/pool/health
```

**Expected response:**
```json
{
  "healthy": true,
  "pools_active": 3,
  "avg_wait_time_ms": 25.83,
  "hit_rate_percent": 98.81,
  "warnings": []
}
```

### 3. Test Message Persistence
- Open: https://ai-agents-backend-singapore.onrender.com
- Send test message in Prime AI Chat
- Reload page
- Verify: Messages still visible (not disappearing)

### 4. Monitor Connection Pool
```bash
curl https://ai-agents-backend-singapore.onrender.com/api/pool/stats
```

**Expected response:**
```json
{
  "pools_created": 3,
  "connections_acquired": 150+,
  "connections_returned": 145+,
  "pool_hits": 200+,
  "pool_misses": 3,
  "avg_wait_time": 0.025,  // 25ms - good
  "pools": {
    "sessions": {"min": 1, "max": 2, "status": "active"},
    "ai_infrastructure": {"min": 1, "max": 2, "status": "active"}
  }
}
```

**Good indicators:**
- ✅ Pool hit rate > 90%
- ✅ Avg wait time < 50ms
- ✅ Active connections < 10
- ✅ No "exhausted" in logs

---

## 🚨 TROUBLESHOOTING

### Issue: "SUPABASE_DB_URL not set" in logs

**Cause:** Variable not added or typo in name

**Fix:**
1. Go to Render Environment tab
2. Verify variable name is exactly: `SUPABASE_DB_URL`
3. Check value matches: `postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres`
4. Save and redeploy

### Issue: Still seeing "connection pool exhausted"

**Cause:** Using Session Mode instead of Transaction Mode

**Check logs for:**
```
 [POOL] Using Session Mode (port 5432) - FALLBACK
```

**Fix:**
1. Verify `SUPABASE_DB_URL_POOLER` is set correctly (port 6543)
2. Check for typos in URL
3. Ensure no extra spaces in environment variable value

### Issue: Messages still not persisting

**Cause:** Upsert endpoint may still be failing

**Check:**
1. Render logs for specific errors
2. Test endpoint directly:
   ```bash
   curl -X POST https://ai-agents-backend-singapore.onrender.com/api/threads/upsert \
     -H "Content-Type: application/json" \
     -d '{"thread_slug":"test123","workspace_id":1,"name":"Test","user_id":1}'
   ```
3. Look for constraint errors in response

### Issue: High wait times (>100ms)

**Cause:** Too many connections or slow queries

**Check:**
```bash
curl https://ai-agents-backend-singapore.onrender.com/api/pool/stats
```

**Fix:**
- If pool hit rate < 80%: Pools not being reused (check code)
- If active connections > 20: Possible connection leak (check for unclosed connections)
- If wait time increasing: Query performance issue (check slow queries)

---

## 📊 EXPECTED PERFORMANCE AFTER UPDATE

### Connection Pool Metrics:
- **Pools Created:** 3-5 (sessions, ai_infrastructure, synergy_sessions, stock_data, kanban_analytics)
- **Max Connections:** 10 (5 schemas × 2 connections each)
- **Free Tier Usage:** 16.7% (10 of 60 connections)
- **Pool Hit Rate:** 95-100%
- **Avg Wait Time:** 10-30ms

### Health Status:
- **Healthy:** true
- **Warnings:** 0
- **Connection Leaks:** 0
- **Pool Exhaustion:** Never

### Message Functionality:
- ✅ Messages save on send
- ✅ Messages persist after reload
- ✅ No duplicates
- ✅ Threads list correctly

---

## 🎉 SUCCESS CRITERIA

Deployment is successful when you see:

1. ✅ Render deployment completes without errors
2. ✅ Logs show " [POOL] Using Transaction Mode (port 6543)"
3. ✅ `/api/pool/health` returns `{"healthy": true}`
4. ✅ Messages persist after page reload
5. ✅ No "connection pool exhausted" errors
6. ✅ Pool hit rate > 90%
7. ✅ Avg wait time < 50ms

---

## 📚 RELATED DOCUMENTATION

- **DATABASE_CONNECTION_AUDIT.md** - Full audit of all connections
- **DATABASE_CONNECTION_STATUS.md** - Current system status
- **DATABASE_TEST_RESULTS_NOV21.md** - Local test results (100% pass rate)
- **SUPABASE_CONNECTION_MODES.md** - Complete dual-URL system guide

---

## 🔄 ROLLBACK PLAN (If Issues Occur)

If deployment causes problems:

1. **Quick Fix:** Remove `SUPABASE_DB_URL` variable
   - Result: Core Flask app still works (uses POOLER)
   - Downside: 18 standalone scripts will fail

2. **Full Rollback:** Revert to single URL
   - Keep only: `SUPABASE_DB_URL=postgresql://...6543/postgres`
   - Remove: `SUPABASE_DB_URL_POOLER` and `SUPABASE_DB_URL_SESSION`
   - Downside: No automatic fallback, back to old system

3. **Safe State:** All 3 URLs with same value
   - Set all 3 to same URL (port 6543)
   - Result: Everything works, but no fallback benefit

---

**Summary:**
Just add 1 variable (`SUPABASE_DB_URL`) to Render.com and you're done! This provides backward compatibility for standalone scripts while maintaining the optimized dual-URL system for Flask core. 🚀

**Estimated Time:** 5 minutes to add + 2 minutes for auto-deploy = 7 minutes total
