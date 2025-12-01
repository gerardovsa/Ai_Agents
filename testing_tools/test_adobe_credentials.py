"""
Test Adobe Firefly Credentials - Verify Database Storage

This script tests:
1. Credentials exist in database
2. Credentials can be retrieved
3. Adobe InDesign implementation can access them

Usage:
    python testing_tools/test_adobe_credentials.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.database_utils import get_database_connection
import json


def test_database_credentials():
    """Test 1: Check credentials in database"""
    print("\n" + "="*80)
    print("TEST 1: Adobe Firefly Credentials in Database")
    print("="*80 + "\n")
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                user_id,
                platform,
                credential_type,
                is_active,
                credentials,
                metadata,
                created_at
            FROM ai_infrastructure.user_platform_credentials
            WHERE platform = 'adobe_firefly'
              AND user_id = 1
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("❌ FAIL: No credentials found in database")
            print("\nℹ️  Run this SQL to insert credentials:")
            print("   scripts/setup/insert_adobe_firefly_credentials.sql")
            return False
        
        # Parse credentials
        credentials = row[5] if isinstance(row[5], dict) else json.loads(row[5])
        metadata = row[6] if isinstance(row[6], dict) else json.loads(row[6])
        
        print("✅ PASS: Credentials found in database")
        print(f"\n📋 Details:")
        print(f"   ID: {row[0]}")
        print(f"   User ID: {row[1]}")
        print(f"   Platform: {row[2]}")
        print(f"   Type: {row[3]}")
        print(f"   Active: {row[4]}")
        print(f"   Created: {row[7]}")
        
        print(f"\n🔑 Credentials (masked):")
        print(f"   Client ID: {credentials.get('client_id', '')[:8]}...")
        print(f"   Client Secret: {credentials.get('client_secret', '')[:8]}...")
        print(f"   Token Endpoint: {credentials.get('token_endpoint', 'N/A')}")
        
        print(f"\nℹ️  Metadata:")
        print(f"   Display Name: {metadata.get('display_name', 'N/A')}")
        print(f"   Service Type: {metadata.get('service_type', 'N/A')}")
        print(f"   API Base URL: {metadata.get('api_base_url', 'N/A')}")
        print(f"   Features: {len(metadata.get('features', []))} available")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_credential_retrieval():
    """Test 2: Retrieve credentials via helper function"""
    print("\n" + "="*80)
    print("TEST 2: Credential Retrieval Function")
    print("="*80 + "\n")
    
    try:
        from tools.implementations.adobe_indesign import _get_adobe_credentials
        
        creds = _get_adobe_credentials(user_id=1)
        
        if not creds.get('client_id') or not creds.get('client_secret'):
            print("❌ FAIL: Credentials not retrieved")
            return False
        
        print("✅ PASS: Credentials retrieved successfully")
        print(f"\n🔑 Retrieved:")
        print(f"   Client ID: {creds['client_id'][:8]}...")
        print(f"   Client Secret: {creds['client_secret'][:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_firefly_client_init():
    """Test 3: Initialize Adobe Firefly client"""
    print("\n" + "="*80)
    print("TEST 3: Adobe Firefly Client Initialization")
    print("="*80 + "\n")
    
    try:
        from tools.implementations.adobe_indesign import AdobeFireflyClient
        
        client = AdobeFireflyClient(user_id=1)
        
        print("✅ PASS: Client initialized successfully")
        print(f"\n📋 Client Details:")
        print(f"   Client ID: {client.client_id[:8]}...")
        print(f"   Base URL: {client.base_url}")
        print(f"   Token: {'Not authenticated yet' if not client.access_token else 'Authenticated'}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Client initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_fallback():
    """Test 4: Config.py fallback"""
    print("\n" + "="*80)
    print("TEST 4: Config.py Fallback Check")
    print("="*80 + "\n")
    
    try:
        from config import ADOBE_FIREFLY_CLIENT_ID, ADOBE_FIREFLY_CLIENT_SECRET
        
        if ADOBE_FIREFLY_CLIENT_ID and ADOBE_FIREFLY_CLIENT_SECRET:
            print("✅ PASS: Config.py has credentials")
            print(f"   Client ID: {ADOBE_FIREFLY_CLIENT_ID[:8]}...")
            print(f"   Client Secret: {ADOBE_FIREFLY_CLIENT_SECRET[:8]}...")
        else:
            print("⚠️  WARNING: Config.py credentials not set (database will be used)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Config import error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 ADOBE FIREFLY CREDENTIALS TEST SUITE")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Database Storage", test_database_credentials()))
    results.append(("Credential Retrieval", test_credential_retrieval()))
    results.append(("Client Initialization", test_firefly_client_init()))
    results.append(("Config Fallback", test_config_fallback()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80 + "\n")
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! All tests passed!")
        print("\n🚀 Next Steps:")
        print("   1. Start server: BISTART")
        print("   2. Test tools: CHAT 'List Adobe InDesign tools'")
        print("   3. Try catalog: CHAT 'Create a product catalog'")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        if not results[0][1]:
            print("\n💡 Quick Fix:")
            print("   Run: scripts/setup/insert_adobe_firefly_credentials.sql")
            print("   Location: Supabase SQL Editor")
    
    print("="*80 + "\n")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
