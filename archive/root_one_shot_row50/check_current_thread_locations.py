"""
Check current location values for threads with email IDs
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n=== CHECKING CURRENT THREAD LOCATIONS ===\n")

# Query threads with email_thread_id
rows = execute_query("""
    SELECT 
        id,
        thread_slug,
        location,
        email_thread_id,
        email_subject,
        updated_at
    FROM sessions.threads
    WHERE user_id = 14 
      AND email_thread_id IS NOT NULL
    ORDER BY updated_at DESC
    LIMIT 30
""", fetch_mode='all')

print(f"Found {len(rows)} threads with email_thread_id:\n")

assigned_count = 0
unassigned_count = 0

for row in rows:
    thread_id = row['id']
    slug = row['thread_slug']
    location = row['location']
    email_id = row['email_thread_id'][:50] + '...' if row['email_thread_id'] else 'None'
    subject = row['email_subject'][:40] if row['email_subject'] else 'No subject'
    updated = row['updated_at']
    
    if location and location != 'unassigned' and location != '':
        assigned_count += 1
        print(f"✅ ASSIGNED: {subject}")
        print(f"   Thread ID: {thread_id} | Slug: {slug}")
        print(f"   Location: {location}")
        print(f"   Updated: {updated}")
        print()
    else:
        unassigned_count += 1
        print(f"❌ UNASSIGNED: {subject}")
        print(f"   Thread ID: {thread_id} | Slug: {slug}")
        print(f"   Location: {location}")
        print(f"   Updated: {updated}")
        print()

print(f"\n📊 SUMMARY:")
print(f"   Assigned: {assigned_count}")
print(f"   Unassigned: {unassigned_count}")
print(f"   Total: {len(rows)}")

# Check what the API would return
print("\n=== WHAT API WOULD RETURN (with filters) ===\n")
api_rows = execute_query("""
    SELECT email_thread_id, thread_slug, location
    FROM sessions.threads
    WHERE user_id = 14 
      AND email_thread_id IS NOT NULL
      AND location IS NOT NULL
      AND location != 'unassigned'
      AND location != ''
    ORDER BY updated_at DESC
""", fetch_mode='all')

print(f"API returns {len(api_rows)} mappings:")
for row in api_rows:
    print(f"  '{row['email_thread_id'][:50]}...' -> '{row['thread_slug']}' (location: {row['location']})")
