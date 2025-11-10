"""Check which database has the users table"""
import sqlite3
from pathlib import Path

data_dir = Path(__file__).parent / 'data'

print("=" * 80)
print("CHECKING USERS TABLE LOCATION")
print("=" * 80)

# Check ai_infrastructure.db
print("\n1. Checking ai_infrastructure.db...")
ai_db = data_dir / 'ai_infrastructure.db'
conn = sqlite3.connect(str(ai_db))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
ai_tables = [row[0] for row in cursor.fetchall()]
print(f"   Tables: {', '.join(ai_tables)}")
print(f"   Has 'users' table: {'users' in ai_tables}")

if 'users' in ai_tables:
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"\n   users table columns ({len(columns)} total):")
    for col in columns:
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        default = f" DEFAULT {col[4]}" if col[4] else ""
        print(f"     - {col[1]} {col[2]} {nullable}{default}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n   users table rows: {count}")

conn.close()

# Check sessions.db
print("\n2. Checking sessions.db...")
sessions_db = data_dir / 'sessions.db'
conn = sqlite3.connect(str(sessions_db))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
session_tables = [row[0] for row in cursor.fetchall()]
print(f"   Tables: {', '.join(session_tables)}")
print(f"   Has 'users' table: {'users' in session_tables}")

if 'users' in session_tables:
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"\n   users table columns ({len(columns)} total):")
    for col in columns:
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        default = f" DEFAULT {col[4]}" if col[4] else ""
        print(f"     - {col[1]} {col[2]} {nullable}{default}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n   users table rows: {count}")

conn.close()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nthread_assignment_routes.py tries to INSERT into users table")
print("Location: ai_infrastructure.db (according to get_db_connection())")
print(f"Result: {'✅ CORRECT' if 'users' in ai_tables else '❌ WRONG - users table not in ai_infrastructure.db'}")
