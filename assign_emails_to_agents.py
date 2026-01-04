"""
Assign specific emails to agents in the database
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n=== ASSIGNING EMAILS TO AGENTS ===\n")

# Define the assignments you want
assignments = [
    {
        'thread_slug': '1767452055170',
        'subject': 'Design',
        'agent': 'prime'
    },
    {
        'thread_slug': '1767451767853',
        'subject': 'RE: LNY Dimensions',
        'agent': 'agent-5'
    },
    {
        'thread_slug': '1767282765489',
        'subject': 'Carlo De Leon - business card request',
        'agent': 'agent-1'
    }
]

for assignment in assignments:
    print(f"Assigning: {assignment['subject']}")
    print(f"  Thread slug: {assignment['thread_slug']}")
    print(f"  Agent: {assignment['agent']}")
    
    # Update the thread location
    execute_query("""
        UPDATE sessions.threads
        SET location = %s,
            updated_at = NOW()
        WHERE user_id = %s
          AND thread_slug = %s
    """, (assignment['agent'], 14, assignment['thread_slug']))
    
    print(f"  ✅ Assigned!\n")

print("\n=== VERIFYING ASSIGNMENTS ===\n")

# Verify the assignments
for assignment in assignments:
    row = execute_query("""
        SELECT thread_slug, location, email_thread_id
        FROM sessions.threads
        WHERE user_id = %s
          AND thread_slug = %s
    """, (14, assignment['thread_slug']), fetch_mode='one')
    
    if row:
        print(f"Thread {row['thread_slug']}: location = {row['location']}")
        print(f"  Email ID: {row['email_thread_id'][:60] if row['email_thread_id'] else 'None'}...")
    else:
        print(f"Thread {assignment['thread_slug']}: NOT FOUND!")

print("\n=== API WOULD NOW RETURN ===\n")

# Check what API returns
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
    email_short = row['email_thread_id'][:50] + '...' if row['email_thread_id'] else 'None'
    print(f"  {email_short} → {row['thread_slug']} ({row['location']})")

print("\n✅ DONE! Now refresh the Communication Hub page to see the badges!")
