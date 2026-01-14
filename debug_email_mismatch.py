import sys
import json
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import execute_query

print('\n=== CHECKING EMAIL ID MISMATCH ===\n')

# Get threads with agents assigned
query = '''
SELECT 
    id,
    thread_slug,
    location,
    email_thread_id,
    metadata,
    name
FROM sessions.threads
WHERE user_id = 14 
  AND location IS NOT NULL
  AND location != 'unassigned'
  AND location != ''
ORDER BY updated_at DESC
LIMIT 10
'''

rows = execute_query(query, fetch_mode='all')

print(f'Found {len(rows)} threads with agents assigned:\n')

for row in rows:
    thread_id = row['id']
    thread_slug = row['thread_slug']
    location = row['location']
    email_thread_id = row['email_thread_id']
    metadata = row['metadata']
    name = row['name']
    
    # Parse metadata JSON
    metadata_dict = {}
    if metadata:
        try:
            metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
        except:
            pass
    
    metadata_email_id = metadata_dict.get('email_id', 'N/A')
    
    print(f"Thread: {name}")
    print(f"  Location: {location}")
    print(f"  Thread Slug: {thread_slug}")
    print(f"  email_thread_id column: {email_thread_id}")
    print(f"  metadata.email_id: {metadata_email_id}")
    
    if email_thread_id and metadata_email_id != 'N/A':
        if email_thread_id == metadata_email_id:
            print(f"  ✅ MATCH")
        else:
            print(f"  ❌ MISMATCH!")
    print()

print('\n=== WHAT API RETURNS ===\n')

# Simulate API response
api_query = '''
SELECT email_thread_id, thread_slug, location
FROM sessions.threads
WHERE user_id = 14 
  AND email_thread_id IS NOT NULL
  AND location IS NOT NULL
  AND location != 'unassigned'
  AND location != ''
ORDER BY updated_at DESC
'''

api_rows = execute_query(api_query, fetch_mode='all')
mappings = {}
for row in api_rows:
    email_id = row['email_thread_id']
    thread_slug = row['thread_slug']
    if email_id and thread_slug:
        mappings[email_id] = thread_slug

print(f'API returns {len(mappings)} mappings:')
for email_id, thread_slug in list(mappings.items())[:5]:
    print(f"  '{email_id[:60]}...' -> '{thread_slug}'")

print(f'\n✅ These {len(mappings)} emails should show agent badges in the AI Agent column!')
