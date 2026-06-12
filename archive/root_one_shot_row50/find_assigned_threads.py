"""
Find all threads with agents assigned (not unassigned)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n=== ALL THREADS WITH AGENTS ASSIGNED ===\n")

# Get all threads with location that indicates an agent
assigned = execute_query("""
    SELECT 
        id,
        thread_slug,
        location,
        email_thread_id,
        email_subject,
        updated_at,
        metadata
    FROM sessions.threads
    WHERE user_id = %s
      AND (
          location = 'prime'
          OR location LIKE 'agent-%%'
      )
    ORDER BY updated_at DESC
    LIMIT 50
""", (14,), fetch_mode='all')

print(f"Found {len(assigned)} threads with agents:\n")

for row in assigned:
    subject = row['email_subject'] or 'No subject'
    print(f"{'='*80}")
    print(f"Thread: {subject[:60]}")
    print(f"  ID: {row['id']}")
    print(f"  Slug: {row['thread_slug']}")
    print(f"  Location: {row['location']}")
    print(f"  Updated: {row['updated_at']}")
    if row['email_thread_id']:
        print(f"  Email ID: {row['email_thread_id'][:80]}")
    else:
        print(f"  Email ID: None (no email linked)")
    print()
