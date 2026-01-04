"""
Run migration to add link_purpose column to oauth_tokens table
Safe migration - only adds column with DEFAULT value, doesn't touch existing auth
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    """Execute the migration SQL"""
    
    print("=" * 60)
    print("🔧 Running Migration: Add link_purpose Column")
    print("=" * 60)
    
    # Run each statement separately to avoid DO $$ block issues
    statements = [
        # Check and add column
        """
        ALTER TABLE oauth_tokens 
        ADD COLUMN IF NOT EXISTS link_purpose TEXT DEFAULT 'primary'
        """,
        
        # Backfill existing records
        """
        UPDATE oauth_tokens 
        SET link_purpose = 'primary' 
        WHERE link_purpose IS NULL
        """,
        
        # Add documentation
        """
        COMMENT ON COLUMN oauth_tokens.link_purpose IS 
        'Purpose of OAuth link: "primary" (full API access for login platform) or "storage" (Drive/OneDrive only for linked platform)'
        """
    ]
    
    try:
        from shared.database_utils import execute_query
        
        for i, stmt in enumerate(statements, 1):
            print(f"\n[{i}/{len(statements)}] Executing statement...")
            # Use fetch_mode=None for DDL/DML statements (no results to fetch)
            execute_query(stmt, fetch_mode=None)
            print(f"✅ Statement {i} completed")
        
        print("\n" + "=" * 60)
        print("✅ Migration Complete!")
        print("=" * 60)
        print("• Column: link_purpose TEXT DEFAULT 'primary'")
        print("• All existing records: link_purpose='primary'")
        print("• Authentication flow: UNCHANGED ✅")
        print("=" * 60)
        
        # Verify
        result = execute_query(
            """SELECT COUNT(*) as total,
                      COUNT(CASE WHEN link_purpose = 'primary' THEN 1 END) as primary_count,
                      COUNT(CASE WHEN link_purpose = 'storage' THEN 1 END) as storage_count
               FROM oauth_tokens""",
            fetch_mode='one'
        )
        
        if result:
            print(f"\n📊 Verification:")
            print(f"   Total OAuth Tokens: {result[0]}")
            print(f"   Primary Accounts: {result[1]}")
            print(f"   Storage Accounts: {result[2]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
