"""Check database schemas for thread persistence"""
import sqlite3
import os

def check_schema(db_path, table_name):
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    
    if result:
        print(f"\n✅ {table_name} table in {os.path.basename(db_path)}:")
        print("-" * 80)
        print(result[0])
        print("-" * 80)
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            print(f"\n📊 Sample data ({len(rows)} rows):")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {', '.join(columns)}")
            for row in rows:
                print(f"  {row}")
        else:
            print("\n📊 Table is empty")
    else:
        print(f"\n❌ Table '{table_name}' not found in {os.path.basename(db_path)}")
    
    conn.close()

# Check all three databases
print("=" * 80)
print("DATABASE SCHEMA VERIFICATION")
print("=" * 80)

check_schema('data/synergy_sessions.db', 'synergy_sessions')
check_schema('data/sessions.db', 'threads')
check_schema('data/ai_infrastructure.db', 'thread_assignments')

print("\n" + "=" * 80)
print("SCHEMA CHECK COMPLETE")
print("=" * 80)
