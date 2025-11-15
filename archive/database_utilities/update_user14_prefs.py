"""Update user 14 preferences with correct values"""
import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'data', 'ai_infrastructure.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update user 14
cursor.execute("""
    UPDATE user_preferences 
    SET nickname = 'G',
        communication_style = 'casual',
        auth_platform = 'microsoft'
    WHERE user_id = 14
""")

conn.commit()

# Verify update
cursor.execute("""
    SELECT user_id, nickname, communication_style, auth_platform, preferred_tools
    FROM user_preferences 
    WHERE user_id = 14
""")

row = cursor.fetchone()
if row:
    print(f"✅ Updated User {row[0]}:")
    print(f"   Nickname: {row[1] or '(not set)'}")
    print(f"   Style: {row[2]}")
    print(f"   Platform: {row[3]}")
    print(f"   Preferred Tools: {row[4][:100] if row[4] else '(not set)'}...")
else:
    print("❌ User 14 not found!")

conn.close()
