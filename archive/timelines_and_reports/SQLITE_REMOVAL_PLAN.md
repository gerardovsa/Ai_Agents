# SQLite Removal/Supabase Migration Plan

## Problem
100+ files have hardcoded SQLite `sqlite3.connect()` calls that bypass Supabase on Render.

## Files Requiring Changes (Priority Order)

### CRITICAL - Core Auth & User Management (MUST FIX FIRST):
1. `AI_infrastructure/auth/user_auth.py` - **17 sqlite3.connect()** calls
2. `AI_infrastructure/auth/credential_injector.py` - **4 sqlite3.connect()** calls  
3. `AI_infrastructure/auth/permission_checker.py` - **1 sqlite3.connect()** call
4. `AI_infrastructure/builders/user_profile_builder.py` - **1 sqlite3.connect()** call
5. `AI_infrastructure/builders/credential_fetcher.py` - **1 sqlite3.connect()** call

### HIGH PRIORITY - Scheduler & Routes:
6. `AI_infrastructure/scheduler.py` - **12 sqlite3.connect()** calls
7. `AI_infrastructure/routes/automation_routes.py` - **2 sqlite3.connect()** calls
8. `AI_infrastructure/routes/account_linking_routes.py` - **1 import sqlite3**

### MEDIUM PRIORITY - Migrations (Already wrapped, just needs testing):
9. All files in `AI_infrastructure/migrations/` - Skip on Render (done)

### LOW PRIORITY - Database Toolkit (Dev tools only):
10. `AI_infrastructure/database_toolkit/*` - 5 files (dev tools, not used in production)

## Solution Strategy

### Option 1: Global Replace (RECOMMENDED)
Replace ALL `sqlite3.connect()` with `get_database_connection()`:

```python
# OLD (SQLite only):
conn = sqlite3.connect(str(db_path))

# NEW (Supabase-aware):
from shared.database_utils import get_database_connection
conn = get_database_connection('ai_infrastructure')  # or 'sessions', 'synergy_sessions'
```

### Option 2: Wrapper Function (SAFER)
Create compatibility wrapper:

```python
def get_db_connection_safe(db_name='ai_infrastructure'):
    """Get database connection (Supabase on Render, SQLite locally)"""
    import os
    if os.getenv('USE_SUPABASE') == 'true' or os.getenv('RENDER') == 'true':
        from shared.database_utils import get_database_connection
        return get_database_connection(db_name)
    else:
        import sqlite3
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / f'{db_name}.db'
        return sqlite3.connect(str(db_path))
```

## Files Changed So Far
- ✅ `AI_infrastructure/flask_app.py` - Wrapped migrations in USE_SUPABASE check
- ✅ `AI_infrastructure/migrations/add_refresh_attempts_column.py` - Added early return

## Next Steps
1. Create `AI_infrastructure/shared/db_connection_wrapper.py` with safe wrapper
2. Replace all `sqlite3.connect()` in critical files (auth, scheduler)
3. Test locally (SQLite) and on Render (Supabase)
4. Deploy

## Estimated Impact
- **24+ critical files** need changes
- **100+ sqlite3.connect() calls** to replace
- **Risk**: Medium (need to preserve SQLite for local dev)
