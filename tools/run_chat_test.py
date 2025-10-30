import urllib.request
import json
import sys

BASE = 'http://localhost:5001'

def post(path, data, headers=None):
    url = BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers or {}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = resp.read()
            try:
                parsed = json.loads(out.decode('utf-8'))
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except Exception:
                print(out.decode('utf-8', errors='replace'))
            return resp.getcode(), out
    except Exception as e:
        print('ERROR during request to', path)
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == '__main__':
    login_payload = {"username": "admin", "password": "vetsuccess"}
    code, body = post('/api/auth/login', login_payload, headers={'Content-Type':'application/json'})
    if not body:
        sys.exit(1)
    try:
        token = json.loads(body.decode('utf-8'))['token']
    except Exception as e:
        print('Failed to parse token from login response')
        sys.exit(1)
    print('\nGot token, length', len(token))

    chat_payload = {
        'message': 'Please list your available tools and run a quick check (if a tool is needed, use it).',
        'provider': 'anthropic',
        'model': 'claude-3-7-sonnet-20250219'
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    post('/api/agent/chat', chat_payload, headers=headers)
