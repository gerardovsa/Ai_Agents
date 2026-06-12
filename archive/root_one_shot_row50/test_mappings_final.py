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

print(f'Returned {len(rows) if rows else 0} rows\n')

if not rows:
    print('❌ NO THREADS WITH EMAIL ASSIGNMENTS FOUND')
    sys.exit(0)

has_agent = []
no_agent = []

for row in rows:
    # Row is a dict, not a tuple
    thread_id = row['id']
    thread_slug = row['thread_slug']
    location = row['location']
    email_id = row['email_thread_id']
    email_subject = row['email_subject']
    name = row['name']
    
    # Truncate long email IDs
    email_id_short = email_id[:80] + '...' if email_id and len(email_id) > 80 else email_id
    
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

print(f'✅ THREADS WITH AGENT ASSIGNED: {len(has_agent)}')
print('=' * 120)
for i, t in enumerate(has_agent, 1):
    print(f"\n{i}. ID: {t['thread_id']} | Slug: {t['thread_slug']} | Agent: {t['location']}")
    print(f"   Email: {t['email_id_short']}")
    print(f"   Subject: {t['email_subject']}")

print(f'\n\n❌ THREADS WITH NO AGENT: {len(no_agent)}')
print('=' * 120)
for i, t in enumerate(no_agent, 1):
    print(f"\n{i}. ID: {t['thread_id']} | Slug: {t['thread_slug']} | Location: {t['location']}")
    print(f"   Email: {t['email_id_short']}")
    print(f"   Subject: {t['email_subject']}")

# Test the mapping that API would return
print('\n\n=== WHAT THE FRONTEND RECEIVES ===')
print('Simulating /api/communication-hub/email-thread-mappings response...\n')

mapping_rows = execute_query(query, fetch_mode='all')
mappings = {}
for row in mapping_rows:
    email_id = row['email_thread_id']
    thread_slug = row['thread_slug']
    if email_id and thread_slug:
        mappings[email_id] = thread_slug

print(f'✅ API returns {len(mappings)} mappings to populate this.state.emailThreads\n')
print('Sample mappings (showing first 10):')
print('=' * 120)
for i, (email_id, thread_slug) in enumerate(list(mappings.items())[:10], 1):
    email_short = email_id[:90] + '...' if len(email_id) > 90 else email_id
    print(f"\n{i}. this.state.emailThreads['{email_short}'] = '{thread_slug}'")

print(f'\n\n🔍 FORMATTER LOOKUP TEST:')
print('=' * 120)
if mappings:
    test_email_id = list(mappings.keys())[0]
    test_thread_slug = mappings[test_email_id]
    print(f"1. Email ID from table: {test_email_id[:90]}...")
    print(f"2. Lookup: this.state.emailThreads['{test_email_id[:40]}...'] = '{test_thread_slug}'")
    print(f"3. ThreadManager.threads.find(t => t.id === '{test_thread_slug}')")
    print(f"\n✅ If ThreadManager has thread with id='{test_thread_slug}', formatter will show agent badge!")
else:
    print("❌ No mappings found!")
