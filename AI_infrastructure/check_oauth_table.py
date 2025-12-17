import psycopg2
import os

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Check if oauth_states table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'oauth_states'
    )
""")
exists = cur.fetchone()[0]

print(f"✅ oauth_states table exists: {exists}")

if not exists:
    print("❌ Table is missing - this is why OAuth fails!")
    print("Creating table now...")
    
    # Create the table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_infrastructure.oauth_states (
            state TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            return_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    """)
    
    # Create index
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_oauth_states_state 
        ON ai_infrastructure.oauth_states(state, platform, expires_at)
    """)
    
    conn.commit()
    print("✅ oauth_states table created!")
else:
    # Check if there are any states
    cur.execute("SELECT COUNT(*) FROM ai_infrastructure.oauth_states")
    count = cur.fetchone()[0]
    print(f"   Currently stored states: {count}")
    
    # Show recent states
    cur.execute("""
        SELECT state, platform, created_at, expires_at 
        FROM ai_infrastructure.oauth_states 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    rows = cur.fetchall()
    if rows:
        print("\n   Recent states:")
        for row in rows:
            print(f"   - {row[1]}: {row[0][:20]}... (expires: {row[3]})")

cur.close()
conn.close()
