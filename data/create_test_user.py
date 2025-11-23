import sqlite3
from shared.database_utils import convert_sql_placeholders

conn = sqlite3.connect('sessions.db')
cursor = conn.cursor()

sql, params = convert_sql_placeholders("""
    INSERT INTO users (username, email, name, created_at)
    VALUES (?, ?, ?, datetime('now'))
""", ('test_user', 'test@example.com', 'Test User'))


cursor.execute(sql, params)

conn.commit()
user_id = cursor.lastrowid

print(f'Created test user:')
print(f'  ID: {user_id}')
print(f'  Username: test_user')
print(f'  Email: test@example.com')

conn.close()
