import sys
sys.path.insert(0, '.')
from shared.database_utils import execute_query

# Get messages for thread 2112 from sessions schema
messages = execute_query('''
    SELECT id, role, content, created_at
    FROM sessions.messages
    WHERE thread_id = 2112
    ORDER BY id ASC
''', fetch_mode='all')

print(f'Total messages in DB: {len(messages)}')

print('\n=== Message Roles Distribution ===')
roles = {}
for msg in messages:
    role = msg['role']
    roles[role] = roles.get(role, 0) + 1
print(roles)

print('\n=== First 5 Messages ===')
for i, msg in enumerate(messages[:5]):
    content_preview = str(msg['content'])[:80] if msg['content'] else 'NULL'
    print(f'{i+1}. ID={msg["id"]}, Role={msg["role"]}, Preview={content_preview}')

print('\n=== Last 5 Messages ===')
for i, msg in enumerate(messages[-5:]):
    content_preview = str(msg['content'])[:80] if msg['content'] else 'NULL'
    print(f'{len(messages)-5+i+1}. ID={msg["id"]}, Role={msg["role"]}, Preview={content_preview}')
