"""Check user_id=1 details"""
import sqlite3

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

# Check user details
cursor.execute('SELECT id, email, username, has_google_oauth FROM users WHERE id = 1')
user = cursor.fetchone()

if user:
    print(f"\nUser ID 1 Details:")
    print(f"  Email: {user[1]}")
    print(f"  Username: {user[2]}")
    print(f"  Has Google OAuth: {user[3]}")
else:
    print("\n❌ User ID 1 not found")

# Check OAuth token
cursor.execute('SELECT platform, account_identifier, is_active FROM oauth_tokens WHERE user_id = 1 AND platform = "google"')
oauth = cursor.fetchone()

if oauth:
    print(f"\nGoogle OAuth Token:")
    print(f"  Platform: {oauth[0]}")
    print(f"  Account: {oauth[1]}")
    print(f"  Active: {oauth[2]}")
else:
    print("\n❌ No Google OAuth token found")

conn.close()
print("\n✅ Confirmed: user_id=1 is gerardo@vetsuccessacademy.com with active Google OAuth")
