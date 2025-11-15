"""Check if messages contain structured content blocks or plain text"""
import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
cursor = conn.cursor()

# Check message 29 (assistant response with tool calls)
cursor.execute("SELECT id, role, content, LENGTH(content) as size FROM messages WHERE thread_id = 1 ORDER BY id")
messages = cursor.fetchall()

print("\n" + "="*100)
print("CONTENT STRUCTURE ANALYSIS")
print("="*100)

for msg_id, role, content, size in messages:
    print(f"\n{'='*100}")
    print(f"Message {msg_id} ({role}) - {size} characters")
    print("="*100)
    
    if not content:
        print("  [EMPTY]")
        continue
    
    # Check if it's JSON array (structured content blocks)
    if content.strip().startswith('['):
        try:
            blocks = json.loads(content)
            if isinstance(blocks, list):
                print(f"  ✅ STRUCTURED CONTENT - {len(blocks)} blocks")
                for i, block in enumerate(blocks):
                    block_type = block.get('type', 'unknown')
                    print(f"\n  Block {i+1}: {block_type}")
                    
                    if block_type == 'text':
                        text = block.get('text', '')
                        print(f"    Length: {len(text)} chars")
                        print(f"    Preview: {text[:100]}...")
                    
                    elif block_type == 'tool_use':
                        tool_name = block.get('name', 'unknown')
                        tool_input = block.get('input', {})
                        print(f"    Tool: {tool_name}")
                        print(f"    Input keys: {list(tool_input.keys())}")
                    
                    elif block_type == 'tool_result':
                        tool_use_id = block.get('tool_use_id', '')
                        result_content = block.get('content', '')
                        
                        if isinstance(result_content, list):
                            print(f"    Result blocks: {len(result_content)}")
                            for j, result_block in enumerate(result_content):
                                result_type = result_block.get('type', 'unknown')
                                if result_type == 'text':
                                    result_text = result_block.get('text', '')
                                    print(f"      Block {j+1} (text): {len(result_text)} chars")
                                    
                                    # Check if contains SQL data
                                    if '"rows":' in result_text or 'SELECT' in result_text:
                                        print(f"        🔴 CONTAINS SQL QUERY RESULTS!")
                                        try:
                                            result_json = json.loads(result_text)
                                            if 'rows' in result_json:
                                                rows = result_json['rows']
                                                print(f"        📊 SQL Data: {len(rows)} rows")
                                                if len(rows) > 0:
                                                    print(f"        📋 Columns: {list(rows[0].keys())}")
                                        except:
                                            pass
                        else:
                            print(f"    Result: {len(str(result_content))} chars")
                    
                    elif block_type == 'thinking':
                        thinking = block.get('thinking', '')
                        print(f"    Thinking: {len(thinking)} chars")
                        print(f"    Preview: {thinking[:100]}...")
            else:
                print(f"  ❌ PLAIN TEXT (parsed as JSON but not array)")
                print(f"  Preview: {content[:200]}...")
        except json.JSONDecodeError:
            print(f"  ❌ PLAIN TEXT (not valid JSON)")
            print(f"  Preview: {content[:200]}...")
    else:
        print(f"  ❌ PLAIN TEXT (doesn't start with [)")
        print(f"  Preview: {content[:200]}...")

conn.close()

print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print("""
If messages show "STRUCTURED CONTENT", then YES - the entire conversation
history including tool results, SQL data, and thinking blocks is being sent
with EVERY new message.

If messages show "PLAIN TEXT", then NO - only the text responses are sent,
not the full structured content with tool results.
""")
print("="*100)
