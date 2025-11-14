"""
CRITICAL MIGRATION: Add ALL missing OAuth columns
Generated from OAuth code analysis
"""

import sqlite3
from pathlib import Path

def run_migration():
    """Add all missing columns identified from OAuth code analysis"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print(f"Running OAuth columns migration on {db_path}")
    
    # Get current schema
    cursor.execute("PRAGMA table_info(users)")
    users_cols = {col[1] for col in cursor.fetchall()}
    
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    oauth_cols = {col[1] for col in cursor.fetchall()}
    

    # oauth_tokens table
    if 'password_hash' not in oauth_tokens_cols:
        cursor.execute("ALTER TABLE oauth_tokens ADD COLUMN password_hash TEXT")
        print(f"  Added oauth_tokens.password_hash (TEXT)")
    
    if 'role' not in oauth_tokens_cols:
        cursor.execute("ALTER TABLE oauth_tokens ADD COLUMN role TEXT")
        print(f"  Added oauth_tokens.role (TEXT)")
    
    if 'username' not in oauth_tokens_cols:
        cursor.execute("ALTER TABLE oauth_tokens ADD COLUMN username TEXT")
        print(f"  Added oauth_tokens.username (TEXT)")
    

    # users table
    if 'access_token' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN access_token TEXT")
        print(f"  Added users.access_token (TEXT)")
    
    if 'error_count' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN error_count INTEGER")
        print(f"  Added users.error_count (INTEGER)")
    
    if 'expires_at' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN expires_at TEXT")
        print(f"  Added users.expires_at (TEXT)")
    
    if 'is_valid' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_valid INTEGER")
        print(f"  Added users.is_valid (INTEGER)")
    
    if 'last_error' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_error TEXT")
        print(f"  Added users.last_error (TEXT)")
    
    if 'last_refreshed_at' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_refreshed_at TEXT")
        print(f"  Added users.last_refreshed_at (TEXT)")
    
    if 'platform' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN platform TEXT")
        print(f"  Added users.platform (TEXT)")
    
    if 'profile_name' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_name TEXT")
        print(f"  Added users.profile_name (TEXT)")
    
    if 'refresh_token' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN refresh_token TEXT")
        print(f"  Added users.refresh_token (TEXT)")
    
    if 'updated_at' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")
        print(f"  Added users.updated_at (TEXT)")
    
    if 'user_id' not in users_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN user_id INTEGER")
        print(f"  Added users.user_id (INTEGER)")
    
    conn.commit()
    conn.close()
    print(" Migration complete!")

if __name__ == '__main__':
    run_migration()
