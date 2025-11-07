import sqlite3
from pathlib import Path

db_path = Path('data/sessions.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get threads table structure
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()

print("Current 'threads' table structure:")
print("=" * 60)
for col in columns:
    print(f"{col[1]:30s} {col[2]:15s} {'NOT NULL' if col[3] else ''} {'DEFAULT ' + str(col[4]) if col[4] else ''}")

print("\n" + "=" * 60)
print("Checking for new columns needed:")
print("=" * 60)

existing_cols = [col[1] for col in columns]
new_columns = ['tags', 'synergy_card_id', 'parent_thread_id', 'branch_point_message_id', 'branch_name', 'summary', 'summary_generated_at']

for new_col in new_columns:
    if new_col in existing_cols:
        print(f"✓ {new_col:30s} ALREADY EXISTS")
    else:
        print(f"✗ {new_col:30s} NEEDS TO BE ADDED")

conn.close()
