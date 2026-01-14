"""
DETAILED DIAGNOSTIC: Show exact content structure for each message in thread 2111
"""
import os
import sys
from dotenv import load_dotenv
import json

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
load_dotenv()

from AI_infrastructure.shared.database_utils import execute_query

thread_id = sys.argv[1] if len(sys.argv) > 1 else '2111'

print(f"\n" + "="*120)
print(f"DETAILED MESSAGE ANALYSIS FOR THREAD {thread_id}")
print("="*120 + "\n")

query = """
    SELECT 
        id,
        role,
        content,
        created_at
    FROM sessions.messages
    WHERE thread_id = %s::bigint
    ORDER BY created_at ASC, id ASC
"""

messages = execute_query(query, (int(thread_id),), fetch_mode='all')

print(f"TOTAL MESSAGES: {len(messages)}\n")
print("="*120 + "\n")

for i, msg in enumerate(messages, 1):
    print("-"*120)
    print(f"MESSAGE #{i} | ID: {msg['id']} | ROLE: {msg['role'].upper()} | Created: {msg['created_at']}")
    print("-"*120)
    
    content = msg['content']
    
    # Analyze content structure
    if isinstance(content, str):
        print(f"  CONTENT TYPE: String")
        print(f"  LENGTH: {len(content)} characters")
        preview = content[:200].replace('\n', ' ')
        print(f"  PREVIEW: {preview}...")
        
    elif isinstance(content, list):
        print(f"  CONTENT TYPE: Array with {len(content)} blocks")
        print(f"\n  BLOCKS:")
        
        for j, block in enumerate(content, 1):
            block_type = block.get('type', 'unknown')
            print(f"\n    [{j}] TYPE: {block_type.upper()}")
            
            if block_type == 'text':
                text = block.get('text', '')
                print(f"        TEXT LENGTH: {len(text)} characters")
                preview = text[:150].replace('\n', ' ')
                print(f"        TEXT PREVIEW: {preview}...")
                
            elif block_type == 'thinking':
                thinking = block.get('thinking', '')
                print(f"        THINKING LENGTH: {len(thinking)} characters")
                preview = thinking[:150].replace('\n', ' ')
                print(f"        THINKING PREVIEW: {preview}...")
                
            elif block_type == 'tool_use':
                tool_name = block.get('name', 'unknown')
                tool_id = block.get('id', 'N/A')
                tool_input = block.get('input', {})
                print(f"        TOOL NAME: {tool_name}")
                print(f"        TOOL ID: {tool_id}")
                print(f"        INPUT KEYS: {list(tool_input.keys())}")
                
            elif block_type == 'tool_result':
                tool_id = block.get('tool_use_id', 'N/A')
                is_error = block.get('is_error', False)
                content_val = block.get('content', '')
                print(f"        TOOL USE ID: {tool_id}")
                print(f"        IS ERROR: {is_error}")
                if isinstance(content_val, str):
                    print(f"        RESULT LENGTH: {len(content_val)} characters")
                    preview = content_val[:150].replace('\n', ' ')
                    print(f"        RESULT PREVIEW: {preview}...")
                else:
                    print(f"        RESULT TYPE: {type(content_val).__name__}")
            else:
                print(f"        RAW BLOCK: {json.dumps(block, indent=10)[:200]}...")
                
    else:
        print(f"  CONTENT TYPE: {type(content).__name__}")
        print(f"  RAW: {str(content)[:200]}...")
    
    print(f"\n")

print("="*120)
print(f"END OF THREAD {thread_id} ANALYSIS")
print("="*120 + "\n")

# Summary
user_msgs = [m for m in messages if m['role'] == 'user']
assistant_msgs = [m for m in messages if m['role'] == 'assistant']

print(f"\nSUMMARY:")
print(f"  Total Messages: {len(messages)}")
print(f"  User Messages: {len(user_msgs)}")
print(f"  Assistant Messages: {len(assistant_msgs)}")

# Analyze assistant messages
assistant_with_text = 0
assistant_with_thinking = 0
assistant_with_tool_use = 0
assistant_empty = 0

for msg in assistant_msgs:
    content = msg['content']
    has_text = False
    has_thinking = False
    has_tool = False
    
    if isinstance(content, list):
        for block in content:
            if block.get('type') == 'text' and block.get('text'):
                has_text = True
            if block.get('type') == 'thinking':
                has_thinking = True
            if block.get('type') == 'tool_use':
                has_tool = True
    elif isinstance(content, str) and content.strip():
        has_text = True
    
    if has_text:
        assistant_with_text += 1
    if has_thinking:
        assistant_with_thinking += 1
    if has_tool:
        assistant_with_tool_use += 1
    if not has_text and not has_thinking and not has_tool:
        assistant_empty += 1

print(f"\nASSISTANT MESSAGE BREAKDOWN:")
print(f"  With TEXT blocks: {assistant_with_text}")
print(f"  With THINKING blocks: {assistant_with_thinking}")
print(f"  With TOOL_USE blocks: {assistant_with_tool_use}")
print(f"  Empty (no content): {assistant_empty}")
