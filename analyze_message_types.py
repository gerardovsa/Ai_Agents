import sys
sys.path.append('AI_infrastructure')
from shared.database_utils import execute_query
import json

# Get ALL assistant messages from thread 2112
messages = execute_query('''
    SELECT id, role, content, created_at
    FROM sessions.messages
    WHERE thread_id = 2112 AND role = 'assistant'
    ORDER BY id
''', fetch_mode='all')

print(f"Found {len(messages)} assistant messages\n")

thinking_only = 0
has_text = 0
has_tool_use = 0

for msg in messages:
    content = msg["content"]
    
    if isinstance(content, list):
        block_types = [block.get('type') for block in content if isinstance(block, dict)]
        
        if 'text' in block_types:
            has_text += 1
            print(f"✅ Message {msg['id']}: HAS TEXT CONTENT")
            # Show first text block
            for block in content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text = block.get('text', '')
                    print(f"   Text: {text[:100]}...")
                    break
        elif 'tool_use' in block_types:
            has_tool_use += 1
            print(f"🔧 Message {msg['id']}: Tool use only")
        else:
            thinking_only += 1
            print(f"💭 Message {msg['id']}: THINKING ONLY (no text/tool_use)")

print(f'\n{"="*60}')
print(f'SUMMARY:')
print(f'  Total assistant messages: {len(messages)}')
print(f'  Messages with TEXT blocks: {has_text} ✅')
print(f'  Messages with TOOL USE: {has_tool_use}')
print(f'  Messages with THINKING ONLY: {thinking_only} ❌')
print(f'\n❌ PROBLEM: {thinking_only} messages have NO visible content!')
print(f'   These messages will not render in the UI.')
