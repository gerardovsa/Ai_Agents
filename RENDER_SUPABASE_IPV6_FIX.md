# Render Supabase IPv6 Connection Fix

## Problem

Production deployment fails with:
```
connection to server at "db.ryoicrdifiqhqpsnjmdo.supabase.co" (IPv6 address), port 6543 failed: Network is unreachable
```

**Root Cause:** Render doesn't support IPv6, but Supabase's direct database URL resolves to IPv6 addresses.

## Solution

Use **Supabase Session Pooler** which provides IPv4-only addresses.

## Correct Environment Variables for Render

### ❌ WRONG (Direct Database - has IPv6):
```bash
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.ryoicrdifiqhqpsnjmdo.supabase.co:6543/postgres
```

### ✅ CORRECT (Session Pooler - IPv4 only):
```bash
SUPABASE_DB_URL=postgresql://postgres.ryoicrdifiqhqpsnjmdo:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## How to Get the Correct URL

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select project: `ryoicrdifiqhqpsnjmdo`
3. Go to **Settings** → **Database**
4. Scroll to **Connection Pooling**
5. Select **Session** mode
6. Copy the **Connection string** (URI format)
7. Replace `[YOUR-PASSWORD]` with your actual database password

## Connection String Format

```
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**Components:**
- `postgres.PROJECT_REF` - Username with project reference
- `PASSWORD` - Database password (not the API key!)
- `aws-0-REGION.pooler.supabase.com` - IPv4 pooler endpoint
- `6543` - Session pooler port (use 5432 for Transaction mode)
- `postgres` - Database name

## How to Update Render Environment Variable

### Option 1: Render Dashboard (Recommended)
1. Go to https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0
2. Click **Environment** tab
3. Find `SUPABASE_DB_URL` variable
4. Click **Edit**
5. Replace with the **Session Pooler** URL from Supabase
6. Click **Save Changes**
7. Render will automatically redeploy

### Option 2: Render CLI
```bash
# Set environment variable
render env set SUPABASE_DB_URL "postgresql://postgres.ryoicrdifiqhqpsnjmdo:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres" -s srv-d4b2723uibrs73ff02t0

# Verify it's set
render env get SUPABASE_DB_URL -s srv-d4b2723uibrs73ff02t0

# Trigger manual deploy
render deploy -s srv-d4b2723uibrs73ff02t0
```

### Option 3: Python Script (Automated)
```python
import requests

service_id = "srv-d4b2723uibrs73ff02t0"
api_key = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
headers = {"Authorization": f"Bearer {api_key}"}

# Update environment variable
url = f"https://api.render.com/v1/services/{service_id}/env-vars"

# Get your actual password from Supabase Settings > Database
supabase_password = "YOUR_ACTUAL_PASSWORD_HERE"

payload = {
    "key": "SUPABASE_DB_URL",
    "value": f"postgresql://postgres.ryoicrdifiqhqpsnjmdo:{supabase_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
}

response = requests.put(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

## Verification Steps

After updating the environment variable:

1. **Wait for deployment** (3-5 minutes)
2. **Check logs** for:
   ```
   ✅ [DB] Connected to Supabase PostgreSQL (schema: ai_infrastructure)
   ```
3. **Test health endpoint**:
   ```bash
   curl https://ai-agents-backend-singapore.onrender.com/health
   ```
4. **Test database connection**:
   ```bash
   curl -X POST https://ai-agents-backend-singapore.onrender.com/api/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test", "user_id": 1}'
   ```

## Expected Success Output

**Before (IPv6 Error):**
```
connection to server at "db.ryoicrdifiqhqpsnjmdo.supabase.co" (2406:da1c:...), port 6543 failed: Network is unreachable
```

**After (Success):**
```
🔷 [DB] Attempting Supabase connection for 'ai_infrastructure'...
✅ [DB] Connected to Supabase PostgreSQL (schema: ai_infrastructure)
Loaded 594 tools from 35 implementations
INFO:waitress:Serving on http://0.0.0.0:10000
```

## Troubleshooting

### Still getting IPv6 error?
- Verify you used **Session Pooler** URL (contains `.pooler.supabase.com`)
- Check you used the correct password (not API key)
- Ensure port is `6543` for Session mode

### Connection timeout?
- Check Supabase project is active (not paused)
- Verify password is correct
- Try increasing `connect_timeout` in `database_utils.py`

### Authentication failed?
- Get password from: Supabase Dashboard → Settings → Database → **Reset Database Password**
- Update URL with new password
- Re-deploy on Render

## Region-Specific Pooler URLs

Supabase pooler URLs vary by region:

| Region | Pooler URL |
|--------|------------|
| US East | `aws-0-us-east-1.pooler.supabase.com` |
| US West | `aws-0-us-west-1.pooler.supabase.com` |
| EU Central | `aws-0-eu-central-1.pooler.supabase.com` |
| AP Southeast | `aws-0-ap-southeast-1.pooler.supabase.com` |

Your project (`ryoicrdifiqhqpsnjmdo`) uses **US East** region.

## Related Files

- `AI_infrastructure/shared/database_utils.py` - Database connection logic
- `AI_infrastructure/flask_app.py` - Flask app initialization
- `render.yaml` - Render deployment configuration
- `.env.master` - Local environment variables (not used in Render)

## Status

- ❌ **Current**: Using direct database URL (IPv6) → Connection fails
- ✅ **Fixed**: Use Session Pooler URL (IPv4) → Connection succeeds

## Next Steps

1. Update `SUPABASE_DB_URL` in Render dashboard with Session Pooler URL
2. Wait for automatic redeploy
3. Monitor deployment logs for `✅ Connected to Supabase PostgreSQL`
4. Test chat endpoint to verify full functionality
5. Commit this documentation to repository

---

**Last Updated:** 2025-11-16  
**Status:** Awaiting environment variable update in Render  
**Deployment:** srv-d4b2723uibrs73ff02t0 (ai-agents-backend-singapore)
