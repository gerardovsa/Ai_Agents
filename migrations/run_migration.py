"""
Run Database Migration for Universal Task Sync
"""
import sqlite3
import os

DATABASE_PATH = 'data/synergy_sessions.db'
MIGRATION_FILE = 'migrations/001_add_task_sync.sql'

def run_migration():
    """Execute SQL migration file"""
    print(f"Running migration: {MIGRATION_FILE}")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Read migration SQL
    with open(MIGRATION_FILE, 'r') as f:
        sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Use executescript to handle multi-line statements and triggers
        cursor.executescript(sql)
        print("[SUCCESS] Migration completed successfully!")
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nDatabase tables: {', '.join(tables)}")
        
    except Exception as e:
        conn.rollback()
        print(f"[FAILED] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
