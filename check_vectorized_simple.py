"""Quick check of vectorized data"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
from psycopg2.extras import RealDictCursor

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("\n=== VECTORIZED DATA CHECK ===\n")

# 1. Vector columns
print("1. VECTOR/EMBEDDING COLUMNS:")
cursor.execute("""
    SELECT table_schema, table_name, column_name
    FROM information_schema.columns
    WHERE column_name LIKE '%embedding%' OR column_name LIKE '%vector%'
    ORDER BY table_schema, table_name;
""")
for row in cursor.fetchall():
    print(f"   {row['table_schema']}.{row['table_name']}.{row['column_name']}")

# 2. Check if populated
print("\n2. WHAT'S BEEN VECTORIZED:")
cursor.execute("SELECT COUNT(*) as count, COUNT(title_embedding) as with_embedding FROM sessions.threads;")
threads = cursor.fetchone()
print(f"   Threads: {threads['count']} total, {threads['with_embedding']} vectorized")

cursor.execute("SELECT COUNT(*) as count, COUNT(content_embedding) as with_embedding FROM sessions.messages;")
messages = cursor.fetchone()
print(f"   Messages: {messages['count']} total, {messages['with_embedding']} vectorized")

cursor.execute("SELECT COUNT(*) as count, COUNT(title_embedding) as with_embedding FROM synergy_sessions.synergy_sessions;")
synergy = cursor.fetchone()
print(f"   Synergy Sessions: {synergy['count']} total, {synergy['with_embedding']} vectorized")

# 3. Check thread_summaries
print("\n3. THREAD SUMMARIES TABLE:")
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'sessions' AND table_name = 'thread_summaries'
    );
""")
exists = cursor.fetchone()['exists']
print(f"   Status: {'EXISTS' if exists else 'NOT CREATED'}")

# 4. Tool intelligence
print("\n4. TOOL INTELLIGENCE LOGS:")
cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.ai_tool_intelligence_log;")
print(f"   Total logs: {cursor.fetchone()['count']}")

cursor.close()
conn.close()

print("\n=== SUMMARY ===")
print("Vector columns EXIST but are NOT populated (0 embeddings)")
print("Need to create vectorization pipeline + memory tools")
print("="*60 + "\n")
