"""
Migration: Fix threads.workspace_id Column Type
from shared.database_utils import convert_sql_placeholders

Changes threads.workspace_id from TEXT to INTEGER for proper foreign key support.

LOCATION: sessions.db (NOT ai_infrastructure.db)
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def migrate_threads_workspace_id():
    """Change threads.workspace_id from TEXT to INTEGER"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'  # CRITICAL: threads table is in sessions.db
    
    print("="*70)
    print("MIGRATION: Fix threads.workspace_id Type (TEXT → INTEGER)")
    print("="*70)
    print(f"Database: {db_path}\n")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("PRAGMA table_info(threads)")
    columns = cursor.fetchall()
    
    workspace_id_col = None
    for col in columns:
        if col['name'] == 'workspace_id':
            workspace_id_col = col
            break
    
    if not workspace_id_col:
        print("❌ ERROR: threads.workspace_id column does not exist!")
        conn.close()
        return False
    
    print(f"Current state: workspace_id is {workspace_id_col['type']}")
    
    if workspace_id_col['type'] == 'INTEGER':
        print("✅ Column is already INTEGER - no migration needed")
        conn.close()
        return True
    
    print("\n[Step 1/5] Backing up current data...")
    cursor.execute("SELECT COUNT(*) as cnt FROM threads")
    thread_count = cursor.fetchone()['cnt']
    print(f"  Found {thread_count} threads to migrate")
    
    # Get current threads data
    sql, params = convert_sql_placeholders("""
        SELECT id, thread_slug, user_id, title, created_at, updated_at, 
               archived, tags, synergy_card_id, metadata, workspace_id,
               name, location, parent_thread_id, branch_point_message_id,
               branch_name, agent_id, message_count
        FROM threads
    """)
    threads_backup = cursor.fetchall()
    
    print(f"\n[Step 2/5] Creating new threads table with INTEGER workspace_id...")
    
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE threads_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'Untitled Thread',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archived INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            synergy_card_id TEXT,
            metadata TEXT DEFAULT '{}',
            workspace_id INTEGER,  -- CHANGED: TEXT → INTEGER
            name TEXT,
            location TEXT,
            parent_thread_id TEXT,
            branch_point_message_id TEXT,
            branch_name TEXT,
            agent_id TEXT DEFAULT 'prime',
            message_count INTEGER DEFAULT 0
        )
    """)
    print("  ✓ New table created")
    
    print(f"\n[Step 3/5] Copying {len(threads_backup)} threads...")
    
    # Copy data with type conversion
    for thread in threads_backup:
        # Convert workspace_id from TEXT to INTEGER
        workspace_id = thread['workspace_id']
        if workspace_id is not None:
            try:
                workspace_id = int(workspace_id)
            except (ValueError, TypeError):
                print(f"  ⚠️  Warning: Invalid workspace_id '{workspace_id}' for thread {thread['id']}, setting to NULL")
                workspace_id = None
        
        cursor.execute("""
            INSERT INTO threads_new (
                id, thread_slug, user_id, title, created_at, updated_at,
                archived, tags, synergy_card_id, metadata, workspace_id,
                name, location, parent_thread_id, branch_point_message_id,
                branch_name, agent_id, message_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            thread['id'], thread['thread_slug'], thread['user_id'], 
            thread['title'], thread['created_at'], thread['updated_at'],
            thread['archived'], thread['tags'], thread['synergy_card_id'],
            thread['metadata'], workspace_id, thread['name'], 
            thread['location'], thread['parent_thread_id'],
            thread['branch_point_message_id'], thread['branch_name'],
            thread['agent_id'], thread['message_count']
        ))

    cursor.execute(sql, params)
    
    print(f"  ✓ Copied {len(threads_backup)} threads")
    
    print("\n[Step 4/5] Replacing old table...")
    cursor.execute("DROP TABLE threads")
    cursor.execute("ALTER TABLE threads_new RENAME TO threads")
    print("  ✓ Table replaced")
    
    print("\n[Step 5/5] Verifying migration...")
    cursor.execute("PRAGMA table_info(threads)")
    columns = cursor.fetchall()
    
    workspace_id_col = None
    for col in columns:
        if col['name'] == 'workspace_id':
            workspace_id_col = col
            break
    
    cursor.execute("SELECT COUNT(*) as cnt FROM threads")
    final_count = cursor.fetchone()['cnt']
    
    if workspace_id_col['type'] == 'INTEGER' and final_count == thread_count:
        print(f"  ✓ Verification successful:")
        print(f"    - workspace_id is now INTEGER")
        print(f"    - {final_count} threads preserved")
        conn.commit()
        success = True
    else:
        print(f"  ❌ Verification failed!")
        print(f"    - Type: {workspace_id_col['type']} (expected INTEGER)")
        print(f"    - Count: {final_count} (expected {thread_count})")
        conn.rollback()
        success = False
    
    conn.close()
    
    print("\n" + "="*70)
    if success:
        print("✅ MIGRATION COMPLETE - threads.workspace_id is now INTEGER")
    else:
        print("❌ MIGRATION FAILED - changes rolled back")
    print("="*70)
    
    return success


if __name__ == '__main__':
    success = migrate_threads_workspace_id()
    sys.exit(0 if success else 1)
