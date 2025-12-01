"""
Test Supabase Credentials in AI_agents Database
Verifies credentials are stored and accessible
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def test_supabase_credentials():
    """Check if Supabase credentials exist in database"""
    
    print("=" * 60)
    print("TESTING SUPABASE CREDENTIALS")
    print("=" * 60)
    
    try:
        # Connect to AI_agents database
        print("\n1. Connecting to AI_agents database...")
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        print("   ✅ Connected successfully")
        
        # Query for Supabase credentials
        print("\n2. Querying for Supabase credentials...")
        cursor.execute("""
            SELECT 
                id,
                user_id,
                platform,
                credential_type,
                is_active,
                credentials,
                metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE platform = 'supabase'
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("   ❌ No Supabase credentials found in database")
            print("\n   ACTION REQUIRED:")
            print("   Run the SQL script in SUPABASE_CREDENTIALS_INSERT.sql")
            cursor.close()
            conn.close()
            return False
        
        print(f"   ✅ Found {len(rows)} Supabase credential record(s)\n")
        
        # Display results (rows are RealDictRow objects - dictionary-like)
        for row in rows:
            print("-" * 60)
            print(f"   ID: {row['id']}")
            print(f"   User ID: {row['user_id']}")
            print(f"   Platform: {row['platform']}")
            print(f"   Credential Type: {row['credential_type']}")
            print(f"   Active: {row['is_active']}")
            
            # Credentials JSONB
            creds = row['credentials'] if row['credentials'] else {}
            print(f"   Supabase URL: {creds.get('url', 'N/A')}")
            print(f"   Project ID: {creds.get('project_id', 'N/A')}")
            print(f"   Service Key: {'***' + creds.get('service_key', '')[-20:] if creds.get('service_key') else 'N/A'}")
            
            # Metadata JSONB
            meta = row['metadata'] if row['metadata'] else {}
            print(f"   Purpose: {meta.get('purpose', 'N/A')}")
        
        print("-" * 60)
        
        # Test credential fields
        print("\n3. Testing credential fields...")
        creds = rows[0]['credentials'] if rows[0]['credentials'] else {}
        required_fields = ['url', 'service_key', 'project_id']
        missing = [f for f in required_fields if f not in creds]
        
        if missing:
            print(f"   ❌ Missing fields: {missing}")
            cursor.close()
            conn.close()
            return False
        else:
            print(f"   ✅ All required fields present")
            print(f"      - URL: {creds.get('url', 'N/A')}")
            print(f"      - Project ID: {creds.get('project_id', 'N/A')}")
            print(f"      - DB Host: {creds.get('db_host', 'N/A')}")
            print(f"      - DB Name: {creds.get('db_name', 'N/A')}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ SUPABASE CREDENTIALS TEST PASSED")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Credentials are stored and accessible")
        print("2. VSA Veterinary Alerts module can use these credentials")
        print("3. No further action needed unless credentials need updating")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_supabase_credentials()
