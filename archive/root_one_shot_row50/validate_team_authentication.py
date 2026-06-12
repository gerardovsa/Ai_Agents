#!/usr/bin/env python3
"""
Team Authentication System - End-to-End Validation Tests
Tests all components of the team authentication system to verify proper operation.
Run this after any deployment or authentication changes.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Change to production URL
TESTS_RUN = 0
TESTS_PASSED = 0
TESTS_FAILED = 0

# Test data
PRIMARY_USER = {
    "username": "test_primary",
    "password": "TestPassword123!",
    "email": "primary@test.local"
}

TEAM_MEMBER = {
    "team_id": "test_sales_north",
    "password": "TeamPassword456!",
    "email": "test.sales@test.local",
    "allowed_tools": ["quote_calculator", "message_send"],
    "allowed_agents": ["prime_ai"]
}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_test(name, passed, details=""):
    """Print test result"""
    global TESTS_RUN, TESTS_PASSED, TESTS_FAILED
    TESTS_RUN += 1
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} | {name}")
    if details:
        print(f"      Details: {details}")
    
    if passed:
        TESTS_PASSED += 1
    else:
        TESTS_FAILED += 1

def test_server_health():
    """Test 1: Server is accessible"""
    print_section("Test 1: Server Health")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_test(
            "Server accessible",
            response.status_code < 500,
            f"Status: {response.status_code}"
        )
        return True
    except requests.ConnectionError:
        print_test("Server accessible", False, f"Cannot connect to {BASE_URL}")
        return False
    except Exception as e:
        print_test("Server accessible", False, str(e))
        return False

def test_primary_user_registration():
    """Test 2: Primary user can register"""
    print_section("Test 2: Primary User Registration")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=PRIMARY_USER,
            timeout=10
        )
        
        success = response.status_code == 201
        print_test(
            "Primary user registration",
            success,
            f"Status: {response.status_code}, Body: {response.text[:100]}"
        )
        
        if success:
            data = response.json()
            global PRIMARY_USER_ID
            PRIMARY_USER_ID = data.get('user_id')
            return data.get('token')
        return None
    except Exception as e:
        print_test("Primary user registration", False, str(e))
        return None

def test_primary_user_login(token):
    """Test 3: Primary user can login"""
    print_section("Test 3: Primary User Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": PRIMARY_USER["username"],
                "password": PRIMARY_USER["password"]
            },
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "Primary user login",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            token = data.get('token')
            print_test(
                "JWT token generated",
                token is not None,
                f"Token type: {type(token)}"
            )
            return token
        return None
    except Exception as e:
        print_test("Primary user login", False, str(e))
        return None

def test_create_team_member(primary_token):
    """Test 4: Create team member with independent password"""
    print_section("Test 4: Create Team Member")
    
    if not primary_token:
        print_test("Create team member", False, "No primary token available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {primary_token}"}
        response = requests.post(
            f"{BASE_URL}/api/auth/team-ids/add",
            json=TEAM_MEMBER,
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 201
        print_test(
            "Team member creation",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            team_member_id = data.get('id')
            is_sub_user = data.get('is_sub_user')
            
            print_test(
                "Team member marked as sub-user",
                is_sub_user == True,
                f"is_sub_user: {is_sub_user}"
            )
            
            return team_member_id
        else:
            print(f"Response body: {response.text}")
        return None
    except Exception as e:
        print_test("Team member creation", False, str(e))
        return None

def test_list_team_members(primary_token):
    """Test 5: List team members"""
    print_section("Test 5: List Team Members")
    
    if not primary_token:
        print_test("List team members", False, "No primary token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {primary_token}"}
        response = requests.get(
            f"{BASE_URL}/api/auth/team-ids",
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "List team members endpoint",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            team_members = data.get('team_ids', [])
            has_test_member = any(
                tm.get('username') == TEAM_MEMBER['team_id'] 
                for tm in team_members
            )
            
            print_test(
                "Test team member appears in list",
                has_test_member,
                f"Total members: {len(team_members)}"
            )
            return has_test_member
        return False
    except Exception as e:
        print_test("List team members", False, str(e))
        return False

def test_team_member_login():
    """Test 6: Team member can login with their own credentials"""
    print_section("Test 6: Team Member Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": TEAM_MEMBER["team_id"],  # Team ID
                "password": TEAM_MEMBER["password"]  # Team's password
            },
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "Team member login with Team ID",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            token = data.get('token')
            is_sub_user = data.get('is_sub_user')
            parent_user_id = data.get('parent_user_id')
            
            print_test(
                "JWT marked as sub-user",
                is_sub_user == True,
                f"is_sub_user: {is_sub_user}"
            )
            
            print_test(
                "Parent user ID set correctly",
                parent_user_id is not None,
                f"parent_user_id: {parent_user_id}"
            )
            
            return token
        else:
            print(f"Response: {response.text}")
        return None
    except Exception as e:
        print_test("Team member login", False, str(e))
        return None

def test_team_member_token_verification(team_token):
    """Test 7: Verify team member JWT token"""
    print_section("Test 7: JWT Token Verification")
    
    if not team_token:
        print_test("Verify team member token", False, "No team token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {team_token}"}
        response = requests.post(
            f"{BASE_URL}/api/auth/verify",
            headers=headers,
            json={},
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "Token verification endpoint",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            is_valid = data.get('valid')
            is_sub_user = data.get('is_sub_user')
            
            print_test(
                "Token is valid",
                is_valid == True,
                f"valid: {is_valid}"
            )
            
            print_test(
                "Token identifies as sub-user",
                is_sub_user == True,
                f"is_sub_user: {is_sub_user}"
            )
            
            return is_valid and is_sub_user
        return False
    except Exception as e:
        print_test("Token verification", False, str(e))
        return False

def test_team_member_permissions(team_token):
    """Test 8: Check team member permissions"""
    print_section("Test 8: Team Member Permissions")
    
    if not team_token:
        print_test("Check permissions", False, "No team token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {team_token}"}
        response = requests.get(
            f"{BASE_URL}/api/auth/permissions",
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "Get permissions endpoint",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            data = response.json()
            allowed_tools = data.get('allowed_tools', [])
            allowed_agents = data.get('allowed_agents', [])
            
            print_test(
                "Allowed tools include quote_calculator",
                "quote_calculator" in allowed_tools,
                f"Tools: {allowed_tools}"
            )
            
            print_test(
                "Allowed agents include prime_ai",
                "prime_ai" in allowed_agents,
                f"Agents: {allowed_agents}"
            )
            
            return True
        return False
    except Exception as e:
        print_test("Check permissions", False, str(e))
        return False

def test_unauthorized_access(team_token):
    """Test 9: Verify team member can't access admin endpoints"""
    print_section("Test 9: Authorization Boundaries")
    
    if not team_token:
        print_test("Check authorization", False, "No team token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {team_token}"}
        
        # Try to access team-ids management (should be restricted or require primary)
        response = requests.get(
            f"{BASE_URL}/api/auth/team-ids",
            headers=headers,
            timeout=10
        )
        
        # Should either be 403 (forbidden) or show only their own data
        is_restricted = response.status_code in [403, 401] or \
                       (response.status_code == 200 and \
                        len(response.json().get('team_ids', [])) == 0)
        
        print_test(
            "Team member can't manage other team members",
            is_restricted,
            f"Status: {response.status_code}"
        )
        
        return is_restricted
    except Exception as e:
        print_test("Check authorization", False, str(e))
        return False

def test_password_change(primary_token, team_member_id):
    """Test 10: Update team member password"""
    print_section("Test 10: Update Team Member Settings")
    
    if not primary_token:
        print_test("Update team member", False, "No primary token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {primary_token}"}
        new_password = "NewTeamPassword789!"
        
        response = requests.put(
            f"{BASE_URL}/api/auth/team-ids/{team_member_id}",
            json={"password": new_password},
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 200
        print_test(
            "Update team member password",
            success,
            f"Status: {response.status_code}"
        )
        
        if success:
            # Try login with new password
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "username": TEAM_MEMBER["team_id"],
                    "password": new_password
                },
                timeout=10
            )
            
            login_success = login_response.status_code == 200
            print_test(
                "Login with new password works",
                login_success,
                f"Status: {login_response.status_code}"
            )
            
            return login_success
        return False
    except Exception as e:
        print_test("Update team member", False, str(e))
        return False

def print_summary():
    """Print test summary"""
    print_section("Test Summary")
    
    print(f"\n{'Test Results':^70}")
    print(f"{'─'*70}")
    print(f"Total Tests Run:    {TESTS_RUN}")
    print(f"Tests Passed:       {TESTS_PASSED} {'✅' if TESTS_PASSED > 0 else ''}")
    print(f"Tests Failed:       {TESTS_FAILED} {'❌' if TESTS_FAILED > 0 else ''}")
    print(f"Success Rate:       {(TESTS_PASSED/TESTS_RUN*100):.1f}%")
    print(f"{'─'*70}")
    
    if TESTS_FAILED == 0:
        print(f"\n🎉 All tests passed! Team authentication system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {TESTS_FAILED} test(s) failed. Review details above.")
        return 1

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  Team Authentication System - Validation Suite")
    print("  Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # Run tests in sequence
    if not test_server_health():
        print("\n❌ Server not accessible. Cannot continue testing.")
        return 1
    
    primary_token = test_primary_user_login(None) or test_primary_user_registration()
    
    if not primary_token:
        print("\n❌ Primary user authentication failed. Cannot continue.")
        return 1
    
    team_member_id = test_create_team_member(primary_token)
    test_list_team_members(primary_token)
    team_token = test_team_member_login()
    test_team_member_token_verification(team_token)
    test_team_member_permissions(team_token)
    test_unauthorized_access(team_token)
    
    if team_member_id:
        test_password_change(primary_token, team_member_id)
    
    return print_summary()

if __name__ == "__main__":
    sys.exit(main())
