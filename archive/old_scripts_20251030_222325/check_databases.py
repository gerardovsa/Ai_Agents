import sqlite3
import os

databases = [
    ('Root Level', 'AI_infrastructure/ai_infrastructure.db'),
    ('Data Folder', 'AI_infrastructure/data/ai_infrastructure.db'),
    ('Sessions DB', 'AI_infrastructure/data/sessions.db'),
]

for name, path in databases:
    print(f"\n{'='*60}")
    print(f"{name}: {path}")
    print(f"{'='*60}")
    
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ Exists: {size:,} bytes ({size/1024:.1f} KB)")
        
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"📊 Tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"   - {table_name}: {count} rows")
        
        conn.close()
    else:
        print(f"❌ Does not exist")
