import sqlite3
import os

databases = {
    'ai_infrastructure.db': 'data/ai_infrastructure.db',
    'sessions.db': 'data/sessions.db',
    'synergy_sessions.db': 'data/synergy_sessions.db',
    'kanban_analytics.db': 'data/kanban_analytics.db',
    'stock_data.db': 'data/stock_data.db'
}

for db_name, db_path in databases.items():
    if not os.path.exists(db_path):
        print(f"\n{db_name}: NOT FOUND")
        continue
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n{'='*60}")
        print(f"{db_name}: {len(tables)} tables")
        print('='*60)
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {table_name:<40} {count:>6} rows")
            except Exception as e:
                print(f"  {table_name:<40} ERROR: {str(e)[:20]}")
        
        conn.close()
    except Exception as e:
        print(f"\n{db_name}: ERROR - {e}")
