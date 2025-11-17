"""
Fix threads.id sequence issue in Supabase
Run this to enable auto-generation of id values
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.master')

# Get connection string from update_render_supabase.py
SUPABASE_DB_URL = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

print("=" * 60)
print("FIX: threads.id Sequence Issue")
print("=" * 60)
print()

try:
    # Connect to Supabase
    print("Connecting to Supabase...")
    conn = psycopg2.connect(SUPABASE_DB_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connected")
    print()
    
    # 1. Check current state
    print("1. Checking current id column definition...")
    cursor.execute("""
        SELECT column_default, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'sessions'
            AND table_name = 'threads'
            AND column_name = 'id'
    """)
    result = cursor.fetchone()
    print(f"   Current default: {result[0]}")
    print(f"   Is nullable: {result[1]}")
    print()
    
    # 2. Get max id
    print("2. Getting max id in use...")
    cursor.execute("SELECT MAX(id), COUNT(*) FROM sessions.threads")
    max_id, total = cursor.fetchone()
    print(f"   Max ID: {max_id}")
    print(f"   Total threads: {total}")
    print()
    
    # 3. Drop existing sequence if exists
    print("3. Dropping existing sequence (if exists)...")
    cursor.execute("DROP SEQUENCE IF EXISTS sessions.threads_id_seq CASCADE")
    print("   Dropped")
    print()
    
    # 4. Create new sequence
    print("4. Creating new sequence...")
    cursor.execute("""
        CREATE SEQUENCE sessions.threads_id_seq
            START WITH 1000
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1
    """)
    print("   Created")
    print()
    
    # 5. Set sequence owner
    print("5. Setting sequence owner...")
    cursor.execute("ALTER SEQUENCE sessions.threads_id_seq OWNED BY sessions.threads.id")
    print("   Owner set")
    print()
    
    # 6. Set sequence start value
    print("6. Setting sequence start value...")
    start_val = (max_id or 0) + 1
    cursor.execute(f"SELECT setval('sessions.threads_id_seq', {start_val}, false)")
    print(f"   Sequence will start at: {start_val}")
    print()
    
    # 7. Set column default
    print("7. Setting id column default...")
    cursor.execute("""
        ALTER TABLE sessions.threads 
            ALTER COLUMN id SET DEFAULT nextval('sessions.threads_id_seq'::regclass)
    """)
    print("   Default set")
    print()
    
    # 8. Verify
    print("8. Verifying fix...")
    cursor.execute("""
        SELECT column_default
        FROM information_schema.columns
        WHERE table_schema = 'sessions'
            AND table_name = 'threads'
            AND column_name = 'id'
    """)
    result = cursor.fetchone()
    print(f"   New default: {result[0]}")
    print()
    
    # 9. Test insert
    print("9. Testing INSERT (will rollback)...")
    cursor.execute("BEGIN")
    cursor.execute("""
        INSERT INTO sessions.threads (
            thread_slug, workspace_id, name, user_id, created_at, updated_at,
            metadata, location, tags
        ) VALUES (
            'TEST_THREAD_999', 1, 'Test Thread', 14, 
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
            '{}', 'prime', '[]'
        )
        RETURNING id, thread_slug, name
    """)
    test_result = cursor.fetchone()
    print(f"   Test INSERT generated ID: {test_result[0]}")
    print(f"   Thread slug: {test_result[1]}")
    print(f"   Thread name: {test_result[2]}")
    cursor.execute("ROLLBACK")
    print("   Rolled back (test only)")
    print()
    
    # Close connection
    conn.close()
    
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print()
    print("The threads.id column now has auto-generation enabled.")
    print("Thread creation should work without errors.")
    print()
    print("Next steps:")
    print("1. Test thread creation in UI")
    print("2. Verify id values are auto-generated")
    print("3. No code changes needed!")
    
except Exception as e:
    print()
    print("=" * 60)
    print("ERROR!")
    print("=" * 60)
    print(f"Failed to fix sequence: {e}")
    print()
    print("You can manually run the SQL in Supabase SQL Editor:")
    print("File: fix_threads_id_sequence.sql")
