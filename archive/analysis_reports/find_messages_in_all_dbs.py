"""Find messages table in all databases"""
import sqlite3
from pathlib import Path

# Find all .db files
base_paths = [
    Path(r'C:\Users\gpoli\GIT\In_House_SQL\G_Folder'),
    Path(r'C:\Users\gpoli\GIT\AI_agents'),
]

db_files = []
for base in base_paths:
    if base.exists():
        db_files.extend(base.rglob('*.db'))

print(f"Found {len(db_files)} database files\n")

for db_path in sorted(set(db_files)):
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        # Check for messages table
        if 'messages' in tables:
            print(f"\n{'='*100}")
            print(f"FOUND MESSAGES TABLE: {db_path}")
            print('='*100)
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
            print(f"Total messages: {count}")
            
            if count > 0:
                # Get recent messages
                cursor.execute("""
                    SELECT id, thread_id, role, 
                           SUBSTR(content, 1, 60) as preview,
                           created_at
                    FROM messages 
                    ORDER BY id DESC 
                    LIMIT 15
                """)
                rows = cursor.fetchall()
                
                print(f"\nRecent messages (last 15):")
                print(f"{'ID':<5} | {'Thread':<8} | {'Role':<10} | {'Preview':<60}")
                print('-'*95)
                for row in rows:
                    content = (row[3] or '').replace('\n', ' ')
                    print(f"{row[0]:<5} | {row[1]:<8} | {row[2]:<10} | {content:<60}")
                
                # Check for duplicate IDs or gaps
                cursor.execute("SELECT id FROM messages ORDER BY id")
                all_ids = [r[0] for r in cursor.fetchall()]
                if all_ids:
                    gaps = []
                    for i in range(len(all_ids)-1):
                        if all_ids[i+1] - all_ids[i] > 1:
                            gaps.append(f"{all_ids[i]}->{all_ids[i+1]}")
                    
                    print(f"\nID Analysis:")
                    print(f"  First ID: {all_ids[0]}")
                    print(f"  Last ID: {all_ids[-1]}")
                    print(f"  ID gaps: {', '.join(gaps) if gaps else 'None (sequential)'}")
        
        conn.close()
    except Exception as e:
        pass  # Skip databases we can't read

print("\n" + "="*100)
