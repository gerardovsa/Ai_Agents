"""
Direct migration execution - Add message_source column
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    print("=" * 80)
    print("Adding message_source column to sessions.messages")
    print("=" * 80)
    
    # Step 1: Add column
    print("\n[1/5] Adding message_source column...")
    try:
        execute_query("""
            ALTER TABLE sessions.messages 
            ADD COLUMN IF NOT EXISTS message_source VARCHAR(50) DEFAULT 'user_input'
        """, fetch_mode=None)
        print("✅ Column added")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Step 2: Add index
    print("\n[2/5] Creating index...")
    try:
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_messages_source 
            ON sessions.messages(message_source)
        """, fetch_mode=None)
        print("✅ Index created")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Step 3: Add constraint
    print("\n[3/5] Adding check constraint...")
    try:
        execute_query("""
            ALTER TABLE sessions.messages 
            ADD CONSTRAINT messages_source_check 
            CHECK (message_source IN ('user_input', 'tool_result', 'assistant_output'))
        """, fetch_mode=None)
        print("✅ Constraint added")
    except Exception as e:
        if "already exists" in str(e):
            print("✅ Constraint already exists")
        else:
            print(f"⚠️ Error: {e}")
    
    # Step 4: Backfill assistant messages
    print("\n[4/5] Backfilling assistant messages...")
    try:
        result = execute_query("""
            UPDATE sessions.messages 
            SET message_source = 'assistant_output'
            WHERE role = 'assistant' 
              AND message_source = 'user_input'
        """, fetch_mode=None)
        print("✅ Assistant messages updated")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Step 5: Backfill tool_result messages
    print("\n[5/5] Backfilling tool_result messages...")
    try:
        result = execute_query("""
            UPDATE sessions.messages 
            SET message_source = 'tool_result'
            WHERE role = 'user' 
              AND content::text LIKE '%"type":"tool_result"%'
              AND message_source = 'user_input'
        """, fetch_mode=None)
        print("✅ Tool result messages updated")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION: Message source distribution")
    print("=" * 80)
    
    try:
        result = execute_query("""
            SELECT message_source, COUNT(*) as count 
            FROM sessions.messages 
            GROUP BY message_source
            ORDER BY count DESC
        """, fetch_mode='all')
        
        print("\n📊 Distribution:")
        total = 0
        for row in result:
            count = row[1]
            total += count
            print(f"  {row[0]}: {count:,} messages")
        print(f"\n  TOTAL: {total:,} messages")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n⚠️ Verification failed: {e}")

if __name__ == '__main__':
    run_migration()
