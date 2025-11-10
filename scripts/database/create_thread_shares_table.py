"""
Create thread_shares Table

Audit trail for thread sharing events and history.

LOCATION: sessions.db (NOT ai_infrastructure.db)
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_thread_shares_table():
    """Create thread_shares table for sharing audit trail"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'  # CRITICAL: threads are in sessions.db
    
    print("="*70)
    print("CREATE TABLE: thread_shares (Sharing Audit Trail)")
    print("="*70)
    print(f"Database: {db_path}\n")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_shares'
    """)
    
    if cursor.fetchone():
        print("⚠️  Table 'thread_shares' already exists")
        
        # Show current structure
        cursor.execute("PRAGMA table_info(thread_shares)")
        columns = cursor.fetchall()
        print(f"\nCurrent structure ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM thread_shares")
        row_count = cursor.fetchone()[0]
        print(f"\nCurrent rows: {row_count}")
        
        conn.close()
        return True
    
    print("[Step 1/3] Creating thread_shares table...")
    
    cursor.execute("""
        CREATE TABLE thread_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            shared_by_user_id INTEGER NOT NULL,
            shared_with_user_id INTEGER,
            shared_with_email TEXT,
            share_type TEXT NOT NULL DEFAULT 'direct',
            action TEXT NOT NULL,
            role_granted TEXT,
            share_token TEXT,
            share_link TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            accessed_at TIMESTAMP,
            revoked_at TIMESTAMP,
            revoked_by_user_id INTEGER,
            revoke_reason TEXT,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
        )
    """)
    print("  ✓ Table created")
    
    print("\n[Step 2/3] Creating indexes...")
    
    # Index for finding shares by thread
    cursor.execute("""
        CREATE INDEX idx_thread_shares_thread 
        ON thread_shares(thread_id, revoked_at)
    """)
    print("  ✓ idx_thread_shares_thread created")
    
    # Index for finding shares by user who shared
    cursor.execute("""
        CREATE INDEX idx_thread_shares_sharer 
        ON thread_shares(shared_by_user_id, created_at)
    """)
    print("  ✓ idx_thread_shares_sharer created")
    
    # Index for finding shares by recipient
    cursor.execute("""
        CREATE INDEX idx_thread_shares_recipient 
        ON thread_shares(shared_with_user_id, revoked_at)
    """)
    print("  ✓ idx_thread_shares_recipient created")
    
    # Index for token-based share lookups
    cursor.execute("""
        CREATE INDEX idx_thread_shares_token 
        ON thread_shares(share_token, revoked_at)
    """)
    print("  ✓ idx_thread_shares_token created")
    
    # Index for email-based share lookups
    cursor.execute("""
        CREATE INDEX idx_thread_shares_email 
        ON thread_shares(shared_with_email, revoked_at)
    """)
    print("  ✓ idx_thread_shares_email created")
    
    print("\n[Step 3/3] Verifying table structure...")
    
    cursor.execute("PRAGMA table_info(thread_shares)")
    columns = cursor.fetchall()
    
    expected_columns = [
        'id', 'thread_id', 'shared_by_user_id', 'shared_with_user_id',
        'shared_with_email', 'share_type', 'action', 'role_granted',
        'share_token', 'share_link', 'created_at', 'expires_at',
        'accessed_at', 'revoked_at', 'revoked_by_user_id', 'revoke_reason', 'metadata'
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
        print("✅ TABLE CREATED - thread_shares ready for audit trail")
    else:
        print("❌ TABLE CREATION FAILED - changes rolled back")
    print("="*70)
    
    return success


if __name__ == '__main__':
    success = create_thread_shares_table()
    sys.exit(0 if success else 1)
