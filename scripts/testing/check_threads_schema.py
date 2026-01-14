"""Check threads table schema"""
import sqlite3

db_path = 'data/ai_infrastructure.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== THREADS TABLE SCHEMA ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='threads'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("threads table not found")

print("\n\n=== THREAD_ASSIGNMENTS TABLE SCHEMA ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='thread_assignments'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("thread_assignments table not found")

print("\n\n=== MESSAGES TABLE SCHEMA (first 500 chars) ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='messages'")
result = cursor.fetchone()
if result:
    print(result[0][:500] + "...")
else:
    print("messages table not found")

print("\n\n=== CHECKING FOR WORKSPACE REFERENCES ===\n")

# Check if threads has workspace_id
cursor.execute("PRAGMA table_info(threads)")
threads_cols = cursor.fetchall()
has_workspace = any(col[1] == 'workspace_id' for col in threads_cols)
print(f"threads.workspace_id exists: {has_workspace}")

if has_workspace:
    cursor.execute("SELECT COUNT(*) FROM threads WHERE workspace_id IS NOT NULL")
    count = cursor.fetchone()[0]
    print(f"Threads with workspace_id: {count}")

# Check threads table columns
print("\n=== THREADS TABLE COLUMNS ===")
for col in threads_cols:
    print(f"  {col[1]} ({col[2]})")

conn.close()
