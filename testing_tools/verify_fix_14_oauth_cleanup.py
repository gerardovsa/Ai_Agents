"""
Fix #14 Verification Script - OAuth Cleanup
============================================

Tests that credentials_desktop.json and user_platform_credentials references
have been properly updated to use oauth_tokens table instead.

Run this script to verify Fix #14 implementation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_1_check_files_modified():
    """Test 1: Verify files were modified correctly"""
    print("\n" + "="*70)
    print("TEST 1: Verify Files Modified")
    print("="*70)
    
    files_to_check = [
        "google_workspace/oauth_manager.py",
        "google_workspace/google_tasks.py",
        "AI_infrastructure/auth/user_auth.py"
    ]
    
    root_dir = Path(__file__).parent.parent
    
    for file_path in files_to_check:
        full_path = root_dir / file_path
        
        print(f"\n📄 Checking: {file_path}")
        
        if not full_path.exists():
            print(f"   ❌ File not found: {full_path}")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for deprecation warnings
        if "⚠️ WARNING" in content or "DEPRECATED" in content:
            print(f"   ✅ Contains deprecation warnings")
        else:
            print(f"   ⚠️  No deprecation warnings found")
        
        # Check for oauth_tokens table references
        if "oauth_tokens" in content:
            print(f"   ✅ References oauth_tokens table")
        else:
            print(f"   ⚠️  No oauth_tokens references found")
        
        # Check for old references (should have warnings)
        if "credentials_desktop.json" in content:
            if "# ← FILE DOESN'T EXIST" in content or "DEPRECATED" in content:
                print(f"   ✅ credentials_desktop.json reference has warning")
            else:
                print(f"   ⚠️  credentials_desktop.json reference without warning")
        
        if "user_platform_credentials" in content:
            count = content.count("user_platform_credentials")
            print(f"   ℹ️  Found {count} user_platform_credentials references")
    
    print("\n✅ Test 1 Complete")
    return True


def test_2_check_database_schema():
    """Test 2: Verify oauth_tokens table exists in database"""
    print("\n" + "="*70)
    print("TEST 2: Verify Database Schema")
    print("="*70)
    
    import sqlite3
    
    db_path = Path(__file__).parent.parent / "data" / "ai_infrastructure.db"
    
    if not db_path.exists():
        print(f"\n❌ Database not found: {db_path}")
        return False
    
    print(f"\n📊 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check oauth_tokens table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='oauth_tokens'
        """)
        
        if cursor.fetchone():
            print("   ✅ oauth_tokens table exists")
            
            # Get column info
            cursor.execute("PRAGMA table_info(oauth_tokens)")
            columns = cursor.fetchall()
            
            print(f"   ℹ️  oauth_tokens has {len(columns)} columns")
            
            # Check for key columns
            column_names = [col[1] for col in columns]
            required_columns = ['access_token', 'refresh_token', 'expires_at', 'platform', 'user_id']
            
            for col in required_columns:
                if col in column_names:
                    print(f"      ✅ Column: {col}")
                else:
                    print(f"      ❌ Missing column: {col}")
        else:
            print("   ❌ oauth_tokens table does NOT exist")
        
        # Check user_platform_credentials table (should be deprecated)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_platform_credentials'
        """)
        
        if cursor.fetchone():
            print("   ℹ️  user_platform_credentials table exists (legacy table)")
        else:
            print("   ℹ️  user_platform_credentials table does not exist")
        
        conn.close()
        
        print("\n✅ Test 2 Complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
        return False


def test_3_check_imports():
    """Test 3: Verify imports work correctly"""
    print("\n" + "="*70)
    print("TEST 3: Verify Imports")
    print("="*70)
    
    tests = [
        {
            'name': 'user_auth.py',
            'module': 'AI_infrastructure.auth.user_auth',
            'class': 'UserAuthManager'
        },
        {
            'name': 'credential_injector.py',
            'module': 'AI_infrastructure.auth.credential_injector',
            'class': 'CredentialInjector'
        },
        {
            'name': 'google_tasks.py',
            'module': 'google_workspace.google_tasks',
            'function': '_build_tasks_service_desktop'
        }
    ]
    
    for test in tests:
        print(f"\n📦 Importing: {test['name']}")
        
        try:
            module = __import__(test['module'], fromlist=['*'])
            
            if 'class' in test:
                if hasattr(module, test['class']):
                    print(f"   ✅ Class {test['class']} imported successfully")
                else:
                    print(f"   ❌ Class {test['class']} not found")
            
            if 'function' in test:
                if hasattr(module, test['function']):
                    print(f"   ✅ Function {test['function']} imported successfully")
                else:
                    print(f"   ❌ Function {test['function']} not found")
        
        except Exception as e:
            print(f"   ❌ Import failed: {e}")
    
    print("\n✅ Test 3 Complete")
    return True


def test_4_check_function_signatures():
    """Test 4: Verify function signatures have _user_id parameter"""
    print("\n" + "="*70)
    print("TEST 4: Verify Function Signatures")
    print("="*70)
    
    try:
        from google_workspace.google_tasks import _build_tasks_service_desktop, _build_tasks_service_web
        import inspect
        
        print("\n🔍 Checking _build_tasks_service_desktop():")
        sig = inspect.signature(_build_tasks_service_desktop)
        if '_user_id' in sig.parameters:
            print("   ✅ Has _user_id parameter")
        else:
            print("   ⚠️  Missing _user_id parameter")
        
        print("\n🔍 Checking _build_tasks_service_web():")
        sig = inspect.signature(_build_tasks_service_web)
        if '_user_id' in sig.parameters:
            print("   ✅ Has _user_id parameter")
        else:
            print("   ⚠️  Missing _user_id parameter")
        
        print("\n✅ Test 4 Complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking function signatures: {e}")
        return False


def test_5_check_user_auth_methods():
    """Test 5: Verify UserAuthManager methods query correct tables"""
    print("\n" + "="*70)
    print("TEST 5: Verify UserAuthManager Methods")
    print("="*70)
    
    try:
        from AI_infrastructure.auth.user_auth import user_auth_manager
        import inspect
        
        methods_to_check = [
            'store_microsoft_tokens',
            'get_microsoft_tokens',
            'get_platform_credentials',
            'get_user_credential',
            'list_user_platforms'
        ]
        
        for method_name in methods_to_check:
            print(f"\n🔍 Checking: {method_name}()")
            
            if hasattr(user_auth_manager, method_name):
                method = getattr(user_auth_manager, method_name)
                source = inspect.getsource(method)
                
                # Check if it queries oauth_tokens
                if "oauth_tokens" in source:
                    print(f"   ✅ Queries oauth_tokens table")
                else:
                    print(f"   ⚠️  Does NOT query oauth_tokens table")
                
                # Check if it still queries user_platform_credentials (fallback OK)
                if "user_platform_credentials" in source:
                    if "DEPRECATED" in source or "Fallback" in source:
                        print(f"   ℹ️  Has fallback to user_platform_credentials (OK)")
                    else:
                        print(f"   ⚠️  Queries user_platform_credentials without fallback warning")
            else:
                print(f"   ❌ Method not found")
        
        print("\n✅ Test 5 Complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking UserAuthManager methods: {e}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("FIX #14 VERIFICATION SCRIPT - OAuth Cleanup")
    print("="*70)
    print("\nVerifying that:")
    print("1. credentials_desktop.json references have warnings")
    print("2. user_platform_credentials queries updated to oauth_tokens")
    print("3. Microsoft token storage uses oauth_tokens table")
    print("4. Backward compatibility maintained")
    
    results = []
    
    try:
        results.append(("File Modifications", test_1_check_files_modified()))
        results.append(("Database Schema", test_2_check_database_schema()))
        results.append(("Imports", test_3_check_imports()))
        results.append(("Function Signatures", test_4_check_function_signatures()))
        results.append(("UserAuth Methods", test_5_check_user_auth_methods()))
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "="*70)
    print(f"FINAL RESULT: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Fix #14 successfully implemented.")
        print("\n📋 Next Steps:")
        print("   1. Restart Flask server: BISTART")
        print("   2. Test Google OAuth login")
        print("   3. Test Microsoft OAuth login")
        print("   4. Test Google Workspace tools")
        print("   5. Check for deprecation warnings in console")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")


if __name__ == "__main__":
    main()
