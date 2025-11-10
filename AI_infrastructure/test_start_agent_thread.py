import requests
import json

url = 'http://localhost:5001/api/agent/agent/1/start'

payload = {
    'message': 'test start',
    'session_id': 'test_session_123',
    'thread_id': '1762594963590',
    'conversation_history': [{'role':'user','content':'hello'}]
}

r = requests.post(url, json=payload)
print(r.status_code)
try:
    print(r.json())
except Exception as e:
    print(r.text)
