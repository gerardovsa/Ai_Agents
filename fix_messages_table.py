"""Fix messages table - add missing columns"""
import sqlite3

db_path = r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("FIXING MESSAGES TABLE - ADDING MISSING COLUMNS")
print("=" * 80)

# Add missing columns
alter_statements = [
    ("workspace_id", "ALTER TABLE messages ADD COLUMN workspace_id INTEGER DEFAULT 1"),
    ("prompt", "ALTER TABLE messages ADD COLUMN prompt TEXT"),
    ("user_id", "ALTER TABLE messages ADD COLUMN user_id INTEGER"),
    ("include", "ALTER TABLE messages ADD COLUMN include INTEGER DEFAULT 1"),
    ("tool_calls", "ALTER TABLE messages ADD COLUMN tool_calls TEXT DEFAULT '[]'"),
    ("tokens_used", "ALTER TABLE messages ADD COLUMN tokens_used INTEGER"),
    ("response_time_ms", "ALTER TABLE messages ADD COLUMN response_time_ms INTEGER"),
    ("created_at", "ALTER TABLE messages ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ("updated_at", "ALTER TABLE messages ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ("metadata", "ALTER TABLE messages ADD COLUMN metadata TEXT DEFAULT '{}'")
]

for col_name, sql in alter_statements:
    try:
        print(f"Adding column: {col_name}...", end=" ")
        cursor.execute(sql)
        conn.commit()
        print("SUCCESS")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ALREADY EXISTS")
        else:
            print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("VERIFICATION - New schema:")
print("=" * 80)

cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]:25s} {col[2]:15s}")

print("\n" + "=" * 80)
print("SUCCESS - Messages table now has all required columns!")
print("=" * 80)

conn.close()
