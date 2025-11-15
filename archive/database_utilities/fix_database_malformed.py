"""
Fix "database disk image is malformed" Error
============================================

This error occurs when:
1. Multiple processes access DB simultaneously
2. WAL (Write-Ahead Log) corruption
3. Unclean shutdown

Solution:
1. STOP Flask server first
2. Checkpoint WAL mode
3. Run VACUUM to rebuild database
4. Verify integrity
"""

import sqlite3
import os
from pathlib import Path
import shutil
from datetime import datetime

# Paths
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / 'data'
DB_PATH = DATA_DIR / 'sessions.db'
BACKUP_PATH = DATA_DIR / f'sessions_before_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

print("=" * 70)
print("FIX: Database Disk Image Malformed Error")
print("=" * 70)

# Check if Flask is running
print("\n⚠️ IMPORTANT: Make sure Flask server is stopped!")
print("   Run: BISTOP (in another terminal)")
response = input("\n✋ Is Flask server stopped? (yes/no): ")

if response.lower() not in ['yes', 'y']:
    print("\n❌ Please stop Flask server first, then run this script again")
    exit(1)

# Step 1: Backup
print(f"\n[STEP 1] Creating backup...")
try:
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"✅ Backup: {BACKUP_PATH}")
except Exception as e:
    print(f"❌ Backup failed: {e}")
    exit(1)

# Step 2: Try to open and checkpoint
print(f"\n[STEP 2] Attempting to checkpoint database...")
try:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('PRAGMA journal_mode=DELETE')  # Disable WAL mode temporarily
    conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')  # Checkpoint any WAL data
    conn.commit()
    conn.close()
    print("✅ Checkpoint complete")
except Exception as e:
    print(f"⚠️ Checkpoint partial: {e}")

# Step 3: Dump to SQL and rebuild
print(f"\n[STEP 3] Dumping and rebuilding database...")
DUMP_FILE = DATA_DIR / 'sessions_dump.sql'
NEW_DB = DATA_DIR / 'sessions_rebuilt.db'

try:
    # Dump the database
    print("   Dumping data...")
    conn = sqlite3.connect(str(DB_PATH))
    with open(DUMP_FILE, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    conn.close()
    print(f"   ✅ Dumped to: {DUMP_FILE}")
    
    # Count records
    with open(DUMP_FILE, 'r', encoding='utf-8') as f:
        inserts = sum(1 for line in f if 'INSERT INTO' in line)
    print(f"   📊 Found {inserts} INSERT statements")
    
    # Create new database from dump
    print("   Creating fresh database...")
    if NEW_DB.exists():
        NEW_DB.unlink()
    
    new_conn = sqlite3.connect(str(NEW_DB))
    with open(DUMP_FILE, 'r', encoding='utf-8') as f:
        new_conn.executescript(f.read())
    new_conn.commit()
    new_conn.close()
    print("   ✅ Fresh database created")
    
    # Replace old with new
    print("   Replacing corrupted database...")
    DB_PATH.unlink()
    shutil.move(str(NEW_DB), str(DB_PATH))
    print("   ✅ Database replaced")
    
except Exception as e:
    print(f"❌ Rebuild failed: {e}")
    print(f"\n⚠️ Restoring backup...")
    if BACKUP_PATH.exists():
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print("✅ Backup restored")
    exit(1)

# Step 4: Verify new database
print(f"\n[STEP 4] Verifying repaired database...")
try:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Integrity check
    cursor.execute('PRAGMA integrity_check')
    result = cursor.fetchone()[0]
    
    if result == 'ok':
        print("✅ Integrity check: PASSED")
    else:
        print(f"⚠️ Integrity check: {result}")
    
    # Count records
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Database Statistics:")
    for table in tables:
        if not table.startswith('sqlite_'):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} records")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
    exit(1)

# Step 5: Clean up
print(f"\n[STEP 5] Cleaning up...")
try:
    if DUMP_FILE.exists():
        DUMP_FILE.unlink()
        print("✅ Removed temporary dump file")
except:
    pass

print("\n" + "=" * 70)
print("DATABASE REPAIR COMPLETE!")
print("=" * 70)
print(f"\n✅ Database repaired: {DB_PATH}")
print(f"✅ Backup saved: {BACKUP_PATH}")
print("\n🚀 You can now restart Flask server: BISTART")
print("\n⚠️ If issues persist, the backup is available for manual restoration")
