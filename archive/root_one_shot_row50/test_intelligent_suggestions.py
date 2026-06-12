"""
Test script to verify intelligent tool suggestions with mandatory guide requirements
"""
import requests
import json

# Test endpoint
url = "http://localhost:5001/api/agent/stream"

# Test message that should trigger calculator suggestions
test_message = "Calculate a quote for business cards"

# Request payload
payload = {
    "message": test_message,
    "user_id": 14,
    "thread_id": "test_thread_001",
    "session_id": "test_session_001"
}

print("="*80)
print("TESTING INTELLIGENT TOOL SUGGESTIONS")
print("="*80)
print(f"Test Message: '{test_message}'")
print(f"Expected: Should suggest calculator tools with mandatory guide warnings")
print("="*80)
print("\nSending request...")

try:
    response = requests.post(url, json=payload, stream=True, timeout=30)
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        print("STREAMING RESPONSE:")
        print("-"*80)
        
        # Collect all chunks to analyze system prompt
        all_text = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_str = decoded_line[6:]  # Remove 'data: ' prefix
                    if data_str.strip() and data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if 'content' in data:
                                all_text += data['content']
                                print(data['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            pass
        
        print("\n" + "-"*80)
        print("\nTEST RESULT:")
        print("✅ Request successful - check Flask terminal logs for system prompt")
        print("   Look for: '🎯 INTELLIGENT TOOL SUGGESTIONS'")
        print("   Should show: '⚠️  MUST call first: inhouse_get_domain_guide() → inhouse_calculator_guide()'")
        
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Error: {e}")
    print("\nMake sure Flask server is running on http://localhost:5001")

print("\n" + "="*80)
print("To see the intelligent suggestions in the system prompt:")
print("1. Check the Flask terminal output")
print("2. Look for '[STREAM] 🎯 INTELLIGENT TOOL SELECTION' logs")
print("3. The AI's system prompt will contain the new mandatory guide warnings")
print("="*80)
