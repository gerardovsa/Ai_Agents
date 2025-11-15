"""Create User ID 1 as system admin for Render tools"""
import sqlite3
from pathlib import Path
import hashlib

root = Path(__file__).parent
db = root / 'data' / 'ai_infrastructure.db'

conn = sqlite3.connect(str(db))
cur = conn.cursor()

# Check if user 1 already exists
cur.execute("SELECT id FROM users WHERE id = 1")
existing = cur.fetchone()

if existing:
    print("✅ User ID 1 already exists")
else:
    # Create a simple password hash (you should change this password later)
    password = "admin123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        # Insert user with ID 1
        cur.execute("""
            INSERT INTO users (
                id, username, email, password_hash, role, 
                is_primary, is_active, allowed_tools, allowed_agents,
                data_access_scope, usage_limit_daily
            ) VALUES (
                1, 'system_admin', 'system@ai-agents.local', ?, 'owner',
                1, 1, NULL, NULL,
                'all', 999999
            )
        """, (password_hash,))
        
        conn.commit()
        print("✅ Created User ID 1 successfully!")
        print("\nDetails:")
        print("  ID: 1")
        print("  Username: system_admin")
        print("  Email: system@ai-agents.local")
        print("  Password: admin123")
        print("  Role: owner (full access)")
        print("  Tools: NULL (all tools allowed)")
        print("  Agents: NULL (all agents allowed)")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        conn.rollback()

conn.close()
