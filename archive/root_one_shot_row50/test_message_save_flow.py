"""
Test script to verify message saving flow and identify missing messages.

Run this after a chat session to check if all messages were saved.
"""

import json
from AI_infrastructure.shared.database_utils import execute_query

def test_message_completeness(thread_slug: str):
    """
    Verify all message types are saved in correct sequence.
    
    Expected pattern for tool-using conversation:
    1. User message (type: text)
    2. Assistant message (type: tool_use + text/thinking)
    3. User message (type: tool_result)
    4. Assistant message (type: text)
    """
    query = """
    SELECT id, role, content, created_at, metadata
    FROM sessions.messages
    WHERE thread_id = (SELECT id FROM sessions.threads WHERE thread_slug = %s)
    ORDER BY created_at ASC
    """
    
    messages = execute_query(query, (thread_slug,), fetch_mode='all')
    
    print(f"\n{'='*80}")
    print(f"Thread: {thread_slug}")
    print(f"Total Messages: {len(messages)}")
    print(f"{'='*80}\n")
    
    issues = []
    
    for i, msg in enumerate(messages, 1):
        msg_id, role, content, created_at, metadata = msg
        content_json = json.loads(content) if isinstance(content, str) else content
        
        print(f"Message {i}: {role} ({created_at})")
        
        if isinstance(content_json, list):
            print(f"  Content blocks: {len(content_json)}")
            for block in content_json:
                block_type = block.get('type', 'unknown')
                print(f"    - {block_type}", end='')
                
                if block_type == 'tool_use':
                    print(f" (name: {block.get('name', 'unknown')})", end='')
                elif block_type == 'tool_result':
                    print(f" (tool_use_id: {block.get('tool_use_id', 'missing')[:8]}...)", end='')
                elif block_type == 'thinking':
                    thinking_text = block.get('thinking', '')
                    print(f" ({len(thinking_text)} chars)", end='')
                
                print()  # newline
        else:
            print(f"  Content: {str(content_json)[:100]}...")
        
        # Check for orphaned tool_use blocks
        if role == 'assistant' and isinstance(content_json, list):
            has_tool_use = any(b.get('type') == 'tool_use' for b in content_json)
            if has_tool_use and i < len(messages):
                next_msg = messages[i]
                next_content = json.loads(next_msg[2]) if isinstance(next_msg[2], str) else next_msg[2]
                next_has_tool_result = any(b.get('type') == 'tool_result' for b in next_content) if isinstance(next_content, list) else False
                
                if not next_has_tool_result:
                    issues.append(f"Message {i}: tool_use block without following tool_result")
        
        # Check for tool_result without preceding tool_use
        if role == 'user' and isinstance(content_json, list):
            has_tool_result = any(b.get('type') == 'tool_result' for b in content_json)
            if has_tool_result and i > 1:
                prev_msg = messages[i-2]
                prev_content = json.loads(prev_msg[2]) if isinstance(prev_msg[2], str) else prev_msg[2]
                prev_has_tool_use = any(b.get('type') == 'tool_use' for b in prev_content) if isinstance(prev_content, list) else False
                
                if not prev_has_tool_use:
                    issues.append(f"Message {i}: tool_result without preceding tool_use")
        
        print()
    
    if issues:
        print("\n⚠️ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ NO ISSUES - All conversation components saved correctly")
    
    print(f"{'='*80}\n")
    
    # Summary statistics
    print("📊 Message Type Breakdown:")
    role_counts = {}
    block_type_counts = {}
    
    for msg in messages:
        role = msg[1]
        content = json.loads(msg[2]) if isinstance(msg[2], str) else msg[2]
        
        role_counts[role] = role_counts.get(role, 0) + 1
        
        if isinstance(content, list):
            for block in content:
                block_type = block.get('type', 'unknown')
                key = f"{role}:{block_type}"
                block_type_counts[key] = block_type_counts.get(key, 0) + 1
    
    print(f"\nBy Role:")
    for role, count in sorted(role_counts.items()):
        print(f"  - {role}: {count} messages")
    
    print(f"\nBy Content Block Type:")
    for key, count in sorted(block_type_counts.items()):
        print(f"  - {key}: {count} blocks")

def check_recent_save_failures():
    """
    Check backend logs for save failures in last 24 hours.
    """
    print("\n📋 Checking for save failures in backend logs...\n")
    
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', 
         'Get-Content AI_infrastructure/flask_app.log -Tail 1000 | Select-String "Failed to save|save.*failed|⚠️.*save"'],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("⚠️ Found save failures:")
        print(result.stdout)
    else:
        print("✅ No save failures found in recent logs")

def test_save_retry_logic():
    """
    Verify that save_message_to_database has retry logic.
    """
    print("\n🔍 Checking save retry logic...\n")
    
    with open('AI_infrastructure/routes/agent_routes_v4.py', 'r') as f:
        content = f.read()
    
    # Check for retry in user message save
    if 'max_retries' in content and 'for attempt in range(max_retries)' in content:
        print("✅ User message save has retry logic")
    else:
        print("❌ User message save MISSING retry logic")
    
    # Check for retry in assistant message save (combined_agent_worker.py)
    with open('AI_infrastructure/core/combined_agent_worker.py', 'r') as f:
        worker_content = f.read()
    
    if 'max_retries' in worker_content and 'save_message_to_database' in worker_content:
        print("✅ Assistant message save has retry logic")
    else:
        print("⚠️ Assistant message save may be missing retry logic")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_message_save_flow.py <thread_slug>")
        print("\nOr run all diagnostic tests:")
        print("  python test_message_save_flow.py --check-all")
        sys.exit(1)
    
    if sys.argv[1] == '--check-all':
        check_recent_save_failures()
        test_save_retry_logic()
    else:
        thread_slug = sys.argv[1]
        test_message_completeness(thread_slug)
        check_recent_save_failures()
        test_save_retry_logic()
