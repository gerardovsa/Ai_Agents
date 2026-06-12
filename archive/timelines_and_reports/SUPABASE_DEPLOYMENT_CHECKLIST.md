# 🎯 Deployment Checklist - Supabase Connection Fix

## Pre-Deployment Verification

- [ ] Read [SUPABASE_FIX_SUMMARY.md](SUPABASE_FIX_SUMMARY.md)
- [ ] Read [RENDER_QUICK_FIX.md](RENDER_QUICK_FIX.md)
- [ ] Understand the root cause (env variable mismatch)
- [ ] Have Supabase dashboard access
- [ ] Have Render dashboard access

---

## Step 1: Get Supabase Connection Strings

### Transaction Mode (Port 6543) - Primary

1. Go to: https://app.supabase.com/project/YOUR_PROJECT_ID/settings/database
2. Scroll to: **Connection Pooling** section
3. Mode: Select **Transaction**
4. **Copy connection string**
5. Save it somewhere (you'll need it in Step 2)

**Format check:**
```
postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
                                                                          ^^^^
                                                                     Port 6543 ✓
```

- [ ] Transaction Mode URL copied (contains `:6543/`)

### Session Mode (Port 5432) - Fallback

1. Same Supabase page
2. Mode: Select **Session**
3. **Copy connection string**
4. Save it somewhere

**Format check:**
```
postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
                                                                          ^^^^
                                                                     Port 5432 ✓
```

- [ ] Session Mode URL copied (contains `:5432/`)

---

## Step 2: Add Environment Variables to Render

1. Go to: https://dashboard.render.com/web/srv-xxxxx/env
2. Click **Environment** tab
3. Click **Add Environment Variable**

### Add Variable 1: SUPABASE_DB_URL_POOLER

```
Key:   SUPABASE_DB_URL_POOLER
Value: [Paste Transaction Mode URL from Step 1]
```

- [ ] `SUPABASE_DB_URL_POOLER` added

### Add Variable 2: SUPABASE_DB_URL_SESSION

```
Key:   SUPABASE_DB_URL_SESSION
Value: [Paste Session Mode URL from Step 1]
```

- [ ] `SUPABASE_DB_URL_SESSION` added

### Review Existing Variables

**Check these are also set:**
- [ ] `USE_SUPABASE` = `true`
- [ ] `SUPABASE_URL` = `https://YOUR_PROJECT.supabase.co`
- [ ] `SUPABASE_SERVICE_KEY` = `eyJ...` (service role key)

### Save Changes

4. Click **Save Changes**
5. Render will automatically trigger a deploy

- [ ] Environment variables saved
- [ ] Auto-deploy started

---

## Step 3: Monitor Deployment

1. Go to: https://dashboard.render.com/web/srv-xxxxx/logs
2. Watch for deployment progress

### Expected Log Output (SUCCESS):

```
[BUILD] Building Docker image...
[BUILD] ✅ Build complete
[DEPLOY] Deploying...
[DEPLOY] Container started
[APP] ✅ [POOL] Created connection pool for 'ai_infrastructure' (4-12 connections)
[APP] [POOL] Using Transaction Mode (port 6543) for 'ai_infrastructure'
[APP] ✅ [POOL] Got connection from pool for 'ai_infrastructure' (wait: 45.2ms)
[APP] INFO:flask_app: 🚀 Flask application started
```

- [ ] Build successful
- [ ] Deployment successful
- [ ] Connection pool created
- [ ] No database errors

### Unexpected Errors?

**If you see:**
```
❌ [DB] SUPABASE CONNECTION FAILED
server closed the connection unexpectedly
```

**Then:**
1. Check environment variables are spelled correctly
2. Verify URLs contain `:6543/` and `:5432/`
3. Check password special characters are URL-encoded
4. Verify Supabase project is active
5. Check Render IP is whitelisted in Supabase

---

## Step 4: Test OAuth Flows

### Test Microsoft Login

1. Go to: https://ai-agents-v10.onrender.com
2. Click **Login with Microsoft**
3. Enter credentials
4. Should redirect successfully

**Expected logs:**
```
INFO:flask_app: ➡️  GET /api/auth/microsoft/login
✅ [POOL] Got connection from pool
INFO:routes: 🔷 Initiating Microsoft login
INFO:flask_app: ⬅️  302 GET /api/auth/microsoft/login

INFO:flask_app: ➡️  GET /api/auth/microsoft/callback
✅ [POOL] Got connection from pool
✅ Microsoft authentication successful: user@example.com
```

- [ ] Microsoft login works
- [ ] No database errors in logs

### Test Google Login

1. Click **Login with Google**
2. Enter credentials
3. Should redirect successfully

- [ ] Google login works
- [ ] No database errors in logs

---

## Step 5: Run Connection Test (Optional)

### Local Test

```bash
cd c:\Users\gpoli\GIT\AI_agents

# Set environment variables (from .env.master or .env.supabase)
$env:SUPABASE_DB_URL_POOLER = "postgresql://..."
$env:SUPABASE_DB_URL_SESSION = "postgresql://..."

# Run test
python test_supabase_connection.py
```

**Expected output:**
```
SUPABASE CONNECTION TEST
======================================================================

1️⃣  Checking Environment Variables...
   ✅ SUPABASE_DB_URL_POOLER: postgresql://postgres.ryoicr...
   ✅ SUPABASE_DB_URL_SESSION: postgresql://postgres.ryoicr...

2️⃣  Testing Database Connection...
   Testing Transaction Mode (port 6543)...
   ✅ Connected successfully!
   ✅ Transaction Mode: WORKING

3️⃣  Testing Connection Pool...
   Creating connection pool for 'ai_infrastructure'...
   ✅ Connection pool created successfully!
   ✅ Test query successful!

TEST SUMMARY
======================================================================
Basic Connection:  ✅ PASS
Connection Pool:   ✅ PASS

🎉 All tests passed! Supabase connection is working.
```

- [ ] Local connection test passed

### Render Shell Test (if needed)

1. Go to Render dashboard → **Shell** tab
2. Run:
   ```bash
   python test_supabase_connection.py
   ```

- [ ] Render connection test passed

---

## Step 6: Commit Changes to Git

```bash
cd c:\Users\gpoli\GIT\AI_agents

# Check what changed
git status

# Add files
git add render.yaml
git add AI_infrastructure/shared/database_utils.py
git add FIX_SUPABASE_CONNECTION.md
git add RENDER_QUICK_FIX.md
git add SUPABASE_FIX_SUMMARY.md
git add SUPABASE_DEPLOYMENT_CHECKLIST.md
git add test_supabase_connection.py

# Commit
git commit -m "Fix: Add Supabase connection pooler environment variables

- Updated render.yaml with SUPABASE_DB_URL_POOLER and SUPABASE_DB_URL_SESSION
- Added backward compatibility fallback in database_utils.py
- Added documentation and test script
- Fixes 'server closed the connection unexpectedly' error
"

# Push to v10 branch
git push origin v10
```

- [ ] Changes committed
- [ ] Changes pushed to GitHub

---

## Step 7: Verify Production

### Health Check

```bash
curl https://ai-agents-v10.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-17T02:30:00Z"
}
```

- [ ] Health check returns 200 OK
- [ ] Database shows as connected

### System Check

```bash
curl https://ai-agents-v10.onrender.com/api/system/check
```

- [ ] System check passes
- [ ] All services operational

---

## Success Criteria

All items must be checked:

- [ ] ✅ Environment variables added to Render
- [ ] ✅ Deployment successful (no build errors)
- [ ] ✅ Connection pool created (logs show success)
- [ ] ✅ No database connection errors
- [ ] ✅ Microsoft OAuth works
- [ ] ✅ Google OAuth works
- [ ] ✅ Health check returns 200
- [ ] ✅ Changes committed to git

---

## 🎉 Deployment Complete!

**Estimated Total Time:** 30-45 minutes

