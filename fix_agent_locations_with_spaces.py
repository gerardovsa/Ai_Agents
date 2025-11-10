"""
Fix thread assignments with trailing spaces in location column
e.g., 'agent-2 ' -> 'agent-2'
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("FIXING THREAD ASSIGNMENTS WITH SPACES")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find all assignments with trailing spaces
cursor.execute("""
    SELECT id, user_id, session_id, location 
    FROM thread_assignments 
    WHERE location != TRIM(location)
""")

bad_assignments = cursor.fetchall()

if not bad_assignments:
    print("\n✅ No assignments with trailing spaces found!")
else:
    print(f"\n❌ Found {len(bad_assignments)} assignments with trailing spaces:")
    
    for assign in bad_assignments:
        print(f"\n  ID: {assign['id']}")
        print(f"  User: {assign['user_id']}")
        print(f"  Session: {assign['session_id']}")
        print(f"  Location: '{assign['location']}' (length: {len(assign['location'])})")
        print(f"  Fixed: '{assign['location'].strip()}'")
    
    # Fix them
    print(f"\n🔧 Fixing {len(bad_assignments)} assignments...")
    
    cursor.execute("""
        UPDATE thread_assignments 
        SET location = TRIM(location)
        WHERE location != TRIM(location)
    """)
    
    conn.commit()
    print(f"✅ Fixed {cursor.rowcount} assignments!")

# Show all current assignments
print("\n" + "=" * 80)
print("CURRENT THREAD ASSIGNMENTS:")
print("=" * 80)

cursor.execute("""
    SELECT id, user_id, session_id, location, created_at
    FROM thread_assignments
    ORDER BY created_at DESC
""")

all_assignments = cursor.fetchall()
print(f"\nTotal assignments: {len(all_assignments)}")

for assign in all_assignments:
    print(f"\n  ID: {assign['id']}")
    print(f"  User: {assign['user_id']}")
    print(f"  Session: {assign['session_id']}")
    print(f"  Location: '{assign['location']}' (length: {len(assign['location'])})")
    print(f"  Created: {assign['created_at']}")

conn.close()
