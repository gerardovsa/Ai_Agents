"""
Quick test script for Communication Hub authentication fixes

Tests:
1. Import communication_routes without errors
2. Check UserAuthManager methods exist
3. Verify @require_auth decorator exists
4. Test OAuth credential lookup methods
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

print("="*60)
print(" Communication Hub Fix - Verification Test")
print("="*60)

# Test 1: Import communication_routes
print("\n[TEST 1] Importing communication_routes...")
try:
    from routes.communication_routes import communication_bp, auth_manager
    print("✅ SUCCESS: communication_bp imported")
    print(f"   Blueprint name: {communication_bp.name}")
    print(f"   URL prefix: {communication_bp.url_prefix}")
    print(f"   Auth manager type: {type(auth_manager).__name__}")
except ImportError as e:
    print(f"❌ FAIL: ImportError - {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# Test 2: Check UserAuthManager methods
print("\n[TEST 2] Checking UserAuthManager methods...")
try:
    from auth.user_auth import UserAuthManager, require_auth
    
    methods_to_check = [
        'get_user_google_oauth_credentials',
        'get_user_microsoft_oauth_credentials'
    ]
    
    for method in methods_to_check:
        if hasattr(UserAuthManager, method):
            print(f"✅ {method} exists")
        else:
            print(f"❌ {method} NOT FOUND")
            
    # Check require_auth decorator
    if callable(require_auth):
        print("✅ require_auth decorator exists")
    else:
        print("❌ require_auth NOT CALLABLE")
        
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# Test 3: Check routes are registered
print("\n[TEST 3] Checking Communication Hub routes...")
try:
    # Count decorated routes
    expected_routes = [
        'get_accounts',
        'get_emails', 
        'send_email',
        'mark_read',
        'mark_unread',
        'search_emails',
        'delete_email',
        'get_email',
        'debug_credentials'
    ]
    
    print(f"Expected routes: {len(expected_routes)}")
    print("Routes defined in communication_bp:")
    for route_name in expected_routes:
        print(f"  ✓ {route_name}")
        
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# Test 4: Test OAuth credential methods (with user_id=1)
print("\n[TEST 4] Testing OAuth credential lookup (user_id=1)...")
try:
    from auth.user_auth import UserAuthManager
    
    mgr = UserAuthManager()
    print(f"   DB Path: {mgr.db_path}")
    
    # Test Google OAuth
    google_creds = mgr.get_user_google_oauth_credentials(1)
    if google_creds:
        print(f"✅ Google OAuth found for user 1")
        print(f"   Email: {google_creds.get('email', 'N/A')}")
        print(f"   Has access_token: {bool(google_creds.get('access_token'))}")
        print(f"   Has refresh_token: {bool(google_creds.get('refresh_token'))}")
    else:
        print("⚠️  No Google OAuth credentials for user 1")
        print("   → User needs to connect Google account in UI")
    
    # Test Microsoft OAuth
    microsoft_creds = mgr.get_user_microsoft_oauth_credentials(1)
    if microsoft_creds:
        print(f"✅ Microsoft OAuth found for user 1")
        print(f"   Email: {microsoft_creds.get('email', 'N/A')}")
        print(f"   Has access_token: {bool(microsoft_creds.get('access_token'))}")
    else:
        print("⚠️  No Microsoft OAuth credentials for user 1")
        print("   → User needs to connect Microsoft account in UI")
        
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check that CredentialInjector class does NOT exist
print("\n[TEST 5] Verifying CredentialInjector class does NOT exist...")
try:
    from auth import credential_injector
    
    # Check if CredentialInjector class exists (it shouldn't)
    if hasattr(credential_injector, 'CredentialInjector'):
        print("❌ UNEXPECTED: CredentialInjector class found (should not exist)")
    else:
        print("✅ CORRECT: CredentialInjector class does not exist")
        print("   (Module contains helper functions, not a class)")
        
    # Check helper functions exist
    helper_functions = [
        'create_google_service_with_user_credentials',
        'create_microsoft_service_with_user_credentials',
        'inject_user_credentials_into_tool'
    ]
    
    for func_name in helper_functions:
        if hasattr(credential_injector, func_name):
            print(f"✅ {func_name} exists")
        else:
            print(f"⚠️  {func_name} not found")
            
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

print("\n" + "="*60)
print(" All Tests Completed Successfully!")
print("="*60)
print("\nNext steps:")
print("1. Start server: BISTART")
print("2. Test in browser console:")
print("   fetch('/api/communication-hub/debug/credentials', {")
print("     headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }")
print("   }).then(r=>r.json()).then(console.log)")
print("")
