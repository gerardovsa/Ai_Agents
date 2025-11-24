"""
Test automation list API endpoint directly
This will trigger the debug logs we added to automation_routes.py
"""

import requests
import json

# Test endpoint
url = 'http://localhost:5001/api/automation/list'
headers = {
    'Authorization': 'Bearer test_token',  # Will be validated by get_user_from_token
    'Content-Type': 'application/json'
}

print('\n=== TESTING /api/automation/list ===')
print(f'URL: {url}')
print(f'Headers: {headers}')

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f'\n=== RESPONSE ===')
    print(f'Status Code: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'\n=== RESPONSE DATA ===')
        print(f'Success: {data.get("success")}')
        print(f'Workflow Count: {data.get("count")}')
        print(f'Workflows Array Length: {len(data.get("workflows", []))}')
        
        workflows = data.get('workflows', [])
        if workflows:
            print(f'\n=== FIRST 3 WORKFLOWS ===')
            for i, wf in enumerate(workflows[:3], 1):
                print(f'{i}. ID: {wf.get("workflow_id")}')
                print(f'   Slug: {wf.get("slug")}')
                print(f'   Name/Title: {wf.get("name") or wf.get("title")}')
                print(f'   Status: {wf.get("status")}')
                print(f'   Shapes: {len(wf.get("shapes", []))} items')
                print(f'   Connections: {len(wf.get("connections", []))} items')
        else:
            print('  (No workflows in response)')
            
        print(f'\n=== FULL RESPONSE JSON ===')
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f'\nError: {response.text}')
        
except requests.exceptions.ConnectionError:
    print('\nERROR: Cannot connect to Flask server at localhost:5001')
    print('Make sure Flask is running with: BISTART')
except Exception as e:
    print(f'\nERROR: {type(e).__name__}: {str(e)}')

print('\n=== CHECK FLASK TERMINAL FOR DEBUG LOGS ===')
print('Look for lines starting with:')
print('  [DEBUG /api/automation/list]')
print('  [ERROR /api/automation/list]')
print('\nThese logs will show:')
print('  - How many rows SQL returned')
print('  - Which workflows successfully transformed')
print('  - Which workflows failed transformation and why')
print('  - Final count in JSON response')
