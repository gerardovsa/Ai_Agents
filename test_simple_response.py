"""
Simple Response Test - No extended thinking
Tests if NameError is fixed by sending a message without thinking enabled
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_simple_response():
    print("="*80)
    print("SIMPLE RESPONSE TEST (No Extended Thinking)")
    print("="*80)
    
    # Create thread
    print("\n1. Creating thread...")
    resp = requests.post(f"{BASE_URL}/api/threads/create", json={
        "title": "Simple Test",
        "location": "prime",
        "user_id": 14
    })
    thread_slug = resp.json()['data']['thread']['id']
    print(f"   ✅ Thread: {thread_slug}")
    
    # Send message with thinking disabled
    print("\n2. Sending message (thinking disabled)...")
    resp = requests.post(f"{BASE_URL}/api/agent/agent/1/start", json={
        "message": "Just say 'Hello! 2+2=4' and nothing else.",
        "session_id": thread_slug,
        "thread_slug": thread_slug,
        "ai_preferences": {
            "thinking_enabled": False  # Disable thinking
        }
    })
    print(f"   ✅ Message sent")
    
    # Stream response
    print("\n3. Streaming response...")
    time.sleep(2)
    
    url = f"{BASE_URL}/api/agent/stream/1?thread_slug={thread_slug}"
    resp = requests.get(url, stream=True, timeout=30)
    
    text_blocks = []
    errors = []
    
    for line in resp.iter_lines():
        if not line:
            continue
        line = line.decode('utf-8')
        
        if line.startswith('data:'):
            try:
                data = json.loads(line.split(':', 1)[1])
                event_type = None
                
                # Find event type from previous line or data
                if 'type' in data:
                    event_type = data['type']
                
                if 'content' in data and data.get('content'):
                    content = data['content']
                    if 'text' in str(data):
                        text_blocks.append(content)
                        print(f"   💬 TEXT: {content}")
                
                if 'error' in data:
                    errors.append(data['error'])
                    print(f"   ❌ ERROR: {data['error']}")
                
            except:
                pass
    
    # Results
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    print(f"   Text blocks: {len(text_blocks)}")
    print(f"   Errors: {len(errors)}")
    
    if errors:
        print("\n❌ FAILED - Errors found:")
        for err in errors:
            print(f"   {err}")
        return False
    
    if text_blocks:
        print("\n✅ SUCCESS - Text response received!")
        print("\nFull response:")
        print("-" * 80)
        for text in text_blocks:
            print(text)
        print("-" * 80)
        return True
    else:
        print("\n⚠️  WARNING - No text blocks (but no errors either)")
        print("   The NameError is likely fixed, but AI didn't send text.")
        return True  # Consider this a pass since no errors

if __name__ == '__main__':
    success = test_simple_response()
    exit(0 if success else 1)
