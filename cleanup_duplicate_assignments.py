"""
Clean up duplicate thread assignments in database
Ensures ONE thread per agent (exclusive assignment)
"""

import sqlite3
import json

# Connect to database
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

print("=" * 60)
print("CLEANING UP DUPLICATE THREAD ASSIGNMENTS")
print("=" * 60)

# Get user metadata
cursor.execute("SELECT id, metadata FROM users WHERE id = 1")
row = cursor.fetchone()

if not row:
    print("❌ User ID 1 not found")
    conn.close()
    exit(1)

user_id, metadata_json = row

# Parse metadata
if metadata_json:
    metadata = json.loads(metadata_json)
else:
    metadata = {}

assignments = metadata.get('thread_assignments', {})

print(f"\n📦 Current assignments ({len(assignments)} total):")
for location, thread_id in assignments.items():
    print(f"  {location}: {thread_id}")

# Check for duplicates
seen_threads = {}
duplicates = []

for location, thread_id in assignments.items():
    if thread_id in seen_threads:
        duplicates.append({
            'thread_id': thread_id,
            'locations': [seen_threads[thread_id], location]
        })
        print(f"\n❌ DUPLICATE: Thread {thread_id} in both {seen_threads[thread_id]} AND {location}")
    else:
        seen_threads[thread_id] = location

if duplicates:
    print(f"\n🧹 Found {len(duplicates)} duplicate assignments, cleaning up...")
    
    # Keep only the LAST occurrence of each thread (most recent assignment)
    cleaned_assignments = {}
    for location, thread_id in assignments.items():
        # Remove any previous occurrence of this thread
        for loc in list(cleaned_assignments.keys()):
            if cleaned_assignments[loc] == thread_id:
                del cleaned_assignments[loc]
                print(f"  🗑️  Removed {thread_id} from {loc}")
        
        # Add current assignment
        cleaned_assignments[location] = thread_id
        print(f"  ✅ Kept {thread_id} in {location}")
    
    # Save cleaned assignments
    metadata['thread_assignments'] = cleaned_assignments
    cursor.execute("UPDATE users SET metadata = ? WHERE id = 1", [json.dumps(metadata)])
    conn.commit()
    
    print(f"\n✅ Cleaned! Now have {len(cleaned_assignments)} unique assignments:")
    for location, thread_id in cleaned_assignments.items():
        print(f"  {location}: {thread_id}")
else:
    print("\n✅ No duplicates found - database is clean!")

conn.close()

print("\n" + "=" * 60)
print("CLEANUP COMPLETE")
print("=" * 60)
