"""Check what tables exist in synergy_sessions.db"""
import sqlite3

conn = sqlite3.connect('data/synergy_sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]

print(f"Tables in synergy_sessions.db: {tables}")

# Check if internal_docs exists
if 'internal_docs' in tables:
    cursor.execute("SELECT COUNT(*) FROM internal_docs")
    count = cursor.fetchone()[0]
    print(f"  internal_docs: {count} rows")
else:
    print("  internal_docs: TABLE DOES NOT EXIST")

conn.close()
