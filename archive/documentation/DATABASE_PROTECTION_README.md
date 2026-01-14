# Database Protection System

## What Was Done

After the database corruption incident on November 9, 2025, we implemented a comprehensive protection system to prevent future data loss.

## 🛡️ Protection Features Implemented

### 1. Automatic Hourly Backups ✅

**Status:** ACTIVE

- Backups run every hour automatically
- Last 24 backups are kept (rolling window)
- Stored in: `data/backups/`
- Backup before backing up to prevent corrupting backups

**How it works:**
- Windows Task Scheduler runs: `python scripts/auto_backup.py` every hour
- Each backup is timestamped: `sessions_backup_YYYYMMDD_HHMMSS.db`
- Old backups are automatically deleted to save space

**Manual backup:**
```powershell
python scripts/auto_backup.py
```

**Check backup status:**
```powershell
# List all backups
dir data\backups\

# View scheduled task
schtasks /query /tn "AI_Agents_DB_Backup" /fo LIST /v
```

### 2. Database Safety Utilities ✅

**Location:** `AI_infrastructure/utils/db_safety.py`

**Features:**
- Health checks before operations
- Corruption detection
- Emergency backups on error
- Automatic repair attempts
- Connection pooling and timeouts

**Usage in code:**
```python
from AI_infrastructure.utils.db_safety import SafeConnection, check_database_health

# Safe connection with auto-rollback on error
with SafeConnection('data/sessions.db') as conn:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO...')
    # Auto-commits on success, rolls back on error

# Manual health check
if check_database_health('data/sessions.db'):
    print('Database is healthy')
```

### 3. Recovery Tools ✅

**restore_from_backup.py** - Attempts to recover data from corrupted backups
```powershell
python restore_from_backup.py
```

**rebuild_database.py** - Clean rebuild when recovery fails
```powershell
python rebuild_database.py
```

**fix_corrupted_database.py** - Comprehensive repair utility
```powershell
python fix_corrupted_database.py
```

## 📊 What Happened (November 9, 2025)

### The Incident
- Database file: `data/sessions.db`
- Error: `database disk image is malformed`
- Impact: All threads and messages lost
- Cause: SQLite corruption (likely concurrent writes or interrupted transaction)

### Recovery Attempt
- Created backup: `data/sessions_corrupt_20251109_135503.db`
- Tried to extract data: **Failed** (too corrupted)
- Result: Had to rebuild from scratch

### Lessons Learned
1. **Need automatic backups** - Now backing up hourly
2. **Need better error handling** - Now have db_safety.py
3. **Need quick recovery** - Now have multiple recovery scripts

## 🔧 How to Use

### Check Database Health
```powershell
python -c "from AI_infrastructure.utils.db_safety import check_database_health; print('Healthy' if check_database_health('data/sessions.db') else 'Corrupted')"
```

### Manual Backup Now
```powershell
python scripts/auto_backup.py
```

### Optimize Database (Prevent Corruption)
```python
from AI_infrastructure.utils.db_safety import optimize_database
optimize_database('data/sessions.db')
```

### Restore from Backup
```powershell
# 1. Stop Flask
BISTOP

# 2. Restore (picks latest backup automatically)
python restore_from_backup.py

# 3. Restart Flask
BISTART
```

## 📁 File Locations

```
AI_agents/
├── data/
│   ├── sessions.db              # Main database
│   ├── backups/                 # Hourly backups (last 24)
│   │   └── sessions_backup_*.db
│   └── emergency_backups/       # Created on error detection
│       └── sessions_emergency_*.db
├── scripts/
│   └── auto_backup.py          # Hourly backup script
├── AI_infrastructure/
│   └── utils/
│       └── db_safety.py        # Safety utilities
├── restore_from_backup.py      # Recovery tool
├── rebuild_database.py         # Clean rebuild tool
└── fix_corrupted_database.py   # Comprehensive repair
```

## ⚠️ Prevention Tips

### DO:
- ✅ Let auto-backup run (it's scheduled hourly)
- ✅ Stop Flask before manual database operations
- ✅ Use `SafeConnection` for database operations
- ✅ Check logs for "DATABASE ERROR" warnings

### DON'T:
- ❌ Kill Flask process forcefully (use BISTOP)
- ❌ Edit database while Flask is running
- ❌ Delete backups (kept automatically at 24)
- ❌ Ignore "database is locked" errors

## 🆘 Emergency Procedures

### If Database Won't Open:
```powershell
# 1. Check health
python -c "from AI_infrastructure.utils.db_safety import check_database_health; print(check_database_health('data/sessions.db'))"

# 2. Try to repair
python fix_corrupted_database.py

# 3. If repair fails, restore from backup
python restore_from_backup.py

# 4. Last resort: rebuild
python rebuild_database.py
```

### If Flask Won't Start:
```powershell
# 1. Check database
dir data\sessions.db

# 2. Check for corruption
python -c "import sqlite3; conn = sqlite3.connect('data/sessions.db'); print(conn.execute('PRAGMA integrity_check').fetchone())"

# 3. If corrupted, restore or rebuild
# See above
```

## 📈 Monitoring

### Check Backup Status:
```powershell
# How many backups?
(dir data\backups\sessions_backup_*.db).Count

# Latest backup?
dir data\backups\sessions_backup_*.db | Sort-Object LastWriteTime | Select-Object -Last 1
```

### Check Scheduled Task:
```powershell
# Is it running?
schtasks /query /tn "AI_Agents_DB_Backup"

# View task details
schtasks /query /tn "AI_Agents_DB_Backup" /fo LIST /v
```

## 🎯 Summary

**What you lost:**
- All threads and messages from before November 9, 2025 13:55

**What's now protected:**
- ✅ Hourly automatic backups (last 24 kept)
- ✅ Emergency backups on error detection
- ✅ Health checks before operations
- ✅ Automatic corruption detection
- ✅ Recovery tools ready to use

**What to do moving forward:**
- Just use the platform normally
- Backups happen automatically every hour
- If errors occur, emergency backups are created
- Recovery tools are ready if needed

---

**Last Updated:** November 9, 2025
**Status:** All systems operational
**Next Backup:** Automatic (every hour)
