"""
Store Google OAuth Credentials in Database

Stores user's Google OAuth token in data/ai_infrastructure.db
for credential injection during tool execution.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

# Database path
db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("STORE GOOGLE OAUTH CREDENTIALS")
print("=" * 80)
print()

# User credentials
user_id = 1  # Assuming user_id = 1 (can check users table)
platform = 'google'
email = 'gerardo@vetsuccessacademy.com'
access_token = 'ya29.A0ATi6K2tWoiuIKk4-fUrHC9t7cQN9JjDZOMkQUqRPsrNqOia-FEuU3ilfX3sMYfpz7fV97aO0kulGZ7eJW-IQrW_fEyBlApc5y9IpStFhML1tiy74xKhM4-5OkQQsFMyPURC77DQn7799TCVvk-Xc7fN6nDtl2P-eJe_v5DRlFANGXsHZT1XqiY2c4eGKawyna015-iyH86Mreg-nUHqG7uTiBeTkHB5G91ESskR5NaLCRT8JfOlvAB6Y_YZR1egzMRdM32FK3j7RRgybSXbuKRboeh1HCwaCgYKASwSARESFQHGX2MizZ5N3sk7NQIYMADKefncig0293'

# Scopes
scopes = [
    'openid',
    'email', 
    'profile',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/tasks'
]

# Token expiry (OAuth tokens typically last 1 hour from issuance)
# Since we don't know when it was issued, set expiry to 1 hour from now
token_expiry = (datetime.now() + timedelta(hours=1)).isoformat()

# Credentials JSON
credentials_json = json.dumps({
    'access_token': access_token,
    'token_expiry': token_expiry,
    'scopes': scopes
})

print(f"Database: {db_path}")
print(f"User ID: {user_id}")
print(f"Platform: {platform}")
print(f"Email: {email}")
print(f"Scopes: {len(scopes)} scopes")
print()

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='user_platform_credentials'
""")

if not cursor.fetchone():
    print("⚠️  Table 'user_platform_credentials' does not exist!")
    print("Creating table...")
    
    cursor.execute("""
        CREATE TABLE user_platform_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            email TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TEXT,
            credentials_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, platform, email)
        )
    """)
    print("✅ Table created!")
print()

# Check if credentials already exist
cursor.execute("""
    SELECT id, created_at, updated_at 
    FROM user_platform_credentials
    WHERE user_id = ? AND platform = ? AND email = ?
""", (user_id, platform, email))

existing = cursor.fetchone()

if existing:
    print(f"📝 Updating existing credentials (ID: {existing[0]})")
    print(f"   Created: {existing[1]}")
    print(f"   Last Updated: {existing[2]}")
    
    cursor.execute("""
        UPDATE user_platform_credentials
        SET access_token = ?,
            token_expiry = ?,
            credentials_json = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND platform = ? AND email = ?
    """, (access_token, token_expiry, credentials_json, user_id, platform, email))
    
    print("✅ Credentials updated!")
else:
    print("✨ Inserting new credentials...")
    
    cursor.execute("""
        INSERT INTO user_platform_credentials 
        (user_id, platform, email, access_token, token_expiry, credentials_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, platform, email, access_token, token_expiry, credentials_json))
    
    print("✅ Credentials stored!")

conn.commit()

# Verify storage
cursor.execute("""
    SELECT id, user_id, platform, email, 
           substr(access_token, 1, 20) || '...' as token_preview,
           token_expiry, created_at, updated_at
    FROM user_platform_credentials
    WHERE user_id = ? AND platform = ? AND email = ?
""", (user_id, platform, email))

row = cursor.fetchone()

print()
print("=" * 80)
print("VERIFICATION")
print("=" * 80)
print(f"ID: {row[0]}")
print(f"User ID: {row[1]}")
print(f"Platform: {row[2]}")
print(f"Email: {row[3]}")
print(f"Token: {row[4]}")
print(f"Expiry: {row[5]}")
print(f"Created: {row[6]}")
print(f"Updated: {row[7]}")

conn.close()

print()
print("=" * 80)
print("✅ CREDENTIALS STORED SUCCESSFULLY!")
print("=" * 80)
print()
print("Next steps:")
print("1. Run the tool execution test again")
print("2. Credential injector will load these credentials")
print("3. Google tools will authenticate with your token")
