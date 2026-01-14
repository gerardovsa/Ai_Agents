"""Check messages table schema"""
import sqlite3

db_path = r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()

print("=" * 80)
print("MESSAGES TABLE SCHEMA:")
print("=" * 80)
for col in columns:
    print(f"{col[1]:20s} {col[2]:15s} NOT NULL: {col[3]} DEFAULT: {col[4]}")

print("\n" + "=" * 80)
print("ThreadManager.add_message() INSERT expects:")
print("=" * 80)
expected_cols = [
    'workspace_id',
    'thread_id',
    'role',
    'content',
    'prompt',
    'user_id',
    'include',
    'tool_calls',
    'tokens_used',
    'response_time_ms',
    'created_at',
    'updated_at',
    'metadata'
]

actual_cols = [col[1] for col in columns]

print("\nExpected columns:")
for col in expected_cols:
    exists = "EXISTS" if col in actual_cols else "MISSING"
    print(f"  {col:25s} {exists}")

print("\nActual columns:")
for col in actual_cols:
    print(f"  {col}")

conn.close()
