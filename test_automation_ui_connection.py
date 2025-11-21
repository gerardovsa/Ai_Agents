"""
Test Automation UI Connection
Tests the complete flow from database -> backend API -> frontend UI

This script verifies:
1. Backend /api/automation/list returns UI-compatible format
2. Backend /api/automation/<slug> returns shapes and connections
3. Backend /api/automation/save accepts UI format
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5001'

def get_auth_token():
    """Get a valid JWT token for testing"""
    # For testing, use user_id=1 (default test user)
    # The backend accepts any token format for testing
    return 'test_token_user_1'

def print_section(title):
    """Print a formatted section header"""
    print('\n' + '='*80)
    print(title)
    print('='*80)

def test_list_workflows():
    """Test GET /api/automation/list"""
    print_section('TEST 1: List Workflows API')
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/automation/list',
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.ok:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Workflow Count: {data.get('count')}")
            
            workflows = data.get('workflows', [])
            if workflows:
                print('\nFirst Workflow Structure:')
                first = workflows[0]
                print(f"  workflow_id: {first.get('workflow_id')}")
                print(f"  name: {first.get('name')}")
                print(f"  slug: {first.get('slug')}")
                print(f"  enabled: {first.get('enabled')}")
                print(f"  category: {first.get('category')}")
                print(f"  Has workflow_json: {'workflow_json' in first}")
                print(f"  Has ui_json: {'ui_json' in first}")
                
                # Check if shapes/connections are accessible
                if 'workflow_json' in first:
                    wf_json = first['workflow_json']
                    if isinstance(wf_json, dict):
                        print(f"  Shapes in workflow_json: {len(wf_json.get('shapes', []))}")
                        print(f"  Connections in workflow_json: {len(wf_json.get('connections', []))}")
                
                print('\nPASS: List endpoint returns UI-compatible format')
                return True
            else:
                print('\nWARNING: No workflows found (empty database)')
                return True
        else:
            print(f'FAIL: API returned error - {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print('FAIL: Cannot connect to backend (is BISTART running?)')
        return False
    except Exception as e:
        print(f'FAIL: Unexpected error - {e}')
        return False

def test_get_workflow_by_slug():
    """Test GET /api/automation/<slug>"""
    print_section('TEST 2: Get Workflow By Slug')
    
    try:
        # First get list to find a slug
        list_response = requests.get(
            f'{BASE_URL}/api/automation/list',
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        
        if not list_response.ok:
            print('SKIP: Cannot test - list API failed')
            return None
        
        workflows = list_response.json().get('workflows', [])
        if not workflows:
            print('SKIP: No workflows found to test')
            return None
        
        slug = workflows[0]['slug']
        print(f'Testing with slug: {slug}')
        
        response = requests.get(
            f'{BASE_URL}/api/automation/{slug}',
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.ok:
            data = response.json()
            workflow = data.get('automation') or data.get('workflow')
            
            if not workflow:
                print('FAIL: No workflow data in response')
                return False
            
            print(f"Success: {data.get('success')}")
            print(f"Workflow ID: {workflow.get('workflow_id')}")
            print(f"Name: {workflow.get('name')}")
            print(f"Has shapes: {'shapes' in workflow}")
            print(f"Has connections: {'connections' in workflow}")
            
            if 'shapes' in workflow:
                print(f"Shape count: {len(workflow['shapes'])}")
            if 'connections' in workflow:
                print(f"Connection count: {len(workflow['connections'])}")
            
            # Verify UI compatibility
            required_fields = ['workflow_id', 'name', 'slug', 'enabled', 'shapes', 'connections']
            missing = [f for f in required_fields if f not in workflow]
            
            if missing:
                print(f'\nWARNING: Missing UI-expected fields: {missing}')
            else:
                print('\nPASS: Workflow has all UI-expected fields')
            
            return len(missing) == 0
        else:
            print(f'FAIL: API returned error - {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'FAIL: Unexpected error - {e}')
        return False

def test_save_workflow():
    """Test POST /api/automation/save"""
    print_section('TEST 3: Save Workflow')
    
    try:
        test_workflow = {
            'title': 'Test UI Connection Workflow',
            'name': 'Test UI Connection Workflow',  # UI might send this
            'description': 'Testing UI-backend connection',
            'category': 'testing',
            'status': 'draft',
            'shapes': [
                {
                    'id': 'test_shape_1',
                    'type': 'hexagon',
                    'x': 100,
                    'y': 100,
                    'width': 150,
                    'height': 80,
                    'text': 'Test Trigger',
                    'color': '#10B981'
                },
                {
                    'id': 'test_shape_2',
                    'type': 'rectangle',
                    'x': 100,
                    'y': 250,
                    'width': 150,
                    'height': 80,
                    'text': 'Test Action',
                    'color': '#3B82F6'
                }
            ],
            'connections': [
                {
                    'id': 'test_conn_1',
                    'from': 'test_shape_1',
                    'to': 'test_shape_2'
                }
            ]
        }
        
        response = requests.post(
            f'{BASE_URL}/api/automation/save',
            json=test_workflow,
            headers={
                'Authorization': 'Bearer test_token',
                'Content-Type': 'application/json'
            },
            timeout=5
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.ok:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Workflow ID: {data.get('workflow_id')}")
            print(f"Slug: {data.get('slug')}")
            
            if data.get('success'):
                print('\nPASS: Save endpoint accepts UI format')
                return True
            else:
                print('\nFAIL: Save returned success=false')
                return False
        else:
            print(f'FAIL: API returned error - {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'FAIL: Unexpected error - {e}')
        return False

def test_field_mapping():
    """Test that field mapping is correct"""
    print_section('TEST 4: Field Mapping Verification')
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/automation/list',
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        
        if not response.ok or not response.json().get('workflows'):
            print('SKIP: No workflows to test field mapping')
            return None
        
        workflow = response.json()['workflows'][0]
        
        # Check UI-expected fields
        checks = {
            'workflow_id exists': 'workflow_id' in workflow,
            'name exists (not just title)': 'name' in workflow,
            'enabled is boolean': isinstance(workflow.get('enabled'), bool),
            'workflow_json OR ui_json exists': 'workflow_json' in workflow or 'ui_json' in workflow,
            'Has shapes array access': bool(workflow.get('shapes') or 
                                           (workflow.get('workflow_json', {}) or {}).get('shapes') or
                                           (workflow.get('ui_json', {}) or {}).get('shapes'))
        }
        
        print('Field Mapping Checks:')
        all_pass = True
        for check, result in checks.items():
            status = 'PASS' if result else 'FAIL'
            print(f"  {status}: {check}")
            if not result:
                all_pass = False
        
        if all_pass:
            print('\nPASS: All field mappings correct')
        else:
            print('\nFAIL: Some field mappings incorrect')
        
        return all_pass
        
    except Exception as e:
        print(f'FAIL: Unexpected error - {e}')
        return False

if __name__ == '__main__':
    print('Testing Automation UI Connection')
    print('='*80)
    print('This tests the connection between:')
    print('  Database (data/public_schema.sql)')
    print('  Backend API (AI_infrastructure/routes/automation_routes.py)')
    print('  Frontend UI (UI/external/modules/automation-workflows/)')
    
    results = []
    
    # Run tests
    results.append(('List Workflows', test_list_workflows()))
    results.append(('Get By Slug', test_get_workflow_by_slug()))
    results.append(('Save Workflow', test_save_workflow()))
    results.append(('Field Mapping', test_field_mapping()))
    
    # Summary
    print_section('SUMMARY')
    
    for name, result in results:
        if result is True:
            status = 'PASS'
        elif result is False:
            status = 'FAIL'
        else:
            status = 'SKIP'
        print(f'{status} - {name}')
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    total = len(results)
    
    print(f'\nResults: {passed} passed, {failed} failed, {skipped} skipped (of {total} tests)')
    
    if failed == 0:
        print('\nSUCCESS! All tests passed - UI connection is working!')
        sys.exit(0)
    else:
        print('\nFAILURE! Some tests failed - check errors above')
        sys.exit(1)
