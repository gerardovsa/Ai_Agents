"""
Fix corrupted sessions.db by creating complete schema with ALL required columns

CRITICAL FIXES:
1. Add threads.name column (required by thread_routes.py line 963)
2. Add users.password_hash column (required by auth, NOT NULL constraint)
3. Add user_gmail_accounts table (required by auth_routes.py line 229)
4. Add all missing columns from upgrade_database.py and user_auth.py
"""

import sqlite3
import os
import shutil
from pathlib import Path

data_dir = Path(__file__).parent / 'data'

print("=" * 80)
print("SESSIONS.DB COMPLETE SCHEMA RECOVERY")
print("=" * 80)

# Check files
sessions_db = data_dir / 'sessions.db'
backup_db = data_dir / 'sessions_incomplete_backup.db'
wal_file = data_dir / 'sessions.db-wal'
shm_file = data_dir / 'sessions.db-shm'

print(f"\nCurrent files:")
print(f"  sessions.db: {sessions_db.exists()}")
print(f"  sessions_incomplete_backup.db: {backup_db.exists()}")
print(f"  sessions.db-wal: {wal_file.exists()}")
print(f"  sessions.db-shm: {shm_file.exists()}")

# Backup existing incomplete database
if sessions_db.exists():
    print(f"\nBacking up incomplete sessions.db...")
    if backup_db.exists():
        backup_db.unlink()
    shutil.copy(sessions_db, backup_db)
    print(f"  Backed up to: {backup_db}")
    sessions_db.unlink()

# Remove WAL files
if wal_file.exists():
    print("Removing old WAL file...")
    wal_file.unlink()
if shm_file.exists():
    print("Removing old SHM file...")
    shm_file.unlink()

# Create fresh database with COMPLETE schema
print(f"\n{'=' * 80}")
print("Creating fresh sessions.db with COMPLETE schema...")
print("=" * 80)

conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()

# ========== THREADS TABLE (with name column) ==========
print("\n1. Creating threads table (WITH name column)...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_slug TEXT UNIQUE NOT NULL,
        workspace_id INTEGER,
        user_id INTEGER,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT,
        location TEXT,
        tags TEXT,
        synergy_card_id INTEGER,
        parent_thread_id INTEGER,
        branch_name TEXT,
        archived INTEGER DEFAULT 0
    )
""")

# ========== MESSAGES TABLE ==========
print("2. Creating messages table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id INTEGER,
        thread_id INTEGER NOT NULL,
        session_id TEXT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        prompt TEXT,
        response_data TEXT,
        user_id INTEGER,
        api_session_id TEXT,
        include BOOLEAN DEFAULT 1,
        feedback_score INTEGER,
        tool_calls TEXT,
        tokens_used INTEGER,
        model TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    )
""")

# ========== USERS TABLE (with password_hash column) ==========
print("3. Creating users table (WITH password_hash column)...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        primary_gmail TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
""")

# ========== USER_GMAIL_ACCOUNTS TABLE (SKIP - DEPRECATED) ==========
# DEPRECATED 2025-11-10: user_gmail_accounts moved to oauth_tokens in ai_infrastructure.db
# This table should NOT be in sessions.db
print("4. Skipping user_gmail_accounts (deprecated - use oauth_tokens in ai_infrastructure.db)...")
# cursor.execute("""...""")  # COMMENTED OUT - table belongs in ai_infrastructure.db, not sessions.db

# ========== USER_SESSIONS TABLE ==========
print("5. Creating user_sessions table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        session_token TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# ========== THREAD_USERS TABLE ==========
print("6. Creating thread_users table...")
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

# ========== THREAD_SHARES TABLE ==========
print("7. Creating thread_shares table...")
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

# ========== SAVED_THREADS TABLE ==========
print("8. Creating saved_threads table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(thread_id, user_id)
    )
""")

# ========== API_SESSIONS TABLE ==========
print("9. Creating api_sessions table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_session_id TEXT UNIQUE NOT NULL,
        workspace_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
""")

# ========== WORKSPACES TABLE ==========
print("10. Creating workspaces table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        owner_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
""")

# Create indexes for performance
print("\nCreating indexes...")
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)",
    "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_thread_users_thread_id ON thread_users(thread_id)",
    "CREATE INDEX IF NOT EXISTS idx_thread_users_user_id ON thread_users(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_thread_shares_thread_id ON thread_shares(thread_id)",
    "CREATE INDEX IF NOT EXISTS idx_thread_shares_shared_with ON thread_shares(shared_with)",
    "CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_threads_slug ON threads(thread_slug)",
    "CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads(updated_at)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token)",
    # "CREATE INDEX IF NOT EXISTS idx_user_gmail_accounts_user_id ON user_gmail_accounts(user_id)",  # DEPRECATED - table removed
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
]

for idx_sql in indexes:
    cursor.execute(idx_sql)

conn.commit()

# Verify schema
print(f"\n{'=' * 80}")
print("SCHEMA VERIFICATION")
print("=" * 80)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\nCreated {len(tables)} tables:")
for table in tables:
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"\n  {table[0]} ({count} rows):")
    for col in columns:
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        default = f" DEFAULT {col[4]}" if col[4] else ""
        print(f"    - {col[1]} {col[2]} {nullable}{default}")

# Verify critical columns exist
print(f"\n{'=' * 80}")
print("CRITICAL COLUMN VERIFICATION")
print("=" * 80)

checks = [
    ("threads", "name", "Required by thread_routes.py line 963"),
    ("users", "password_hash", "Required by auth (NOT NULL constraint)")
    # user_gmail_accounts removed - deprecated table, use oauth_tokens in ai_infrastructure.db instead
]

all_good = True
for table, column, reason in checks:
    if column:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if column in columns:
            print(f"  ✅ {table}.{column} - {reason}")
        else:
            print(f"  ❌ MISSING: {table}.{column} - {reason}")
            all_good = False
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cursor.fetchone():
            print(f"  ✅ {table} table exists - {reason}")
        else:
            print(f"  ❌ MISSING: {table} table - {reason}")
            all_good = False

conn.close()

print(f"\n{'=' * 80}")
if all_good:
    print("✅ SUCCESS! Complete schema created with all required columns")
else:
    print("❌ FAILED! Some critical columns/tables are still missing")
print("=" * 80)

print("\nNext steps:")
print("1. Start Flask: BISTART")
print("2. Test profile endpoint: http://localhost:5001/api/auth/profile")
print("3. Test thread assignments")
print("4. Verify no 'database is locked' errors")
print("5. If issues persist, check Flask logs")

print(f"\nBackups:")
print(f"  Incomplete schema: {backup_db}")
print(f"  Original corrupted: data/sessions_corrupted_backup.db")
