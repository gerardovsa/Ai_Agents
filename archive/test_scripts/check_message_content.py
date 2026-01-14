import sqlite3
import json

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT role, content 
    FROM messages 
    WHERE thread_id = "1762926885059" 
    ORDER BY id DESC 
    LIMIT 3
''')

messages = cursor.fetchall()

print('\n=== Last 3 messages from thread 1762926885059 ===\n')

for i, (role, content) in enumerate(messages):
    print(f'\n{i+1}. Role: {role}')
    try:
        parsed = json.loads(content)
        print(f'Content: {json.dumps(parsed, indent=2)[:500]}...')
        
        # Check if thinking blocks are present
        if isinstance(parsed, list):
            block_types = [block.get('type') for block in parsed]
            print(f'Block types: {block_types}')
            
            # Check for thinking blocks
            has_thinking = 'thinking' in block_types or 'redacted_thinking' in block_types
            print(f'Has thinking blocks: {has_thinking}')
            
            # Show first block details
            if parsed:
                first_block = parsed[0]
                print(f'First block type: {first_block.get("type")}')
                if first_block.get('type') == 'thinking':
                    print(f'  - Has signature: {"signature" in first_block}')
                    if 'signature' in first_block:
                        sig = first_block['signature']
                        print(f'  - Signature length: {len(sig) if sig else 0}')
                        print(f'  - Signature preview: {sig[:50] if sig else "None"}...')
    except Exception as e:
        print(f'Error parsing: {e}')
        print(f'Raw content: {content[:200]}...')

conn.close()
