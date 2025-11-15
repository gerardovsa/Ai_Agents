"""
Migrate saved_threads table to new schema with agent_id and other metadata fields

This fixes: "table saved_threads has no column named agent_id"

Old schema: id, thread_id, user_id, saved_at
New schema: thread_id (PK), agent_id, session_id, user_id, location, thread_name, 
            conversation, message_count, context, created_at, saved_at, last_updated,
            tags, synergy_card_id, parent_thread_id, branch_point_message_id, 
            branch_name, summary, summary_generated_at
"""

import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent / 'data' / 'sessions.db'
    
    print(f"Migrating saved_threads table in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_threads'")
    if cursor.fetchone():
        print("  Found existing saved_threads table")
        
        # Check current columns
        cursor.execute("PRAGMA table_info(saved_threads)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"  Current columns: {', '.join(columns)}")
        
        # Check if migration needed
        if 'agent_id' in columns:
            print("  Table already has agent_id column - migration not needed")
            conn.close()
            return
        
        # Backup old data
        print("  Backing up old data...")
        cursor.execute("SELECT * FROM saved_threads")
        old_data = cursor.fetchall()
        print(f"  Backed up {len(old_data)} rows")
        
        # Drop old table
        print("  Dropping old table...")
        cursor.execute("DROP TABLE saved_threads")
        conn.commit()
    else:
        print("  No existing saved_threads table found")
        old_data = []
    
    # Create new table with updated schema
    print("  Creating new table with updated schema...")
    create_table_query = """
        CREATE TABLE IF NOT EXISTS saved_threads (
            thread_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_id INTEGER DEFAULT 1,
            location TEXT DEFAULT 'prime',
            thread_name TEXT,
            conversation TEXT NOT NULL,
            message_count INTEGER,
            context TEXT,
            created_at TEXT,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            tags TEXT DEFAULT '[]',
            synergy_card_id TEXT DEFAULT NULL,
            parent_thread_id TEXT DEFAULT NULL,
            branch_point_message_id TEXT DEFAULT NULL,
            branch_name TEXT DEFAULT NULL,
            summary TEXT DEFAULT NULL,
            summary_generated_at TEXT DEFAULT NULL
        )
    """
    cursor.execute(create_table_query)
    conn.commit()
    
    print("  Created new table successfully")
    
    # Restore old data if any (with default values for new columns)
    if old_data:
        print(f"  Restoring {len(old_data)} rows with default values for new columns...")
        for row in old_data:
            # Old schema: id, thread_id, user_id, saved_at
            old_id, thread_id, user_id, saved_at = row
            
            # Try to extract agent_id and session_id from thread_id (format: agent_id_session_id)
            parts = thread_id.split('_', 1)
            if len(parts) == 2:
                agent_id, session_id = parts
            else:
                agent_id = 'unknown'
                session_id = thread_id
            
            cursor.execute("""
                INSERT INTO saved_threads 
                (thread_id, agent_id, session_id, user_id, location, thread_name, 
                 conversation, message_count, context, saved_at, last_updated)
                VALUES (?, ?, ?, ?, 'prime', 'Migrated Thread', '[]', 0, '{}', ?, ?)
            """, (thread_id, agent_id, session_id, user_id, saved_at, saved_at))
        
        conn.commit()
        print(f"  Restored {len(old_data)} rows")
    
    # Verify new schema
    cursor.execute("PRAGMA table_info(saved_threads)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"  New columns: {', '.join(columns)}")
    
    conn.close()
    print("  Migration complete!")

if __name__ == '__main__':
    migrate()
