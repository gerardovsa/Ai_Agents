"""
Test Google Docs Tool Execution via AI Agent API
=================================================
This tests if the AI agent can actually execute Google Docs tools
with the fixed OAuth credentials.
"""

import requests
import json
import time

# API endpoint
API_URL = "http://localhost:5001/api/agent/chat"

print("="*70)
print("🧪 Testing Google Docs Tool Execution via AI Agent")
print("="*70)

# Test request payload
payload = {
    "user_id": 1,  # admin user with Google OAuth
    "message": "Create a Google Doc titled 'AI Agent Test Document' with the content: 'This is a test document created by the AI agent to verify tool execution is working correctly.'",
    "ui_context": "business_ai_platform",
    "provider": "anthropic",
    "session_id": f"test_session_{int(time.time())}",
    "enable_tools": True  # Explicitly enable tools
}

print(f"\n📤 Sending request to AI agent:")
print(f"   User ID: {payload['user_id']}")
print(f"   Message: {payload['message'][:80]}...")
print(f"   Tools Enabled: {payload['enable_tools']}")

try:
    print(f"\n🔄 Calling API endpoint: {API_URL}")
    
    response = requests.post(
        API_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60  # 60 second timeout for tool execution
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ SUCCESS! AI Agent Response:")
        print(f"   Response Length: {len(data.get('response', ''))} chars")
        print(f"   Tools Used: {data.get('tools_used', 'Unknown')}")
        
        # Print the full response
        print(f"\n📄 Full AI Response:")
        print("-" * 70)
        print(data.get('response', 'No response'))
        print("-" * 70)
        
        # Check if a document was created
        if 'document' in data.get('response', '').lower() or 'created' in data.get('response', '').lower():
            print(f"\n🎉 Document appears to have been created!")
            
            # Try to extract document ID or URL from response
            response_text = data.get('response', '')
            if 'docs.google.com' in response_text:
                print(f"   ✅ Google Docs URL found in response")
            if 'document_id' in response_text.lower():
                print(f"   ✅ Document ID mentioned in response")
        else:
            print(f"\n⚠️ Not clear if document was created. Check response above.")
        
    elif response.status_code == 401:
        print(f"\n❌ AUTHENTICATION ERROR (401)")
        print(f"   The API requires authentication.")
        print(f"   Solution: Update the test to use proper authentication headers.")
        
    elif response.status_code == 500:
        print(f"\n❌ SERVER ERROR (500)")
        try:
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"   Raw error: {response.text[:200]}")
            
    else:
        print(f"\n❌ UNEXPECTED STATUS CODE: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"\n❌ REQUEST TIMEOUT")
    print(f"   The request took longer than 60 seconds.")
    print(f"   This might mean the tool is executing but taking a while.")
    
except requests.exceptions.ConnectionError:
    print(f"\n❌ CONNECTION ERROR")
    print(f"   Could not connect to {API_URL}")
    print(f"   Make sure Flask server is running (run BISTART)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ Test Complete")
print("="*70)

print(f"\n💡 NEXT STEPS:")
print(f"   1. Check the Flask console logs for tool execution details")
print(f"   2. Check your Google Drive for the created document")
print(f"   3. If document wasn't created, check OAuth credentials are valid")
