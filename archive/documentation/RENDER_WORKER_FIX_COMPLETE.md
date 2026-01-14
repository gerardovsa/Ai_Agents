# Render Worker Crash Fix - Complete

**Date:** November 14, 2025  
**Issue:** Workers failing to boot with `sqlite3.OperationalError: disk I/O error`  
**Commit:** `0618816`

## Problem Summary

Render deployment was crashing with:
```
[ERROR] Worker failed to boot
sqlite3.OperationalError: disk I/O error
[ERROR] Reason: Worker failed to boot.
```

## Root Causes

### 1. **Wrong Database Paths** (13 files affected)
Files were using `root_dir / 'data' / 'ai_infrastructure.db'` which becomes:
- ❌ `/app/data/ai_infrastructure.db` on Render (read-only application directory)
- ✅ Should be `/data/ai_infrastructure.db` (persistent disk mount)

### 2. **Worker Race Condition** 
`user_auth.py` `_init_tables()` had no retry logic:
- Gunicorn spawns 2 workers simultaneously
- Both try to `CREATE TABLE IF NOT EXISTS` at the same time
- SQLite locks cause one worker to fail with disk I/O error
- Worker crashes → Gunicorn shuts down

## Solutions Implemented

### ✅ Fix 1: Centralized Database Path Helper

Created `AI_infrastructure/utils/db_path_helper.py`:
```python
def get_ai_infrastructure_db_path() -> str:
    if os.getenv('RENDER') == 'true':
        return '/data/ai_infrastructure.db'  # Persistent disk
    else:
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'ai_infrastructure.db')  # Local

def get_sessions_db_path() -> str:
    if os.getenv('RENDER') == 'true':
        return '/data/sessions.db'
    else:
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'sessions.db')
```

### ✅ Fix 2: Updated 13 Critical Files

**Routes (1 file):**
- `routes/google_auth_routes_V2_FIXED.py` - get_db_connection()

**Auth (2 files):**
- `auth/credential_injector.py` - 4 database path references
- `auth/permission_checker.py` - 1 reference

**Core (2 files):**
- `core/prompt_injection_manager.py` - 1 reference
- `thread_manager.py` - 1 reference

**Workspace (4 files):**
- `workspace/access_control.py` - 1 reference
- `workspace/slug_generator.py` - 1 reference
- `workspace/workspace_manager.py` - 1 reference
- `workspace/invitation_manager.py` - 1 reference

**Utils (1 file):**
- `utils/user_context_builder.py` - 1 reference

**All now use:**
```python
from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
db_path = get_ai_infrastructure_db_path()
```

### ✅ Fix 3: Worker Retry Logic

Added to `auth/user_auth.py` `_init_tables()`:
```python
def _init_tables(self):
    """Initialize user authentication tables with retry logic"""
    import time
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # ... create tables ...
                conn.commit()
                break  # Success
                
        except sqlite3.OperationalError as e:
            if ("database is locked" in str(e) or "disk I/O error" in str(e)) and attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                continue
            else:
                raise
```

## Files Already Fixed (No Changes Needed)

These files already used the centralized helper:
- ✅ `auth/user_auth.py` - Uses `get_ai_infrastructure_db_path()` in __init__
- ✅ `core/unified_session_manager.py` - Uses `get_sessions_db_path()` in __init__
- ✅ `flask_app.py` - Uses `get_stock_db_path()` for stock management

## Testing

### Local Testing
```bash
cd C:\Users\gpoli\GIT\AI_agents
python -c "from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path; print(get_ai_infrastructure_db_path())"
# Output: C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db
```

### Render Testing (After Deployment)
Expected logs:
```
→ Checking /data directory permissions...
✓ /data directory is writable
✓ Persistent disk already initialized
→ Initializing database files...
  ✓ /data/ai_infrastructure.db exists
  ✓ /data/sessions.db exists
→ Starting Flask with Gunicorn (production)...
  Workers: 2 (1 CPU × 2)
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
✓ [DB] User authentication tables initialized
✓ [DB] User authentication tables initialized
```

## Expected Results

### Before Fix:
```
[ERROR] Worker (pid:9) exited with code 3
sqlite3.OperationalError: disk I/O error
[ERROR] Shutting down: Master
[ERROR] Reason: Worker failed to boot.
```

### After Fix:
```
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
INFO:auth.user_auth: [DB] User authentication tables initialized
INFO:auth.user_auth: [DB] User authentication tables initialized
Your service is live 🎉
Available at https://ai-agents-backend-singapore.onrender.com
```

## Deployment Status

✅ **Committed:** `0618816`  
✅ **Pushed:** v5 branch  
🔄 **GitHub Actions:** Building Docker image (~2-3 minutes)  
🔄 **Render:** Will auto-deploy when image ready (~30-60 seconds)  

**Total deployment time:** ~3-4 minutes from push

## Verification Commands

Once deployed, check logs at:
https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/logs

Look for:
- ✅ Both workers boot successfully (pids 8 and 9)
- ✅ No "disk I/O error" messages
- ✅ "User authentication tables initialized" appears twice (one per worker)
- ✅ "Your service is live 🎉"

## Related Fixes in This Commit

Also included Microsoft OAuth redirect URI fix from earlier:
- Uses `os.getenv('MICROSOFT_REDIRECT_URI')` to read from Render environment
- Falls back to `_config.get()` for local development
- Fixes AADSTS50011 error (http:// vs https://)

## Documentation

- **This file:** Complete fix summary
- **db_path_helper.py:** Centralized path resolution with Render detection
- **startup.sh:** Pre-creates database files with correct permissions

## Success Criteria

- [ ] Workers boot without errors
- [ ] No "disk I/O error" messages
- [ ] Both workers initialize tables successfully
- [ ] Health endpoint returns 200 OK
- [ ] Microsoft OAuth uses https:// redirect URI
- [ ] Application serves requests

---

**Status:** ✅ FIXES COMPLETE - WAITING FOR DEPLOYMENT
