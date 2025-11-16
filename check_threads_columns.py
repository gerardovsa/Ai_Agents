"""
Check if workflow_slug and other columns exist in sessions.threads table
"""

import os
from dotenv import load_dotenv
load_dotenv('.env')

import psycopg2

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

conn = psycopg2.connect(SUPABASE_DB_URL)
cursor = conn.cursor()

print("=" * 80)
print("CHECKING sessions.threads TABLE COLUMNS")
print("=" * 80)

# Get all columns
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = 'sessions' 
    AND table_name = 'threads'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()

print(f"\nFound {len(columns)} columns in sessions.threads:\n")
for col in columns:
    print(f"  - {col[0]:<30} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL':<10} {col[3] or ''}")

# Check for specific columns mentioned in error
required_cols = ['workflow_slug', 'workflow_title', 'internal_doc_slug', 'internal_doc_title']
existing_cols = [col[0] for col in columns]

print("\n" + "=" * 80)
print("CHECKING REQUIRED COLUMNS")
print("=" * 80)

for col in required_cols:
    if col in existing_cols:
        print(f"  ✅ {col} - EXISTS")
    else:
        print(f"  ❌ {col} - MISSING")

conn.close()
