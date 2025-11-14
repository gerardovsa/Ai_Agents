import sqlite3

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%prompt%'")
tables = cursor.fetchall()

print("Prompt-related tables:")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"    {col[1]} ({col[2]})")

conn.close()
