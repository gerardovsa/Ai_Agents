"""Check and add UNIQUE constraint on sessions.threads.thread_slug"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('sessions')
cursor = conn.cursor()

# Check existing constraints
print("Checking existing constraints on sessions.threads...")
cursor.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'sessions.threads'::regclass
""")
constraints = cursor.fetchall()
print(f"Found {len(constraints)} constraints:")
for c in constraints:
    print(f"  {c['conname']} ({c['contype']}): {c['pg_get_constraintdef']}")

# Check if thread_slug has UNIQUE constraint
has_unique = any('thread_slug' in str(c['pg_get_constraintdef']) and c['contype'] == 'u' for c in constraints)

if has_unique:
    print("\n✅ thread_slug already has UNIQUE constraint")
else:
    print("\n❌ thread_slug missing UNIQUE constraint")
    print("Adding UNIQUE constraint on thread_slug...")
    
    try:
        cursor.execute("""
            ALTER TABLE sessions.threads 
            ADD CONSTRAINT threads_thread_slug_unique 
            UNIQUE (thread_slug)
        """)
        conn.commit()
        print("✅ UNIQUE constraint added successfully")
    except Exception as e:
        print(f"❌ Failed to add constraint: {e}")
        conn.rollback()

conn.close()
