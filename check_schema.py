"""Check threads table schema"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n" + "=" * 70)
print("THREADS TABLE SCHEMA CHECK")
print("=" * 70)

cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()

print(f"\nTotal columns: {len(columns)}")
print("\n{:<5} {:<30} {:<10} {:<8} {:<20}".format("ID", "Name", "Type", "NotNull", "Default"))
print("-" * 70)

for col in columns:
    col_id, name, col_type, not_null, default_val, pk = col
    print(f"{col_id:<5} {name:<30} {col_type:<10} {not_null:<8} {default_val if default_val else 'NULL':<20}")

print("\n" + "=" * 70)

# Check for new columns
required_columns = [
    'tags', 'synergy_card_id', 'parent_thread_id', 
    'branch_point_message_id', 'branch_name', 'summary', 
    'summary_generated_at', 'location'
]

existing_column_names = [col[1] for col in columns]

print("\nNEW COLUMNS STATUS:")
print("-" * 70)

all_present = True
for col in required_columns:
    status = "✅" if col in existing_column_names else "❌ MISSING"
    print(f"{status} {col}")
    if col not in existing_column_names:
        all_present = False

print("\n" + "=" * 70)

if all_present:
    print("✅ ALL NEW COLUMNS PRESENT - Schema ready for thread features!")
else:
    print("❌ MISSING COLUMNS - Run migrate_threads.py")

print("=" * 70 + "\n")

conn.close()
