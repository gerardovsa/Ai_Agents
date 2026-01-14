import sys
sys.path.append('AI_infrastructure')
from shared.database_utils import execute_query
import json

# Get assistant messages from thread 2112
messages = execute_query('''
    SELECT id, role, content, created_at
    FROM sessions.messages
    WHERE thread_id = 2112 AND role = 'assistant'
    ORDER BY id
''', fetch_mode='all')

print(f"Found {len(messages)} assistant messages\n")

for msg in messages:
    print(f'\n{"="*60}')
    print(f'Message ID: {msg["id"]}')
    print(f'Role: {msg["role"]}')
    print(f'Created: {msg["created_at"]}')
    print(f'{"="*60}')
    
    content = msg["content"]
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            print(f'Content is JSON: {type(parsed).__name__}')
            
            if isinstance(parsed, list):
                print(f'Array with {len(parsed)} blocks:')
                for idx, block in enumerate(parsed):
                    if isinstance(block, dict):
                        block_type = block.get('type', 'unknown')
                        print(f'\n  Block {idx}: type="{block_type}"')
                        
                        if block_type == 'text':
                            text = block.get('text', '')
                            print(f'    TEXT CONTENT: {text[:150]}...' if len(text) > 150 else f'    TEXT CONTENT: {text}')
                        elif block_type == 'thinking':
                            thinking = block.get('thinking', '')
                            print(f'    THINKING CONTENT: {thinking[:150]}...' if len(thinking) > 150 else f'    THINKING CONTENT: {thinking}')
                        elif block_type == 'tool_use':
                            print(f'    TOOL: {block.get("name", "unknown")}')
                    else:
                        print(f'  Block {idx}: {type(block).__name__}')
            else:
                print(f'Content: {str(parsed)[:300]}...')
        except json.JSONDecodeError as e:
            print(f'Not valid JSON: {e}')
            print(f'Raw content: {content[:300]}...')
    else:
        print(f'Content type: {type(content).__name__}')
        print(f'Content: {str(content)[:300]}...')

print(f'\n\n{"="*60}')
print('SUMMARY:')
print(f'Total assistant messages checked: {len(messages)}')
