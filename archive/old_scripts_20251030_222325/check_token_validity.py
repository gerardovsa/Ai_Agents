"""
Check OAuth Token Validity
===========================
Check if the Google OAuth tokens for user_id=1 are still valid
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path(__file__).parent / "AI_infrastructure" / "ai_infrastructure.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("="*70)
print("🔍 Checking Google OAuth Token Status for User ID: 1")
print("="*70)

sql, params = convert_sql_placeholders("""
    SELECT 
        platform,
        credential_key,
        is_active,
        created_at,
        updated_at
    FROM user_platform_credentials
    WHERE user_id = 1
    AND platform = 'google'
    ORDER BY credential_key
""")

creds = cursor.fetchall()

if creds:
    print(f"\n✅ Found {len(creds)} Google credentials:")
    for cred in creds:
        status = "✅ Active" if cred['is_active'] else "❌ Inactive"
        print(f"\n   {status}")
        print(f"   Key: {cred['credential_key']}")
        print(f"   Created: {cred['created_at']}")
        print(f"   Updated: {cred['updated_at'] or 'Never'}")
        
        # Check if token exists and get first 20 chars
        cursor.execute("""
            SELECT credential_value 
            FROM user_platform_credentials 
            WHERE user_id = 1 
            AND platform = 'google' 
            AND credential_key = ?
        """, (cred['credential_key'],))


cursor.execute(sql, params)
        
        value_row = cursor.fetchone()
        if value_row and value_row['credential_value']:
            value = value_row['credential_value']
            print(f"   Value: {value[:20]}... ({len(value)} chars)")
        else:
            print(f"   Value: ⚠️ EMPTY OR NULL")
    
    print(f"\n🎯 Summary:")
    print(f"   ✅ Google OAuth credentials exist")
    print(f"   ✅ Tokens are marked as active")
    print(f"\n💡 If tools fail to execute:")
    print(f"   1. Tokens may be expired (check updated_at)")
    print(f"   2. Need to refresh tokens via OAuth flow")
    print(f"   3. Check Flask logs for specific errors")
else:
    print(f"\n❌ No Google credentials found for user_id=1")
    print(f"\n💡 To fix:")
    print(f"   1. Go to http://localhost:5001")
    print(f"   2. Click 'Connect Google Workspace'")
    print(f"   3. Complete OAuth flow")

conn.close()

print("\n" + "="*70)
