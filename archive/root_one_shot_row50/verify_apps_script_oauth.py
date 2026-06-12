"""
Google Apps Script OAuth Verification Script
Run this AFTER completing OAuth setup to verify credentials are working
"""

import sys
sys.path.insert(0, '.')

from tools.registry_v3 import RegistryV3
from AI_infrastructure.auth.user_auth import UserAuthManager

print("=" * 80)
print("GOOGLE APPS SCRIPT OAUTH VERIFICATION")
print("=" * 80)

# Step 1: Check if user has Google OAuth credentials
print("\n[STEP 1] Checking OAuth credentials in database...")
auth_manager = UserAuthManager()

# Get your user ID (change this to your actual user_id)
USER_ID = 12  # ← CHANGE THIS to your user ID

try:
    creds = auth_manager.get_user_google_oauth_credentials(USER_ID)
    
    if not creds:
        print(f"❌ FAILED: No Google OAuth credentials found for user_id={USER_ID}")
        print("\n📋 Next Steps:")
        print(f"   1. Visit: http://localhost:5001/api/auth/google/login")
        print(f"   2. Sign in with Google")
        print(f"   3. Run this script again")
        sys.exit(1)
    
    print(f"✅ OAuth credentials found for user_id={USER_ID}")
    print(f"   Email: {creds.get('email', 'N/A')}")
    print(f"   Token expiry: {creds.get('token_expiry', 'N/A')}")
    
    # Check if scopes include Apps Script
    scopes = creds.get('scopes', '')
    has_script_projects = 'script.projects' in scopes
    has_script_processes = 'script.processes' in scopes
    has_script_deployments = 'script.deployments' in scopes
    
    print(f"\n[STEP 2] Checking Apps Script scopes...")
    print(f"   script.projects: {'✅' if has_script_projects else '❌ MISSING'}")
    print(f"   script.processes: {'✅' if has_script_processes else '❌ MISSING'}")
    print(f"   script.deployments: {'✅' if has_script_deployments else '❌ MISSING'}")
    
    if not (has_script_projects and has_script_processes and has_script_deployments):
        print("\n❌ FAILED: Apps Script scopes not found!")
        print("\n📋 Next Steps:")
        print("   1. Go to: https://console.cloud.google.com/")
        print("   2. APIs & Services → OAuth consent screen → EDIT APP")
        print("   3. Add Apps Script scopes (see GOOGLE_APPS_SCRIPT_OAUTH_SETUP.md)")
        print("   4. Visit: http://localhost:5001/api/auth/google/login?prompt=consent")
        print("   5. Re-authenticate to get new scopes")
        print("   6. Run this script again")
        sys.exit(1)
    
    print(f"✅ All Apps Script scopes present!")
    
except Exception as e:
    print(f"❌ FAILED: Error retrieving credentials: {e}")
    sys.exit(1)

# Step 3: Test tool execution
print(f"\n[STEP 3] Testing google_apps_script_list_projects...")
print("-" * 80)

registry = RegistryV3()

try:
    result = registry.execute_tool(
        tool_name='google_apps_script_list_projects',
        _user_id=USER_ID,
        _injected_credentials=True
    )
    
    print(f"Tool execution result:")
    print(f"  Success: {result.get('success', False)}")
    
    if result.get('success'):
        projects = result.get('projects', [])
        print(f"  Projects found: {len(projects)}")
        
        if len(projects) > 0:
            print(f"\n  Your Apps Script Projects:")
            for i, project in enumerate(projects[:5], 1):  # Show first 5
                print(f"    {i}. {project.get('title', 'Untitled')} (ID: {project.get('scriptId', 'N/A')[:20]}...)")
            
            if len(projects) > 5:
                print(f"    ... and {len(projects) - 5} more")
        
        print(f"\n✅ SUCCESS! Google Apps Script tools are working!")
        print(f"\n🎉 You can now use all 14 Apps Script tools:")
        print(f"   - google_apps_script_debug_script(script_id='...')")
        print(f"   - google_apps_script_fix_common_issues(script_id='...')")
        print(f"   - google_apps_script_get_content(script_id='...')")
        print(f"   - ... and 11 more!")
        
    else:
        error = result.get('error', 'Unknown error')
        print(f"  Error: {error}")
        
        if 'access_token required' in error:
            print(f"\n❌ FAILED: Credentials not being injected properly")
            print(f"\n📋 Debug Steps:")
            print(f"   1. Check if user_id={USER_ID} is correct")
            print(f"   2. Verify oauth_tokens table has entry for this user")
            print(f"   3. Check credential_injector.py is working")
        elif 'permission' in error.lower() or '403' in error:
            print(f"\n❌ FAILED: Permission denied by Google")
            print(f"\n📋 Possible causes:")
            print(f"   - Apps Script API not enabled")
            print(f"   - OAuth scopes incorrect")
            print(f"   - User doesn't have access to scripts")
        else:
            print(f"\n❌ FAILED: {error}")
        
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FAILED: Exception during tool execution: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test credential injection directly
print(f"\n[STEP 4] Testing credential injection...")
print("-" * 80)

try:
    from AI_infrastructure.auth.credential_injector import CredentialInjector
    
    injector = CredentialInjector()
    test_params = {'test': 'value'}
    
    injected = injector.inject_credentials(
        tool_name='google_apps_script_list_projects',
        params=test_params,
        user_id=USER_ID
    )
    
    has_token = 'access_token' in injected
    has_refresh = 'refresh_token' in injected
    
    print(f"  Credential injection working: {'✅' if has_token else '❌'}")
    print(f"  Access token present: {'✅' if has_token else '❌'}")
    print(f"  Refresh token present: {'✅' if has_refresh else '❌'}")
    
    if has_token:
        token_preview = injected['access_token'][:20] + "..."
        print(f"  Token preview: {token_preview}")
    
    if not has_token:
        print(f"\n❌ FAILED: Credentials not being injected!")
        print(f"📋 Check credential_injector.py implementation")
        sys.exit(1)
    
    print(f"✅ Credential injection working!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print(f"✅ OAuth credentials: FOUND")
print(f"✅ Apps Script scopes: PRESENT")
print(f"✅ Tool execution: WORKING")
print(f"✅ Credential injection: WORKING")
print(f"\n🎉 ALL CHECKS PASSED - Google Apps Script tools ready to use!")
print("=" * 80)

print(f"\n📖 Next Steps:")
print(f"   1. Find your script ID (from the URL when editing in Apps Script)")
print(f"   2. Debug your Northecote File Extractor:")
print(f"      result = registry.execute_tool(")
print(f"          tool_name='google_apps_script_debug_script',")
print(f"          script_id='YOUR_SCRIPT_ID',")
print(f"          _user_id={USER_ID}")
print(f"      )")
print(f"   3. Review the diagnostic report")
print(f"   4. Apply auto-fixes if needed")
