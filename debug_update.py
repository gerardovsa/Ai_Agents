import requests
import json

# Create test session
session_data = {
    'title': 'Debug Test',
    'next_steps': [{'description': 'Test step', 'completed': False}]
}

r = requests.post('http://localhost:5001/api/synergy/create', json=session_data)
result = r.json()
sid = result['session_id']
print(f'Created: {sid}')

# Update with nested updates object
update = {
    'updates': {
        'next_steps': [{'description': 'Test step', 'completed': True}]
    }
}

r2 = requests.patch(f'http://localhost:5001/api/synergy/{sid}', json=update)
print(f'Update response: {r2.json()}')

# Get session to verify
r3 = requests.get(f'http://localhost:5001/api/synergy/{sid}')
session = r3.json()['session']
print(f'Next steps after update: {session["next_steps"]}')

# Cleanup
requests.delete(f'http://localhost:5001/api/synergy/{sid}')
