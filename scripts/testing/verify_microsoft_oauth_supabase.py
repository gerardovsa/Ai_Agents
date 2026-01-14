"""
Verify Microsoft OAuth Tokens in Supabase - Diagnostic Tool
============================================================

This script checks if your Microsoft OAuth tokens exist in Supabase PostgreSQL.

Usage:
    python scripts/testing/verify_microsoft_oauth_supabase.py
"""

import sys
from pathlib import Path

# Add project root and AI_infrastructure to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent.parent / '.env.master')

def check_microsoft_tokens():
    """Check Microsoft OAuth tokens in Supabase"""
    print("\n" + "="*80)
    print("MICROSOFT OAUTH TOKEN VERIFICATION (SUPABASE)")
    print("="*80)
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query for Microsoft tokens (same query as backend)
        print("\n1. Checking oauth_tokens table for user_id=14...")
        cursor.execute("""
            SELECT 
                id,
                user_id,
                platform,
                access_token,
                refresh_token,
                token_type,
                expires_at,
                scope,
                granted_scopes,
                account_identifier,
                account_name,
                is_active,
                is_valid,
                created_at,
                updated_at
            FROM ai_infrastructure.oauth_tokens
            WHERE user_id = %s AND platform = 'microsoft'
            ORDER BY updated_at DESC
        """, (14,))
        
        rows = cursor.fetchall()
        
        if not rows:
            print("   ❌ NO MICROSOFT OAUTH TOKENS FOUND")
            print("\n   This means:")
            print("   - Your tokens exist locally but NOT in Supabase")
            print("   - You need to re-authenticate on Render deployment")
            print("   - Or migrate your local tokens to Supabase")
            
            # Check if ANY tokens exist for this user
            print("\n2. Checking ALL platforms for user_id=14...")
            cursor.execute("""
                SELECT platform, is_active, created_at
                FROM ai_infrastructure.oauth_tokens
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (14,))
            
            all_rows = cursor.fetchall()
            if all_rows:
                print(f"   Found {len(all_rows)} token(s) for other platforms:")
                for row in all_rows:
                    platform = row['platform']
                    is_active = row['is_active']
                    created_at = row['created_at']
                    status = "✅" if is_active else "❌"
                    print(f"      {status} {platform} (created: {created_at})")
            else:
                print("   ❌ NO TOKENS FOUND AT ALL")
                print("   User 14 has never authenticated on this Supabase instance")
        else:
            print(f"   ✅ Found {len(rows)} Microsoft OAuth token(s)")
            
            for i, row in enumerate(rows, 1):
                print(f"\n   Token {i}:")
                print(f"      ID: {row['id']}")
                print(f"      User ID: {row['user_id']}")
                print(f"      Platform: {row['platform']}")
                print(f"      Access Token: {row['access_token'][:20]}..." if row['access_token'] else "      Access Token: None")
                print(f"      Refresh Token: {row['refresh_token'][:20]}..." if row['refresh_token'] else "      Refresh Token: None")
                print(f"      Expires At: {row['expires_at']}")
                print(f"      Scope: {row['scope']}")
                print(f"      Account: {row['account_name']} ({row['account_identifier']})")
                print(f"      Is Active: {row['is_active']}")
                print(f"      Is Valid: {row['is_valid']}")
                print(f"      Created: {row['created_at']}")
                print(f"      Updated: {row['updated_at']}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*80)
    return True


def check_local_tokens():
    """Check if Microsoft tokens exist locally (for comparison)"""
    print("\n" + "="*80)
    print("LOCAL DATABASE CHECK (FOR COMPARISON)")
    print("="*80)
    
    try:
        import sqlite3
        local_db = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
        
        if not local_db.exists():
            print("   ⚠️  Local database not found (expected on Render)")
            return
        
        conn = sqlite3.connect(str(local_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT platform, is_active, created_at
            FROM oauth_tokens
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (14,))
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"   Found {len(rows)} local token(s):")
            for row in rows:
                platform = row['platform']
                is_active = row['is_active']
                created_at = row['created_at']
                status = "✅" if is_active else "❌"
                print(f"      {status} {platform} (created: {created_at})")
        else:
            print("   ❌ No local tokens found")
        
        conn.close()
        
    except Exception as e:
        print(f"   ⚠️  Could not check local database: {e}")
    
    print("="*80)


def main():
    """Main diagnostic routine"""
    print("\n🔍 Microsoft OAuth Token Diagnostic Tool")
    print("   Purpose: Verify tokens exist in Supabase PostgreSQL")
    print("   User: 14 (Gerard)")
    
    # Check Supabase (production)
    supabase_ok = check_microsoft_tokens()
    
    # Check local (for comparison)
    check_local_tokens()
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    print("""
If tokens NOT found in Supabase:

Option 1: Re-authenticate on Render (Recommended)
   1. Open your Render deployment URL
   2. Click "Connect Microsoft Account"
   3. Complete OAuth flow
   4. Tokens will be stored in Supabase automatically

Option 2: Migrate local tokens to Supabase
   1. Run: python Supabase/migrate_to_supabase.py
   2. This will copy your local tokens to Supabase
   3. Refresh your Render deployment

Option 3: Manual token insert (Advanced)
   1. Extract tokens from local database
   2. Use Supabase SQL editor to insert
   3. Use scripts/testing/insert_microsoft_token_to_supabase.py
    """)
    
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
