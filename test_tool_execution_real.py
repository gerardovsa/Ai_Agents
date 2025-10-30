#!/usr/bin/env python3
"""
Test actual tool execution via the AI agent chat endpoint.
This will verify if tools are actually being executed or just described in XML.
"""

import requests
import json
import time

print("="*80)
print("TESTING REAL TOOL EXECUTION - GOOGLE DOCS CREATION")
print("="*80)

# Step 1: Login (dev mode)
print("\n[1/3] Logging in...")
login_response = requests.get('http://localhost:5001/api/auth/login')
if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()['token']
print(f"✅ Logged in successfully")

# Step 2: Send chat message requesting Google Docs creation
print("\n[2/3] Sending chat request to create Google Doc...")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

chat_payload = {
    'message': 'Create a Google Doc titled "Tool Execution Test" with the content "This document tests if tools actually execute."',
    'conversation_id': None,
    'stream': False
}

chat_response = requests.post(
    'http://localhost:5001/api/agent/chat',
    headers=headers,
    json=chat_payload,
    timeout=60
)

if chat_response.status_code != 200:
    print(f"❌ Chat request failed: {chat_response.status_code}")
    print(f"Response: {chat_response.text}")
    exit(1)

response_data = chat_response.json()
print("✅ Chat response received")

# Step 3: Analyze the response
print("\n[3/3] Analyzing response...")
print("="*80)

ai_response = response_data.get('response', '')
print(f"AI Response (first 500 chars):\n{ai_response[:500]}")
print("="*80)

# Check for XML-like tool call formatting (BAD - means not actually executing)
if '<tool_call>' in ai_response or '<invoke' in ai_response:
    print("\n❌ FAILURE: AI is outputting XML text instead of executing tools!")
    print("   The response contains XML-like tool call syntax.")
    print("   This means Claude is DESCRIBING tools, not USING them.")
    print("\n   Example of what we're seeing:")
    print("   <tool_call><function_name>create_google_doc</function_name>...")
    print("\n   This is the hallucination problem - no real API calls are made!")
    
# Check for actual tool execution indicators
elif 'tool_use' in str(response_data) or 'tools_used' in str(response_data):
    print("\n✅ SUCCESS: Tools appear to be executing!")
    print("   Response contains tool execution metadata.")
    
    # Check if tools_used array is populated
    tools_used = response_data.get('tools_used', [])
    if tools_used:
        print(f"\n   Tools executed: {len(tools_used)}")
        for tool in tools_used:
            print(f"   - {tool.get('tool_name', 'unknown')}")
    else:
        print("\n   ⚠️ tools_used array is empty - may still be XML output issue")
        
else:
    print("\n⚠️ UNCLEAR: Cannot determine if tools executed")
    print("   Response doesn't contain obvious tool execution indicators")

# Check for Google Docs URL in response
import re
docs_url_pattern = r'https://docs\.google\.com/document/d/[\w-]+/edit'
urls_found = re.findall(docs_url_pattern, ai_response)

if urls_found:
    print(f"\n📄 Google Docs URL found: {urls_found[0]}")
    print("   ⚠️ BUT this could be hallucinated! Trying to verify...")
    
    # Try to extract document ID and verify it exists
    doc_id_match = re.search(r'/document/d/([\w-]+)/', urls_found[0])
    if doc_id_match:
        doc_id = doc_id_match.group(1)
        print(f"   Document ID: {doc_id}")
        
        # Try to access the document via API (requires proper auth)
        print(f"   Note: You would need to manually open this URL to verify if it's real")
        print(f"   If you get '404 Not Found', the URL was hallucinated!")
else:
    print("\n📄 No Google Docs URL found in response")

# Print full response for manual inspection
print("\n" + "="*80)
print("FULL RESPONSE DATA:")
print("="*80)
print(json.dumps(response_data, indent=2))

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
if '<tool_call>' in ai_response:
    print("❌ Tools are NOT executing - AI is outputting XML text (hallucinating)")
    print("   The three fixes (prompt, schema, model) may not be active yet.")
    print("   Flask may need a restart or the fixes aren't loaded.")
elif tools_used:
    print("✅ Tools ARE executing - Real API calls being made!")
else:
    print("⚠️ Unable to determine - Manual verification needed")
