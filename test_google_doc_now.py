"""
Direct Test: AI Agent Google Docs Tool Execution
=================================================
"""

import requests
import json

print("="*70)
print("🧪 Testing AI Agent - Create Google Doc")
print("="*70)

# Prepare the request
url = "http://localhost:5001/api/agent/chat"
payload = {
    "user_id": 1,
    "message": "Create a Google Doc titled 'AI Agent Test Document' with the following content:\n\n# AI Agent Test\n\nThis document was created automatically by the AI agent to verify that:\n- OAuth credentials are correctly detected\n- Tool execution is working\n- Google Docs API integration is functional\n\n**Status:** Testing in progress...",
    "ui_context": "business_ai_platform",
    "provider": "anthropic",
    "session_id": "test_session_123"
}

print(f"\n📤 Sending request:")
print(f"   Endpoint: {url}")
print(f"   User ID: {payload['user_id']}")
print(f"   Message: Create Google Doc titled 'AI Agent Test Document'")

try:
    print(f"\n⏳ Waiting for AI agent response (this may take 10-30 seconds)...")
    
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ SUCCESS! Response received")
        print("="*70)
        print(data.get('response', 'No response'))
        print("="*70)
        
        # Look for document URL
        response_text = data.get('response', '')
        if 'docs.google.com' in response_text:
            print(f"\n🎉 DOCUMENT CREATED! URL found in response")
            # Extract URL
            import re
            urls = re.findall(r'https://docs\.google\.com/document/d/[^\s\)]+', response_text)
            if urls:
                print(f"   📄 Document URL: {urls[0]}")
        elif 'document_id' in response_text.lower():
            print(f"\n✅ Document ID mentioned in response")
        else:
            print(f"\n⚠️ Response received but no clear document URL/ID found")
            
    elif response.status_code == 401:
        print(f"\n❌ AUTHENTICATION ERROR (401)")
        print(f"   API endpoint requires authentication")
        
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   {json.dumps(error_data, indent=2)}")
        except:
            print(f"   {response.text[:300]}")
            
except requests.exceptions.ConnectionError:
    print(f"\n❌ CONNECTION ERROR - Flask server not running?")
    print(f"   Run: BISTART")
    
except requests.exceptions.Timeout:
    print(f"\n⏰ TIMEOUT - Request took longer than 60 seconds")
    print(f"   The AI agent might still be processing...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*70)
