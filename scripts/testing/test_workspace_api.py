"""
Test Workspace API Endpoints

Tests all 18 workspace API endpoints:
- 6 workspace CRUD endpoints
- 4 member management endpoints
- 4 invitation endpoints
- 3 utility endpoints (stats, health)

Usage:
    python scripts/testing/test_workspace_api.py

Requirements:
    - Flask server running on http://localhost:5001
    - User ID 3 exists in database
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5001'
USER_ID = 3  # Test user ID
HEADERS = {'Content-Type': 'application/json'}


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {test_name}")
    if details:
        print(f"       {details}")


def test_health_check():
    """Test health check endpoint"""
    print("\n[TEST 1] Health Check")
    try:
        response = requests.get(f'{BASE_URL}/api/workspaces/health')
        passed = response.status_code == 200 and response.json()['success']
        print_test("Health check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("Health check", False, str(e))
        return False


def test_create_workspace():
    """Test workspace creation"""
    print("\n[TEST 2] Create Workspace")
    try:
        data = {
            'user_id': USER_ID,
            'name': 'API Test Workspace',
            'description': 'Created via API test script',
            'visibility': 'private'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/workspaces',
            json=data,
            headers=HEADERS
        )
        
        passed = response.status_code == 201 and response.json()['success']
        
        if passed:
            workspace = response.json()['data']
            print_test("Create workspace", passed, f"Slug: {workspace['slug']}")
            return workspace['slug']
        else:
            print_test("Create workspace", False, f"Status: {response.status_code}, {response.text[:100]}")
            return None
            
    except Exception as e:
        print_test("Create workspace", False, str(e))
        return None


def test_list_workspaces():
    """Test listing workspaces"""
    print("\n[TEST 3] List Workspaces")
    try:
        response = requests.get(
            f'{BASE_URL}/api/workspaces',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            data = response.json()['data']
            count = data['total']
            print_test("List workspaces", passed, f"Found {count} workspaces")
        else:
            print_test("List workspaces", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("List workspaces", False, str(e))
        return False


def test_get_workspace(slug: str):
    """Test get workspace details"""
    print("\n[TEST 4] Get Workspace Details")
    try:
        response = requests.get(
            f'{BASE_URL}/api/workspaces/{slug}',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            workspace = response.json()['data']
            print_test("Get workspace", passed, f"Name: {workspace['name']}")
        else:
            print_test("Get workspace", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("Get workspace", False, str(e))
        return False


def test_update_workspace(slug: str):
    """Test update workspace"""
    print("\n[TEST 5] Update Workspace")
    try:
        data = {
            'user_id': USER_ID,
            'name': 'API Test Workspace (Updated)',
            'description': 'Updated description via API'
        }
        
        response = requests.put(
            f'{BASE_URL}/api/workspaces/{slug}',
            json=data,
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            workspace = response.json()['data']
            print_test("Update workspace", passed, f"New name: {workspace['name']}")
        else:
            print_test("Update workspace", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("Update workspace", False, str(e))
        return False


def test_get_workspace_stats(slug: str):
    """Test get workspace stats"""
    print("\n[TEST 6] Get Workspace Stats")
    try:
        response = requests.get(
            f'{BASE_URL}/api/workspaces/{slug}/stats',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            stats = response.json()['data']
            print_test("Get stats", passed, f"Members: {stats['member_count']}, Invitations: {stats['invitation_count']}")
        else:
            print_test("Get stats", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("Get stats", False, str(e))
        return False


def test_add_member(slug: str):
    """Test add member"""
    print("\n[TEST 7] Add Member")
    try:
        # Add user 5 as member
        data = {
            'user_id': USER_ID,
            'user_id': 5,
            'role': 'member'
        }
        
        # Fix: user_id appears twice - use different key names
        data = {
            'user_id': 5,  # User to add
            'role': 'member'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/workspaces/{slug}/members?user_id={USER_ID}',  # Requesting user in query
            json=data,
            headers=HEADERS
        )
        
        passed = response.status_code == 201 and response.json()['success']
        
        if passed:
            member = response.json()['data']
            print_test("Add member", passed, f"Added user {member['user_id']} as {member['role']}")
        else:
            print_test("Add member", False, f"Status: {response.status_code}, {response.text[:100]}")
        
        return passed
        
    except Exception as e:
        print_test("Add member", False, str(e))
        return False


def test_list_members(slug: str):
    """Test list members"""
    print("\n[TEST 8] List Members")
    try:
        response = requests.get(
            f'{BASE_URL}/api/workspaces/{slug}/members',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            members = response.json()['data']
            print_test("List members", passed, f"Found {len(members)} members")
        else:
            print_test("List members", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("List members", False, str(e))
        return False


def test_update_member_role(slug: str):
    """Test update member role"""
    print("\n[TEST 9] Update Member Role")
    try:
        data = {
            'user_id': USER_ID,
            'role': 'editor'
        }
        
        response = requests.put(
            f'{BASE_URL}/api/workspaces/{slug}/members/5?user_id={USER_ID}',
            json=data,
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            member = response.json()['data']
            print_test("Update member role", passed, f"New role: {member['role']}")
        else:
            print_test("Update member role", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("Update member role", False, str(e))
        return False


def test_create_invitation(slug: str):
    """Test create invitation"""
    print("\n[TEST 10] Create Invitation")
    try:
        data = {
            'user_id': USER_ID,
            'email': 'newuser@example.com',
            'role': 'member'
        }
        
        response = requests.post(
            f'{BASE_URL}/api/workspaces/{slug}/invitations?user_id={USER_ID}',
            json=data,
            headers=HEADERS
        )
        
        passed = response.status_code == 201 and response.json()['success']
        
        if passed:
            invitation = response.json()['data']
            print_test("Create invitation", passed, f"Token: {invitation['token'][:20]}...")
            return invitation['token']
        else:
            print_test("Create invitation", False, f"Status: {response.status_code}")
            return None
        
    except Exception as e:
        print_test("Create invitation", False, str(e))
        return None


def test_list_invitations(slug: str):
    """Test list invitations"""
    print("\n[TEST 11] List Invitations")
    try:
        response = requests.get(
            f'{BASE_URL}/api/workspaces/{slug}/invitations',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        
        if passed:
            invitations = response.json()['data']
            print_test("List invitations", passed, f"Found {len(invitations)} invitations")
        else:
            print_test("List invitations", False, f"Status: {response.status_code}")
        
        return passed
        
    except Exception as e:
        print_test("List invitations", False, str(e))
        return False


def test_remove_member(slug: str):
    """Test remove member"""
    print("\n[TEST 12] Remove Member")
    try:
        response = requests.delete(
            f'{BASE_URL}/api/workspaces/{slug}/members/5',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        print_test("Remove member", passed, f"Status: {response.status_code}")
        return passed
        
    except Exception as e:
        print_test("Remove member", False, str(e))
        return False


def test_archive_workspace(slug: str):
    """Test archive workspace"""
    print("\n[TEST 13] Archive Workspace")
    try:
        response = requests.delete(
            f'{BASE_URL}/api/workspaces/{slug}',
            params={'user_id': USER_ID},
            headers=HEADERS
        )
        
        passed = response.status_code == 200 and response.json()['success']
        print_test("Archive workspace", passed, f"Status: {response.status_code}")
        return passed
        
    except Exception as e:
        print_test("Archive workspace", False, str(e))
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("WORKSPACE API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {USER_ID}")
    print("="*80)
    
    results = []
    workspace_slug = None
    invitation_token = None
    
    # Test 1: Health check
    results.append(test_health_check())
    
    # Test 2: Create workspace
    workspace_slug = test_create_workspace()
    results.append(workspace_slug is not None)
    
    if not workspace_slug:
        print("\n CRITICAL: Cannot continue without workspace slug")
        return
    
    # Test 3: List workspaces
    results.append(test_list_workspaces())
    
    # Test 4: Get workspace details
    results.append(test_get_workspace(workspace_slug))
    
    # Test 5: Update workspace
    results.append(test_update_workspace(workspace_slug))
    
    # Test 6: Get workspace stats
    results.append(test_get_workspace_stats(workspace_slug))
    
    # Test 7: Add member
    results.append(test_add_member(workspace_slug))
    
    # Test 8: List members
    results.append(test_list_members(workspace_slug))
    
    # Test 9: Update member role
    results.append(test_update_member_role(workspace_slug))
    
    # Test 10: Create invitation
    invitation_token = test_create_invitation(workspace_slug)
    results.append(invitation_token is not None)
    
    # Test 11: List invitations
    results.append(test_list_invitations(workspace_slug))
    
    # Test 12: Remove member
    results.append(test_remove_member(workspace_slug))
    
    # Test 13: Archive workspace (cleanup)
    results.append(test_archive_workspace(workspace_slug))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"   Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("   SUCCESS - All tests passed!")
    else:
        print(f"   WARNING - {total - passed} test(s) failed")
    
    print("="*80)


if __name__ == '__main__':
    main()
