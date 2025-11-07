"""
Sync printing@inhouseprint.com.au user from ai_infrastructure.db to sessions.db
"""

import sqlite3
from pathlib import Path
from datetime import datetime

root_dir = Path(__file__).parent

# Database paths
ai_infra_db = root_dir / 'data' / 'ai_infrastructure.db'
sessions_db = root_dir / 'data' / 'sessions.db'

print("=" * 80)
print("SYNCING PRINTING USER FROM AI_INFRASTRUCTURE.DB TO SESSIONS.DB")
print("=" * 80)

# Step 1: Get user from ai_infrastructure.db
print("\n[1] Fetching user from ai_infrastructure.db...")
conn_infra = sqlite3.connect(str(ai_infra_db))
cursor_infra = conn_infra.cursor()

cursor_infra.execute("""
    SELECT id, username, email, role, created_at 
    FROM users 
    WHERE email = 'printing@inhouseprint.com.au'
""")
user = cursor_infra.fetchone()

if not user:
    print("  ERROR: printing@inhouseprint.com.au not found in ai_infrastructure.db!")
    conn_infra.close()
    exit(1)

user_id_infra, username, email, role, created_at = user
print(f"  Found user:")
print(f"    ID: {user_id_infra}")
print(f"    Username: {username}")
print(f"    Email: {email}")
print(f"    Role: {role}")
print(f"    Created: {created_at}")

conn_infra.close()

# Step 2: Check if user exists in sessions.db
print("\n[2] Checking sessions.db...")
conn_sessions = sqlite3.connect(str(sessions_db))
cursor_sessions = conn_sessions.cursor()

# Get sessions.db schema
cursor_sessions.execute("PRAGMA table_info(users)")
cols = cursor_sessions.fetchall()
print(f"  sessions.db users table columns: {[c[1] for c in cols]}")

cursor_sessions.execute("""
    SELECT id, username, email 
    FROM users 
    WHERE email = 'printing@inhouseprint.com.au'
""")
existing_user = cursor_sessions.fetchone()

if existing_user:
    print(f"  User already exists in sessions.db:")
    print(f"    ID: {existing_user[0]}")
    print(f"    Username: {existing_user[1]}")
    print(f"    Email: {existing_user[2]}")
    print("\n  No sync needed - user already exists!")
    conn_sessions.close()
    exit(0)

print("  User NOT found in sessions.db - will create")

# Step 3: Insert user into sessions.db
print("\n[3] Creating user in sessions.db...")

# Use same ID from ai_infrastructure.db for consistency
try:
    cursor_sessions.execute("""
        INSERT INTO users (id, username, email, role, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id_infra,  # Use same ID
        username,
        email,
        role or 'user',
        created_at or datetime.now().isoformat(),
        '{}'  # Empty metadata JSON
    ))
    
    conn_sessions.commit()
    print(f"  SUCCESS: User created in sessions.db!")
    print(f"    ID: {user_id_infra}")
    print(f"    Username: {username}")
    print(f"    Email: {email}")
    
except sqlite3.IntegrityError as e:
    print(f"  ERROR: Could not create user - {e}")
    print("  Trying with auto-increment ID instead...")
    
    cursor_sessions.execute("""
        INSERT INTO users (username, email, role, created_at, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        email,
        role or 'user',
        created_at or datetime.now().isoformat(),
        '{}'
    ))
    
    conn_sessions.commit()
    new_id = cursor_sessions.lastrowid
    print(f"  SUCCESS: User created with new ID: {new_id}")

# Step 4: Verify creation
print("\n[4] Verifying user in sessions.db...")
cursor_sessions.execute("""
    SELECT id, username, email, role, created_at
    FROM users 
    WHERE email = 'printing@inhouseprint.com.au'
""")
verified_user = cursor_sessions.fetchone()

if verified_user:
    print(f"  VERIFIED: User exists in sessions.db:")
    print(f"    ID: {verified_user[0]}")
    print(f"    Username: {verified_user[1]}")
    print(f"    Email: {verified_user[2]}")
    print(f"    Role: {verified_user[3]}")
    print(f"    Created: {verified_user[4]}")
else:
    print("  ERROR: User not found after creation!")

conn_sessions.close()

print("\n" + "=" * 80)
print("SYNC COMPLETE")
print("=" * 80)
print("\nNEXT STEPS:")
print("1. Verify user can now load threads:")
print("   curl 'http://localhost:5001/api/threads/list?user_id=14'")
print("")
print("2. Test in browser:")
print("   - Refresh business-ai-platform-v2.html")
print("   - Login as printing@inhouseprint.com.au")
print("   - Check if threads load")
print("")
print("3. If threads still don't load, check:")
print("   - What user_id is frontend sending?")
print("   - Browser console for errors")
print("   - Network tab for API calls")
