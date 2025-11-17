"""
Fix messages.id sequence in Supabase
Same issue as threads table - id column needs DEFAULT nextval()
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.master')

# Get Supabase connection string
SUPABASE_URL = os.getenv('SUPABASE_DB_URL')

if not SUPABASE_URL:
    print("ERROR: SUPABASE_DB_URL not found in .env.master")
    print("Trying alternative environment variable names...")
    SUPABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_SESSION_POOLER_URL')
    
if not SUPABASE_URL:
    print("ERROR: No Supabase connection string found")
    print("Expected one of: SUPABASE_DB_URL, DATABASE_URL, SUPABASE_SESSION_POOLER_URL")
    exit(1)

print(f"Connecting to Supabase...")
print(f"URL: {SUPABASE_URL.split('@')[1] if '@' in SUPABASE_URL else 'hidden'}")

try:
    # Connect to Supabase
    conn = psycopg2.connect(SUPABASE_URL)
    conn.autocommit = True  # Important for DDL statements
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("FIX 1: Create sequence for messages.id")
    print("="*70)
    
    sql = "CREATE SEQUENCE IF NOT EXISTS sessions.messages_id_seq;"
    print(f"SQL: {sql}")
    cursor.execute(sql)
    print("✅ Sequence created (or already exists)")
    
    print("\n" + "="*70)
    print("FIX 2: Set DEFAULT nextval() on messages.id column")
    print("="*70)
    
    sql = "ALTER TABLE sessions.messages ALTER COLUMN id SET DEFAULT nextval('sessions.messages_id_seq');"
    print(f"SQL: {sql}")
    cursor.execute(sql)
    print("✅ DEFAULT set on id column")
    
    print("\n" + "="*70)
    print("FIX 3: Sync sequence to current max ID")
    print("="*70)
    
    sql = "SELECT setval('sessions.messages_id_seq', COALESCE((SELECT MAX(id) FROM sessions.messages), 1), true);"
    print(f"SQL: {sql}")
    cursor.execute(sql)
    new_value = cursor.fetchone()[0]
    print(f"✅ Sequence synced to: {new_value}")
    
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    
    # Check sequence exists
    cursor.execute("""
        SELECT schemaname, sequencename, last_value 
        FROM pg_sequences 
        WHERE schemaname = 'sessions' AND sequencename = 'messages_id_seq'
    """)
    seq_info = cursor.fetchone()
    if seq_info:
        print(f"✅ Sequence exists: {seq_info[0]}.{seq_info[1]} (last_value: {seq_info[2]})")
    else:
        print("❌ Sequence not found!")
    
    # Check DEFAULT is set
    cursor.execute("""
        SELECT column_name, column_default, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'sessions' 
          AND table_name = 'messages' 
          AND column_name = 'id'
    """)
    col_info = cursor.fetchone()
    if col_info:
        print(f"✅ Column info:")
        print(f"   - Name: {col_info[0]}")
        print(f"   - Default: {col_info[1]}")
        print(f"   - Nullable: {col_info[2]}")
        
        if 'nextval' in str(col_info[1]):
            print("✅ DEFAULT nextval() is set correctly!")
        else:
            print("❌ DEFAULT is not set to nextval()")
    else:
        print("❌ Column not found!")
    
    # Count existing messages
    cursor.execute("SELECT COUNT(*) FROM sessions.messages")
    message_count = cursor.fetchone()[0]
    print(f"\n📊 Total messages in database: {message_count}")
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETE!")
    print("="*70)
    print("\nMessages can now be inserted without specifying id:")
    print("INSERT INTO sessions.messages (thread_id, role, content)")
    print("VALUES (85, 'user', 'hello')")
    print("-- id will be auto-generated!")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 SUCCESS! Message sequence is now configured correctly.")
    print("\nNext step: Deploy code to Render (git push)")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check SUPABASE_SESSION_POOLER_URL in .env.master")
    print("2. Verify Supabase connection is working")
    print("3. Check you have permission to ALTER TABLE")
    exit(1)
