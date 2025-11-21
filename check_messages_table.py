"""Check sessions.messages table structure"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('sessions')
cursor = conn.cursor()

# Check if messages table exists
print("Checking sessions.messages table...")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'sessions' AND table_name = 'messages'
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()

if not columns:
    print("❌ sessions.messages table does NOT exist!")
    print("Creating sessions.messages table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions.messages (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}',
            FOREIGN KEY (thread_id) REFERENCES sessions.threads(thread_slug) ON DELETE CASCADE
        )
    """)
    
    # Create index on thread_id for fast lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_thread_id 
        ON sessions.messages(thread_id)
    """)
    
    conn.commit()
    print("✅ sessions.messages table created with indexes")
else:
    print(f"✅ sessions.messages table exists with {len(columns)} columns:")
    for col in columns:
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        print(f"  - {col['column_name']}: {col['data_type']} {nullable}")

# Check constraints
cursor.execute("""
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'sessions.messages'::regclass
""")
constraints = cursor.fetchall()
print(f"\nConstraints: {len(constraints)}")
for c in constraints:
    print(f"  {c['conname']} ({c['contype']}): {c['pg_get_constraintdef']}")

conn.close()
