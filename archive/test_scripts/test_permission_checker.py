"""
Test permission checker implementation

Tests all permission checking functions:
- Tool permissions
- Agent access
- Data access
- Work hours
- Usage limits
- Account expiry
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from auth.permission_checker import PermissionChecker, PermissionError


def test_permission_checker():
    """Test permission checker with various scenarios"""
    
    print("=" * 60)
    print("PERMISSION CHECKER TEST")
    print("=" * 60)
    
    checker = PermissionChecker()
    
    # Use user ID 3 (inhouse user that exists)
    test_user_id = 3
    
    # Test 1: Get user permissions
    print("\nTest 1: Get User Permissions")
    print("-" * 60)
    perms = checker.get_user_permissions(test_user_id)
    if perms:
        print(f"User {test_user_id} permissions:")
        print(f"  Role: {perms['role']}")
        print(f"  Is sub-user: {perms['is_sub_user']}")
        print(f"  Data scope: {perms['data_access_scope']}")
        print(f"  Allowed tools: {perms['allowed_tools']}")
        print(f"  Allowed agents: {perms['allowed_agents']}")
        print(f"  Usage limit: {perms['usage_limit_daily']}")
        print(f"  Work hours: {perms['access_start_time']} - {perms['access_end_time']}")
        print(f"  Expires: {perms['account_expires_at']}")
        print("Result: SUCCESS")
    else:
        print("Result: User not found")
    
    # Test 2: Check tool permission
    print("\nTest 2: Check Tool Permission")
    print("-" * 60)
    test_tool = 'gmail_send_email'
    try:
        result = checker.check_tool_permission(test_user_id, test_tool)
        print(f"Tool: {test_tool}")
        print(f"User {test_user_id} can access: {result}")
        print("Result: SUCCESS")
    except PermissionError as e:
        print(f"Tool: {test_tool}")
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (expected if restricted)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 3: Check agent access
    print("\nTest 3: Check Agent Access")
    print("-" * 60)
    test_agent = 'prime'
    try:
        result = checker.check_agent_access(test_user_id, test_agent)
        print(f"Agent: {test_agent}")
        print(f"User {test_user_id} can access: {result}")
        print("Result: SUCCESS")
    except PermissionError as e:
        print(f"Agent: {test_agent}")
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (expected if restricted)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 4: Check data access (own data)
    print("\nTest 4: Check Data Access (Own Data)")
    print("-" * 60)
    try:
        result = checker.check_data_access(test_user_id, test_user_id)
        print(f"User {test_user_id} accessing own data (resource_owner={test_user_id})")
        print(f"Access allowed: {result}")
        print("Result: SUCCESS")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (unexpected!)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 5: Check data access (other user's data)
    print("\nTest 5: Check Data Access (Other User's Data)")
    print("-" * 60)
    try:
        result = checker.check_data_access(test_user_id, 5)
        print(f"User {test_user_id} accessing user 5's data")
        print(f"Access allowed: {result}")
        print("Result: SUCCESS (user has 'all' scope or is admin)")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (expected if scope='own')")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 6: Check work hours
    print("\nTest 6: Check Work Hours")
    print("-" * 60)
    try:
        result = checker.is_within_work_hours(test_user_id)
        print(f"User {test_user_id} work hours check")
        print(f"Access allowed: {result}")
        print("Result: SUCCESS (within hours or no restriction)")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (outside work hours)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 7: Check usage limit
    print("\nTest 7: Check Usage Limit")
    print("-" * 60)
    try:
        result = checker.check_usage_limit(test_user_id)
        print(f"User {test_user_id} usage limit check")
        print(f"Access allowed: {result}")
        print("Result: SUCCESS (TODO: tracking not implemented yet)")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (limit exceeded)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 8: Check account expiry
    print("\nTest 8: Check Account Expiry")
    print("-" * 60)
    try:
        result = checker.check_account_expiry(test_user_id)
        print(f"User {test_user_id} account expiry check")
        print(f"Account active: {result}")
        print("Result: SUCCESS (not expired or no expiry set)")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED (account expired)")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 9: Check all restrictions at once
    print("\nTest 9: Check All Restrictions")
    print("-" * 60)
    try:
        result = checker.check_all_restrictions(
            user_id=test_user_id,
            tool_name='gmail_send_email',
            agent_id='prime',
            resource_owner_id=test_user_id
        )
        print(f"User {test_user_id} full permission check")
        print(f"All restrictions passed: {result}")
        print("Result: SUCCESS")
    except PermissionError as e:
        print(f"Access denied: {e}")
        print("Result: PERMISSION DENIED")
    except Exception as e:
        print(f"Error: {e}")
        print("Result: ERROR")
    
    # Test 10: Role hierarchy
    print("\nTest 10: Role Hierarchy Check")
    print("-" * 60)
    print("Role levels:")
    for role in ['guest', 'readonly', 'team', 'user', 'team_lead', 'admin', 'owner']:
        level = checker.get_role_level(role)
        print(f"  {role}: {level}")
    print("Result: SUCCESS")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    test_permission_checker()
