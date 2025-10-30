"""
Test V3 Chat Server - Send a request to test tool execution
"""

import requests
import json

print("\n" + "="*80)
print("📨 SENDING TEST REQUEST TO V3 CHAT SERVER")
print("="*80 + "\n")

# Step 1: Check server status
print("[1] Checking V3 server status...")
try:
    response = requests.get("http://localhost:5002/api/v3/status", timeout=5)
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Server operational")
        print(f"   Tools loaded: {status['tools_loaded']}")
        print(f"   Implementations: {status['implementations']}")
    else:
        print(f"❌ Server returned status {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    exit(1)

# Step 2: Send chat request
print(f"\n[2] Sending chat request...")

payload = {
    "message": "List my Gmail messages",
    "user_id": 1
}

print(f"   Message: {payload['message']}")
print(f"   User ID: {payload['user_id']}")

try:
    response = requests.post(
        "http://localhost:5002/api/v3/chat",
        json=payload,
        timeout=30
    )
    
    print(f"\n[3] Response received")
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n{'='*80}")
        print("✅ V3 CHAT REQUEST SUCCESSFUL")
        print("="*80)
        
        print(f"\n📝 AI Response:")
        print(f"   {result['response'][:200]}...")
        
        print(f"\n🔧 Tools Used:")
        tools_used = result.get('tools_used', [])
        if tools_used:
            for tool in tools_used:
                status = "✅" if tool['success'] else "❌"
                print(f"   {status} {tool['name']}")
                if tool.get('error'):
                    print(f"      Error: {tool['error']}")
        else:
            print(f"   No tools used (Claude responded without tools)")
        
        print(f"\n📊 Metadata:")
        print(f"   Stop reason: {result.get('stop_reason')}")
        print(f"   Success: {result.get('success')}")
        
        print(f"\n{'='*80}")
        
        # Check if tools were actually used
        if not tools_used:
            print(f"\n⚠️  WARNING: Claude did NOT use tools!")
            print(f"   This means Claude described tools instead of using them.")
            print(f"   The XML vs JSON tool_use issue may still exist.")
        else:
            print(f"\n🎉 SUCCESS: Claude USED tools via V3 system!")
            print(f"   V3 architecture is working correctly.")
        
    else:
        print(f"\n❌ Request failed")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Request error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
