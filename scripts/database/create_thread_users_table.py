"""
Create thread_users Table

Enables multi-user thread access with role-based permissions.

LOCATION: sessions.db (NOT ai_infrastructure.db)
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_thread_users_table():
    """Create thread_users table for multi-user thread access"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'  # CRITICAL: threads are in sessions.db
    
    print("="*70)
    print("CREATE TABLE: thread_users (Multi-User Thread Access)")
    print("="*70)
    print(f"Database: {db_path}\n")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_users'
    """)
    
    if cursor.fetchone():
        print("⚠️  Table 'thread_users' already exists")
        
        # Show current structure
        cursor.execute("PRAGMA table_info(thread_users)")
        columns = cursor.fetchall()
        print(f"\nCurrent structure ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM thread_users")
        row_count = cursor.fetchone()[0]
        print(f"\nCurrent rows: {row_count}")
        
        conn.close()
        return True
    
    print("[Step 1/3] Creating thread_users table...")
    
    cursor.execute("""
        CREATE TABLE thread_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            access_level TEXT NOT NULL DEFAULT 'read',
            added_by_user_id INTEGER NOT NULL,
            added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            removed_at TIMESTAMP,
            last_accessed_at TIMESTAMP,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
            UNIQUE(thread_id, user_id, removed_at)
        )
    """)
    print("  ✓ Table created")
    
    print("\n[Step 2/3] Creating indexes...")
    
    # Index for finding threads by user
    cursor.execute("""
        CREATE INDEX idx_thread_users_user 
        ON thread_users(user_id, removed_at)
    """)
    print("  ✓ idx_thread_users_user created")
    
    # Index for finding users in thread
    cursor.execute("""
        CREATE INDEX idx_thread_users_thread 
        ON thread_users(thread_id, removed_at)
    """)
    print("  ✓ idx_thread_users_thread created")
    
    # Index for role-based queries
    cursor.execute("""
        CREATE INDEX idx_thread_users_role 
        ON thread_users(role, removed_at)
    """)
    print("  ✓ idx_thread_users_role created")
    
    print("\n[Step 3/3] Verifying table structure...")
    
    cursor.execute("PRAGMA table_info(thread_users)")
    columns = cursor.fetchall()
    
    expected_columns = [
        'id', 'thread_id', 'user_id', 'role', 'access_level',
        'added_by_user_id', 'added_at', 'removed_at', 'last_accessed_at', 'metadata'
    ]
    
    actual_columns = [col[1] for col in columns]
    
    if set(expected_columns) == set(actual_columns):
        print(f"  ✓ All {len(expected_columns)} columns created:")
        for col in columns:
            default = f" DEFAULT {col[4]}" if col[4] else ""
            pk = " (PRIMARY KEY)" if col[5] else ""
            print(f"    - {col[1]} ({col[2]}){default}{pk}")
        
        conn.commit()
        success = True
    else:
        print("  ❌ Column mismatch!")
        print(f"  Expected: {expected_columns}")
        print(f"  Actual: {actual_columns}")
        conn.rollback()
        success = False
    
    conn.close()
    
    print("\n" + "="*70)
    if success:
        print("✅ TABLE CREATED - thread_users ready for multi-user access")
    else:
        print("❌ TABLE CREATION FAILED - changes rolled back")
    print("="*70)
    
    return success


if __name__ == '__main__':
    success = create_thread_users_table()
    sys.exit(0 if success else 1)
