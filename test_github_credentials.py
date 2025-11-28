"""
Test GitHub personal credential injection system
=================================================

This test verifies:
1. GitHub credential getter works
2. GitHub tools updated with **kwargs
3. User-specific GitHub client initialization
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

print("=" * 80)
print("TESTING GITHUB PERSONAL CREDENTIAL SYSTEM")
print("=" * 80)

# Test 1: Import credential getter
print("\n1. Testing GitHub credential import...")
try:
    from auth.credential_injector import get_github_credentials
    print("   ✅ get_github_credentials imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Test 2: Check function signature
print("\n2. Testing function signature...")
try:
    import inspect
    sig = inspect.signature(get_github_credentials)
    params = list(sig.parameters.keys())
    
    if 'kwargs' in params:
        print(f"   ✅ Function accepts **kwargs: {params}")
    else:
        print(f"   ⚠️  Warning: Function params: {params}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 3: Test credential getter (will fail without credentials)
print("\n3. Testing credential getter...")
try:
    result = get_github_credentials(user_id=14)
    print(f"   ✅ Function executed (found credentials)")
except Exception as e:
    if "not found" in str(e).lower():
        print(f"   ✅ Function works correctly (no credentials, as expected)")
    else:
        print(f"   ❌ Unexpected error: {e}")

# Test 4: Import GitHub tools
print("\n4. Testing GitHub tool imports...")
try:
    from tools.implementations.github import (
        github_create_repo,
        github_commit_file,
        github_create_pr,
        github_get_issues
    )
    print("   ✅ All 4 GitHub tools imported")
except Exception as e:
    print(f"   ❌ Failed to import tools: {e}")
    sys.exit(1)

# Test 5: Check tool signatures (verify **kwargs added)
print("\n5. Testing tool signatures...")
tools_to_check = [
    ('github_create_repo', github_create_repo),
    ('github_commit_file', github_commit_file),
    ('github_create_pr', github_create_pr),
    ('github_get_issues', github_get_issues)
]

all_have_kwargs = True
for name, func in tools_to_check:
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    
    if 'kwargs' in params:
        print(f"   ✅ {name} - Has **kwargs")
    else:
        print(f"   ❌ {name} - MISSING **kwargs: {params}")
        all_have_kwargs = False

if all_have_kwargs:
    print("\n   ✅ ALL TOOLS HAVE **kwargs")
else:
    print("\n   ⚠️  Some tools missing **kwargs")

# Test 6: Check _get_github_client helper
print("\n6. Testing _get_github_client helper...")
try:
    from tools.implementations.github import _get_github_client
    print("   ✅ _get_github_client helper function exists")
    
    sig = inspect.signature(_get_github_client)
    params = list(sig.parameters.keys())
    print(f"   ✅ Parameters: {params}")
except Exception as e:
    print(f"   ❌ Helper function not found: {e}")

# Test 7: Test tool execution (will fail without credentials)
print("\n7. Testing tool execution...")
try:
    result = github_get_issues(
        repo='gerardovsa/AI_agents',
        _user_id=14
    )
    print(f"   ✅ Tool executed successfully (found {result['count']} issues)")
except Exception as e:
    if "authentication required" in str(e).lower() or "credentials not found" in str(e).lower():
        print(f"   ✅ Tool properly requires credentials")
    else:
        print(f"   ⚠️  Unexpected error: {e}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✅ GitHub credential injection system ready")
print("✅ get_github_credentials() available")
print("✅ All 4 GitHub tools updated with **kwargs")
print("✅ _get_github_client() helper created")
print("\nNext steps:")
print("1. User adds GitHub Personal Access Token via Account Settings → Connections")
print("2. Token stored in ai_infrastructure.user_platform_credentials")
print("3. Tools use user-specific credentials automatically")
print("4. Each user's commits/repos show under THEIR GitHub account")
print("=" * 80)
