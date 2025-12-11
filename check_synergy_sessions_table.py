import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Use Supabase pooler connection
conn = psycopg2.connect(os.getenv('SUPABASE_DB_URL_POOLER'))
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name, data_type, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_schema = 'synergy_sessions' 
    AND table_name = 'synergy_sessions' 
    ORDER BY ordinal_position
""")

print("synergy_sessions table columns:")
print("-" * 80)
for row in cursor.fetchall():
    col_name, data_type, max_len = row
    if max_len:
        print(f"{col_name:30} {data_type}({max_len})")
    else:
        print(f"{col_name:30} {data_type}")

cursor.close()
conn.close()
