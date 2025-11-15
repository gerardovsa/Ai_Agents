"""
Setup Automatic Database Backups
Creates a scheduled task to backup the database every hour
"""

import os
import shutil
from datetime import datetime

BACKUP_SCRIPT = """
import sqlite3
import shutil
import os
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = Path('data/sessions.db')
BACKUP_DIR = Path('data/backups')
MAX_BACKUPS = 24  # Keep last 24 hours

# Create backup directory
BACKUP_DIR.mkdir(exist_ok=True)

# Create backup with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = BACKUP_DIR / f'sessions_backup_{timestamp}.db'

try:
    # Check if database is healthy before backup
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('PRAGMA integrity_check')
    result = cursor.fetchone()
    conn.close()
    
    if result[0] == 'ok':
        # Database is healthy, create backup
        shutil.copy2(DB_PATH, backup_path)
        print(f'[OK] Backup created: {backup_path.name}')
        
        # Cleanup old backups (keep last MAX_BACKUPS)
        backups = sorted(BACKUP_DIR.glob('sessions_backup_*.db'))
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[:-MAX_BACKUPS]:
                old_backup.unlink()
                print(f'[CLEANUP] Removed old backup: {old_backup.name}')
    else:
        print(f'[ERROR] Database corrupted, skipping backup')
        
except Exception as e:
    print(f'[ERROR] Backup failed: {e}')
"""

# Write backup script
script_path = 'scripts/auto_backup.py'
os.makedirs('scripts', exist_ok=True)

with open(script_path, 'w') as f:
    f.write(BACKUP_SCRIPT)

print('[OK] Backup script created:', script_path)

# Create Windows Task Scheduler command
task_command = f"""
schtasks /create /tn "AI_Agents_DB_Backup" /tr "python {os.path.abspath(script_path)}" /sc hourly /f
"""

print()
print('=' * 60)
print('AUTOMATIC BACKUP SETUP')
print('=' * 60)
print()
print('[INFO] To enable automatic hourly backups, run this command:')
print()
print(task_command.strip())
print()
print('[INFO] Or manually run backups with:')
print(f'    python {script_path}')
print()
print('[INFO] Backups will be stored in: data/backups/')
print('[INFO] Last 24 backups will be kept')
