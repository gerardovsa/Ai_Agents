# 🚨 IMMEDIATE FIX - Supabase Connection on Render

## ⚡ 2-Minute Fix (Do This NOW)

1. **Go to Render Dashboard**
   ```
   https://dashboard.render.com/web/srv-xxxxx/env
   ```

2. **Click "Environment" tab**

3. **Add TWO new environment variables:**

   **Variable 1: SUPABASE_DB_URL_POOLER**
   ```
   Key: SUPABASE_DB_URL_POOLER
   Value: [See Step 4 below]
   ```

   **Variable 2: SUPABASE_DB_URL_SESSION**
   ```
   Key: SUPABASE_DB_URL_SESSION
   Value: [See Step 5 below]
   ```

4. **Get Transaction Mode URL (Port 6543)**
   - Go to: https://app.supabase.com/project/YOUR_PROJECT_ID/settings/database
   - Section: **Connection Pooling**
   - Mode: Select **Transaction**
   - **Copy the connection string** (it will look like):
     ```
     postgresql://postgres.ryoicrdifiqhqpsnjmdo:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
     ```
   - Paste into **SUPABASE_DB_URL_POOLER** in Render

5. **Get Session Mode URL (Port 5432)**
   - Same page in Supabase
   - Mode: Select **Session**
   - **Copy the connection string** (it will look like):
     ```
     postgresql://postgres.ryoicrdifiqhqpsnjmdo:YOUR_PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
     ```
   - Paste into **SUPABASE_DB_URL_SESSION** in Render

6. **Click "Save Changes"**

7. **Redeploy**
   - Render will automatically redeploy
   - OR click "Manual Deploy" → "Deploy latest commit"

8. **Monitor Logs**
   ```
   https://dashboard.render.com/web/srv-xxxxx/logs
   ```
   
   **Look for these SUCCESS messages:**
   ```
   ✅ [POOL] Created connection pool for 'ai_infrastructure' (4-12 connections)
   ✅ [POOL] Got connection from pool for 'ai_infrastructure' (wait: 45.2ms)
   ```

   **NO LONGER SEE these ERROR messages:**
   ```
   ❌ [DB] SUPABASE CONNECTION FAILED - UNEXPECTED ERROR
   server closed the connection unexpectedly
   ```

---

## 📋 Visual Guide: Where to Find Connection Strings

### Supabase Dashboard

1. Navigate to: **Settings** → **Database**
2. Scroll to: **Connection Pooling** section
3. You'll see this:

```
┌─────────────────────────────────────────────────────────┐
│ Connection Pooling                                       │
├─────────────────────────────────────────────────────────┤
│ Mode: [Transaction ▼] [Session]                         │
│                                                          │
│ Connection string:                                       │
│ postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION... │
│                                                [Copy]    │
└─────────────────────────────────────────────────────────┘
```

4. **For SUPABASE_DB_URL_POOLER:**
   - Select: **Transaction**
   - Look for: **:6543/** in the URL
   - Click **Copy**

5. **For SUPABASE_DB_URL_SESSION:**
   - Select: **Session**
   - Look for: **:5432/** in the URL
   - Click **Copy**

---

## ✅ Verification Checklist

After deployment completes:

- [ ] Logs show: `✅ [POOL] Created connection pool`
- [ ] Logs show: `[POOL] Using Transaction Mode (port 6543)`
- [ ] No errors: `server closed the connection unexpectedly`
- [ ] Microsoft OAuth login works
- [ ] Google OAuth login works
- [ ] Health check returns 200: https://ai-agents-v10.onrender.com/health

---

## 🔍 Troubleshooting

### Still seeing connection errors?

**Check 1: Environment variables set correctly**
```bash
# In Render Shell
echo $SUPABASE_DB_URL_POOLER
echo $SUPABASE_DB_URL_SESSION
```

Should output connection strings (not blank).

**Check 2: Password special characters**
If your password has special characters (`@`, `#`, `!`, etc.), they must be URL-encoded:

| Character | Encoded |
|-----------|---------|
| `@` | `%40` |
| `#` | `%23` |
| `!` | `%21` |
| `$` | `%24` |
| `%` | `%25` |
| `&` | `%26` |

Example:
```
Password: MyP@ss#123!
Encoded:  MyP%40ss%23123%21
```

**Check 3: Correct region**
Your connection string should match your Supabase region:
- Australia/Singapore: `aws-0-ap-southeast-1.pooler.supabase.com`
- US East: `aws-0-us-east-1.pooler.supabase.com`
- Europe: `aws-0-eu-central-1.pooler.supabase.com`

**Check 4: IP whitelist**
Render's IPs must be whitelisted in Supabase:
- Go to: Supabase → Settings → API → **IP Allow List**
- Option 1: Allow all IPs: `0.0.0.0/0` (development)
- Option 2: Add Render's IP ranges (more secure)

---

## 📝 What Changed?

### Before (BROKEN):
```yaml
# render.yaml (OLD)
- key: SUPABASE_DB_URL
  sync: false
```

Code looked for: `SUPABASE_DB_URL_POOLER` → **NOT FOUND** → Connection failed

### After (FIXED):
```yaml
# render.yaml (NEW)
- key: SUPABASE_DB_URL_POOLER
  sync: false
  
- key: SUPABASE_DB_URL_SESSION
  sync: false
```

Code finds: `SUPABASE_DB_URL_POOLER` → **FOUND** → Connection succeeds

---

## 🎯 Why Two Variables?

### SUPABASE_DB_URL_POOLER (Port 6543)
- **Primary connection**
- Transaction mode = Fast, short-lived connections
- Perfect for Flask web apps
- 200 client limit, 60 backend limit

### SUPABASE_DB_URL_SESSION (Port 5432)
- **Fallback connection**
- Session mode = Long-running connections
- Used for migrations, admin tasks
- 60 connection limit

The code tries **POOLER first**, falls back to **SESSION** if needed.

---

## 📞 Need Help?

If still having issues after following these steps:

1. Check Render logs for specific error messages
2. Verify Supabase is online: https://status.supabase.com
3. Test connection locally:
   ```bash
   psql "postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres"
   ```

---

## 🚀 After This Fix Works

Once connections are working:

1. **Commit the updated files:**
   ```bash
   git add render.yaml
   git add AI_infrastructure/shared/database_utils.py
   git commit -m "Fix: Add Supabase connection pooler environment variables"
   git push origin v10
   ```

2. **Test OAuth flows:**
   - Microsoft login
   - Google login
   - Token storage
   - User creation

3. **Monitor performance:**
   - Check connection pool stats in logs
   - Watch for connection leaks
   - Verify keepalives working

---

## ⏱️ Estimated Time to Fix

- **Reading this guide:** 3 minutes
- **Getting Supabase URLs:** 2 minutes
- **Adding to Render:** 1 minute
- **Deployment:** 1-2 minutes
- **Verification:** 1 minute

**Total:** ~10 minutes to complete fix

---

## 🎉 Success Indicators

You'll know it's working when you see:

```
INFO:flask_app: ➡️  GET /api/auth/microsoft/login
INFO:flask_app: 🔷 Initiating Microsoft login
✅ [POOL] Created connection pool for 'ai_infrastructure' (4-12 connections)
✅ [POOL] Got connection from pool for 'ai_infrastructure' (wait: 45.2ms)
INFO:flask_app: ⬅️  302 GET /api/auth/microsoft/login

INFO:flask_app: ➡️  GET /api/auth/microsoft/callback
✅ Microsoft authentication successful: printing@inhouseprint.com.au
INFO:flask_app: ⬅️  302 GET /api/auth/microsoft/callback
```

**NO MORE:**
```
❌ [DB] SUPABASE CONNECTION FAILED - UNEXPECTED ERROR
server closed the connection unexpectedly
```

