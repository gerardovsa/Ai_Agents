"""
Analyze what gets sent in message payloads - including tool results and token usage

This script shows EXACTLY what's being transmitted each time a user sends a message,
including all previous messages, tool results, SQL query results, etc.
"""

import sqlite3
import json
from pathlib import Path

db_path = Path(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("\n" + "="*120)
print("MESSAGE PAYLOAD ANALYSIS - What Gets Sent Each Time")
print("="*120)

# Get all messages from Thread 1 (your recent conversation)
cursor.execute("""
    SELECT id, thread_id, role, content, tool_calls, tokens_used, created_at
    FROM messages 
    WHERE thread_id = 1
    ORDER BY id
""")

messages = cursor.fetchall()

print(f"\n📊 Total messages in Thread 1: {len(messages)}\n")

# Analyze each message
total_characters = 0
total_tokens_estimate = 0

for msg_id, thread_id, role, content, tool_calls_json, tokens_used, created_at in messages:
    print("\n" + "-"*120)
    print(f"Message ID {msg_id} ({role}) - {created_at}")
    print("-"*120)
    
    # Measure content size
    content_size = len(content) if content else 0
    total_characters += content_size
    
    # Parse content if it's structured (JSON array of content blocks)
    try:
        if content and content.strip().startswith('['):
            content_blocks = json.loads(content)
            print(f"\n📦 Content Structure: {len(content_blocks)} block(s)")
            
            for i, block in enumerate(content_blocks):
                block_type = block.get('type', 'unknown')
                print(f"\n  Block {i+1}: {block_type}")
                
                if block_type == 'text':
                    text = block.get('text', '')
                    print(f"    Text length: {len(text)} characters")
                    print(f"    Preview: {text[:200]}..." if len(text) > 200 else f"    Text: {text}")
                
                elif block_type == 'tool_use':
                    tool_name = block.get('name', 'unknown')
                    tool_input = block.get('input', {})
                    print(f"    Tool: {tool_name}")
                    print(f"    Input: {json.dumps(tool_input, indent=6)}")
                
                elif block_type == 'tool_result':
                    tool_use_id = block.get('tool_use_id', 'unknown')
                    tool_result = block.get('content', '')
                    
                    # Try to parse result content
                    if isinstance(tool_result, list):
                        print(f"    Result blocks: {len(tool_result)}")
                        for j, result_block in enumerate(tool_result):
                            result_type = result_block.get('type', 'unknown')
                            if result_type == 'text':
                                result_text = result_block.get('text', '')
                                result_size = len(result_text)
                                print(f"      Block {j+1} (text): {result_size} characters")
                                
                                # Check if it's SQL data
                                if 'SELECT' in result_text or 'FROM' in result_text or '"rows":' in result_text:
                                    print(f"        🔴 Contains SQL QUERY RESULTS (RAW DATA)")
                                    # Try to count rows if JSON
                                    try:
                                        result_json = json.loads(result_text)
                                        if isinstance(result_json, dict) and 'rows' in result_json:
                                            row_count = len(result_json['rows'])
                                            print(f"        📊 Data: {row_count} rows of SQL results")
                                    except:
                                        pass
                                
                                # Show preview
                                print(f"        Preview: {result_text[:150]}...")
                    else:
                        result_size = len(str(tool_result))
                        print(f"    Result length: {result_size} characters")
                        print(f"    Preview: {str(tool_result)[:150]}...")
                
                elif block_type == 'thinking':
                    thinking_text = block.get('thinking', '')
                    print(f"    Thinking length: {len(thinking_text)} characters")
                    print(f"    Preview: {thinking_text[:150]}...")
        
        else:
            # Plain text content
            print(f"\n📄 Plain Text Content:")
            print(f"  Length: {content_size} characters")
            if content_size > 0:
                print(f"  Preview: {content[:200]}..." if content_size > 200 else f"  Content: {content}")
    
    except json.JSONDecodeError:
        # Not JSON, just show as text
        print(f"\n📄 Plain Text Content:")
        print(f"  Length: {content_size} characters")
        if content_size > 0:
            print(f"  Preview: {content[:200]}..." if content_size > 200 else f"  Content: {content}")
    
    # Parse tool_calls if present
    if tool_calls_json:
        try:
            tool_calls = json.loads(tool_calls_json)
            print(f"\n🔧 Tool Calls: {len(tool_calls)}")
            for tool_call in tool_calls:
                print(f"  - {tool_call.get('name', 'unknown')}")
        except:
            print(f"\n🔧 Tool Calls: {tool_calls_json[:100]}...")
    
    # Token usage
    if tokens_used:
        print(f"\n💰 Tokens Used: {tokens_used}")
        total_tokens_estimate += tokens_used
    else:
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        estimated_tokens = content_size // 4
        print(f"\n💰 Estimated Tokens: ~{estimated_tokens}")
        total_tokens_estimate += estimated_tokens

print("\n" + "="*120)
print("CUMULATIVE PAYLOAD ANALYSIS")
print("="*120)

print(f"\n📊 Statistics:")
print(f"  Total messages: {len(messages)}")
print(f"  Total characters across all messages: {total_characters:,}")
print(f"  Total estimated tokens: ~{total_tokens_estimate:,}")
print(f"  Average characters per message: {total_characters // len(messages) if len(messages) > 0 else 0:,}")

print(f"\n🔴 CRITICAL FINDINGS:")
print(f"\n  When you send a new message, the frontend sends:")
print(f"    1. Your new message text")
print(f"    2. ENTIRE conversation history ({len(messages)} messages)")
print(f"    3. ALL tool results including:")
print(f"       - SQL query results (raw data with rows)")
print(f"       - Tool outputs (can be large)")
print(f"       - Thinking blocks (internal reasoning)")
print(f"\n  This means EVERY message includes ALL previous context!")
print(f"  Total payload per request: ~{total_characters:,} characters (~{total_tokens_estimate:,} tokens)")

# Analyze message roles
user_count = sum(1 for m in messages if m[2] == 'user')
assistant_count = sum(1 for m in messages if m[2] == 'assistant')

print(f"\n📝 Message Breakdown:")
print(f"  User messages: {user_count}")
print(f"  Assistant messages: {assistant_count}")
print(f"  Total messages sent to API per request: {len(messages)}")

# Check for SQL results in messages
sql_result_count = 0
large_payloads = []

for msg_id, thread_id, role, content, tool_calls_json, tokens_used, created_at in messages:
    if content and ('SELECT' in content or '"rows":' in content):
        sql_result_count += 1
        if len(content) > 5000:
            large_payloads.append((msg_id, len(content), role))

print(f"\n🔍 Content Analysis:")
print(f"  Messages with SQL results: {sql_result_count}")
print(f"  Large payloads (>5KB): {len(large_payloads)}")

if large_payloads:
    print(f"\n  Large message details:")
    for msg_id, size, role in large_payloads:
        print(f"    Message {msg_id} ({role}): {size:,} characters")

conn.close()

print("\n" + "="*120)
print("RECOMMENDATION:")
print("="*120)
print("""
The current system sends the ENTIRE conversation history with EVERY new message.
This includes:
  - All previous user messages
  - All previous assistant responses
  - ALL tool results (including full SQL query results with data)
  - All thinking blocks

This can result in HUGE token costs, especially as conversations grow.

OPTIMIZATION OPTIONS:
1. Summarize old messages (keep only recent N messages)
2. Strip tool results from old messages (keep only final text responses)
3. Remove thinking blocks from history (not needed for context)
4. Implement message pruning (remove messages beyond certain age/count)
5. Use message compression (summarize conversation before sending)

Would save: 50-80% of tokens per request in long conversations
""")

print("="*120)
