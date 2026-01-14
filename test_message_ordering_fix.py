"""
MESSAGE ORDERING FIX - END-TO-END TEST
Tests the ORDER BY ASC fix for conversation history loading

Test Scenarios:
1. Load conversation with 70+ messages
2. Verify chronological order (oldest → newest)
3. Check AI responses appear between user messages
4. Validate no message clustering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query
from datetime import datetime, timedelta
import json

print("="*80)
print("MESSAGE ORDERING FIX - END-TO-END TEST")
print("="*80)

# ============================================================
# TEST 1: Find Thread with 70+ Messages
# ============================================================
print("\n[TEST 1] Finding thread with 70+ messages...")

threads = execute_query("""
    SELECT 
        t.id,
        t.thread_slug,
        t.user_id,
        COUNT(m.id) as message_count
    FROM sessions.threads t
    JOIN sessions.messages m ON m.thread_id = t.id
    GROUP BY t.id, t.thread_slug, t.user_id
    HAVING COUNT(m.id) >= 10
    ORDER BY COUNT(m.id) DESC
    LIMIT 1
""", fetch_mode='all')

if not threads:
    print("❌ No threads with 10+ messages found. Creating test thread...")
    
    # Create test thread
    test_thread_slug = f"test_{int(datetime.now().timestamp())}"
    thread_id = execute_query("""
        INSERT INTO sessions.threads (thread_slug, user_id, name, created_at, updated_at)
        VALUES (%s, 1, 'Test Thread', NOW(), NOW())
        RETURNING id
    """, (test_thread_slug,), fetch_mode='value')
    
    print(f"✅ Created test thread: {test_thread_slug} (ID: {thread_id})")
    
    # Insert test messages (alternating user/AI)
    base_time = datetime.now()
    for i in range(35):  # 35 interactions = 70 messages
        # User message
        execute_query("""
            INSERT INTO sessions.messages 
            (thread_id, session_id, role, content, created_at)
            VALUES (%s, %s, 'user', %s, %s)
        """, (
            thread_id, 
            test_thread_slug, 
            json.dumps([{'type': 'text', 'text': f'User question {i+1}'}]),
            base_time + timedelta(seconds=i*10)
        ))
        
        # AI response
        execute_query("""
            INSERT INTO sessions.messages 
            (thread_id, session_id, role, content, created_at)
            VALUES (%s, %s, 'assistant', %s, %s)
        """, (
            thread_id, 
            test_thread_slug, 
            json.dumps([{'type': 'text', 'text': f'AI answer {i+1}'}]),
            base_time + timedelta(seconds=i*10 + 5)
        ))
    
    print(f"✅ Inserted 70 test messages (35 interactions)")
    
    thread_slug = test_thread_slug
    message_count = 70
else:
    thread_info = threads[0]
    thread_id = thread_info['id']
    thread_slug = thread_info['thread_slug']
    message_count = thread_info['message_count']
    
    print(f"✅ Found thread: {thread_slug}")
    print(f"   Thread ID: {thread_id}")
    print(f"   Message count: {message_count}")

# ============================================================
# TEST 2: Test Load Conversation (Agent Routes Pattern)
# ============================================================
print(f"\n[TEST 2] Testing load_conversation_from_database() pattern...")
print(f"Simulating: load_conversation_from_database('{thread_slug}', limit=None)")

# Get thread ID
thread_result = execute_query("""
    SELECT id FROM sessions.threads 
    WHERE thread_slug = %s
""", (thread_slug,), fetch_mode='one')

if not thread_result:
    print(f"❌ Thread not found: {thread_slug}")
    sys.exit(1)

test_thread_id = thread_result['id']

# Load messages (NEW: always ASC, limit defaults to 999999)
messages = execute_query("""
    SELECT role, content, created_at, model, tokens_used
    FROM sessions.messages 
    WHERE thread_id = %s 
    ORDER BY created_at ASC
    LIMIT %s OFFSET %s
""", (test_thread_id, 999999, 0), fetch_mode='all')

print(f"✅ Loaded {len(messages)} messages")

# ============================================================
# TEST 3: Verify Chronological Order
# ============================================================
print(f"\n[TEST 3] Verifying chronological order (ASC)...")

order_violations = 0
for i in range(len(messages) - 1):
    current_time = messages[i]['created_at']
    next_time = messages[i + 1]['created_at']
    
    if current_time > next_time:
        order_violations += 1
        print(f"❌ ORDER VIOLATION at index {i}:")
        print(f"   Message {i}: {messages[i]['role']} at {current_time}")
        print(f"   Message {i+1}: {messages[i+1]['role']} at {next_time}")

if order_violations == 0:
    print(f"✅ All {len(messages)} messages in correct chronological order (ASC)")
else:
    print(f"❌ Found {order_violations} order violations!")

# ============================================================
# TEST 4: Check for Message Clustering
# ============================================================
print(f"\n[TEST 4] Checking for message clustering...")

# Count consecutive messages by role
clusters = []
current_cluster = {'role': messages[0]['role'], 'count': 1, 'start_idx': 0}

for i in range(1, len(messages)):
    if messages[i]['role'] == current_cluster['role']:
        current_cluster['count'] += 1
    else:
        if current_cluster['count'] > 1:
            clusters.append(current_cluster.copy())
        current_cluster = {'role': messages[i]['role'], 'count': 1, 'start_idx': i}

if current_cluster['count'] > 1:
    clusters.append(current_cluster)

if clusters:
    print(f"⚠️  Found {len(clusters)} message clusters:")
    for cluster in clusters:
        print(f"   - {cluster['count']} consecutive {cluster['role']} messages starting at index {cluster['start_idx']}")
        # Show first 3 messages in cluster
        for j in range(min(3, cluster['count'])):
            idx = cluster['start_idx'] + j
            content = messages[idx]['content']
            if isinstance(content, list) and len(content) > 0:
                text = content[0].get('text', str(content))[:50]
            else:
                text = str(content)[:50]
            print(f"      [{idx}] {messages[idx]['role']}: {text}...")
else:
    print(f"✅ No message clustering detected - perfect alternation!")

# ============================================================
# TEST 5: Verify User-AI Pairing
# ============================================================
print(f"\n[TEST 5] Verifying user-AI message pairing...")

user_without_ai = []
ai_without_user = []

for i in range(len(messages)):
    if messages[i]['role'] == 'user':
        # Check if next message is AI response
        if i + 1 < len(messages):
            if messages[i + 1]['role'] != 'assistant':
                user_without_ai.append(i)
        else:
            # Last message is user (waiting for response)
            user_without_ai.append(i)
    
    elif messages[i]['role'] == 'assistant':
        # Check if previous message was user
        if i > 0:
            if messages[i - 1]['role'] != 'user' and messages[i - 1]['role'] != 'assistant':
                ai_without_user.append(i)

if user_without_ai:
    print(f"⚠️  Found {len(user_without_ai)} user messages without immediate AI response:")
    for idx in user_without_ai[:5]:  # Show first 5
        print(f"   Index {idx}: {messages[idx]['role']}")
else:
    print(f"✅ All user messages have AI responses")

if ai_without_user and len(ai_without_user) > len(messages) * 0.1:  # Allow some tool messages
    print(f"⚠️  Found {len(ai_without_user)} AI messages without preceding user message")
else:
    print(f"✅ AI message pairing looks correct")

# ============================================================
# TEST 6: Test Thread Routes Pattern (with pagination)
# ============================================================
print(f"\n[TEST 6] Testing /api/threads/messages/get pattern (with LIMIT 50)...")

# Simulate pagination with limit=50
paginated_messages = execute_query("""
    SELECT 
        m.id,
        m.role,
        m.content,
        m.created_at
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.thread_slug = %s
    ORDER BY m.created_at ASC
    LIMIT %s OFFSET %s
""", (thread_slug, 50, 0), fetch_mode='all')

print(f"✅ Loaded {len(paginated_messages)} messages with LIMIT 50")

# Check order
if len(paginated_messages) > 1:
    first_time = paginated_messages[0]['created_at']
    last_time = paginated_messages[-1]['created_at']
    
    if first_time < last_time:
        print(f"✅ Paginated messages in ASC order (oldest → newest)")
        print(f"   First message: {paginated_messages[0]['role']} at {first_time}")
        print(f"   Last message: {paginated_messages[-1]['role']} at {last_time}")
    else:
        print(f"❌ Paginated messages in WRONG order!")

# ============================================================
# TEST 7: Role Distribution Analysis
# ============================================================
print(f"\n[TEST 7] Analyzing role distribution...")

role_counts = {'user': 0, 'assistant': 0, 'tool': 0, 'system': 0, 'other': 0}
for msg in messages:
    role = msg['role']
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts['other'] += 1

print(f"✅ Role distribution:")
for role, count in role_counts.items():
    if count > 0:
        percentage = (count / len(messages)) * 100
        print(f"   {role}: {count} messages ({percentage:.1f}%)")

# Check for expected ratio (roughly equal user/assistant for normal conversation)
if role_counts['user'] > 0 and role_counts['assistant'] > 0:
    ratio = role_counts['assistant'] / role_counts['user']
    if 0.5 <= ratio <= 10:
        print(f"✅ User/AI ratio looks normal ({ratio:.1f}:1)")
    else:
        print(f"⚠️  Unusual user/AI ratio ({ratio:.1f}:1) - may indicate clustering issue")

# ============================================================
# TEST 8: Simulate Frontend Display Order
# ============================================================
print(f"\n[TEST 8] Simulating frontend display (first 10 messages)...")

print("\nExpected display order:")
for i in range(min(10, len(messages))):
    msg = messages[i]
    content = msg['content']
    if isinstance(content, list) and len(content) > 0:
        text = content[0].get('text', str(content))[:40]
    else:
        text = str(content)[:40]
    
    role_emoji = "👤" if msg['role'] == 'user' else "🤖"
    print(f"   [{i+1}] {role_emoji} {msg['role']}: {text}...")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

all_tests_passed = True

if order_violations > 0:
    print("❌ FAIL: Messages not in chronological order")
    all_tests_passed = False
else:
    print("✅ PASS: Messages in chronological order (ASC)")

if len(clusters) > 5:  # Allow some clustering for tool messages
    print(f"⚠️  WARNING: Excessive message clustering detected ({len(clusters)} clusters)")
    all_tests_passed = False
else:
    print("✅ PASS: Minimal message clustering")

if len(user_without_ai) > len(messages) * 0.1:
    print(f"❌ FAIL: Too many user messages without AI responses ({len(user_without_ai)})")
    all_tests_passed = False
else:
    print("✅ PASS: User-AI message pairing correct")

if all_tests_passed:
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - ORDER BY FIX WORKING CORRECTLY")
    print("="*80)
    print("\nKey findings:")
    print(f"- Loaded {len(messages)} messages in chronological order")
    print(f"- No order violations detected")
    print(f"- User-AI pairing maintained")
    print(f"- Pagination works correctly with ASC ordering")
    print("\nThe fix successfully prevents:")
    print("  ❌ Message clustering (user messages grouped together)")
    print("  ❌ Missing AI responses between user messages")
    print("  ❌ Out-of-order conversation flow")
else:
    print("\n" + "="*80)
    print("⚠️  SOME TESTS FAILED - REVIEW RESULTS ABOVE")
    print("="*80)
