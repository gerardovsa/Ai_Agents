#!/usr/bin/env python3
"""
Debug tool execution - check exactly what's being sent to Claude API
"""

import requests
import json

print("="*80)
print("DEBUG TOOL EXECUTION")
print("="*80)

# Login
print("\n[1] Logging in...")
login_response = requests.get('http://localhost:5001/api/auth/login')
token = login_response.json()['token']
print(f"✅ Token: {token[:20]}...")

# Send chat with explicit model
print("\n[2] Sending chat (Watch Flask console for diagnostic output)...")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

chat_payload = {
    'message': 'List my Gmail messages',  # Simple tool call
    'provider': 'anthropic',
    'model': 'claude-sonnet-4-5-20250929'  # Explicit model
}

print(f"\n📤 REQUEST:")
print(json.dumps(chat_payload, indent=2))

chat_response = requests.post(
    'http://localhost:5001/api/agent/chat',
    headers=headers,
    json=chat_payload,
    timeout=60
)

print(f"\n📥 RESPONSE STATUS: {chat_response.status_code}")

if chat_response.status_code == 200:
    data = chat_response.json()
    response_text = data.get('response', '')
    
    print(f"\n📄 AI RESPONSE (first 300 chars):")
    print(response_text[:300])
    
    print(f"\n🔍 METADATA:")
    print(f"   tools_used: {data.get('tools_used', [])}")
    print(f"   tool_calls: {len(data.get('tool_calls', []))}")
    
    # Check for XML hallucination
    if '<tool' in response_text.lower() or '<execute>' in response_text:
        print(f"\n❌ PROBLEM: Response contains XML-like tool syntax!")
        print(f"   This means Claude is DESCRIBING tools, not USING them")
    elif data.get('tools_used'):
        print(f"\n✅ SUCCESS: Tools were actually executed!")
        print(f"   Tools used: {[t.get('tool_name') for t in data.get('tools_used', [])]}")
    else:
        print(f"\n⚠️  UNCLEAR: No tools used, but no XML either")
        print(f"   Response might be conversational or error")
else:
    print(f"❌ REQUEST FAILED: {chat_response.status_code}")
    print(chat_response.text)

print("\n" + "="*80)
print("CHECK FLASK CONSOLE OUTPUT FOR DIAGNOSTIC LOGS")
print("="*80)
