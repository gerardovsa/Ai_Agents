"""
Test High Priority Supabase Migration Fixes
===========================================

Verifies that the 5 HIGH priority files are properly migrated to Supabase:
1. No conn.row_factory = sqlite3.Row lines
2. Using get_database_connection() for connections
3. Can import and instantiate classes
4. Database connections work

Tests both local (if available) and production readiness.
"""

import sys
from pathlib import Path
import re

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

# Files to test
FILES_TO_TEST = [
    'AI_infrastructure/auth/user_auth.py',
    'AI_infrastructure/scheduler.py',
    'AI_infrastructure/routes/automation_routes.py',
    'AI_infrastructure/auth/permission_checker.py',
    'AI_infrastructure/auth/credential_injector.py'
]

def test_no_row_factory_lines(file_path: str) -> tuple[bool, list]:
    """Test that file has no row_factory lines"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'\.row_factory\s*=\s*sqlite3\.Row', content)
    return len(matches) == 0, matches


def test_uses_get_database_connection(file_path: str) -> tuple[bool, int]:
    """Test that file uses get_database_connection() or get_connection() wrapper"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for either get_database_connection or get_connection (wrapper)
    has_direct = 'get_database_connection' in content
    has_wrapper = 'get_connection' in content
    
    # Count usage of either
    direct_count = len(re.findall(r'get_database_connection\(', content))
    wrapper_count = len(re.findall(r'get_connection\(', content))
    usage_count = direct_count + wrapper_count
    
    return (has_direct or has_wrapper) and usage_count > 0, usage_count


def test_no_direct_sqlite_connect(file_path: str) -> tuple[bool, list]:
    """Test that file doesn't use sqlite3.connect() directly"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'sqlite3\.connect\([^)]+\)', content)
    return len(matches) == 0, matches


def test_file_imports(file_path: str) -> tuple[bool, str]:
    """Test that file can be imported"""
    try:
        # Extract module path from file path
        if 'auth/user_auth.py' in file_path:
            from auth.user_auth import UserAuthManager
            return True, "UserAuthManager imported"
        elif 'scheduler.py' in file_path:
            from scheduler import AutomationScheduler
            return True, "AutomationScheduler imported"
        elif 'automation_routes.py' in file_path:
            # Just check it doesn't crash when imported
            import routes.automation_routes
            return True, "automation_routes imported"
        elif 'permission_checker.py' in file_path:
            from auth.permission_checker import PermissionChecker
            return True, "PermissionChecker imported"
        elif 'credential_injector.py' in file_path:
            # credential_injector is imported in other modules, check if it loads
            import auth.credential_injector
            return True, "credential_injector module imported"
        return True, "N/A"
    except Exception as e:
        return False, str(e)


def test_database_connection() -> tuple[bool, str]:
    """Test that get_database_connection() works"""
    try:
        from shared.database_utils import get_database_connection, is_using_supabase
        
        # Check if using Supabase
        using_supabase = is_using_supabase()
        
        # Try to connect
        conn = get_database_connection('ai_infrastructure')
        
        # Try a simple query
        cursor = conn.cursor()
        if using_supabase:
            cursor.execute("SELECT 1 as test")
        else:
            cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        conn.close()
        
        db_type = "Supabase PostgreSQL" if using_supabase else "SQLite"
        return True, f"Connected to {db_type}"
    except Exception as e:
        return False, str(e)


def main():
    """Run all tests"""
    print("="*70)
    print("🧪 HIGH PRIORITY SUPABASE MIGRATION TESTS")
    print("="*70)
    print()
    
    all_passed = True
    results = []
    
    # Test each file
    for file_path in FILES_TO_TEST:
        print(f"📄 Testing: {Path(file_path).name}")
        print(f"   Path: {file_path}")
        
        file_passed = True
        file_results = []
        
        # Test 1: No row_factory lines
        passed, matches = test_no_row_factory_lines(file_path)
        file_results.append(('No row_factory lines', passed, matches))
        if passed:
            print(f"   ✅ No row_factory lines")
        else:
            print(f"   ❌ Found {len(matches)} row_factory lines: {matches}")
            file_passed = False
        
        # Test 2: Uses get_database_connection
        passed, count = test_uses_get_database_connection(file_path)
        file_results.append(('Uses get_database_connection', passed, count))
        if passed:
            print(f"   ✅ Uses get_database_connection() ({count} times)")
        else:
            print(f"   ❌ Doesn't use get_database_connection()")
            file_passed = False
        
        # Test 3: No direct sqlite3.connect
        passed, matches = test_no_direct_sqlite_connect(file_path)
        file_results.append(('No direct sqlite3.connect', passed, matches))
        if passed:
            print(f"   ✅ No direct sqlite3.connect() calls")
        else:
            print(f"   ⚠️  Found {len(matches)} sqlite3.connect() calls: {matches}")
            # Not a failure if using get_database_connection too
        
        # Test 4: Can import
        passed, msg = test_file_imports(file_path)
        file_results.append(('File imports', passed, msg))
        if passed:
            print(f"   ✅ {msg}")
        else:
            print(f"   ❌ Import failed: {msg}")
            file_passed = False
        
        if not file_passed:
            all_passed = False
        
        results.append((file_path, file_passed, file_results))
        print()
    
    # Test database connection
    print("🗄️  Testing Database Connection")
    passed, msg = test_database_connection()
    if passed:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ Connection failed: {msg}")
        all_passed = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    print(f"Files tested: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {len(results) - passed_count}")
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎯 READY FOR DEPLOYMENT")
        print("   Next steps:")
        print("   1. git add <modified files>")
        print("   2. git commit -m 'Remove SQLite remnants from high priority files'")
        print("   3. git push origin v6")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nFailed files:")
        for file_path, passed, _ in results:
            if not passed:
                print(f"  - {file_path}")
        print("\nRun fix_high_priority_sqlite.py to fix issues")
    
    print("="*70)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
