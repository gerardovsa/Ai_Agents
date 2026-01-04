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
    name,
    CASE 
        WHEN location IS NOT NULL AND location != 'unassigned' THEN 'HAS AGENT'
        ELSE 'NO AGENT'
    END as agent_status
FROM sessions.threads
WHERE user_id = 14 
  AND email_thread_id IS NOT NULL
ORDER BY updated_at DESC
LIMIT 20
'''

print('\n=== THREADS WITH EMAIL ASSIGNMENTS (User 14) ===\n')

rows = execute_query(query, fetch_mode='all')

print(f'DEBUG: Type of rows: {type(rows)}')
print(f'DEBUG: Number of rows: {len(rows) if rows else 0}')
if rows:
    print(f'DEBUG: First row: {rows[0]}')
    print(f'DEBUG: First row type: {type(rows[0])}')

if not rows or len(rows) == 0:
    print('❌ NO THREADS WITH EMAIL ASSIGNMENTS FOUND')
else:
    print('❌ NO THREADS WITH EMAIL ASSIGNMENTS FOUND')
else:
    print(f'Found {len(rows)} threads with email assignments:\n')
    
    has_agent = []
    no_agent = []
    
    for row in rows:
        thread_id, thread_slug, location, email_id, email_subject, name, status = row
        
        thread_info = {
            'thread_id': thread_id,
            'thread_slug': thread_slug,
            'location': location,
            'email_id': email_id[:60] + '...' if email_id and len(email_id) > 60 else email_id,
            'email_subject': email_subject,
            'name': name
        }
        
        if status == 'HAS AGENT':
            has_agent.append(thread_info)
        else:
            no_agent.append(thread_info)
    
    print(f'✅ THREADS WITH AGENT ASSIGNED: {len(has_agent)}')
    print('=' * 80)
    for t in has_agent:
        print(f"Thread ID: {t['thread_id']} | Slug: {t['thread_slug']}")
        print(f"  Location: {t['location']}")
        print(f"  Email ID: {t['email_id']}")
        print(f"  Subject: {t['email_subject']}")
        print(f"  Name: {t['name']}")
        print()
    
    print(f'\n❌ THREADS WITH NO AGENT (unassigned): {len(no_agent)}')
    print('=' * 80)
    for t in no_agent:
        print(f"Thread ID: {t['thread_id']} | Slug: {t['thread_slug']}")
        print(f"  Location: {t['location']}")
        print(f"  Email ID: {t['email_id']}")
        print(f"  Subject: {t['email_subject']}")
        print(f"  Name: {t['name']}")
        print()

print('\n=== MAPPING TEST ===')
print('Testing what the API endpoint returns...\n')

# Simulate what the API returns
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

print(f'API would return {len(mappings)} email-to-thread mappings:')
print('\nSample mappings (first 5):')
for i, (email_id, thread_slug) in enumerate(list(mappings.items())[:5]):
    print(f"  '{email_id[:60]}...' -> '{thread_slug}'")

print(f'\n✅ Total mappings that would populate this.state.emailThreads: {len(mappings)}')
