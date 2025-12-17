# 🔴 CRITICAL: Supabase Connection Failure - Root Cause Analysis

## Problem Summary

Your AI_agents deployment on Render is experiencing **persistent database connection failures**:

```
psycopg2.DatabaseError: server closed the connection unexpectedly
This probably means the server terminated abnormally before or while processing the request.
```

## Root Cause

**Environment Variable Mismatch**

The code expects these environment variables (from `database_utils.py` line 147-152):
- `SUPABASE_DB_URL_POOLER` (Transaction Mode, port 6543) - PRIMARY
- `SUPABASE_DB_URL_SESSION` (Session Mode, port 5432) - FALLBACK

But your `render.yaml` only defines:
- `SUPABASE_DB_URL` (line 136)

**Result:** The connection pool cannot find the database URL, attempts to connect with `None`, and fails.

---

## Why This Causes "Server Closed Connection"

1. Code tries to get `SUPABASE_DB_URL_POOLER` → returns `None`
2. Code tries to get `SUPABASE_DB_URL_SESSION` → returns `None`  
3. Code creates connection pool with `dsn=None`
4. psycopg2 attempts connection with invalid/null DSN
5. PostgreSQL server immediately closes the connection
6. Error: "server closed the connection unexpectedly"

---

## Fix #1: Update render.yaml (RECOMMENDED)

Replace the single `SUPABASE_DB_URL` with TWO environment variables:

```yaml
# ==================== Database Configuration ====================

# ✅ TRANSACTION MODE POOLER (PRIMARY) - Best for Flask/serverless
- key: SUPABASE_DB_URL_POOLER
  sync: false
  # Format: postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
  # Example: postgresql://postgres.ryoicrdifiqhqpsnjmdo:your-password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# ✅ SESSION MODE POOLER (FALLBACK) - For long-running connections
- key: SUPABASE_DB_URL_SESSION
  sync: false
  # Format: postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
  # Example: postgresql://postgres.ryoicrdifiqhqpsnjmdo:your-password@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

# ❌ REMOVE THIS (old variable)
# - key: SUPABASE_DB_URL
#   sync: false
```

---

## Fix #2: Add to Render Dashboard

1. Go to: https://dashboard.render.com/web/srv-xxxxx/env
2. Add TWO new environment variables:

**SUPABASE_DB_URL_POOLER** (Transaction Mode - Port 6543)
```
postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**SUPABASE_DB_URL_SESSION** (Session Mode - Port 5432)
```
postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

**Where to get the values:**

1. Go to Supabase dashboard: https://app.supabase.com/project/PROJECT_ID/settings/database
2. Scroll to **Connection Pooling** section
3. Mode: **Transaction**
4. Copy connection string (port 6543) → paste into `SUPABASE_DB_URL_POOLER`
5. Change mode to **Session**
6. Copy connection string (port 5432) → paste into `SUPABASE_DB_URL_SESSION`
7. Click **Save Changes** in Render

---

## Fix #3: Code Fallback (Quick Workaround)

If you want to keep using `SUPABASE_DB_URL`, modify `database_utils.py`:

**Location:** `AI_infrastructure/shared/database_utils.py` line 147-152

**Replace:**
```python
# Try Transaction Mode pooler first (optimal for Flask/serverless)
db_url = os.getenv('SUPABASE_DB_URL_POOLER')
connection_mode = 'Transaction Mode (port 6543)'

if not db_url:
    # Fallback to Session Mode pooler
    db_url = os.getenv('SUPABASE_DB_URL_SESSION')
    connection_mode = 'Session Mode (port 5432) - FALLBACK'
    cprint(f"[WARNING] [POOL] Transaction pooler not configured, using Session Mode fallback", Colors.WARNING)
```

**With:**
```python
# Try Transaction Mode pooler first (optimal for Flask/serverless)
db_url = os.getenv('SUPABASE_DB_URL_POOLER')
connection_mode = 'Transaction Mode (port 6543)'

if not db_url:
    # Fallback to Session Mode pooler
    db_url = os.getenv('SUPABASE_DB_URL_SESSION')
    connection_mode = 'Session Mode (port 5432) - FALLBACK'
    cprint(f"[WARNING] [POOL] Transaction pooler not configured, using Session Mode fallback", Colors.WARNING)

if not db_url:
    # Final fallback to old SUPABASE_DB_URL variable (backward compatibility)
    db_url = os.getenv('SUPABASE_DB_URL')
    connection_mode = 'Legacy SUPABASE_DB_URL (auto-detect port)'
    cprint(f"[WARNING] [POOL] Using legacy SUPABASE_DB_URL variable", Colors.WARNING)
```

---

## Why Two Connection Modes?

### Transaction Mode (Port 6543) - DEFAULT
- **Best for:** Flask, serverless, short-lived requests
- **How it works:** Each SQL statement is a transaction, connection released after
- **Limits:** 200 client connections, 60 backend connections
- **Speed:** Fastest for quick queries

### Session Mode (Port 5432) - FALLBACK  
- **Best for:** Long-running processes, migrations, admin tasks
- **How it works:** Connection stays open for entire session
- **Limits:** 60 total connections
- **Speed:** Slower to acquire, but keeps connection

---

## Verification Steps

After applying fix, verify connection:

```bash
# SSH into Render shell
# From Render dashboard → Shell tab

# Check environment variables
echo $SUPABASE_DB_URL_POOLER
echo $SUPABASE_DB_URL_SESSION

# Test connection
python3 << 'EOF'
import os
import psycopg2

# Test Transaction Mode
url = os.getenv('SUPABASE_DB_URL_POOLER')
print(f"Testing: {url[:50]}...")

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("✅ Transaction Mode connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

Expected output:
```
Testing: postgresql://postgres.ryoicrdifiqhqpsnjmdo:***...
✅ Transaction Mode connection successful!
```

---

## Current Connection Pool Settings

From `database_utils.py` (line 169-180):

```python
_connection_pools[schema_name] = pool.ThreadedConnectionPool(
    minconn=4,      # Keep 4 connections ready
    maxconn=12,     # Allow up to 12 concurrent connections
    dsn=db_url,
    sslmode='require',
    connect_timeout=10,
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=5
)
```

**Total potential connections:** 12 per schema × 3 schemas = **36 connections**  
**Supabase Nano limit:** 60 connections  
**Safety margin:** 24 connections (40% buffer)

---

## Expected Behavior After Fix

### Before (BROKEN):
```
[POOL] Using Transaction Mode for 'ai_infrastructure'
❌ [DB] SUPABASE CONNECTION FAILED - UNEXPECTED ERROR
Error: server closed the connection unexpectedly
```

### After (WORKING):
```
[POOL] Using Transaction Mode (port 6543) for 'ai_infrastructure'
✅ [POOL] Created connection pool for 'ai_infrastructure' (4-12 connections)
✅ [POOL] Got connection from pool for 'ai_infrastructure' (wait: 45.2ms)
```

---

## Summary - Choose One Fix

| Fix | Time | Difficulty | Recommendation |
|-----|------|-----------|----------------|
| **Fix #1: Update render.yaml** | 5 min | Easy | ✅ BEST - Permanent solution |
| **Fix #2: Render Dashboard** | 2 min | Very Easy | ✅ QUICKEST - Immediate fix |
| **Fix #3: Code Fallback** | 10 min | Medium | ⚠️ Workaround only |

**Recommended approach:**
1. Use **Fix #2** NOW (2 minutes, immediate relief)
2. Apply **Fix #1** later (permanent, version-controlled)
3. Commit updated `render.yaml` to git
4. Redeploy to apply infrastructure-as-code

---

## Next Steps

1. Choose a fix (recommend Fix #2 for immediate resolution)
2. Apply the fix
3. Monitor logs: `https://dashboard.render.com/web/srv-xxxxx/logs`
4. Test authentication: Try Microsoft/Google login
5. Verify: Should see `✅ [POOL] Created connection pool` in logs

---

## Questions?

- **"Which port should I use?"** → Port 6543 (Transaction Mode) for web apps
- **"Can I use both?"** → Yes! Code automatically tries 6543 first, falls back to 5432
- **"What if I only add one?"** → Transaction Mode (6543) is sufficient for Flask
- **"Is this why OAuth fails?"** → YES! Auth requires database to store tokens/state

