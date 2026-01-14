"""
Check thread message structure to see what's being saved and re-sent
"""

import sqlite3
import json

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

cursor.execute('SELECT id, conversation FROM threads ORDER BY updated_at DESC LIMIT 1')
row = cursor.fetchone()
conn.close()

if row:
    thread_id, conversation_json = row
    conv = json.loads(conversation_json)
    
    print(f"Thread: {thread_id}")
    print(f"Total messages: {len(conv)}")
    
    # Calculate total size
    total_chars = sum(len(str(msg.get('content', ''))) for msg in conv)
    estimated_tokens = total_chars // 4
    
    print(f"Total chars: {total_chars:,}")
    print(f"Estimated tokens: {estimated_tokens:,}")
    
    print(f"\n{'='*80}")
    print("MESSAGE BREAKDOWN:")
    print(f"{'='*80}")
    
    for i, msg in enumerate(conv):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        
        if isinstance(content, str):
            chars = len(content)
            tokens = chars // 4
            content_preview = content[:100].replace('\n', ' ')
        elif isinstance(content, list):
            chars = sum(len(str(block.get('content', ''))) for block in content if isinstance(block, dict))
            tokens = chars // 4
            content_preview = f"[{len(content)} blocks]"
        else:
            chars = len(str(content))
            tokens = chars // 4
            content_preview = str(content)[:100]
        
        print(f"\nMessage {i+1}: {role}")
        print(f"  Size: {chars:,} chars (~{tokens:,} tokens)")
        print(f"  Preview: {content_preview}...")
        
        # Check for tool_result blocks
        if isinstance(content, list):
            tool_results = [b for b in content if b.get('type') == 'tool_result']
            if tool_results:
                print(f"  ⚠️  Contains {len(tool_results)} tool_result blocks")
                for tr in tool_results:
                    tr_content = str(tr.get('content', ''))
                    tr_tokens = len(tr_content) // 4
                    print(f"    - Tool result: {tr_tokens:,} tokens")
else:
    print("No threads found")
