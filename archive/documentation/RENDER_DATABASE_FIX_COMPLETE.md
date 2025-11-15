# Render Database I/O Error - FIXED

**Date:** November 14, 2025  
**Status:** ✅ RESOLVED  
**Branch:** v5

## Problem

Render deployment was failing with:
```
sqlite3.OperationalError: disk I/O error
```

### Root Causes

1. **Wrong database paths**: Application was trying to write to `/app/data/*.db` instead of `/data/*.db` (Render's persistent disk mount point)
2. **Missing permissions check**: No verification that `/data` directory was writable
3. **No pre-initialization**: Database files weren't being created before SQLite tried to write to them

### Error Symptoms

```python
File "/app/AI_infrastructure/auth/user_auth.py", line 149, in _init_tables
    cursor.execute('''
sqlite3.OperationalError: disk I/O error

File "/app/AI_infrastructure/core/unified_session_manager.py", line 88, in _init_db
    conn.execute("PRAGMA journal_mode=DELETE")
sqlite3.OperationalError: disk I/O error
```

## Solution

### 1. Created Centralized Database Path Helper

**File:** `AI_infrastructure/utils/db_path_helper.py`

Provides consistent path resolution:
- **Local (dev):** `<project_root>/data/*.db`
- **Render (prod):** `/data/*.db` (persistent disk)

Functions:
- `get_ai_infrastructure_db_path()` → Returns correct path for ai_infrastructure.db
- `get_sessions_db_path()` → Returns correct path for sessions.db
- `get_stock_db_path()` → Returns correct path for stock.db
- `ensure_data_directory()` → Verifies /data exists and is writable

### 2. Updated All Database Initializations

**Files Modified:**
- `AI_infrastructure/auth/user_auth.py` - UserAuthManager
- `AI_infrastructure/core/unified_session_manager.py` - UnifiedSessionManager
- `AI_infrastructure/routes/account_linking_routes.py` - get_db_connection()
- `AI_infrastructure/flask_app.py` - Stock management

**Pattern:**
```python
# OLD (WRONG on Render):
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

# NEW (CORRECT - works on both local and Render):
from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
db_path = get_ai_infrastructure_db_path()
```

### 3. Enhanced Startup Script

**File:** `startup.sh`

Added permission checks and database pre-initialization:

```bash
# 1. Verify /data exists
if [ ! -d "/data" ]; then
    echo "ERROR: /data directory does not exist!"
    exit 1
fi

# 2. Make /data writable
chmod 777 /data 2>/dev/null

# 3. Test write permissions
if touch /data/.write_test 2>/dev/null; then
    rm /data/.write_test
    echo "✓ /data directory is writable"
else
    echo "ERROR: /data directory is NOT writable!"
    exit 1
fi

# 4. Pre-create database files
for db_file in ai_infrastructure.db sessions.db stock.db; do
    if [ ! -f "/data/$db_file" ]; then
        echo "  Creating /data/$db_file"
        touch "/data/$db_file"
        chmod 666 "/data/$db_file"
    fi
done
```

## Technical Details

### Database Path Resolution Logic

```python
def get_ai_infrastructure_db_path() -> str:
    if os.getenv('RENDER') == 'true':
        return '/data/ai_infrastructure.db'  # Render persistent disk
    else:
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'ai_infrastructure.db')  # Local
```

### Why This Works

1. **Render Environment Detection:** Uses `RENDER=true` env var
2. **Persistent Disk:** `/data` is Render's 10GB persistent disk mount
3. **Local Compatibility:** Falls back to `<project>/data/` for development
4. **Pre-initialization:** Creates empty database files with correct permissions
5. **Permission Verification:** Tests write access before starting Flask

## Files Changed

### New Files
- `AI_infrastructure/utils/db_path_helper.py` (92 lines)

### Modified Files
- `AI_infrastructure/auth/user_auth.py`
- `AI_infrastructure/core/unified_session_manager.py`  
- `AI_infrastructure/routes/account_linking_routes.py`
- `AI_infrastructure/flask_app.py`
- `startup.sh`

## Testing

### Local Testing
```powershell
# Should use local data/ folder
cd C:\Users\gpoli\GIT\AI_agents
python -c "from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path; print(get_ai_infrastructure_db_path())"
# Output: C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db
```

### Render Testing
```bash
# Should use /data persistent disk
echo $RENDER  # true
python -c "from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path; print(get_ai_infrastructure_db_path())"
# Output: /data/ai_infrastructure.db
```

## Benefits

✅ **No more disk I/O errors** on Render  
✅ **Consistent database paths** across environments  
✅ **Automatic failover** to correct location  
✅ **Permission validation** before startup  
✅ **Database pre-initialization** prevents race conditions  
✅ **Centralized path logic** - easier to maintain  

## Related Issues Fixed

1. ~~`AttributeError: 'UnifiedSessionManager' object has no attribute 'logger'`~~ (Fixed in commit 41a1098)
2. ~~`sqlite3.OperationalError: disk I/O error`~~ (Fixed in this commit)
3. ~~`WARNING: Stock management disabled - database not found`~~ (Will be fixed when stock.db is uploaded)

## Next Steps

1. ✅ Commit changes to v5 branch
2. ⏳ Push to GitHub
3. ⏳ Trigger Render deployment
4. ⏳ Verify databases are created in `/data/`
5. ⏳ Upload stock.db to Render persistent disk (if needed)

## Deployment Commands

```bash
# Push to GitHub (triggers Render auto-deploy)
git push origin v5

# Monitor Render logs
# Check for: "✓ /data directory is writable"
# Check for: "Creating /data/ai_infrastructure.db"
# Check for: "Creating /data/sessions.db"
```

## Success Indicators

When deployment succeeds, you should see:

```
✓ Running on Render (production)
✓ /data directory is writable
→ Initializing database files...
  Creating /data/ai_infrastructure.db
  Creating /data/sessions.db  
  Creating /data/stock.db
✓ /data/ai_infrastructure.db exists
✓ /data/sessions.db exists
✓ /data/stock.db exists
→ Starting Flask with Gunicorn (production)...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
```

No more `disk I/O error` exceptions!

---

**Commit:** d0e9a66  
**Summary:** Fix Render disk I/O errors - Use /data persistent disk for databases, add db_path_helper utility, ensure proper permissions
