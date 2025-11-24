"""Test Google OAuth user creation fix"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

# Test the INSERT RETURNING syntax
conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Test data
test_email = 'test_oauth_fix@example.com'
test_username = 'test_oauth_fix_user'

try:
    # Clean up any existing test user
    cursor.execute(
        'DELETE FROM ai_infrastructure.users WHERE email = %s',
        (test_email,)
    )
    conn.commit()
    print(f"Cleaned up existing test user")
    
    # Test INSERT with RETURNING id
    cursor.execute('''
        INSERT INTO ai_infrastructure.users (username, email, password_hash, role) 
        VALUES (%s, %s, %s, %s)
        RETURNING id
    ''', (test_username, test_email, 'oauth_google', 'user'))
    
    user_id = cursor.fetchone()['id']
    conn.commit()
    
    print(f"SUCCESS: Created user with ID: {user_id}")
    
    # Verify the user was created
    cursor.execute(
        'SELECT id, username, email FROM ai_infrastructure.users WHERE id = %s',
        (user_id,)
    )
    user = cursor.fetchone()
    
    print(f"Verified user:")
    print(f"  ID: {user['id']}")
    print(f"  Username: {user['username']}")
    print(f"  Email: {user['email']}")
    
    # Clean up
    cursor.execute('DELETE FROM ai_infrastructure.users WHERE id = %s', (user_id,))
    conn.commit()
    print(f"\nCleaned up test user")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
