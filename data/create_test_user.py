import sqlite3

conn = sqlite3.connect('sessions.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO users (username, email, name, created_at)
    VALUES (?, ?, ?, datetime('now'))
""", ('test_user', 'test@example.com', 'Test User'))

conn.commit()
user_id = cursor.lastrowid

print(f'Created test user:')
print(f'  ID: {user_id}')
print(f'  Username: test_user')
print(f'  Email: test@example.com')

conn.close()
