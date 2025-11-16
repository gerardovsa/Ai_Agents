"""
Test /api/auth/profile and /api/auth/verify endpoints with Supabase

This simulates what the endpoints do without needing JWT tokens
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

# Import database utilities
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection, convert_sql_placeholders, is_using_supabase

print("=" * 80)
print("TESTING AUTH ENDPOINTS WITH SUPABASE")
print("=" * 80)

# Test user (from your browser logs)
test_user_id = 14  # printing@inhouseprint.com.au

print(f"\n1. Testing /api/auth/profile logic for user_id: {test_user_id}")
print("-" * 80)

try:
    # Connect to Supabase
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Query 1: Get password_hash to determine auth platform
    print("\n[Query 1] Get password_hash from users table:")
    query1 = convert_sql_placeholders('SELECT id, email, username, password_hash FROM ai_infrastructure.users WHERE id = ?')
    print(f"  SQL: {query1}")
    cursor.execute(query1, (test_user_id,))
    user_row = cursor.fetchone()
    
    if user_row:
        print(f"  ✅ User found:")
        print(f"     ID: {user_row['id']}")
        print(f"     Email: {user_row['email']}")
        print(f"     Username: {user_row['username']}")
        print(f"     Password Hash: {user_row['password_hash'][:20]}..." if user_row['password_hash'] else "     Password Hash: None")
        
        # Determine auth platform
        auth_platform = None
        password_hash = user_row['password_hash']
        if password_hash == 'oauth_google':
            auth_platform = 'google'
        elif password_hash in ['oauth_microsoft', 'OAUTH_USER_NO_PASSWORD']:
            auth_platform = 'microsoft'
        
        print(f"     Auth Platform: {auth_platform}")
    else:
        print(f"  ❌ User {test_user_id} NOT FOUND")
        exit(1)
    
    # Query 2: Check Google OAuth connection
    print("\n[Query 2] Check Google OAuth tokens:")
    bool_true = True if is_using_supabase() else 1
    now_sql = "NOW()" if is_using_supabase() else "datetime('now')"
    
    query2 = convert_sql_placeholders(f'''
        SELECT COUNT(*) as count 
        FROM ai_infrastructure.oauth_tokens 
        WHERE user_id = ? 
        AND platform = 'google' 
        AND access_token IS NOT NULL
        AND (is_active = ? OR is_active IS NULL)
        AND (expires_at IS NULL OR expires_at > {now_sql})
    ''')
    print(f"  SQL: {query2.replace(chr(10), ' ')[:100]}...")
    cursor.execute(query2, (test_user_id, bool_true))
    result = cursor.fetchone()
    google_oauth_connected = (result['count'] if isinstance(result, dict) else result[0]) > 0 if result else False
    print(f"  ✅ Google OAuth Connected: {google_oauth_connected}")
    
    # Query 3: Check Microsoft OAuth connection
    print("\n[Query 3] Check Microsoft OAuth tokens:")
    query3 = convert_sql_placeholders(f'''
        SELECT COUNT(*) as count 
        FROM ai_infrastructure.oauth_tokens 
        WHERE user_id = ? 
        AND (platform = 'microsoft' OR platform = 'microsoft365')
        AND access_token IS NOT NULL
        AND (is_active = ? OR is_active IS NULL)
        AND (expires_at IS NULL OR expires_at > {now_sql})
    ''')
    print(f"  SQL: {query3.replace(chr(10), ' ')[:100]}...")
    cursor.execute(query3, (test_user_id, bool_true))
    result = cursor.fetchone()
    microsoft_oauth_connected = (result['count'] if isinstance(result, dict) else result[0]) > 0 if result else False
    print(f"  ✅ Microsoft OAuth Connected: {microsoft_oauth_connected}")
    
    # Query 4: Get all OAuth tokens for this user (debug)
    print("\n[Query 4] Get all OAuth tokens for debugging:")
    query4 = convert_sql_placeholders('''
        SELECT id, platform, email, is_active, expires_at, created_at 
        FROM ai_infrastructure.oauth_tokens 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    cursor.execute(query4, (test_user_id,))
    tokens = cursor.fetchall()
    
    if tokens:
        print(f"  ✅ Found {len(tokens)} OAuth tokens:")
        for token in tokens:
            print(f"     - Platform: {token['platform']}, Email: {token['email']}, Active: {token['is_active']}, Expires: {token['expires_at']}")
    else:
        print(f"  ⚠️  No OAuth tokens found for user {test_user_id}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("EXPECTED /api/auth/profile RESPONSE:")
    print("=" * 80)
    print({
        "success": True,
        "profile": {
            "user_id": test_user_id,
            "email": user_row['email'],
            "username": user_row['username'],
            "id": test_user_id,
            "auth_platform": auth_platform,
            "google_oauth_connected": google_oauth_connected,
            "microsoft_oauth_connected": microsoft_oauth_connected
        }
    })
    
    print("\n" + "=" * 80)
    print("✅ ALL QUERIES SUCCESSFUL - Endpoints should work!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
