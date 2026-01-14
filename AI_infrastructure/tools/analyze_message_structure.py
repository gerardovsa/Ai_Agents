#!/usr/bin/env python3
"""
Analyze message structure in database to compare user vs assistant messages
"""

import sys
import json
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents/AI_infrastructure')

from shared.database_utils import execute_query

def analyze_messages():
    thread_slug = '1767316586323'
    
    # First find the thread ID from thread_slug
    thread_query = '''
    SELECT id, thread_slug, name 
    FROM sessions.threads 
    WHERE thread_slug = %s
    '''
    
    thread_rows = execute_query(thread_query, (thread_slug,), fetch_mode='all')
    
    if not thread_rows:
        print(f'ERROR: Thread not found with thread_slug {thread_slug}')
        return
    
    thread_id = thread_rows[0]['id']
    thread_title = thread_rows[0]['name']
    
    print(f'Found thread: ID={thread_id}, Slug={thread_slug}, Title="{thread_title}"')
    print()
    
    query = '''
    SELECT 
        role,
        content,
        created_at
    FROM sessions.messages
    WHERE thread_id = %s
    ORDER BY created_at ASC
    '''
    
    rows = execute_query(query, (thread_id,), fetch_mode='all')
    
    print('=' * 80)
    print(f'ANALYZING {len(rows)} MESSAGES IN THREAD "{thread_title}"')
    print(f'Thread ID: {thread_id}, Slug: {thread_slug}')
    print('=' * 80)
    
    user_count = 0
    assistant_count = 0
    
    for i, row in enumerate(rows, 1):
        role = row['role']
        content_raw = row['content']
        created_at = row['created_at']
        
        # Parse content
        if isinstance(content_raw, str):
            try:
                content = json.loads(content_raw)
            except:
                content = content_raw
        else:
            content = content_raw
        
        if role == 'user':
            user_count += 1
        elif role == 'assistant':
            assistant_count += 1
        
        print(f'\n--- Message {i} ({role}) ---')
        print(f'Created: {created_at}')
        print(f'Content type: {type(content).__name__}')
        
        if isinstance(content, list):
            print(f'Content is ARRAY with {len(content)} blocks:')
            for j, block in enumerate(content):
                if isinstance(block, dict):
                    block_type = block.get('type', 'unknown')
                    print(f'  Block {j+1}: type="{block_type}"')
                    
                    if block_type == 'text':
                        text = block.get('text', '')
                        print(f'    Text length: {len(text)} chars')
                        try:
                            if len(text) < 200:
                                print(f'    Text: "{text}"')
                            else:
                                preview = text[:200].encode('utf-8', errors='ignore').decode('utf-8')
                                print(f'    Preview: "{preview}..."')
                        except:
                            print(f'    Text preview failed (encoding issue)')
                    
                    elif block_type == 'tool_result':
                        tool_use_id = block.get('tool_use_id', '')
                        content_str = str(block.get('content', ''))
                        print(f'    tool_use_id: "{tool_use_id}"')
                        print(f'    content length: {len(content_str)} chars')
                    
                    elif block_type == 'tool_use':
                        print(f'    name: "{block.get("name", "")}"')
                        print(f'    id: "{block.get("id", "")}"')
                    
                    elif block_type == 'thinking':
                        thinking = block.get('thinking', '')
                        print(f'    thinking length: {len(thinking)} chars')
                else:
                    print(f'  Block {j+1}: {type(block).__name__} = {str(block)[:100]}')
        
        elif isinstance(content, str):
            print(f'Content is STRING with {len(content)} chars')
            if len(content) < 500:
                print(f'Content: "{content}"')
            else:
                print(f'Preview: "{content[:500]}..."')
        
        else:
            print(f'Content: {content}')
        
        # Show first 5 and last 5 messages in detail, summarize middle
        if i == 6 and len(rows) > 10:
            print(f'\n... (skipping {len(rows) - 10} messages) ...')
            continue
        if i > 5 and i < len(rows) - 4:
            continue
    
    print('\n' + '=' * 80)
    print(f'SUMMARY: {len(rows)} total messages')
    print(f'  User messages: {user_count}')
    print(f'  Assistant messages: {assistant_count}')
    print(f'  Other: {len(rows) - user_count - assistant_count}')
    print('=' * 80)
    
    # Show role pattern
    print('\nMESSAGE ROLE PATTERN (in order):')
    for i, row in enumerate(rows, 1):
        role = row['role']
        print(f'{i:3d}. {role}')

if __name__ == '__main__':
    analyze_messages()
