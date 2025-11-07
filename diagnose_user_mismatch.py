import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("CHECKING ALL USERS AND THEIR MICROSOFT CREDENTIALS")
print("=" * 80)

# Get all users
cursor.execute("SELECT id, username, email FROM users ORDER BY id")
users = cursor.fetchall()
print(f"\nAll users:")
for user in users:
    print(f"  User ID {user[0]}: {user[1]} ({user[2]})")

print("\n" + "=" * 80)
print("MICROSOFT OAUTH TOKENS BY USER_ID")
print("=" * 80)

# Get all Microsoft tokens
cursor.execute("""
    SELECT user_id, email, is_active, expires_at, updated_at
    FROM oauth_tokens
    WHERE platform = 'microsoft'
    ORDER BY user_id
""")
tokens = cursor.fetchall()

for token in tokens:
    user_id, email, is_active, expires_at, updated_at = token
    print(f"\nUser ID {user_id}:")
    print(f"  Email: {email}")
    print(f"  Active: {is_active}")
    print(f"  Expires: {expires_at}")
    print(f"  Updated: {updated_at}")
    
    # Check if expired
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            now_dt = datetime.now()
            if expires_dt < now_dt:
                print(f"  Status: EXPIRED (expired {(now_dt - expires_dt).days} days ago)")
            else:
                hours_left = (expires_dt - now_dt).total_seconds() / 3600
                print(f"  Status: VALID (expires in {hours_left:.1f} hours)")
        except:
            print(f"  Status: UNKNOWN (cannot parse date)")

print("\n" + "=" * 80)
print("CHATM AUTHENTICATION")
print("=" * 80)

# Check which user_id CHATM uses
chatm_email = "Gerardo@minivetguide.onmicrosoft.com"
cursor.execute("SELECT id FROM users WHERE email = ?", (chatm_email,))
chatm_user = cursor.fetchone()

if chatm_user:
    chatm_user_id = chatm_user[0]
    print(f"\nCHATM authenticates as: User ID {chatm_user_id}")
    
    # Check if this user has credentials
    cursor.execute("""
        SELECT COUNT(*) FROM oauth_tokens
        WHERE user_id = ? AND platform = 'microsoft' AND is_active = 1
    """, (chatm_user_id,))
    cred_count = cursor.fetchone()[0]
    
    if cred_count > 0:
        print(f"  Credentials: FOUND ({cred_count} active tokens)")
    else:
        print(f"  Credentials: NOT FOUND")
        print(f"\n  PROBLEM: CHATM uses user_id={chatm_user_id} but credentials are under different user_id!")

conn.close()

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
