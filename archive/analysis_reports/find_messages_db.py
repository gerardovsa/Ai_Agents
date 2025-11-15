"""Find which database has the messages table"""
import sqlite3
from pathlib import Path

databases = [
    r'C:\Users\gpoli\GIT\In_House_SQL\G_Folder\data\sessions.db',
    r'C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure\data\sessions.db',
]

for db_path_str in databases:
    db_path = Path(db_path_str)
    if not db_path.exists():
        print(f"\nSkipping (doesn't exist): {db_path}")
        continue
    
    print(f"\n{'='*80}")
    print(f"Database: {db_path}")
    print('='*80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {', '.join([t[0] for t in tables])}")
        
        # Check for messages table
        if ('messages',) in tables:
            print("\nFOUND MESSAGES TABLE!")
            cursor.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
            print(f"Message count: {count}")
            
            # Get recent messages
            cursor.execute("""
                SELECT id, thread_id, role, 
                       SUBSTR(content, 1, 50) as preview,
                       created_at
                FROM messages 
                ORDER BY id DESC 
                LIMIT 10
            """)
            rows = cursor.fetchall()
            
            print(f"\n{'ID':<5} | {'Thread':<8} | {'Role':<10} | {'Preview':<50}")
            print('-'*85)
            for row in rows:
                print(f"{row[0]:<5} | {row[1]:<8} | {row[2]:<10} | {row[3] or '':<50}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*80)
