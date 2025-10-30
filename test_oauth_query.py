#!/usr/bin/env python3
"""Test OAuth credential detection for user 1 (admin)"""

import sqlite3
import os

# Connect to database
db_path = os.path.join(os.path.dirname(__file__), 'AI_infrastructure', 'ai_infrastructure.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("="*60)
print("TESTING OAUTH CREDENTIAL DETECTION FOR USER 1 (admin)")
print("="*60)

# Check user details
cursor.execute('SELECT id, username, email, password_hash FROM users WHERE id = 1')
user = cursor.fetchone()
if user:
    print(f"\n✅ User found:")
    print(f"   ID: {user['id']}")
    print(f"   Username: {user['username']}")
    print(f"   Email: {user['email']}")
    print(f"   Password Hash: {user['password_hash'][:20]}... (local account)")
else:
    print("\n❌ User 1 not found!")
    exit(1)

# Test 1: Check with credential_type (from auth_routes.py fix)
print(f"\n{'='*60}")
print("TEST 1: Query WITH credential_type='oauth' (auth_routes.py)")
print(f"{'='*60}")
cursor.execute('''
    SELECT COUNT(*) as count 
    FROM user_platform_credentials 
    WHERE user_id = ? 
    AND platform = 'google' 
    AND credential_type = 'oauth'
    AND credential_key = 'access_token'
    AND is_active = 1
''', (1,))
result = cursor.fetchone()
count_with_type = result['count']
print(f"Result: {count_with_type} tokens found")
if count_with_type > 0:
    print("✅ Google OAuth credentials detected!")
else:
    print("❌ No Google OAuth credentials found")

# Test 2: Check WITHOUT credential_type (from agent_routes.py)
print(f"\n{'='*60}")
print("TEST 2: Query WITHOUT credential_type (agent_routes.py)")
print(f"{'='*60}")
cursor.execute('''
    SELECT COUNT(*) as count 
    FROM user_platform_credentials 
    WHERE user_id = ? 
    AND platform = 'google' 
    AND credential_key = 'access_token'
    AND is_active = 1
''', (1,))
result = cursor.fetchone()
count_without_type = result['count']
print(f"Result: {count_without_type} tokens found")
if count_without_type > 0:
    print("✅ Google OAuth credentials detected!")
else:
    print("❌ No Google OAuth credentials found")

# Show actual credentials
print(f"\n{'='*60}")
print("ACTUAL CREDENTIALS IN DATABASE FOR USER 1:")
print(f"{'='*60}")
cursor.execute('''
    SELECT credential_key, credential_type, platform, 
           LENGTH(credential_value) as value_length, is_active
    FROM user_platform_credentials 
    WHERE user_id = 1 
    AND platform = 'google'
    ORDER BY credential_key
''')
credentials = cursor.fetchall()
if credentials:
    for cred in credentials:
        print(f"✅ {cred['credential_key']}: ")
        print(f"   Platform: {cred['platform']}")
        print(f"   Type: {cred['credential_type']}")
        print(f"   Value Length: {cred['value_length']} chars")
        print(f"   Active: {'Yes' if cred['is_active'] else 'No'}")
else:
    print("❌ No Google credentials found for user 1")

conn.close()

print(f"\n{'='*60}")
print("CONCLUSION:")
print(f"{'='*60}")
if count_with_type > 0 and count_without_type > 0:
    print("✅ BOTH queries work - OAuth will be detected correctly!")
elif count_with_type > 0:
    print("⚠️ Only query WITH credential_type works (auth_routes.py OK, agent_routes.py might fail)")
elif count_without_type > 0:
    print("⚠️ Only query WITHOUT credential_type works (agent_routes.py OK, auth_routes.py might fail)")
else:
    print("❌ Neither query works - OAuth detection will fail!")
