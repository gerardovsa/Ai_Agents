"""
Diagnostic Script: Check for Duplicate Assistant Messages in Database
Analyzes thread 1768796970052 (from server logs) for consecutive assistant messages
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AI_infrastructure.shared.database_utils import execute_query

print("="*100)
print("DIAGNOSTIC: Checking for Duplicate Assistant Messages")
print("="*100)

# Thread ID from server logs
thread_slug = "1768796970052"

# Step 1: Get thread's internal ID
print(f"\n[STEP 1] Looking up internal thread ID for slug: {thread_slug}")
thread_result = execute_query("""
    SELECT id, thread_slug, name, user_id 
    FROM sessions.threads 
    WHERE thread_slug = %s
""", (thread_slug,), fetch_mode='one')

if not thread_result:
    print(f"❌ Thread not found: {thread_slug}")
    sys.exit(1)

thread_id = thread_result['id']
print(f"✅ Found thread: ID={thread_id}, Name='{thread_result['name']}', User={thread_result['user_id']}")

# Step 2: Load ALL messages in chronological order
print(f"\n[STEP 2] Loading all messages in chronological order (ASC)...")
messages = execute_query("""
    SELECT id, role, created_at, 
           LEFT(content::text, 100) as content_preview
    FROM sessions.messages
    WHERE thread_id = %s
    ORDER BY created_at ASC, id ASC
""", (thread_id,), fetch_mode='all')

print(f"✅ Loaded {len(messages)} messages")

# Step 3: Analyze for consecutive assistant messages
print(f"\n[STEP 3] Analyzing for consecutive assistant messages...")
print("-"*100)

consecutive_groups = []
current_group = []

for i, msg in enumerate(messages):
    role = msg['role']
    msg_id = msg['id']
    created_at = msg['created_at']
    preview = msg['content_preview']
    
    # Print each message
    print(f"[{i:3d}] {role:10s} | ID={msg_id:5d} | {created_at} | {preview[:60]}...")
    
    # Check if this is part of a consecutive assistant group
    if role == 'assistant':
        if current_group and messages[i-1]['role'] == 'assistant':
            # Continuing consecutive group
            current_group.append((i, msg))
        else:
            # Start new group (only if next is also assistant)
            if i + 1 < len(messages) and messages[i+1]['role'] == 'assistant':
                current_group = [(i, msg)]
    else:
        # User message - end any current group
        if len(current_group) > 1:
            consecutive_groups.append(current_group)
        current_group = []

# Catch last group
if len(current_group) > 1:
    consecutive_groups.append(current_group)

print("-"*100)

# Step 4: Report findings
print(f"\n[STEP 4] FINDINGS:")
print("="*100)

if not consecutive_groups:
    print("✅ NO consecutive assistant messages found in database!")
    print("   → Database is clean, duplication must be happening during message validation")
else:
    print(f"❌ FOUND {len(consecutive_groups)} group(s) of consecutive assistant messages:")
    for group_idx, group in enumerate(consecutive_groups, 1):
        print(f"\n  Group {group_idx}: {len(group)} consecutive assistant messages")
        for msg_idx, (i, msg) in enumerate(group, 1):
            print(f"    [{i:3d}] ID={msg['id']:5d} | {msg['created_at']} | {msg['content_preview'][:60]}...")

print("\n" + "="*100)
print("RECOMMENDATION:")
if not consecutive_groups:
    print("  ✅ Database is clean - issue is in conversation validation (combined_agent_worker.py)")
    print("  ✅ Fix applied: Duplicate assistant messages now DISCARDED instead of APPENDED")
    print("  → Restart Flask server to apply fix")
else:
    print("  ❌ Database contains duplicate assistant messages!")
    print("  → Run cleanup script to remove duplicates from database")
    print("  → Investigate message save logic to prevent future duplicates")
print("="*100)
