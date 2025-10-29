import sqlite3

conn = sqlite3.connect('C:/Users/gpoli/GIT/AI_agents/AI_infrastructure/data/sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== DATABASE SCHEMA ===\n")
for table in tables:
    if table[0]:
        print(table[0])
        print("\n")

# Get row count for each table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = [row[0] for row in cursor.fetchall()]

print("\n=== TABLE ROW COUNTS ===\n")
for table_name in table_names:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} rows")

conn.close()
