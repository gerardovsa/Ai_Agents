"""Check OAuth tokens table and create proper connections display"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_oauth_tokens(user_id=14):
    """Check OAuth tokens for user"""
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    print(f"\nChecking oauth_tokens for user_id={user_id}...")
    
    cursor.execute("""
        SELECT 
            id,
            user_id,
            platform,
            email,
            is_active,
            is_valid,
            created_at,
            updated_at,
            expires_at,
            last_refreshed_at
        FROM ai_infrastructure.oauth_tokens
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    print(f"✅ Found {len(rows)} OAuth connections\n")
    
    for row in rows:
        row_dict = dict(row) if isinstance(row, dict) else {
            'id': row[0],
            'user_id': row[1],
            'platform': row[2],
            'email': row[3],
            'is_active': row[4],
            'is_valid': row[5],
            'created_at': row[6],
            'updated_at': row[7],
            'expires_at': row[8],
            'last_refreshed_at': row[9]
        }
        
        print(f"Connection #{row_dict['id']}:")
        print(f"  Platform: {row_dict['platform']}")
        print(f"  Email: {row_dict['email']}")
        print(f"  Active: {row_dict['is_active']}")
        print(f"  Valid: {row_dict['is_valid']}")
        print(f"  Created: {row_dict['created_at']}")
        print(f"  Expires: {row_dict['expires_at']}")
        print()
    
    cursor.close()
    conn.close()
    
    return rows

def check_users_table(user_id=14):
    """Check users table for OAuth flags"""
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    print(f"\nChecking users table for user_id={user_id}...")
    
    cursor.execute("""
        SELECT 
            id,
            email,
            has_google_oauth,
            has_microsoft_oauth,
            is_active,
            created_at
        FROM ai_infrastructure.users
        WHERE id = %s
    """, (user_id,))
    
    row = cursor.fetchone()
    
    if row:
        row_dict = dict(row) if isinstance(row, dict) else {
            'id': row[0],
            'email': row[1],
            'has_google_oauth': row[2],
            'has_microsoft_oauth': row[3],
            'is_active': row[4],
            'created_at': row[5]
        }
        
        print(f"✅ User found:")
        print(f"  Email: {row_dict['email']}")
        print(f"  Has Google OAuth: {row_dict['has_google_oauth']}")
        print(f"  Has Microsoft OAuth: {row_dict['has_microsoft_oauth']}")
        print(f"  Active: {row_dict['is_active']}")
    else:
        print(f"❌ User {user_id} not found!")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    oauth_tokens = check_oauth_tokens()
    check_users_table()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total OAuth connections: {len(oauth_tokens)}")
    print("\nThe Connections tab should display OAuth tokens from")
    print("ai_infrastructure.oauth_tokens, NOT user_platform_credentials")
