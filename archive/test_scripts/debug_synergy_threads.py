"""
Debug Synergy Thread Integration Issues
"""
import sqlite3
import json
from shared.database_utils import convert_sql_placeholders

print("\n" + "="*80)
print("SYNERGY THREAD INTEGRATION DEBUG")
print("="*80)

# Check synergy_sessions with thread_ids
print("\n1. Synergy Sessions with thread_ids:")
print("-" * 80)
conn = sqlite3.connect('data/synergy_sessions.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

sql, params = convert_sql_placeholders("""
    SELECT session_id, title, thread_ids 
    FROM synergy_sessions 
    WHERE thread_ids IS NOT NULL AND thread_ids != '[]'
    LIMIT 5
""")

synergy_sessions = cursor.fetchall()
print(f"Found {len(synergy_sessions)} sessions with thread_ids\n")

for session in synergy_sessions:
    print(f"Session: {session['session_id'][:50]}")
    print(f"  Title: {session['title']}")
    thread_ids = json.loads(session['thread_ids'])
    print(f"  Thread IDs: {thread_ids}")
    print()

conn.close()

# Check if those threads exist
print("\n2. Checking if threads exist in sessions.db:")
print("-" * 80)

conn = sqlite3.connect('data/sessions.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get first session's thread_ids for testing
if synergy_sessions:
    test_thread_ids = json.loads(synergy_sessions[0]['thread_ids'])
    print(f"Testing with thread IDs: {test_thread_ids}\n")
    
    for thread_id in test_thread_ids[:3]:  # Test first 3
        cursor.execute("""
            SELECT id, thread_slug, name, synergy_card_id 
            FROM threads 
            WHERE id = ? OR thread_slug = ?
        """, (thread_id, thread_id))


cursor.execute(sql, params)
        
        thread = cursor.fetchone()
        if thread:
            print(f"✅ Thread found: {thread_id}")
            print(f"   ID: {thread['id']}")
            print(f"   Slug: {thread['thread_slug']}")
            print(f"   Name: {thread['name']}")
            print(f"   Synergy: {thread['synergy_card_id']}")
        else:
            print(f"❌ Thread NOT found: {thread_id}")
        print()

conn.close()

# Check thread_assignments table
print("\n3. Checking thread_assignments:")
print("-" * 80)

conn = sqlite3.connect('data/ai_infrastructure.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

if synergy_sessions:
    test_thread_ids = json.loads(synergy_sessions[0]['thread_ids'])
    
    for thread_id in test_thread_ids[:3]:
        sql, params = convert_sql_placeholders("""
            SELECT thread_id, agent_id, agent_name 
            FROM thread_assignments 
            WHERE thread_id = ?
        """, (thread_id,))

        cursor.execute(sql, params)
        
        assignment = cursor.fetchone()
        if assignment:
            print(f"✅ Assignment found: {thread_id}")
            print(f"   Agent ID: {assignment['agent_id']}")
            print(f"   Agent Name: {assignment['agent_name']}")
        else:
            print(f"❌ No assignment for: {thread_id}")
        print()

conn.close()

# Test the /api/threads/details endpoint logic
print("\n4. Testing endpoint logic:")
print("-" * 80)

if synergy_sessions:
    thread_ids = json.loads(synergy_sessions[0]['thread_ids'])
    print(f"Thread IDs to fetch: {thread_ids}\n")
    
    # Build query like the endpoint does
    placeholders = ','.join(['?' for _ in thread_ids])
    query = f"""
        SELECT 
            t.id,
            t.thread_slug,
            t.name,
            t.created,
            t.updated,
            t.synergy_card_id,
            t.synergy_card_name,
            ta.agent_id,
            ta.agent_name
        FROM threads t
        LEFT JOIN thread_assignments ta ON t.id = ta.thread_id
        WHERE t.id IN ({placeholders})
        ORDER BY t.updated DESC
    """
    
    print(f"Query: {query[:200]}...")
    print(f"Params: {thread_ids}\n")
    
    try:
        # sessions.db doesn't have thread_assignments - that's the issue!
        conn = sqlite3.connect('data/sessions.db')
        cursor = conn.cursor()
        cursor.execute(query, thread_ids)
        results = cursor.fetchall()
        print(f"✅ Query executed successfully")
        print(f"   Results: {len(results)} rows")
        conn.close()
    except Exception as e:
        print(f"❌ Query failed: {e}")

print("\n" + "="*80)
print("DEBUG COMPLETE")
print("="*80 + "\n")
