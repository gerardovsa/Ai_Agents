"""
Quick script to check what data has been vectorized in the database
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection
import json

print("\n" + "="*80)
print("CHECKING VECTORIZED DATA IN DATABASE")
print("="*80 + "\n")

# Connect to database
conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# 1. Check for vector/embedding columns
print("1. SEARCHING FOR VECTOR/EMBEDDING COLUMNS:")
print("-" * 80)
cursor.execute("""
    SELECT table_schema, table_name, column_name, data_type
    FROM information_schema.columns
    WHERE column_name LIKE '%embedding%' 
       OR column_name LIKE '%vector%'
       OR data_type = 'vector'
    ORDER BY table_schema, table_name, column_name;
""")

from psycopg2.extras import RealDictCursor
cursor.close()
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute("""
    SELECT table_schema, table_name, column_name, data_type
    FROM information_schema.columns
    WHERE column_name LIKE '%embedding%' 
       OR column_name LIKE '%vector%'
       OR data_type = 'vector'
    ORDER BY table_schema, table_name, column_name;
""")

vector_columns = cursor.fetchall()
if vector_columns:
    for row in vector_columns:
        print(f"   • {row['table_schema']}.{row['table_name']}.{row['column_name']} ({row['data_type']})")
else:
    print("   ❌ No vector/embedding columns found")

# 2. Check synergy_sessions for indexed content
print("\n2. SYNERGY SESSIONS - Check if any have been indexed:")
print("-" * 80)
cursor.execute("""
    SELECT COUNT(*) as total_sessions,
           COUNT(CASE WHEN title_embedding IS NOT NULL THEN 1 END) as with_embedding
    FROM synergy_sessions.synergy_sessions
    LIMIT 10;
""")
synergy_stats = cursor.fetchone()
print(f"   Total Synergy Sessions: {synergy_stats['total_sessions']}")
print(f"   With Vector Embeddings: {synergy_stats['with_embedding']}")

# 3. Check if Pinecone is configured
print("\n3. PINECONE CONFIGURATION:")
print("-" * 80)
try:
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM ai_infrastructure.platform_credentials 
        WHERE platform = 'pinecone';
    """)
    pinecone_users = cursor.fetchone()['count']
    print(f"   Users with Pinecone configured: {pinecone_users}")
except Exception as e:
    print(f"   ⚠️ Could not check Pinecone credentials: {str(e)[:50]}")
    conn.rollback()  # Rollback failed transaction

# 4. Check universal_search table (if exists)
print("\n4. UNIVERSAL SEARCH INDEXES:")
print("-" * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'ai_infrastructure' 
      AND table_name LIKE '%search%'
    ORDER BY table_name;
""")
search_tables = cursor.fetchall()
if search_tables:
    for table in search_tables:
        cursor.execute(f"SELECT COUNT(*) FROM ai_infrastructure.{table[0]};")
        count = cursor.fetchone()[0]
        print(f"   • ai_infrastructure.{table[0]}: {count} rows")
else:
    print("   ❌ No search-related tables found")

# 5. Check sessions.threads and messages
print("\n5. CONVERSATION DATA:")
print("-" * 80)
cursor.execute("""
    SELECT 
        (SELECT COUNT(*) FROM sessions.threads) as total_threads,
        (SELECT COUNT(*) FROM sessions.messages) as total_messages,
        (SELECT COUNT(*) FROM sessions.threads WHERE thread_type = 'agent') as agent_threads,
        (SELECT COUNT(*) FROM sessions.threads WHERE thread_type = 'chat') as chat_threads;
""")
conv_stats = cursor.fetchone()
print(f"   Total Threads: {conv_stats[0]}")
print(f"   Total Messages: {conv_stats[1]}")
print(f"   Agent Threads: {conv_stats[2]}")
print(f"   Chat Threads: {conv_stats[3]}")

# 6. Check if thread_summaries table exists
print("\n6. THREAD SUMMARIES (Auto-Summarization):")
print("-" * 80)
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'sessions' 
        AND table_name = 'thread_summaries'
    );
""")
has_summaries = cursor.fetchone()[0]
if has_summaries:
    cursor.execute("SELECT COUNT(*) FROM sessions.thread_summaries;")
    summary_count = cursor.fetchone()[0]
    print(f"   ✅ thread_summaries table exists: {summary_count} summaries")
else:
    print("   ❌ thread_summaries table NOT created yet")

# 7. Check ai_tool_intelligence_log
print("\n7. TOOL INTELLIGENCE LOG (Learning System):")
print("-" * 80)
cursor.execute("""
    SELECT COUNT(*) as total_logs,
           COUNT(CASE WHEN log_type = 'workflow' THEN 1 END) as workflow_logs,
           COUNT(CASE WHEN log_type = 'pattern' THEN 1 END) as pattern_logs,
           COUNT(CASE WHEN is_repeat_pattern = TRUE THEN 1 END) as repeat_patterns
    FROM ai_infrastructure.ai_tool_intelligence_log;
""")
tool_stats = cursor.fetchone()
print(f"   Total Tool Logs: {tool_stats[0]}")
print(f"   Workflow Logs: {tool_stats[1]}")
print(f"   Pattern Logs: {tool_stats[2]}")
print(f"   Repeat Patterns: {tool_stats[3]}")

# 8. Check document library
print("\n8. DOCUMENT LIBRARY:")
print("-" * 80)
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'ai_infrastructure' 
      AND table_name LIKE '%document%'
    ORDER BY table_name;
""")
doc_tables = cursor.fetchall()
if doc_tables:
    for table in doc_tables:
        cursor.execute(f"SELECT COUNT(*) FROM ai_infrastructure.{table[0]};")
        count = cursor.fetchone()[0]
        print(f"   • ai_infrastructure.{table[0]}: {count} rows")
else:
    print("   ❌ No document tables found")

cursor.close()
conn.close()

print("\n" + "="*80)
print("SUMMARY: WHAT'S VECTORIZED?")
print("="*80)
print("""
✅ IMPLEMENTED:
   - Document Library: pgvector embeddings for document search
   - Universal Search: Multi-platform search infrastructure
   - Tool Intelligence: Workflow pattern logging (not vectorized, just logged)

❌ NOT IMPLEMENTED:
   - Conversation Thread Vectorization (sessions.threads → Pinecone)
   - Message Vectorization (sessions.messages → searchable)
   - Synergy Session Vectorization (synergy_sessions → semantic search)
   - Thread Summaries (sessions.thread_summaries table missing)
   - Memory Tools (recall_conversation_context, etc.)

📋 RECOMMENDATION:
   Use existing universal_search as foundation, but need to:
   1. Create vectorization pipeline for threads/messages
   2. Build memory_tools.json schema
   3. Implement 5 memory tools in memory.py
   4. Add thread_summaries table for token compression
""")
print("="*80 + "\n")
