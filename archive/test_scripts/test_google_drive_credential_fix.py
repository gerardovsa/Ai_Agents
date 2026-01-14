"""
Test Google Drive Credential Injection Fix
==========================================

Tests that all 8 fixed functions now properly use user OAuth credentials
instead of service account credentials.

Run this after restarting Flask server.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_credential_injection_signatures():
    """Test that all functions have correct signatures"""
    print("Testing Google Drive credential injection signatures...")
    print("=" * 70)
    
    from google_workspace import google_drive
    
    functions_to_check = [
        'google_drive_update_file',
        'google_drive_move_file',
        'google_drive_copy_file',
        'google_drive_list_permissions',
        'google_drive_remove_permission',
        'google_drive_export_file',
        'google_drive_get_storage_quota',
        'google_drive_restore_file'
    ]
    
    all_passed = True
    
    for func_name in functions_to_check:
        func = getattr(google_drive, func_name)
        
        # Get function signature
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        # Check for credential injection parameters
        has_user_id = '_user_id' in params
        has_injected_creds = '_injected_credentials' in params
        has_kwargs = 'kwargs' in params
        
        status = "✅" if (has_user_id and has_injected_creds and has_kwargs) else "❌"
        
        print(f"\n{status} {func_name}")
        print(f"   _user_id: {has_user_id}")
        print(f"   _injected_credentials: {has_injected_creds}")
        print(f"   **kwargs: {has_kwargs}")
        
        if not (has_user_id and has_injected_creds and has_kwargs):
            all_passed = False
            print(f"   ⚠️  MISSING CREDENTIAL INJECTION!")
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ ALL FUNCTIONS HAVE CORRECT SIGNATURES!")
        print("\nCredential injection parameters present:")
        print("  - _user_id (for user identification)")
        print("  - _injected_credentials (for credential flag)")
        print("  - **kwargs (for additional parameters)")
    else:
        print("❌ SOME FUNCTIONS MISSING CREDENTIAL INJECTION!")
        print("   Functions need _user_id, _injected_credentials, and **kwargs")
    
    return all_passed


def test_function_implementation():
    """Test that functions use create_google_service_with_user_credentials"""
    print("\n\nTesting Google Drive function implementations...")
    print("=" * 70)
    
    from google_workspace import google_drive
    import inspect
    
    functions_to_check = [
        'google_drive_update_file',
        'google_drive_move_file',
        'google_drive_copy_file',
        'google_drive_list_permissions',
        'google_drive_remove_permission',
        'google_drive_export_file',
        'google_drive_get_storage_quota',
        'google_drive_restore_file'
    ]
    
    all_passed = True
    
    for func_name in functions_to_check:
        func = getattr(google_drive, func_name)
        
        # Get function source code
        source = inspect.getsource(func)
        
        # Check for credential injection logic
        has_if_user_id = 'if _user_id and _injected_credentials:' in source
        has_create_service = 'create_google_service_with_user_credentials' in source
        has_fallback = 'else:' in source and '_get_drive_service()' in source
        
        status = "✅" if (has_if_user_id and has_create_service and has_fallback) else "❌"
        
        print(f"\n{status} {func_name}")
        print(f"   Checks _user_id: {has_if_user_id}")
        print(f"   Uses create_google_service_with_user_credentials: {has_create_service}")
        print(f"   Has fallback to _get_drive_service: {has_fallback}")
        
        if not (has_if_user_id and has_create_service and has_fallback):
            all_passed = False
            print(f"   ⚠️  INCORRECT IMPLEMENTATION!")
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ ALL FUNCTIONS HAVE CORRECT IMPLEMENTATION!")
        print("\nExpected pattern found:")
        print("  1. Check if _user_id and _injected_credentials")
        print("  2. Use create_google_service_with_user_credentials")
        print("  3. Fallback to _get_drive_service if no credentials")
    else:
        print("❌ SOME FUNCTIONS HAVE INCORRECT IMPLEMENTATION!")
    
    return all_passed


def main():
    """Run all tests"""
    print("Google Drive Credential Injection Fix - Verification")
    print("=" * 70)
    print("Testing 8 functions that were fixed:")
    print("  1. google_drive_update_file")
    print("  2. google_drive_move_file")
    print("  3. google_drive_copy_file")
    print("  4. google_drive_list_permissions")
    print("  5. google_drive_remove_permission")
    print("  6. google_drive_export_file")
    print("  7. google_drive_get_storage_quota")
    print("  8. google_drive_restore_file")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Check function signatures
        sig_passed = test_credential_injection_signatures()
        
        # Test 2: Check function implementations
        impl_passed = test_function_implementation()
        
        # Final summary
        print("\n\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        
        if sig_passed and impl_passed:
            print("🎉 SUCCESS! All functions fixed correctly!")
            print("\nNext steps:")
            print("  1. Restart Flask server: BISTART")
            print("  2. Test google_drive_move_file operation")
            print("  3. Verify no more 404 errors")
            return 0
        else:
            print("⚠️  ISSUES FOUND - Review output above")
            return 1
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
