"""
Check Google OAuth Scopes in Database
======================================
Diagnostic script to verify what scopes are granted for Google OAuth tokens
"""

import sqlite3
from pathlib import Path

# Database path
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f"🔍 Checking Google OAuth scopes in: {db_path}")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query oauth_tokens table
cursor.execute("""
    SELECT id, user_id, platform, account_identifier, account_name,
           scope, is_valid, is_active, created_at, updated_at
    FROM oauth_tokens
    WHERE platform = 'google'
    ORDER BY user_id, updated_at DESC
""")

rows = cursor.fetchall()

if not rows:
    print("❌ No Google OAuth tokens found in database")
    print("\nUser needs to authorize Google account:")
    print("  1. Go to: http://localhost:5001")
    print("  2. Navigate to: Account Linking → Link Google Account")
    print("  3. Grant all requested permissions")
    conn.close()
    exit(1)

print(f"\n✅ Found {len(rows)} Google OAuth token(s)\n")

# Required scopes for full functionality
REQUIRED_SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',  # ← CRITICAL for Docs creation
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/tasks'
]

for idx, row in enumerate(rows, 1):
    print(f"Token #{idx}:")
    print(f"  User ID: {row['user_id']}")
    print(f"  Account: {row['account_identifier']} ({row['account_name']})")
    print(f"  Valid: {bool(row['is_valid'])}")
    print(f"  Active: {bool(row['is_active'])}")
    print(f"  Created: {row['created_at']}")
    print(f"  Updated: {row['updated_at']}")
    
    # Parse granted scopes
    scope_string = row['scope'] or ''
    granted_scopes = [s.strip() for s in scope_string.split() if s.strip()]
    
    print(f"\n  Granted Scopes ({len(granted_scopes)}):")
    
    # Check each required scope
    missing_scopes = []
    for required in REQUIRED_SCOPES:
        if required in granted_scopes:
            print(f"    ✅ {required}")
        else:
            print(f"    ❌ {required} (MISSING!)")
            missing_scopes.append(required)
    
    # Show extra scopes (if any)
    extra_scopes = [s for s in granted_scopes if s not in REQUIRED_SCOPES]
    if extra_scopes:
        print(f"\n  Extra Scopes ({len(extra_scopes)}):")
        for scope in extra_scopes:
            print(f"    ℹ️  {scope}")
    
    if missing_scopes:
        print(f"\n  ⚠️  WARNING: {len(missing_scopes)} required scope(s) missing!")
        print(f"  🔧 USER ACTION REQUIRED:")
        print(f"     1. Go to: http://localhost:5001")
        print(f"     2. Navigate to: Account Linking → Unlink Google Account")
        print(f"     3. Navigate to: Account Linking → Link Google Account")
        print(f"     4. Grant ALL requested permissions (including Google Docs)")
        print(f"\n  Missing scopes:")
        for scope in missing_scopes:
            scope_name = scope.split('/')[-1]
            print(f"     - {scope_name}")
    else:
        print(f"\n  ✅ All required scopes granted!")
    
    print("\n" + "-" * 80 + "\n")

conn.close()

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)

# Re-query to get summary
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN is_valid = 1 AND is_active = 1 THEN 1 ELSE 0 END) as active
    FROM oauth_tokens
    WHERE platform = 'google'
""")
row = cursor.fetchone()
conn.close()

total, active = row[0], row[1]

print(f"Total Google OAuth tokens: {total}")
print(f"Active tokens: {active}")

if active == 0:
    print("\n❌ No active Google OAuth tokens!")
    print("Action: User must link Google account with proper permissions")
elif active < total:
    print(f"\n⚠️  {total - active} inactive token(s) found")
    print("Action: Consider cleaning up inactive tokens")
else:
    print("\n✅ All tokens are active")

print("\n" + "=" * 80)
