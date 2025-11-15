import sqlite3
from datetime import datetime

# Create default user in sessions.db
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

print("Creating default user (ID=1)...")

try:
    cursor.execute("""
        INSERT INTO users (id, username, email, role, created_at, last_active, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        'default_user',
        'gerardo@vetsuccessacademy.com',
        'admin',
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        '{}'  # Empty JSON object for metadata
    ))
    
    conn.commit()
    print("✅ Default user created successfully!")
    
    # Verify
    cursor.execute("SELECT id, username, email, metadata FROM users WHERE id = 1")
    user = cursor.fetchone()
    print(f"\nVerified user:")
    print(f"  ID: {user[0]}")
    print(f"  Username: {user[1]}")
    print(f"  Email: {user[2]}")
    print(f"  Metadata: {user[3]}")
    
except sqlite3.IntegrityError as e:
    print(f"⚠️  User already exists or constraint violation: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
