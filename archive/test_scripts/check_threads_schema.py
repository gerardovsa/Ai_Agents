import sqlite3

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

# Get CREATE TABLE statement
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='threads'")
create_statement = cursor.fetchone()[0]
print("CREATE TABLE statement:")
print(create_statement)
print("\n" + "="*80 + "\n")

# Check for string values in integer columns
cursor.execute("""
    SELECT 
        id, 
        thread_slug, 
        parent_thread_id,
        typeof(parent_thread_id) as parent_type
    FROM threads 
    WHERE typeof(parent_thread_id) = 'text'
    LIMIT 5
""")

rows = cursor.fetchall()
if rows:
    print("Threads with TEXT parent_thread_id:")
    for row in rows:
        print(f"  ID: {row[0]}, slug: {row[1]}, parent_thread_id: {row[2]} (type: {row[3]})")
else:
    print("No threads with TEXT parent_thread_id found")

conn.close()
