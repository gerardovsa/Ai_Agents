import sqlite3

conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]

print("All tables in database:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    prefix = "_ARCHIVED_" if table.startswith("_ARCHIVED_") else ""
    marker = "🗄️  " if prefix else "📊 "
    print(f"{marker}{table}: {count} rows")

conn.close()
