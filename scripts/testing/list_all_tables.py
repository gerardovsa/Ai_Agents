"""List all tables in database"""
import sqlite3

db_path = 'data/ai_infrastructure.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=== ALL TABLES IN DATABASE ===\n")
for table in tables:
    print(f"  - {table[0]}")
    
print(f"\nTotal: {len(tables)} tables")

conn.close()
