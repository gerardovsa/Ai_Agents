"""
Test OAuth Status Detection Fix
================================
Tests that OAuth credentials are detected correctly for all account types
"""

import sqlite3
from pathlib import Path

# Database path
base_dir = Path(__file__).parent / 'AI_infrastructure'
db_path = base_dir / 'ai_infrastructure.db'

print("="*70)
print("🧪 Testing OAuth Status Detection Fix")
print("="*70)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Test for user_id = 1 (admin)
user_id = 1

# Fetch user data
cursor.execute('''
    SELECT username, email, password_hash, created_at 
    FROM users 
    WHERE id = ?
''', (user_id,))
user_row = cursor.fetchone()

if user_row:
    user_name = user_row['username']
    user_email = user_row['email']
    user_platform = None
    user_account_type = None
    
    # Detect authentication platform
    if user_row['password_hash'] == 'oauth_google':
        user_platform = 'google'
        user_account_type = 'Google Workspace OAuth'
    elif user_row['password_hash'] == 'oauth_microsoft':
        user_platform = 'microsoft'
        user_account_type = 'Microsoft 365 OAuth'
    else:
        user_account_type = 'Local Account (Username/Password)'
    
    print(f"\n👤 User Profile:")
    print(f"   ID: {user_id}")
    print(f"   Name: {user_name}")
    print(f"   Email: {user_email}")
    print(f"   Account Type: {user_account_type}")
    print(f"   Platform: {user_platform or 'local/traditional'}")
    
    # ✅ NEW FIX: Check OAuth credentials regardless of account type
    print(f"\n🔍 Checking OAuth Credentials (NEW LOGIC)...")
    
    # Check Google OAuth credentials
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM user_platform_credentials 
        WHERE user_id = ? 
        AND platform = 'google' 
        AND credential_key = 'access_token'
        AND is_active = 1
    ''', (user_id,))
    result = cursor.fetchone()
    google_oauth_connected = result['count'] > 0 if result else False
    
    # Check Microsoft OAuth credentials
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM user_platform_credentials 
        WHERE user_id = ? 
        AND (platform = 'microsoft' OR platform = 'microsoft365')
        AND credential_key = 'access_token'
        AND is_active = 1
    ''', (user_id,))
    result = cursor.fetchone()
    microsoft_oauth_connected = result['count'] > 0 if result else False
    
    print(f"\n✅ OAuth Status Detection Results:")
    print(f"   Google OAuth: {google_oauth_connected} {'✅' if google_oauth_connected else '❌'}")
    print(f"   Microsoft OAuth: {microsoft_oauth_connected} {'✅' if microsoft_oauth_connected else '❌'}")
    
    # Verify credentials exist in database
    print(f"\n📊 Credential Details in Database:")
    cursor.execute('''
        SELECT platform, credential_key, is_active, created_at
        FROM user_platform_credentials
        WHERE user_id = ?
        ORDER BY platform, credential_key
    ''', (user_id,))
    
    creds = cursor.fetchall()
    if creds:
        for cred in creds:
            status = "✅ Active" if cred['is_active'] else "❌ Inactive"
            print(f"   {status} - {cred['platform']}/{cred['credential_key']} (created: {cred['created_at']})")
    else:
        print(f"   ⚠️ No credentials found")
    
    # Expected vs Actual
    print(f"\n🎯 Verification:")
    expected_google = len([c for c in creds if c['platform'] == 'google']) > 0
    expected_microsoft = len([c for c in creds if c['platform'] in ('microsoft', 'microsoft365')]) > 0
    
    google_match = google_oauth_connected == expected_google
    microsoft_match = microsoft_oauth_connected == expected_microsoft
    
    print(f"   Google: Expected={expected_google}, Detected={google_oauth_connected} {'✅' if google_match else '❌ MISMATCH'}")
    print(f"   Microsoft: Expected={expected_microsoft}, Detected={microsoft_oauth_connected} {'✅' if microsoft_match else '❌ MISMATCH'}")
    
    if google_match and microsoft_match:
        print(f"\n🎉 SUCCESS! OAuth status detection is working correctly!")
    else:
        print(f"\n⚠️ FAILURE! OAuth status detection has issues!")

conn.close()

print("\n" + "="*70)
print("✅ Test Complete")
print("="*70)
