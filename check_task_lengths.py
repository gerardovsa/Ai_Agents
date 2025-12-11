#!/usr/bin/env python3
"""Check length of task fields"""
import psycopg2

DB_URL = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

print("Checking task field lengths...\n")

for table in ['tasks', 'subtasks']:
    cursor.execute(f"""
        SELECT 
            MAX(LENGTH(task)) as max_length,
            AVG(LENGTH(task)) as avg_length,
            COUNT(*) as total_count,
            COUNT(CASE WHEN LENGTH(task) > 500 THEN 1 END) as over_500
        FROM synergy_sessions.{table}
    """)
    
    max_len, avg_len, total, over_500 = cursor.fetchone()
    
    print(f"{table}:")
    print(f"  Total records: {total}")
    print(f"  Max length: {max_len}")
    print(f"  Avg length: {avg_len:.1f}")
    print(f"  Over 500 chars: {over_500}")
    
    if over_500 > 0:
        print(f"\n  Sample long tasks:")
        cursor.execute(f"""
            SELECT task_id, LEFT(task, 100) as preview, LENGTH(task) as len
            FROM synergy_sessions.{table}
            WHERE LENGTH(task) > 500
            LIMIT 5
        """)
        for task_id, preview, length in cursor.fetchall():
            print(f"    [{task_id}] {length} chars: {preview}...")
    print()

cursor.close()
conn.close()
