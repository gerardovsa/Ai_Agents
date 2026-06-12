"""
Inspect message [16] from thread 1768890633197 to find what's causing 383K chars
"""
import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query
import json
import tiktoken

# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model("gpt-4")

def count_tokens(text: str) -> int:
    """Count tokens in text"""
    return len(tokenizer.encode(text))

print("\n" + "="*80)
print("[DEBUG] INSPECTING MESSAGE [16] - 383,448 CHARACTERS")
print("="*80 + "\n")

# Get thread ID
thread = execute_query(
    "SELECT id FROM sessions.threads WHERE thread_slug = %s",
    ('1768890633197',),
    fetch_mode='one'
)

if not thread:
    print("Thread not found!")
    sys.exit(1)

thread_id = thread['id']

# Get all messages
messages = execute_query(
    """
    SELECT role, content, created_at
    FROM sessions.messages
    WHERE thread_id = %s
    ORDER BY created_at ASC
    """,
    (thread_id,),
    fetch_mode='all'
)

if len(messages) < 16:
    print(f"Only {len(messages)} messages found!")
    sys.exit(1)

# Get message [16] (index 15)
msg = messages[15]
content = msg['content']

print(f"Role: {msg['role']}")
print(f"Created: {msg['created_at']}")
print(f"Content type: {type(content)}\n")

# Parse JSONB
if isinstance(content, str):
    content = json.loads(content)

print(f"Content is a list with {len(content)} blocks\n")

# Analyze each block
total_tokens = 0
for idx, block in enumerate(content, 1):
    if not isinstance(block, dict):
        print(f"Block [{idx}]: {type(block)} - {str(block)[:100]}")
        continue
    
    block_type = block.get('type', 'unknown')
    
    if block_type == 'text':
        text = block.get('text', '')
        tokens = count_tokens(text)
        total_tokens += tokens
        print(f"Block [{idx}]: text - {len(text):,} chars | {tokens:,} tokens")
        print(f"  Preview: {text[:200]}...")
        print()
    
    elif block_type == 'tool_use':
        name = block.get('name', '?')
        input_data = block.get('input', {})
        input_json = json.dumps(input_data, indent=2)
        tokens = count_tokens(input_json)
        total_tokens += tokens
        print(f"Block [{idx}]: tool_use - {name}")
        print(f"  Input: {len(input_json):,} chars | {tokens:,} tokens")
        print(f"  Preview: {input_json[:300]}...")
        print()
    
    elif block_type == 'tool_result':
        tool_use_id = block.get('tool_use_id', '?')
        result_content = block.get('content', [])
        
        # Calculate size
        result_json = json.dumps(result_content, indent=2)
        tokens = count_tokens(result_json)
        total_tokens += tokens
        
        print(f"Block [{idx}]: tool_result - {tool_use_id}")
        print(f"  Content: {len(result_json):,} chars | {tokens:,} tokens")
        print(f"  ⚠️  THIS IS THE CULPRIT!")
        print(f"  Preview: {result_json[:500]}...")
        print()
        
        # Check if content is a list
        if isinstance(result_content, list):
            for ridx, rblock in enumerate(result_content, 1):
                if isinstance(rblock, dict):
                    rtype = rblock.get('type', '?')
                    rtext = rblock.get('text', '')
                    print(f"    Result block [{ridx}]: {rtype} - {len(rtext):,} chars")
                    if rtype == 'text' and len(rtext) > 1000:
                        print(f"      ⚠️  LARGE TEXT BLOCK DETECTED")
                        print(f"      First 500 chars: {rtext[:500]}...")
                        print(f"      Last 500 chars: ...{rtext[-500:]}")

print(f"\n{'='*80}")
print(f"TOTAL TOKENS IN MESSAGE [16]: {total_tokens:,}")
print(f"{'='*80}\n")
