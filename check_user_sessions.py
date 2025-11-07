"""
Check user_sessions table structure and find sessions
"""
import sqlite3
import json

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("USER SESSIONS FOR printing@inhouseprint.com.au (user_id: 14)")
print("=" * 80)

# Check user_sessions table structure
cursor.execute("PRAGMA table_info(user_sessions)")
columns = cursor.fetchall()
print("\nuser_sessions table structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get all sessions for user_id 14
cursor.execute("""
    SELECT * FROM user_sessions 
    WHERE user_id = 14 
    ORDER BY created_at DESC
""")
sessions = cursor.fetchall()

if sessions:
    print(f"\n✅ Found {len(sessions)} sessions:\n")
    
    # Get column names
    col_names = [description[0] for description in cursor.description]
    
    for i, session in enumerate(sessions, 1):
        print(f"\n{'='*60}")
        print(f"SESSION {i}")
        print('='*60)
        for col_name, value in zip(col_names, session):
            if col_name == 'session_data' and value:
                try:
                    data = json.loads(value)
                    print(f"{col_name}:")
                    print(f"  Keys: {list(data.keys())}")
                    if 'messages' in data:
                        print(f"  Messages: {len(data.get('messages', []))}")
                except:
                    print(f"{col_name}: {value[:100]}..." if len(str(value)) > 100 else f"{col_name}: {value}")
            else:
                print(f"{col_name}: {value}")
else:
    print("\n⚠️ No sessions found for user_id 14")

# Also check sessions.db with correct structure
print("\n" + "=" * 80)
print("CHECKING sessions.db")
print("=" * 80)

try:
    sess_conn = sqlite3.connect('data/sessions.db')
    sess_cursor = sess_conn.cursor()
    
    # Get table structure
    sess_cursor.execute("PRAGMA table_info(sessions)")
    sess_cols = sess_cursor.fetchall()
    print("\nsessions table structure:")
    for col in sess_cols:
        print(f"  {col[1]} ({col[2]})")
    
    # Get all sessions (no user_id column, so get all)
    sess_cursor.execute("""
        SELECT session_id, created_at, last_accessed, data
        FROM sessions
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    flask_sessions = sess_cursor.fetchall()
    
    if flask_sessions:
        print(f"\n✅ Found {len(flask_sessions)} recent Flask sessions:\n")
        for i, (sess_id, created, accessed, data) in enumerate(flask_sessions, 1):
            print(f"{i}. Session ID: {sess_id}")
            print(f"   Created: {created}")
            print(f"   Last Accessed: {accessed}")
            if data:
                try:
                    import pickle
                    session_data = pickle.loads(data)
                    print(f"   Data keys: {list(session_data.keys())}")
                    if 'user_id' in session_data:
                        print(f"   User ID: {session_data['user_id']}")
                except:
                    print(f"   Data length: {len(data)} bytes")
            print()
    
    sess_conn.close()
except Exception as e:
    print(f"\n❌ Error: {e}")

conn.close()

print("=" * 80)
print("DONE")
print("=" * 80)
