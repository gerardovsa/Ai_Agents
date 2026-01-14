"""
Check the 2 assigned threads to see if they have email_thread_id
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n=== CHECKING ASSIGNED THREADS ===\n")

# Check thread 2120 (prime)
print("Thread 2120 - Invoice Payment Received (prime):")
row = execute_query("""
    SELECT id, thread_slug, location, email_thread_id, email_subject
    FROM sessions.threads
    WHERE user_id = %s AND id = %s
""", (14, 2120), fetch_mode='one')

if row:
    print(f"  Slug: {row['thread_slug']}")
    print(f"  Location: {row['location']}")
    print(f"  Email ID: {row['email_thread_id']}")
    print()

# Check thread 2112 (agent-2)
print("Thread 2112 - In House Tool Guide (agent-2):")
row = execute_query("""
    SELECT id, thread_slug, location, email_thread_id, email_subject
    FROM sessions.threads
    WHERE user_id = %s AND id = %s
""", (14, 2112), fetch_mode='one')

if row:
    print(f"  Slug: {row['thread_slug']}")
    print(f"  Location: {row['location']}")
    print(f"  Email ID: {row['email_thread_id']}")
    print()

# Check what API returns
print("\n=== WHAT API RETURNS ===\n")
api_rows = execute_query("""
    SELECT email_thread_id, thread_slug, location
    FROM sessions.threads
    WHERE user_id = %s
      AND email_thread_id IS NOT NULL
      AND location IS NOT NULL
      AND location != 'unassigned'
      AND location != ''
    ORDER BY updated_at DESC
""", (14,), fetch_mode='all')

print(f"API returns {len(api_rows)} mappings:")
for row in api_rows:
    print(f"  Thread {row['thread_slug']} ({row['location']})")
    print(f"    Email ID: {row['email_thread_id'][:80] if row['email_thread_id'] else 'NULL'}")
