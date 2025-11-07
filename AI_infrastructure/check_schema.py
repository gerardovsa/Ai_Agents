import sqlite3
from pathlib import Path

# Use correct database location in data/ folder (not AI_infrastructure/)
root_dir = Path(__file__).parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'
print(f'🔷 Database path: {db_path}')

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get users table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
result = cursor.fetchone()
if result:
    print("=== USERS TABLE ===")
    print(result[0])
    print()

# Get user_platform_credentials schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_platform_credentials'")
result = cursor.fetchone()
if result:
    print("=== USER_PLATFORM_CREDENTIALS TABLE ===")
    print(result[0])
    print()

# Get user_sessions schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_sessions'")
result = cursor.fetchone()
if result:
    print("=== USER_SESSIONS TABLE ===")
    print(result[0])
    print()

conn.close()
