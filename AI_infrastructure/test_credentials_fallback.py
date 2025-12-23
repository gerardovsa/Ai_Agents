"""
Test script for two-tier credential system with fallback to user_id=1

Tests:
1. Direct database query for user 14 credentials
2. Direct database query for user 1 (platform global) credentials  
3. Credential fallback logic in get_platform_credentials
4. Vector DB initialization with fallback
5. API endpoint responses

Usage:
    python test_credentials_fallback.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth.user_auth import UserAuthManager
from shared.database_utils import execute_query

def test_database_credentials():
    """Test 1: Direct database queries"""
    print("\n" + "="*60)
    print("TEST 1: Direct Database Queries")
    print("="*60)
    
    # Check user 14 credentials
    print("\n🔍 Checking user 14 credentials...")
    result = execute_query("""
        SELECT user_id, platform, credential_key, is_active
        FROM ai_infrastructure.user_platform_credentials
        WHERE user_id = 14 AND platform IN ('pinecone', 'voyager', 'openai_embeddings')
        ORDER BY platform
    """, fetch_mode='all')
    
    print(f"Found {len(result) if result else 0} credentials for user 14:")
    if result:
        for row in result:
            print(f"  - {row}")
    else:
        print("  ❌ No credentials found for user 14")
    
    # Check user 1 (platform global) credentials
    print("\n🔍 Checking user 1 (platform global) credentials...")
    result = execute_query("""
        SELECT user_id, platform, credential_key, is_active, 
               SUBSTRING(credential_value, 1, 20) || '...' as value_preview
        FROM ai_infrastructure.user_platform_credentials
        WHERE user_id = 1 AND platform IN ('pinecone', 'voyager', 'openai_embeddings')
        ORDER BY platform
    """, fetch_mode='all')
    
    print(f"Found {len(result) if result else 0} credentials for user 1:")
    if result:
        for row in result:
            print(f"  ✅ {row}")
    else:
        print("  ❌ No credentials found for user 1")
    
    return bool(result)


def test_auth_manager_fallback():
    """Test 2: UserAuthManager.get_platform_credentials with fallback"""
    print("\n" + "="*60)
    print("TEST 2: UserAuthManager Fallback Logic")
    print("="*60)
    
    auth_manager = UserAuthManager()
    
    platforms = ['pinecone', 'voyager', 'openai_embeddings']
    success_count = 0
    
    for platform in platforms:
        print(f"\n🔍 Testing {platform} for user 14...")
        try:
            creds = auth_manager.get_platform_credentials(14, platform)
            if creds:
                print(f"  ✅ Found credentials!")
                print(f"  Keys: {list(creds.keys())}")
                # Don't print actual values for security
                success_count += 1
            else:
                print(f"  ❌ No credentials returned")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'✅' if success_count == len(platforms) else '❌'} Result: {success_count}/{len(platforms)} platforms have credentials")
    return success_count == len(platforms)


def test_credential_injector():
    """Test 3: Credential injector functions"""
    print("\n" + "="*60)
    print("TEST 3: Credential Injector Functions")
    print("="*60)
    
    from auth.credential_injector import (
        get_pinecone_credentials,
        get_voyager_credentials,
        get_openai_embeddings_credentials
    )
    
    tests = [
        ("Pinecone", get_pinecone_credentials),
        ("Voyager", get_voyager_credentials),
        ("OpenAI Embeddings", get_openai_embeddings_credentials)
    ]
    
    success_count = 0
    
    for name, func in tests:
        print(f"\n🔍 Testing {name}...")
        try:
            creds = func(user_id=14)
            if creds:
                print(f"  ✅ Got credentials!")
                print(f"  Keys: {list(creds.keys())}")
                success_count += 1
            else:
                print(f"  ❌ No credentials returned")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n{'✅' if success_count == len(tests) else '❌'} Result: {success_count}/{len(tests)} injectors working")
    return success_count == len(tests)


def test_vector_db_initialization():
    """Test 4: Vector DB credential loading"""
    print("\n" + "="*60)
    print("TEST 4: Vector DB Initialization")
    print("="*60)
    
    try:
        from routes.vector_db_routes import _get_vector_db_credentials
        
        print("\n🔍 Loading credentials for user 14...")
        creds = _get_vector_db_credentials(14)
        
        print(f"\nCredential keys found: {list(creds.keys())}")
        
        checks = {
            'Pinecone API Key': 'pinecone_api_key' in creds,
            'Pinecone Index': 'pinecone_index_name' in creds,
            'Voyager API Key': 'voyager_api_key' in creds,
            'OpenAI API Key (fallback)': 'openai_api_key' in creds or 'voyager_api_key' in creds
        }
        
        for check_name, result in checks.items():
            print(f"  {'✅' if result else '❌'} {check_name}")
        
        all_passed = checks['Pinecone API Key'] and (checks['Voyager API Key'] or checks['OpenAI API Key (fallback)'])
        print(f"\n{'✅' if all_passed else '❌'} Vector DB initialization: {'PASSED' if all_passed else 'FAILED'}")
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test 5: API endpoint behavior"""
    print("\n" + "="*60)
    print("TEST 5: API Endpoints (Manual Test Required)")
    print("="*60)
    
    print("\n📋 Manual testing steps:")
    print("1. Ensure Flask server is running (BISTART)")
    print("2. Open browser to http://localhost:5001")
    print("3. Login as any user (user 14)")
    print("4. Open Vector Database sidebar")
    print("5. Check if it shows platform credentials")
    print("\nExpected behavior:")
    print("  ✅ Vector DB should initialize with user 1's credentials")
    print("  ✅ Platform Connections modal should show global credentials")
    print("  ✅ Credentials should be marked as 'Platform Global'")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 CREDENTIAL FALLBACK SYSTEM TEST SUITE")
    print("="*60)
    print("\nTesting two-tier credential system:")
    print("  Tier 1: User-specific credentials (user_id = 14)")
    print("  Tier 2: Platform global credentials (user_id = 1)")
    print("\nFallback hierarchy: User → Platform → Error")
    
    results = []
    
    # Run tests
    results.append(("Database Queries", test_database_credentials()))
    results.append(("Auth Manager Fallback", test_auth_manager_fallback()))
    results.append(("Credential Injector", test_credential_injector()))
    results.append(("Vector DB Init", test_vector_db_initialization()))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        print(f"  {'✅ PASS' if passed else '❌ FAIL'} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n{'✅' if total_passed == total_tests else '❌'} Overall: {total_passed}/{total_tests} tests passed")
    
    test_api_endpoints()
    
    print("\n" + "="*60)
    
    return total_passed == total_tests


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
