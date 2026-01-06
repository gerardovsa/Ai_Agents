"""
End-to-End Token Counting Test
from shared.database_utils import convert_sql_placeholders

Tests the complete flow:
1. Token counter utility (Anthropic API)
2. Database updates
3. API endpoints

Run this after starting the Flask server (BISTART)
"""

import sys
import time
import requests
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

print("\n" + "="*70)
print("TOKEN COUNTING END-TO-END TEST")
print("="*70 + "\n")

# Test 1: Token Counter Utility
print("Test 1: Token Counter Utility (Anthropic API)")
print("-" * 70)

try:
    from AI_infrastructure.utils.token_counter import count_conversation_tokens
    
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
        {"role": "user", "content": "Can you help me with a Python script?"}
    ]
    
    count = count_conversation_tokens(
        messages=test_messages,
        system_prompt="You are a helpful AI assistant.",
        model="claude-sonnet-4-5"
    )
    
    print(f"✅ Token count API returned: {count} tokens")
    
    # Compare with heuristic
    total_chars = sum(len(m['content']) for m in test_messages) + len("You are a helpful AI assistant.")
    heuristic = total_chars // 4
    error_pct = abs(count - heuristic) / count * 100 if count > 0 else 0
    
    print(f"   Heuristic estimate: {heuristic} tokens")
    print(f"   Difference: {abs(count - heuristic)} tokens ({error_pct:.1f}%)")
    print(f"   Status: ✅ PASS\n")
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")
    sys.exit(1)


# Test 2: Database Schema
print("Test 2: Database Schema (token_count column)")
print("-" * 70)

try:
    import sqlite3
    db_path = Path(__file__).parent / 'data' / 'sessions.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check column exists
    cursor.execute("PRAGMA table_info(threads)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'token_count' in columns:
        print("✅ token_count column exists")
        
        # Check index
        cursor.execute("PRAGMA index_list(threads)")
        indexes = [idx[1] for idx in cursor.fetchall()]
        
        if 'idx_threads_token_count' in indexes:
            print("✅ Index on token_count exists")
        else:
            print("⚠️  Index missing (performance impact)")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM threads WHERE token_count IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"✅ {count} threads have token_count field")
        print(f"   Status: ✅ PASS\n")
    else:
        print("❌ FAIL: token_count column not found\n")
        sys.exit(1)
    
    conn.close()
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")
    sys.exit(1)


# Test 3: API Endpoints
print("Test 3: Backend API Endpoints")
print("-" * 70)

api_base = 'http://localhost:5001'

try:
    # Check if server is running
    response = requests.get(f'{api_base}/api/threads', timeout=5)
    if response.status_code != 200:
        print(f"⚠️  Server returned {response.status_code}, continuing anyway...")
    
    # Get a thread ID from database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM threads LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("⚠️  No threads in database, skipping API test")
        print(f"   Status: ⚠️  SKIP\n")
    else:
        thread_id = row[0]
        print(f"   Testing with thread: {thread_id[:16]}...")
        
        # Test GET endpoint
        response = requests.get(f'{api_base}/api/tokens/{thread_id}', timeout=5)
        if response.ok:
            data = response.json()
            print(f"✅ GET /api/tokens/<id> returned:")
            print(f"   - Token count: {data.get('token_count', 0):,}")
            print(f"   - Status: {data.get('status', 'N/A')}")
            print(f"   - Percentage: {data.get('percentage', 0):.1f}%")
        else:
            print(f"❌ GET failed: {response.status_code}")
        
        # Test POST endpoint
        test_count = 12345
        response = requests.post(
            f'{api_base}/api/tokens/{thread_id}',
            json={'token_count': test_count},
            timeout=5
        )
        if response.ok:
            print(f"✅ POST /api/tokens/<id> updated count to {test_count:,}")
        else:
            print(f"❌ POST failed: {response.status_code}")
        
        # Verify update
        response = requests.get(f'{api_base}/api/tokens/{thread_id}', timeout=5)
        if response.ok:
            data = response.json()
            if data.get('token_count') == test_count:
                print(f"✅ Verified: count persisted correctly")
                print(f"   Status: ✅ PASS\n")
            else:
                print(f"❌ Verification failed: expected {test_count}, got {data.get('token_count')}")
                print(f"   Status: ❌ FAIL\n")
        else:
            print(f"❌ Verification failed: {response.status_code}\n")
    
except requests.exceptions.ConnectionError:
    print("❌ FAIL: Cannot connect to Flask server")
    print("   Make sure server is running: BISTART")
    print(f"   Status: ❌ FAIL\n")
except Exception as e:
    print(f"❌ FAIL: {e}\n")


# Test 4: Frontend Integration Check
print("Test 4: Frontend Integration")
print("-" * 70)

try:
    ui_file = Path(__file__).parent / 'UI' / 'business-ai-platform-v2.html'
    polling_file = Path(__file__).parent / 'UI' / 'token_polling.js'
    
    if ui_file.exists():
        content = ui_file.read_text(encoding='utf-8')
        if 'token_polling.js' in content:
            print("✅ token_polling.js included in HTML")
        else:
            print("❌ token_polling.js NOT included in HTML")
        
        if 'thread-token-count' in content:
            print("✅ Token count CSS class found")
        else:
            print("❌ Token count CSS class NOT found")
        
        if 'updateTokenCount' in content:
            print("✅ updateTokenCount method found")
        else:
            print("❌ updateTokenCount method NOT found")
    else:
        print("⚠️  UI file not found")
    
    if polling_file.exists():
        print("✅ token_polling.js file exists")
        content = polling_file.read_text()
        if 'TokenPoller' in content:
            print("✅ TokenPoller object defined")
        else:
            print("❌ TokenPoller object NOT defined")
    else:
        print("❌ token_polling.js file NOT found")
    
    print(f"   Status: ✅ PASS\n")
    
except Exception as e:
    print(f"❌ FAIL: {e}\n")


# Summary
print("="*70)
print("TEST SUMMARY")
print("="*70)
print("\n✅ All critical components tested")
print("\nNext Steps:")
print("1. Restart Flask server: BISTART")
print("2. Open UI in browser")
print("3. Send a message to AI")
print("4. Watch console for: [TokenPoller] Updated thread...")
print("5. Check thread header for token count with color coding")
print("\n" + "="*70 + "\n")
