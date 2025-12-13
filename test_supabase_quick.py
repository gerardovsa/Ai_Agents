"""Test Supabase Credentials - Find the Error"""
import os
os.environ['SUPABASE_DB_URL_POOLER'] = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

print("Testing Supabase Connection...")
try:
    from AI_infrastructure.auth.supabase_credentials import SupabaseCredentialsManager
    manager = SupabaseCredentialsManager()
    print(f"Is Render: {manager.is_render}")
    
    if manager.test_connection():
        print("✅ Connection works")
        
        # Test fetching credentials
        sql_creds = manager.get_credentials('inhouse_print')
        if sql_creds:
            print(f"✅ SQL creds found: {sql_creds.get('database')}")
        else:
            print("❌ SQL creds NOT FOUND")
            
        config = manager.get_inhouse_print_config()
        print(f"✅ Config created: {config['DatabaseConnections']['Primary']['DatabaseName']}")
    else:
        print("❌ Connection failed")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
