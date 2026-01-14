from shared.database_utils import get_sessions_connection

conn = get_sessions_connection()
cursor = conn.cursor()

sql = """
    SELECT thread_slug, location 
    FROM sessions.threads 
    WHERE user_id = %s 
      AND location IS NOT NULL 
      AND location != 'prime'
    ORDER BY updated_at DESC
"""

cursor.execute(sql, (14,))
results = cursor.fetchall()

print(f"Found {len(results)} assignments:")
for row in results:
    print(f"  {row['location']}: {row['thread_slug']}")

conn.close()
