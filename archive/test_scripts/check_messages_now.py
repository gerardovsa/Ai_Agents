"""
Check messages in database after append-only fix
"""
import sqlite3
from pathlib import Path

# Connect to database - In_House_SQL project
db_path = Path(r'C:\Users\gpoli\GIT\In_House_SQL\G_Folder\data\sessions.db')
print(f"Connecting to: {db_path}")
print(f"Database exists: {db_path.exists()}")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get recent messages
cursor.execute("""
    SELECT id, thread_id, role, 
           SUBSTR(content, 1, 60) as content_preview, 
           created_at 
    FROM messages 
    ORDER BY id DESC 
    LIMIT 25
""")

rows = cursor.fetchall()

print("\n" + "="*110)
print("RECENT MESSAGES (Last 25, newest first)")
print("="*110)
print(f"{'ID':<5} | {'Thread':<8} | {'Role':<10} | {'Content Preview':<60} | {'Created':<19}")
print("-"*110)

for row in rows:
    msg_id, thread_id, role, content, created = row
    content = content.replace('\n', ' ') if content else ''
    print(f"{msg_id:<5} | {thread_id:<8} | {role:<10} | {content:<60} | {created}")

# Get total count
cursor.execute("SELECT COUNT(*) FROM messages")
total = cursor.fetchone()[0]

print("-"*110)
print(f"\nTotal messages in database: {total}")

# Group by thread
cursor.execute("""
    SELECT thread_id, COUNT(*) as msg_count
    FROM messages
    GROUP BY thread_id
    ORDER BY thread_id
""")

thread_counts = cursor.fetchall()
print(f"\nMessages per thread:")
for thread_id, count in thread_counts:
    print(f"  Thread {thread_id}: {count} messages")

conn.close()

print("\n" + "="*110)
print("ANALYSIS:")
print("  - Check if message IDs are sequential (no gaps = no deletions)")
print("  - Check if new messages were added to existing threads")
print("  - Old IDs should still exist if append-only mode is working")
print("="*110)
