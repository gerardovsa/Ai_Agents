"""
Check specific threads that should be assigned
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n=== CHECKING SPECIFIC THREADS ===\n")

# Check the threads mentioned in earlier logs
thread_slugs = ['1767452055170', '1767451767853', '1767282765489']

for slug in thread_slugs:
    row = execute_query("""
        SELECT 
            id,
            thread_slug,
            location,
            email_thread_id,
            email_subject,
            updated_at
        FROM sessions.threads
        WHERE user_id = 14 
          AND thread_slug = %s
    """, (slug,), fetch_mode='one')
    
    if row:
        print(f"Thread: {row['email_subject']}")
        print(f"  Slug: {row['thread_slug']}")
        print(f"  Location: {row['location']}")
        print(f"  Email ID: {row['email_thread_id'][:60]}...")
        print(f"  Updated: {row['updated_at']}")
        print()
    else:
        print(f"Thread {slug} not found!\n")

# Now check what threads ARE assigned
print("\n=== ALL ASSIGNED THREADS (location != 'unassigned') ===\n")
assigned = execute_query("""
    SELECT 
        id,
        thread_slug,
        location,
        email_thread_id,
        email_subject
    FROM sessions.threads
    WHERE user_id = 14 
      AND location IS NOT NULL
      AND location != 'unassigned'
      AND location != ''
    ORDER BY updated_at DESC
    LIMIT 20
""", fetch_mode='all')

print(f"Found {len(assigned)} assigned threads:")
for row in assigned:
    print(f"  {row['email_subject'][:40]:40} → {row['location']:10} (slug: {row['thread_slug']})")
    if row['email_thread_id']:
        print(f"    Email ID: {row['email_thread_id'][:60]}...")
