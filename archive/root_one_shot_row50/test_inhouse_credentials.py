#!/usr/bin/env python3
"""Test InHouse Print database credentials and connection."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from AI_infrastructure.shared.database_utils import execute_query

def test_credentials():
    """Test credential fetching from Supabase."""
    print("Testing InHouse Print credentials...")
    
    # Check credentials exist
    creds = execute_query(
        "SELECT platform, credentials FROM ai_infrastructure.user_platform_credentials WHERE user_id=1 AND platform=%s",
        ('inhouse_print',),
        fetch_mode='one'
    )
    
    if creds:
        print(f"✅ Found credentials for platform: {creds['platform']}")
        print(f"   Has credentials: {bool(creds['credentials'])}")
        if creds['credentials']:
            import json
            cred_data = json.loads(creds['credentials']) if isinstance(creds['credentials'], str) else creds['credentials']
            print(f"   Credential keys: {list(cred_data.keys())}")
        return True
    else:
        print("❌ No credentials found in Supabase")
        return False

def test_db_connector():
    """Test db_connector can initialize."""
    print("\nTesting db_connector initialization...")
    try:
        # Change to inhouse-print directory
        inhouse_dir = os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'inhouse-print')
        os.chdir(inhouse_dir)
        sys.path.insert(0, inhouse_dir)
        
        from db_connector import InHousePrintDB
        
        db = InHousePrintDB()
        print("✅ InHousePrintDB initialized successfully")
        print(f"   Connection method: {'Supabase' if hasattr(db, 'from_supabase') else 'Local config'}")
        return True
    except Exception as e:
        print(f"❌ InHousePrintDB initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = True
    success = test_credentials() and success
    success = test_db_connector() and success
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)
    
    sys.exit(0 if success else 1)
