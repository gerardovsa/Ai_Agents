import sys
sys.path.insert(0, 'AI_infrastructure')

from auth.user_auth import UserAuthManager

# Initialize UserAuthManager - this will create tables if they don't exist
auth_manager = UserAuthManager()
print("✅ UserAuthManager initialized")

# Check if gerardo user exists
import sqlite3
conn = sqlite3.connect('ai_infrastructure.db')
cursor = conn.cursor()

try:
    cursor.execute('SELECT user_id, username, email FROM users')
    users = cursor.fetchall()
    print(f"\n📊 Users in database:")
    for user in users:
        print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    # Check if gerardo exists
    gerardo_exists = any(u[2] == 'gerardo@vetsuccessacademy.com' for u in users)
    
    if not gerardo_exists:
        print("\n❌ gerardo@vetsuccessacademy.com not found")
        print("   Creating user...")
        # Register gerardo
        result = auth_manager.register_user(
            username='gerardo',
            email='gerardo@vetsuccessacademy.com',
            password='test123',  # Simple password for testing
            primary_gmail='gerardo@vetsuccessacademy.com',
            role='admin'
        )
        if result['success']:
            print(f"   ✅ Created user ID: {result['user_id']}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    else:
        print(f"\n✅ gerardo@vetsuccessacademy.com exists")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

conn.close()
