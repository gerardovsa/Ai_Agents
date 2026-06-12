import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import execute_query

# Query threads with email assignments for user 14
query = '''
SELECT 
    id,
    thread_slug,
    location,
    email_thread_id,
    email_subject,
    name
FROM sessions.threads
WHERE user_id = 14 
  AND email_thread_id IS NOT NULL
ORDER BY updated_at DESC
LIMIT 20
'''

print('\n=== THREADS WITH EMAIL ASSIGNMENTS (User 14) ===\n')

rows = execute_query(query, fetch_mode='all')

print(f'Returned {len(rows) if rows else 0} rows')

if not rows:
    print('❌ NO THREADS WITH EMAIL ASSIGNMENTS FOUND')
    sys.exit(0)

has_agent = []
no_agent = []

for row in rows:
    thread_id, thread_slug, location, email_id, email_subject, name = row
    
    # Truncate long email IDs
    email_id_short = email_id[:60] + '...' if email_id and len(email_id) > 60 else email_id
    
    thread_info = {
        'thread_id': thread_id,
        'thread_slug': thread_slug,
        'location': location or 'NULL',
        'email_id': email_id,
        'email_id_short': email_id_short,
        'email_subject': email_subject or 'No subject',
        'name': name or 'Untitled'
    }
    
    # Check if has agent assignment
    if location and location != 'unassigned' and location != '':
        has_agent.append(thread_info)
    else:
        no_agent.append(thread_info)

print(f'\n✅ THREADS WITH AGENT ASSIGNED: {len(has_agent)}')
print('=' * 100)
for i, t in enumerate(has_agent, 1):
    print(f"\n{i}. Thread ID: {t['thread_id']} | Slug: {t['thread_slug']}")
    print(f"   Location (Agent): {t['location']}")
    print(f"   Email ID: {t['email_id_short']}")
    print(f"   Subject: {t['email_subject']}")
    print(f"   Name: {t['name']}")

print(f'\n\n❌ THREADS WITH NO AGENT (unassigned/NULL): {len(no_agent)}')
print('=' * 100)
for i, t in enumerate(no_agent, 1):
    print(f"\n{i}. Thread ID: {t['thread_id']} | Slug: {t['thread_slug']}")
    print(f"   Location: {t['location']}")
    print(f"   Email ID: {t['email_id_short']}")
    print(f"   Subject: {t['email_subject']}")
    print(f"   Name: {t['name']}")

# Test the mapping that API would return
print('\n\n=== API ENDPOINT SIMULATION ===')
print('Testing what /api/communication-hub/email-thread-mappings returns...\n')

mapping_query = '''
SELECT email_thread_id, thread_slug, location
FROM sessions.threads
WHERE user_id = 14 
  AND email_thread_id IS NOT NULL
ORDER BY updated_at DESC
'''

mapping_rows = execute_query(mapping_query, fetch_mode='all')
mappings = {}
for row in mapping_rows:
    email_id, thread_slug, location = row
    if email_id and thread_slug:
        mappings[email_id] = thread_slug

print(f'✅ API would return {len(mappings)} email-to-thread mappings')
print('\nFirst 10 mappings:')
print('=' * 100)
for i, (email_id, thread_slug) in enumerate(list(mappings.items())[:10], 1):
    email_short = email_id[:80] + '...' if len(email_id) > 80 else email_id
    print(f"{i}. Email: {email_short}")
    print(f"   → Thread Slug: {thread_slug}\n")

print(f'\n✅ RESULT: {len(mappings)} mappings would populate this.state.emailThreads')
print(f'   Frontend formatter would look up thread by slug: "{list(mappings.values())[0] if mappings else "N/A"}"')
