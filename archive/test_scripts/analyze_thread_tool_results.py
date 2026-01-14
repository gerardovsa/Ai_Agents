"""
Check if tool_result content is in saved messages
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import json

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

# Get most recent thread with many messages
sql, params = convert_sql_placeholders('''
    SELECT thread_id, COUNT(*) as msg_count 
    FROM messages 
    GROUP BY thread_id 
    ORDER BY MAX(id) DESC 
    LIMIT 10
''')

threads = cursor.fetchall()

print("Recent threads:")
for thread_id, count in threads:
    sql, params = convert_sql_placeholders('SELECT SUM(LENGTH(content)) FROM messages WHERE thread_id = ?', (thread_id,))

    cursor.execute(sql, params)
    total_chars = cursor.fetchone()[0]
    print(f"  Thread {thread_id}: {count} messages, {total_chars:,} chars (~{total_chars//4:,} tokens)")

# Pick the thread with most content
print("\n" + "="*80)
cursor.execute('''
    SELECT thread_id, SUM(LENGTH(content)) as total
    FROM messages 
    GROUP BY thread_id 
    ORDER BY total DESC 
    LIMIT 1
''')

biggest_thread = cursor.fetchone()
if biggest_thread:
    thread_id, total_chars = biggest_thread
    print(f"ANALYZING BIGGEST THREAD: {thread_id} ({total_chars:,} chars)")
    print("="*80)
    
    # Get all messages
    cursor.execute('''
        SELECT id, role, content, LENGTH(content) as size
        FROM messages 
        WHERE thread_id = ?
        ORDER BY id
    ''', (thread_id,))

cursor.execute(sql, params)
    
    messages = cursor.fetchall()
    
    tool_result_count = 0
    tool_result_tokens = 0
    
    for msg_id, role, content_str, size in messages:
        try:
            content = json.loads(content_str)
            
            # Check if it's a list of blocks
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_result':
                        tool_result_count += 1
                        block_size = len(str(block.get('content', '')))
                        tool_result_tokens += block_size // 4
                        print(f"\nMessage {msg_id} ({role}): tool_result found")
                        print(f"  Size: {block_size:,} chars (~{block_size//4:,} tokens)")
                        content_preview = str(block.get('content', ''))[:200]
                        print(f"  Preview: {content_preview}...")
        except:
            pass
    
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Total messages: {len(messages)}")
    print(f"  Tool results found: {tool_result_count}")
    print(f"  Tool result tokens: {tool_result_tokens:,}")
    print(f"  Percentage of thread: {tool_result_tokens/(total_chars//4)*100:.1f}%")

conn.close()
