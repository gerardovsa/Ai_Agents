import urllib.request
import json

BASE = 'http://localhost:5001'

# Login
login_req = urllib.request.Request(
    BASE + '/api/auth/login',
    data=json.dumps({"username": "admin", "password": "vetsuccess"}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(login_req, timeout=30) as resp:
    token = json.loads(resp.read().decode('utf-8'))['token']

print(f"Logged in, token length: {len(token)}\n")

# FORCE TOOL EXECUTION with explicit request
chat_req = urllib.request.Request(
    BASE + '/api/agent/chat',
    data=json.dumps({
        'message': 'Use the list_platform_tools tool RIGHT NOW to show me what tools are available. Execute the tool, do not just describe it.',
        'debug': True,
        'provider': 'anthropic',
        'model': 'claude-3-7-sonnet-20250219'
    }).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(chat_req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        
        print("=" * 60)
        print("TOOL EXECUTION TEST RESULTS")
        print("=" * 60)
        print(f"Response mode: {result.get('mode')}")
        print(f"Tool calls made: {len(result.get('tool_calls', []))}")
        print(f"Tools used: {result.get('tools_used', [])}")
        
        if result.get('tool_calls'):
            print("\nTool calls:")
            for call in result['tool_calls']:
                print(f"  - {call.get('name')}: {call.get('status')}")
        
        if result.get('content_blocks'):
            print(f"\nContent blocks: {len(result['content_blocks'])}")
            for i, block in enumerate(result['content_blocks']):
                print(f"  [{i+1}] {block.get('type')}")
        
        print("\n" + "=" * 60)
        print("AI Response (first 500 chars):")
        print("=" * 60)
        print(result.get('response', '')[:500])
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
