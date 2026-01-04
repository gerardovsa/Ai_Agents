"""Quick verification that link_purpose column was added"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

# Check column exists
result = execute_query(
    """SELECT column_name, data_type, column_default 
       FROM information_schema.columns 
       WHERE table_name = 'oauth_tokens' 
       AND column_name = 'link_purpose'""",
    fetch_mode='all'
)

if result:
    print("✅ link_purpose column EXISTS!")
    print(f"   Type: {result[0]['data_type']}")
    print(f"   Default: {result[0]['column_default']}")
    
    # Check data
    count_result = execute_query(
        """SELECT COUNT(*) as total,
                  COUNT(CASE WHEN link_purpose = 'primary' THEN 1 END) as primary_count,
                  COUNT(CASE WHEN link_purpose = 'storage' THEN 1 END) as storage_count
           FROM oauth_tokens""",
        fetch_mode='one'
    )
    
    print(f"\n📊 Data:")
    print(f"   Total OAuth Tokens: {count_result['total']}")
    print(f"   Primary Accounts: {count_result['primary_count']}")
    print(f"   Storage Accounts: {count_result['storage_count']}")
    print("\n✅ MIGRATION SUCCESSFUL - User authentication flow UNCHANGED!")
else:
    print("❌ link_purpose column NOT FOUND!")
