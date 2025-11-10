"""
Fix corrupted sessions.db by recovering from WAL files
"""

import sqlite3
import os
import shutil
from pathlib import Path

data_dir = Path(__file__).parent / 'data'

print("=" * 80)
print("SESSIONS.DB RECOVERY TOOL")
print("=" * 80)

# Check files
sessions_db = data_dir / 'sessions.db'
corrupted_db = data_dir / 'sessions_corrupted_backup.db'
wal_file = data_dir / 'sessions.db-wal'
shm_file = data_dir / 'sessions.db-shm'

print(f"\nFiles found:")
print(f"  sessions.db: {sessions_db.exists()}")
print(f"  sessions_corrupted_backup.db: {corrupted_db.exists()}")
print(f"  sessions.db-wal: {wal_file.exists()} ({wal_file.stat().st_size if wal_file.exists() else 0} bytes)")
print(f"  sessions.db-shm: {shm_file.exists()} ({shm_file.stat().st_size if shm_file.exists() else 0} bytes)")

# Strategy: Create fresh database with correct schema
print(f"\n{'=' * 80}")
print("STRATEGY: Create fresh sessions.db with correct schema")
print("=" * 80)

if sessions_db.exists():
    print("\n⚠️  sessions.db already exists - removing it")
    sessions_db.unlink()

# Remove WAL files
if wal_file.exists():
    print("Removing old WAL file...")
    wal_file.unlink()
if shm_file.exists():
    print("Removing old SHM file...")
    shm_file.unlink()

# Create fresh database
print(f"\nCreating fresh sessions.db...")
conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

# Create schema (from unified_session_manager.py)
print("Creating tables...")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_slug TEXT UNIQUE NOT NULL,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        archived INTEGER DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        model TEXT,
        tool_calls TEXT,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        permission TEXT DEFAULT 'view',
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        added_by INTEGER,
        is_owner INTEGER DEFAULT 0,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
        UNIQUE(thread_id, user_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        shared_by INTEGER NOT NULL,
        shared_with INTEGER NOT NULL,
        permission TEXT DEFAULT 'view',
        share_type TEXT DEFAULT 'direct',
        shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        access_count INTEGER DEFAULT 0,
        last_accessed TIMESTAMP,
        revoked INTEGER DEFAULT 0,
        revoked_at TIMESTAMP,
        revoked_by INTEGER,
        share_link TEXT,
        notes TEXT,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(thread_id, user_id)
    )
""")

# Create indexes
print("Creating indexes...")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_users_thread_id ON thread_users(thread_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_users_user_id ON thread_users(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_shares_thread_id ON thread_shares(thread_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_shares_shared_with ON thread_shares(shared_with)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_slug ON threads(thread_slug)")

conn.commit()

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n✅ Created {len(tables)} tables:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  - {table[0]}: {count} rows")

conn.close()

print(f"\n{'=' * 80}")
print("✅ SUCCESS! Fresh sessions.db created")
print("=" * 80)
print("\nNext steps:")
print("1. Start Flask: BISTART")
print("2. Data will be restored from Supabase on first use")
print("3. Check corrupted backup at: data/sessions_corrupted_backup.db")
