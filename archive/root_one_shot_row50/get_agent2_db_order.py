"""
DIAGNOSTIC: Query Supabase database directly for Agent 2 message order
"""
import os
import sys
from dotenv import load_dotenv

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

load_dotenv()

from AI_infrastructure.shared.database_utils import execute_query

# Get thread ID for Agent 2 from command line or use default
thread_id = sys.argv[1] if len(sys.argv) > 1 else '1736002010772'

print(f"\n🔍 QUERYING SUPABASE DATABASE FOR AGENT 2")
print(f"Thread ID: {thread_id}")
print("=" * 100)

# Query database - use BIGINT for thread_id
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

print(f"\n📊 TOTAL MESSAGES IN DATABASE: {len(messages)}")
print("=" * 100)
print("| # | ID          | ROLE      | CONTENT PREVIEW (first 80 chars)")
print("=" * 100)

for i, msg in enumerate(messages, 1):
    msg_id = str(msg['id'])
    role = msg['role'].upper().ljust(9)
    
    # Extract preview
    content = msg['content']
    if isinstance(content, str):
        preview = content[:80].replace('\n', ' ')
    elif isinstance(content, list):
        # Show block types
        block_types = ', '.join([b.get('type', 'unknown') for b in content])
        # Try to find text
        text_blocks = [b for b in content if b.get('type') == 'text' and b.get('text')]
        if text_blocks:
            preview = text_blocks[0]['text'][:80].replace('\n', ' ')
        else:
            preview = f"[{len(content)} blocks: {block_types}]"
    else:
        preview = str(content)[:80]
    
    print(f"| {i:3d} | {msg_id:11s} | {role} | {preview}")

print("=" * 100)

# Summary
user_count = sum(1 for m in messages if m['role'] == 'user')
assistant_count = sum(1 for m in messages if m['role'] == 'assistant')

print(f"\n📈 SUMMARY:")
print(f"   USER messages: {user_count}")
print(f"   ASSISTANT messages: {assistant_count}")
print(f"   TOTAL: {len(messages)}")

print("\n🎯 EXPECTED PATTERN (first 20 messages):")
for i, msg in enumerate(messages[:20], 1):
    print(f"   {i:2d}. {msg['role'].upper()}")

print("\n✅ This is the CORRECT order from Supabase database!\n")
