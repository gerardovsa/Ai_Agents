"""Check tables in ai_infrastructure.db"""
import sqlite3

db_path = r'C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("TABLES IN ai_infrastructure.db:")
print("=" * 80)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\n{table_name}:")
    
    # Get schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]:25s} {col[2]:15s}")

conn.close()
