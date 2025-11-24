"""
Test message pagination performance
Compare loading 5 messages vs all messages
"""

import requests
import time
import json

API_BASE = "http://localhost:5001"

# Use a thread that has many messages (from the console logs)
THREAD_ID = "1763825917803"  # G 23 AI prime test - has 37 messages

def test_pagination():
    print("=" * 80)
    print("MESSAGE PAGINATION PERFORMANCE TEST")
    print("=" * 80)
    
    # Test 1: Load only 5 messages (FAST)
    print("\n[TEST 1] Loading only 5 most recent messages...")
    start = time.time()
    response = requests.get(
        f"{API_BASE}/api/threads/messages/get",
        params={"thread_id": THREAD_ID, "limit": 5, "offset": 0}
    )
    elapsed_5 = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Loaded {data['data']['count']} messages in {elapsed_5:.3f}s")
        print(f"   Total messages in thread: {data['data']['total']}")
        print(f"   Has more: {data['data']['has_more']}")
        print(f"   Message roles: {[m['role'] for m in data['data']['messages']]}")
    else:
        print(f"❌ FAILED: {response.status_code} - {response.text}")
        return
    
    # Test 2: Load ALL messages (SLOW)
    print("\n[TEST 2] Loading ALL messages (no pagination)...")
    start = time.time()
    response = requests.get(
        f"{API_BASE}/api/threads/messages/get",
        params={"thread_id": THREAD_ID}
    )
    elapsed_all = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Loaded {data['data']['count']} messages in {elapsed_all:.3f}s")
        print(f"   Total messages: {data['data']['total']}")
    else:
        print(f"❌ FAILED: {response.status_code} - {response.text}")
        return
    
    # Calculate improvement
    improvement = ((elapsed_all - elapsed_5) / elapsed_all) * 100
    speedup = elapsed_all / elapsed_5
    
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print(f"5 messages:  {elapsed_5:.3f}s")
    print(f"All messages: {elapsed_all:.3f}s")
    print(f"\n🚀 SPEEDUP: {speedup:.1f}x faster ({improvement:.0f}% reduction)")
    print("=" * 80)

    # Test 3: Load next page
    print("\n[TEST 3] Loading next 5 messages (offset=5)...")
    start = time.time()
    response = requests.get(
        f"{API_BASE}/api/threads/messages/get",
        params={"thread_id": THREAD_ID, "limit": 5, "offset": 5}
    )
    elapsed_page2 = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Loaded page 2 ({data['data']['count']} messages) in {elapsed_page2:.3f}s")
        print(f"   Offset: {data['data']['offset']}")
        print(f"   Has more: {data['data']['has_more']}")
    else:
        print(f"❌ FAILED: {response.status_code} - {response.text}")

if __name__ == '__main__':
    test_pagination()
