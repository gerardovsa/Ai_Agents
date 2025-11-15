"""
Fix thread locations with trailing spaces in location column
e.g., 'agent-2 ' -> 'agent-2'

NOTE: Uses threads.location (sessions.db) as primary source per architectural decision.
See: THREAD_LOCATION_ARCHITECTURE.md
"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'  # Changed from ai_infrastructure.db

print("=" * 80)
print("FIXING THREAD LOCATIONS WITH SPACES (using threads.location)")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find all threads with trailing spaces in location
cursor.execute("""
    SELECT id, thread_slug, name, location 
    FROM threads 
    WHERE location IS NOT NULL AND location != TRIM(location)
""")

bad_locations = cursor.fetchall()

if not bad_locations:
    print("\n✅ No threads with trailing spaces in location found!")
else:
    print(f"\n❌ Found {len(bad_locations)} threads with trailing spaces:")
    
    for thread in bad_locations:
        print(f"\n  ID: {thread['id']}")
        print(f"  Thread Slug: {thread['thread_slug']}")
        print(f"  Name: {thread['name']}")
        print(f"  Location: '{thread['location']}' (length: {len(thread['location'])})")
        print(f"  Fixed: '{thread['location'].strip()}'")
    
    # Fix them
    print(f"\n🔧 Fixing {len(bad_locations)} threads...")
    
    cursor.execute("""
        UPDATE threads 
        SET location = TRIM(location)
        WHERE location IS NOT NULL AND location != TRIM(location)
    """)
    
    conn.commit()
    print(f"✅ Fixed {cursor.rowcount} threads!")

# Show all current thread locations
print("\n" + "=" * 80)
print("CURRENT THREAD LOCATIONS:")
print("=" * 80)

cursor.execute("""
    SELECT id, thread_slug, name, location, created_at
    FROM threads
    WHERE location IS NOT NULL
    ORDER BY updated_at DESC
    LIMIT 20
""")

all_threads = cursor.fetchall()
print(f"\nTotal threads with locations: {len(all_threads)}")

for thread in all_threads:
    print(f"\n  ID: {thread['id']}")
    print(f"  Thread Slug: {thread['thread_slug']}")
    print(f"  Name: {thread['name']}")
    print(f"  Location: '{assign['location']}' (length: {len(assign['location'])})")
    print(f"  Created: {assign['created_at']}")

conn.close()
