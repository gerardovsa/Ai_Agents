"""
Check Message Metadata Structure
=================================
Shows what metadata is currently captured for messages
"""

import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('data/sessions.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("MESSAGE METADATA ANALYSIS")
print("=" * 80)

# Get table structure
print("\n1. DATABASE SCHEMA - messages table:")
print("-" * 80)
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()

print(f"{'Column Name':<30} {'Type':<15} {'Nullable':<10} {'Default'}")
print("-" * 80)
for col in columns:
    nullable = "NO" if col['notnull'] else "YES"
    default = col['dflt_value'] if col['dflt_value'] else "-"
    print(f"{col['name']:<30} {col['type']:<15} {nullable:<10} {default}")

# Count messages
cursor.execute("SELECT COUNT(*) as total FROM messages")
total = cursor.fetchone()['total']
print(f"\n2. TOTAL MESSAGES: {total}")

# Messages with metadata
cursor.execute("SELECT COUNT(*) as count FROM messages WHERE metadata IS NOT NULL AND metadata != '{}'")
with_metadata = cursor.fetchone()['count']
print(f"   Messages with metadata: {with_metadata}")

# Messages with tool calls
cursor.execute("SELECT COUNT(*) as count FROM messages WHERE tool_calls IS NOT NULL")
with_tools = cursor.fetchone()['count']
print(f"   Messages with tool_calls: {with_tools}")

# Messages with tokens
cursor.execute("SELECT COUNT(*) as count FROM messages WHERE tokens_used IS NOT NULL")
with_tokens = cursor.fetchone()['count']
print(f"   Messages with tokens_used: {with_tokens}")

# Messages with timing
cursor.execute("SELECT COUNT(*) as count FROM messages WHERE response_time_ms IS NOT NULL")
with_timing = cursor.fetchone()['count']
print(f"   Messages with response_time_ms: {with_timing}")

# Sample message with full metadata
print("\n3. SAMPLE MESSAGE (FULL METADATA):")
print("-" * 80)
cursor.execute("""
    SELECT *
    FROM messages
    WHERE metadata IS NOT NULL OR tool_calls IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 1
""")

msg = cursor.fetchone()
if msg:
    print(f"ID: {msg['id']}")
    print(f"Thread ID: {msg['thread_id']}")
    print(f"Session ID: {msg['session_id']}")
    print(f"Role: {msg['role']}")
    print(f"User ID: {msg['user_id']}")
    print(f"Created: {msg['created_at']}")
    print(f"Updated: {msg['updated_at']}")
    print(f"\nContent (first 150 chars):")
    print(f"  {msg['content'][:150] if msg['content'] else 'None'}...")
    
    if msg['prompt']:
        print(f"\nPrompt (first 150 chars):")
        print(f"  {msg['prompt'][:150]}...")
    
    if msg['tool_calls']:
        print(f"\nTool Calls:")
        try:
            tools = json.loads(msg['tool_calls'])
            if isinstance(tools, list):
                for i, tool in enumerate(tools[:3], 1):
                    print(f"  {i}. {tool.get('name', 'unknown')}")
            else:
                print(f"  {str(tools)[:200]}")
        except:
            print(f"  {msg['tool_calls'][:200]}")
    
    print(f"\nPerformance Metrics:")
    print(f"  Tokens Used: {msg['tokens_used']}")
    print(f"  Response Time: {msg['response_time_ms']} ms")
    
    if msg['metadata']:
        print(f"\nMetadata JSON:")
        try:
            meta = json.loads(msg['metadata'])
            print(json.dumps(meta, indent=2))
        except:
            print(f"  {msg['metadata']}")
    
    if msg['response_data']:
        print(f"\nResponse Data (first 200 chars):")
        print(f"  {msg['response_data'][:200]}...")

# What metadata fields are being used
print("\n4. METADATA FIELDS IN USE:")
print("-" * 80)
cursor.execute("""
    SELECT metadata
    FROM messages
    WHERE metadata IS NOT NULL AND metadata != '{}'
    LIMIT 50
""")

all_keys = set()
for row in cursor.fetchall():
    try:
        meta = json.loads(row['metadata'])
        if isinstance(meta, dict):
            all_keys.update(meta.keys())
    except:
        pass

if all_keys:
    print("Metadata keys found across messages:")
    for key in sorted(all_keys):
        print(f"  - {key}")
else:
    print("  No metadata fields found")

# Message role distribution
print("\n5. MESSAGE DISTRIBUTION:")
print("-" * 80)
cursor.execute("""
    SELECT role, COUNT(*) as count
    FROM messages
    GROUP BY role
    ORDER BY count DESC
""")
for row in cursor.fetchall():
    print(f"  {row['role']:<20} {row['count']:>6} messages")

# Recent messages
print("\n6. RECENT MESSAGES (Last 5):")
print("-" * 80)
cursor.execute("""
    SELECT id, role, created_at, session_id, 
           SUBSTR(content, 1, 80) as content_preview
    FROM messages
    ORDER BY created_at DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"\nID {row['id']}: {row['role']}")
    print(f"  Time: {row['created_at']}")
    print(f"  Session: {row['session_id']}")
    print(f"  Content: {row['content_preview']}...")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"""
Currently Captured Per Message:
  ✓ Basic: id, thread_id, session_id, role, content
  ✓ User: user_id
  ✓ Timing: created_at, updated_at, response_time_ms
  ✓ AI Metrics: prompt, response_data, tokens_used
  ✓ Tools: tool_calls (JSON array of tool invocations)
  ✓ Feedback: feedback_score, include (boolean)
  ✓ Context: api_session_id, workspace_id
  ✓ Advanced: embedding_vector (for semantic search)
  ✓ Custom: metadata (JSON field for anything else)

Total Fields: {len(columns)} columns in messages table
Messages with metadata: {with_metadata}/{total}
Messages with tool calls: {with_tools}/{total}
""")

conn.close()
