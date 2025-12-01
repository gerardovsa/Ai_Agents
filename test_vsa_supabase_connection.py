"""
Test VSA Veterinary Alerts Module - Supabase Connection
Tests that the module can connect to the Supabase database using stored credentials
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AI_infrastructure'))

from get_supabase_credentials import get_supabase_credentials_for_frontend, get_supabase_credentials_for_backend
import json

def test_frontend_credentials():
    """Test frontend-safe credentials (anon_key only)"""
    print("\n" + "="*80)
    print("TEST 1: Frontend Credentials (anon_key)")
    print("="*80)
    
    try:
        creds = get_supabase_credentials_for_frontend(user_id=1)
        
        if not creds:
            print("❌ FAILED: No credentials found")
            return False
        
        # Check expected fields
        required = ['url', 'anon_key', 'project_id', 'region']
        missing = [field for field in required if field not in creds]
        
        if missing:
            print(f"❌ FAILED: Missing fields: {missing}")
            return False
        
        # Verify no service_key in frontend credentials
        if 'service_key' in creds:
            print("❌ FAILED: service_key should NOT be in frontend credentials")
            return False
        
        print("✅ SUCCESS: Frontend credentials valid")
        print(f"   URL: {creds['url']}")
        print(f"   Project ID: {creds['project_id']}")
        print(f"   Region: {creds['region']}")
        print(f"   Anon Key: {creds['anon_key'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_backend_credentials():
    """Test backend credentials (includes service_key)"""
    print("\n" + "="*80)
    print("TEST 2: Backend Credentials (service_key)")
    print("="*80)
    
    try:
        creds = get_supabase_credentials_for_backend(user_id=1)
        
        if not creds:
            print("❌ FAILED: No credentials found")
            return False
        
        # Check expected fields
        required = ['url', 'anon_key', 'service_key', 'db_host', 'db_port', 'db_name', 'db_user', 'db_password']
        missing = [field for field in required if field not in creds]
        
        if missing:
            print(f"❌ FAILED: Missing fields: {missing}")
            return False
        
        print("✅ SUCCESS: Backend credentials valid")
        print(f"   URL: {creds['url']}")
        print(f"   DB Host: {creds['db_host']}")
        print(f"   DB Port: {creds['db_port']}")
        print(f"   DB Name: {creds['db_name']}")
        print(f"   Service Key: {creds['service_key'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_supabase_connection():
    """Test actual connection to Supabase"""
    print("\n" + "="*80)
    print("TEST 3: Supabase Connection Test")
    print("="*80)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        creds = get_supabase_credentials_for_backend(user_id=1)
        
        if not creds:
            print("❌ FAILED: No credentials found")
            return False
        
        # Build connection string
        conn_str = f"postgresql://{creds['db_user']}:{creds['db_password']}@{creds['db_host']}:{creds['db_port']}/{creds['db_name']}"
        
        print(f"Connecting to: {creds['db_host']}")
        
        # Connect
        conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Test query - count veterinary_calls
        cursor.execute("SELECT COUNT(*) as count FROM public.veterinary_calls")
        result = cursor.fetchone()
        
        count = result['count']
        
        conn.close()
        
        print(f"✅ SUCCESS: Connected to Supabase")
        print(f"   Total veterinary_calls: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_vsa_module_credentials():
    """Test that VSA module credentials match database"""
    print("\n" + "="*80)
    print("TEST 4: VSA Module Credentials Match")
    print("="*80)
    
    try:
        # Read VSA module JS file
        module_path = os.path.join(
            os.path.dirname(__file__), 
            'UI', 'modules_external', 'vsa-veterinary-alerts', 'vsa-veterinary-alerts.js'
        )
        
        if not os.path.exists(module_path):
            print(f"❌ FAILED: Module file not found at {module_path}")
            return False
        
        with open(module_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Get credentials from database
        db_creds = get_supabase_credentials_for_backend(user_id=1)
        
        if not db_creds:
            print("❌ FAILED: No credentials in database")
            return False
        
        # Check if URL and service_key are in JS file
        url_in_js = db_creds['url'] in js_content
        key_in_js = db_creds['service_key'] in js_content
        
        if url_in_js and key_in_js:
            print("✅ SUCCESS: VSA module has correct hardcoded credentials")
            print(f"   URL matches: {db_creds['url']}")
            print(f"   Service key matches: {db_creds['service_key'][:50]}...")
        else:
            print("⚠️  WARNING: VSA module credentials don't match database")
            print(f"   URL in JS: {url_in_js}")
            print(f"   Service key in JS: {key_in_js}")
            print("\n   RECOMMENDATION: Update vsa-veterinary-alerts.js lines 14-15")
            print("   Or modify to fetch credentials from /api/credentials/supabase")
        
        return url_in_js and key_in_js
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def main():
    print("\n" + "="*80)
    print("VSA VETERINARY ALERTS MODULE - CREDENTIAL TESTING")
    print("="*80)
    
    results = {
        'Frontend Credentials': test_frontend_credentials(),
        'Backend Credentials': test_backend_credentials(),
        'Supabase Connection': test_supabase_connection(),
        'VSA Module Match': test_vsa_module_credentials()
    }
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nRESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - VSA module is ready to use!")
    else:
        print("\n⚠️  SOME TESTS FAILED - review errors above")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
