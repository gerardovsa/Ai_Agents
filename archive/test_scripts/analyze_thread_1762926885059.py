import sqlite3
import json

conn = sqlite3.connect('data/sessions.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
    SELECT id, role, content 
    FROM messages 
    WHERE thread_id = 27
    ORDER BY id
''')

print("Thread 27 (1762926885059 slug) - Message Analysis")
print("=" * 80)

for row in cursor.fetchall():
    msg_id = row['id']
    role = row['role']
    content_raw = row['content']
    
    print(f"\nMessage ID: {msg_id} | Role: {role}")
    
    try:
        # Parse content
        if isinstance(content_raw, str):
            content = json.loads(content_raw)
        elif content_raw is None:
            content = []
        else:
            content = content_raw
        
        # Analyze blocks
        if isinstance(content, list):
            print(f"  Blocks: {len(content)}")
            for idx, block in enumerate(content):
                if isinstance(block, dict):
                    btype = block.get('type', 'unknown')
                    print(f"    [{idx}] {btype}", end='')
                    
                    if btype == 'thinking':
                        has_sig = 'signature' in block
                        print(f" (has_signature: {has_sig})")
                    elif btype == 'text':
                        text_len = len(block.get('text', ''))
                        print(f" ({text_len} chars)")
                    elif btype == 'tool_use':
                        print(f" (name: {block.get('name')})")
                    elif btype == 'tool_result':
                        print(f" (tool_use_id: {block.get('tool_use_id')})")
                    else:
                        print()
        elif isinstance(content, str):
            print(f"  String content: {content[:100]}...")
        else:
            print(f"  Unknown type: {type(content)}")
    
    except Exception as e:
        print(f"  Error: {e}")

conn.close()
print("\n" + "=" * 80)
