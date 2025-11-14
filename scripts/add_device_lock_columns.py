"""
Add device lock columns to database
Run once to upgrade existing databases
"""

import sqlite3
from pathlib import Path

# Device registry goes in ai_infrastructure.db
AI_DB_PATH = Path(__file__).parent.parent / 'data' / 'ai_infrastructure.db'
# Threads table is in sessions.db
SESSIONS_DB_PATH = Path(__file__).parent.parent / 'data' / 'sessions.db'

def migrate():
    print("Starting device lock migration...\n")
    
    # Part 1: Migrate ai_infrastructure.db (device_registry and history)
    print("=== Migrating ai_infrastructure.db ===")
    conn_ai = sqlite3.connect(str(AI_DB_PATH))
    cursor_ai = conn_ai.cursor()
    
    try:
        # Create device_registry table
        cursor_ai.execute("""
            CREATE TABLE IF NOT EXISTS device_registry (
                device_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                device_name TEXT NOT NULL,
                device_fingerprint TEXT,
                last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        print("  Created device_registry table")
        
        # Create index
        cursor_ai.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_user 
            ON device_registry(user_id)
        """)
        
        # Create thread_lock_history table
        cursor_ai.execute("""
            CREATE TABLE IF NOT EXISTS thread_lock_history (
                lock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device_registry(device_id)
            )
        """)
        print("  Created thread_lock_history table")
        
        conn_ai.commit()
        print("  ai_infrastructure.db migration complete!\n")
        
    except Exception as e:
        conn_ai.rollback()
        print(f"  ERROR in ai_infrastructure.db: {e}\n")
    finally:
        conn_ai.close()
    
    # Part 2: Migrate sessions.db (threads table lock columns)
    print("=== Migrating sessions.db ===")
    if not SESSIONS_DB_PATH.exists():
        print("  WARNING: sessions.db not found - skipping thread lock columns\n")
        return
    
    conn_sessions = sqlite3.connect(str(SESSIONS_DB_PATH))
    cursor_sessions = conn_sessions.cursor()
    
    try:
        # Check if threads table exists
        cursor_sessions.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='threads'
        """)
        threads_table_exists = cursor_sessions.fetchone() is not None
        
        if threads_table_exists:
            # Add columns to threads table
            try:
                cursor_sessions.execute("""
                    ALTER TABLE threads 
                    ADD COLUMN locked_to_device_id TEXT DEFAULT NULL
                """)
                print("  Added locked_to_device_id column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("  locked_to_device_id column already exists")
                else:
                    raise
            
            try:
                cursor_sessions.execute("""
                    ALTER TABLE threads 
                    ADD COLUMN locked_at TIMESTAMP DEFAULT NULL
                """)
                print("  Added locked_at column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("  locked_at column already exists")
                else:
                    raise
            
            try:
                cursor_sessions.execute("""
                    ALTER TABLE threads 
                    ADD COLUMN lock_mode TEXT DEFAULT 'unlocked'
                """)
                print("  Added lock_mode column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("  lock_mode column already exists")
                else:
                    raise
            
            # Create index on locked_to_device_id
            cursor_sessions.execute("""
                CREATE INDEX IF NOT EXISTS idx_thread_locks 
                ON threads(locked_to_device_id)
            """)
            print("  Created index on locked_to_device_id")
        else:
            print("  WARNING: threads table not found in sessions.db")
        
        conn_sessions.commit()
        print("  sessions.db migration complete!\n")
        
    except Exception as e:
        conn_sessions.rollback()
        print(f"  ERROR in sessions.db: {e}\n")
        raise
    
    finally:
        conn_sessions.close()
    
    print("=== Migration Complete! ===")
    print("Summary:")
    print("  - device_registry table created in ai_infrastructure.db")
    print("  - thread_lock_history table created in ai_infrastructure.db")
    print("  - Lock columns added to threads table in sessions.db")
    print("\nYou can now use device locking features!")

if __name__ == '__main__':
    migrate()
