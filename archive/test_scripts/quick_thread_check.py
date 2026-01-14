import sqlite3

conn = sqlite3.connect('data/sessions.db')
c = conn.cursor()

print("THREADS TABLE COLUMNS:")
c.execute('PRAGMA table_info(threads)')
for row in c.fetchall():
    pk = "[PK]" if row[5] else ""
    print(f"  {row[1]:25} {row[2]:15} {pk}")

print("\nSample thread:")
c.execute('SELECT id, thread_slug, name, location FROM threads LIMIT 1')
row = c.fetchone()
if row:
    print(f"  ID: {row[0]}")
    print(f"  Slug: {row[1]}")
    print(f"  Name: {row[2]}")
    print(f"  Location: {row[3]}")

conn.close()
