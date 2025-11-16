"""
Add missing workflow and internal doc columns to sessions.threads table
"""

import os
from dotenv import load_dotenv
load_dotenv('.env')

import psycopg2

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

conn = psycopg2.connect(SUPABASE_DB_URL)
cursor = conn.cursor()

print("Adding missing columns to sessions.threads...")

# Add workflow_slug column
try:
    cursor.execute("""
        ALTER TABLE sessions.threads 
        ADD COLUMN IF NOT EXISTS workflow_slug TEXT
    """)
    conn.commit()
    print("  ✅ workflow_slug added")
except Exception as e:
    print(f"  ⚠️  workflow_slug: {e}")
    conn.rollback()

# Add workflow_title column
try:
    cursor.execute("""
        ALTER TABLE sessions.threads 
        ADD COLUMN IF NOT EXISTS workflow_title TEXT
    """)
    conn.commit()
    print("  ✅ workflow_title added")
except Exception as e:
    print(f"  ⚠️  workflow_title: {e}")
    conn.rollback()

# Add internal_doc_slug column
try:
    cursor.execute("""
        ALTER TABLE sessions.threads 
        ADD COLUMN IF NOT EXISTS internal_doc_slug TEXT
    """)
    conn.commit()
    print("  ✅ internal_doc_slug added")
except Exception as e:
    print(f"  ⚠️  internal_doc_slug: {e}")
    conn.rollback()

# Add internal_doc_title column
try:
    cursor.execute("""
        ALTER TABLE sessions.threads 
        ADD COLUMN IF NOT EXISTS internal_doc_title TEXT
    """)
    conn.commit()
    print("  ✅ internal_doc_title added")
except Exception as e:
    print(f"  ⚠️  internal_doc_title: {e}")
    conn.rollback()

# Verify columns were added
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'sessions' 
    AND table_name = 'threads'
    AND column_name IN ('workflow_slug', 'workflow_title', 'internal_doc_slug', 'internal_doc_title')
    ORDER BY column_name
""")

added_cols = cursor.fetchall()
print(f"\n✅ Verified {len(added_cols)} columns added:")
for col in added_cols:
    print(f"  - {col[0]}")

conn.close()
print("\n✅ COMPLETE: All workflow columns added to sessions.threads")
