import sqlite3

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

# Find threads with sess_ slugs
cursor.execute("SELECT * FROM threads WHERE thread_slug LIKE 'sess_%' LIMIT 1")
row = cursor.fetchone()

if row:
    cursor.execute('PRAGMA table_info(threads)')
    cols = cursor.fetchall()
    
    print("Thread with 'sess_' slug:")
    print("="*80)
    for i, col_info in enumerate(cols):
        col_name = col_info[1]
        col_type = col_info[2]
        value = row[i]
        print(f"{col_name} ({col_type}): {value} [type: {type(value).__name__}]")
else:
    print("No threads with 'sess_' slug found")

conn.close()

