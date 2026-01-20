"""
Get the actual tool_result from message [16] in thread 1768890633197
"""
import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query
import json

print("\n" + "="*80)
print("[DEBUG] FETCHING TOOL_RESULT FROM MESSAGE [16]")
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
print(f"Thread ID: {thread_id}\n")

# Get message [16] (0-indexed as 15)
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

# Get message [16]
msg = messages[15]
content = msg['content']

# Parse JSONB
if isinstance(content, str):
    content = json.loads(content)

print(f"Message [16] - {msg['role']}")
print(f"Created: {msg['created_at']}")
print(f"Number of blocks: {len(content)}\n")

# Find tool_result block
tool_result_block = None
for block in content:
    if isinstance(block, dict) and block.get('type') == 'tool_result':
        tool_result_block = block
        break

if not tool_result_block:
    print("No tool_result block found!")
    sys.exit(1)

print("="*80)
print("TOOL_RESULT BLOCK FOUND")
print("="*80)
print(f"Tool Use ID: {tool_result_block.get('tool_use_id')}")
print(f"Is Error: {tool_result_block.get('is_error', False)}")

result_content = tool_result_block.get('content', [])
print(f"\nResult content type: {type(result_content)}")

# Handle both string and list formats
if isinstance(result_content, str):
    print(f"Result content is a STRING with {len(result_content):,} characters\n")
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result_content)
        print(f"String is valid JSON!")
        print(f"\nJSON structure (first 3000 chars):")
        print(json.dumps(parsed, indent=2)[:3000])
        
        # Check for metadata
        if isinstance(parsed, dict) and '_metadata' in parsed:
            metadata = parsed['_metadata']
            print(f"\n--- METADATA ---")
            print(f"Tool name: {metadata.get('tool_name')}")
            print(f"Intent: {metadata.get('intent')}")
            print(f"Estimated tokens: {metadata.get('estimated_tokens'):,}")
            print(f"Original tokens: {metadata.get('original_tokens'):,}")
            print(f"Size bytes: {metadata.get('size_bytes'):,}")
            print(f"Truncated: {metadata.get('truncated')}")
        
        # Show what data is actually in the result
        if isinstance(parsed, dict):
            print(f"\n--- RESULT DATA KEYS ---")
            for key in list(parsed.keys())[:20]:
                if key != '_metadata':
                    value = parsed[key]
                    if isinstance(value, list):
                        print(f"  {key}: list with {len(value)} items")
                        if len(value) > 0:
                            print(f"    First item: {str(value[0])[:100]}...")
                    elif isinstance(value, dict):
                        print(f"  {key}: dict with {len(value)} keys")
                    else:
                        preview = str(value)[:100]
                        print(f"  {key}: {preview}...")
    
    except json.JSONDecodeError as e:
        print(f"String is NOT valid JSON: {e}")
        print(f"String preview (first 2000 chars):")
        print(result_content[:2000])
        print(f"\n...")
        print(f"String preview (last 2000 chars):")
        print(result_content[-2000:])

elif isinstance(result_content, list):
    print(f"Result content is a LIST with {len(result_content)} items\n")
    for idx, item in enumerate(result_content, 1):
        if isinstance(item, dict):
            item_type = item.get('type', 'unknown')
            print(f"\n--- Result Content Item [{idx}]: {item_type} ---")
            
            if item_type == 'text':
                text = item.get('text', '')
                print(f"Text length: {len(text):,} characters")
                
                # Try to parse as JSON to see metadata
                try:
                    parsed = json.loads(text)
                    print(f"Text is valid JSON!")
                    print(f"\nJSON structure:")
                    print(json.dumps(parsed, indent=2)[:3000])
                    
                    # Check for metadata
                    if isinstance(parsed, dict) and '_metadata' in parsed:
                        metadata = parsed['_metadata']
                        print(f"\n--- METADATA ---")
                        print(f"Tool name: {metadata.get('tool_name')}")
                        print(f"Intent: {metadata.get('intent')}")
                        print(f"Estimated tokens: {metadata.get('estimated_tokens'):,}")
                        print(f"Original tokens: {metadata.get('original_tokens'):,}")
                        print(f"Size bytes: {metadata.get('size_bytes'):,}")
                        print(f"Truncated: {metadata.get('truncated')}")
                    
                    # Show what data is actually in the result
                    if isinstance(parsed, dict):
                        print(f"\n--- RESULT DATA KEYS ---")
                        for key in parsed.keys():
                            if key != '_metadata':
                                value = parsed[key]
                                if isinstance(value, (list, dict)):
                                    print(f"  {key}: {type(value).__name__} with {len(value)} items")
                                else:
                                    preview = str(value)[:100]
                                    print(f"  {key}: {preview}...")
                
                except json.JSONDecodeError:
                    print(f"Text is NOT JSON")
                    print(f"Text preview (first 1000 chars):")
                    print(text[:1000])
                    print(f"\n...")
                    print(f"Text preview (last 1000 chars):")
                    print(text[-1000:])
            else:
                print(f"Content: {json.dumps(item, indent=2)[:500]}...")
        else:
            print(f"\n--- Result Content Item [{idx}]: {type(item)} ---")
            print(f"Value: {str(item)[:200]}...")

print("\n" + "="*80)
print("END OF TOOL_RESULT INSPECTION")
print("="*80 + "\n")
