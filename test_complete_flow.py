"""
Complete Test: Login + Create Google Doc
==========================================
1. Login to get JWT token
2. Use token to call AI agent
3. Ask AI to create Google Doc
"""

import requests
import json

print("="*70)
print("🧪 Complete Test: Login + AI Agent + Google Docs")
print("="*70)

BASE_URL = "http://localhost:5001"

# Step 1: Login (using dev mode - GET request from localhost)
print(f"\n📝 Step 1: Getting dev token (localhost auto-login)...")
login_response = requests.get(
    f"{BASE_URL}/api/auth/login"
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text[:200]}")
    print(f"\n💡 Try updating the password in the script")
    exit(1)

login_data = login_response.json()
if not login_data.get('success'):
    print(f"❌ Login failed: {login_data.get('error', 'Unknown error')}")
    exit(1)

token = login_data.get('token')
print(f"✅ Login successful!")
print(f"   Token: {token[:30]}...")
print(f"   User: {login_data.get('user', {}).get('username')}")

# Step 2: Call AI Agent to create Google Doc
print(f"\n📝 Step 2: Asking AI to create Google Doc...")
chat_response = requests.post(
    f"{BASE_URL}/api/agent/chat",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "message": "Create a Google Doc titled 'AI Agent Test Document' with this content:\n\n# AI Agent Test\n\nThis document was created automatically to verify:\n- ✅ OAuth credentials detected correctly\n- ✅ Tool execution working\n- ✅ Google Docs API integration functional\n\n**Status:** Success!",
        "session_id": "test_session_123",
        "provider": "anthropic"
    },
    timeout=60
)

print(f"\n📥 AI Agent Response Status: {chat_response.status_code}")

if chat_response.status_code == 200:
    data = chat_response.json()
    
    print(f"\n✅ SUCCESS! AI Agent responded")
    print("="*70)
    print(data.get('response', 'No response'))
    print("="*70)
    
    # Look for document URL
    response_text = data.get('response', '')
    if 'docs.google.com' in response_text:
        print(f"\n🎉 DOCUMENT CREATED! URL found in response")
        import re
        urls = re.findall(r'https://docs\.google\.com/document/d/[^\s\)]+', response_text)
        if urls:
            print(f"   📄 Document URL: {urls[0]}")
    elif 'created' in response_text.lower() and 'document' in response_text.lower():
        print(f"\n✅ Document appears to have been created")
    else:
        print(f"\n⚠️ No clear document URL in response")
        
    # Check if tools were used
    if 'tools_used' in data:
        print(f"\n🔧 Tools Used: {data.get('tools_used')}")
        
elif chat_response.status_code == 401:
    print(f"\n❌ AUTHENTICATION ERROR - Token might be invalid")
    
else:
    print(f"\n❌ ERROR: {chat_response.status_code}")
    try:
        print(f"   {json.dumps(chat_response.json(), indent=2)}")
    except:
        print(f"   {chat_response.text[:300]}")

print("\n" + "="*70)
print("✅ Test Complete")
print("="*70)
