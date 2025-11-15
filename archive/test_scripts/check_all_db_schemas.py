"""Check all database schemas"""
import sqlite3

db_path = r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("SESSIONS.DB - ALL TABLES")
print("=" * 80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"\nTable: {table[0]}")

print("\n" + "=" * 80)
print("MESSAGES TABLE - FULL SCHEMA")
print("=" * 80)

cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]:25s} {col[2]:15s} NOT NULL: {col[3]}")

print("\n" + "=" * 80)
print("COMPARING WITH DATABASE_SCHEMA_COMPLETE.sql")
print("=" * 80)

expected_from_complete_schema = [
    'id',
    'workspace_id',
    'thread_id',
    'session_id',
    'role',
    'content',
    'prompt',
    'response_data',
    'user_id',
    'api_session_id',
    'include',
    'feedback_score',
    'tool_calls',
    'tokens_used',
    'response_time_ms',
    'embedding_vector',
    'created_at',
    'updated_at',
    'metadata'
]

actual_cols = [col[1] for col in columns]

print("\nMISSING columns from DATABASE_SCHEMA_COMPLETE.sql:")
for col in expected_from_complete_schema:
    if col not in actual_cols:
        print(f"  MISSING: {col}")

print("\nEXTRA columns not in DATABASE_SCHEMA_COMPLETE.sql:")
for col in actual_cols:
    if col not in expected_from_complete_schema:
        print(f"  EXTRA: {col}")

conn.close()
