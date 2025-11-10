"""
Clear user 12's phantom thread assignments
"""

import sqlite3
import json
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

print(f"Clearing user 12 metadata in: {db_path}")
print("=" * 60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Show before
cursor.execute("SELECT metadata FROM users WHERE id = 12")
row = cursor.fetchone()
if row and row[0]:
    metadata = json.loads(row[0])
    assignments = metadata.get('thread_assignments', {})
    print(f"\nBEFORE: User 12 has {len(assignments)} thread assignments:")
    for loc, thread_id in assignments.items():
        print(f"  {loc} → {thread_id}")
else:
    print("\nBEFORE: User 12 has no metadata")

# Clear
cursor.execute("""
    UPDATE users
    SET metadata = '{}',
        last_active = CURRENT_TIMESTAMP
    WHERE id = 12
""")

conn.commit()

# Show after
cursor.execute("SELECT metadata FROM users WHERE id = 12")
row = cursor.fetchone()
if row and row[0]:
    metadata = json.loads(row[0])
    assignments = metadata.get('thread_assignments', {})
    print(f"\nAFTER: User 12 has {len(assignments)} thread assignments")
    if assignments:
        for loc, thread_id in assignments.items():
            print(f"  {loc} → {thread_id}")
else:
    print("\nAFTER: User 12 metadata cleared successfully ✅")

conn.close()

print("\n" + "=" * 60)
print("✅ User 12 metadata cleared")
print("🔄 Refresh browser to see clean slate")
print("=" * 60)
