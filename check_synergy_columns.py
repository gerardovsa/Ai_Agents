#!/usr/bin/env python3
"""Check actual columns in synergy tables"""
import psycopg2

DB_URL = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

for table in ['milestones', 'tasks', 'subtasks']:
    print(f"\n{'='*60}")
    print(f"Table: synergy_sessions.{table}")
    print('='*60)
    
    cursor.execute(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'synergy_sessions'
        AND table_name = '{table}'
        ORDER BY ordinal_position
    """)
    
    for row in cursor.fetchall():
        col, dtype, maxlen, nullable = row
        length = f"({maxlen})" if maxlen else ""
        null = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"  {col:25} {dtype}{length:15} {null}")

cursor.close()
conn.close()
