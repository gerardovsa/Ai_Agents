"""Direct Supabase query to understand the data"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
from psycopg2.extras import RealDictCursor
import json

conn = get_database_connection('sessions')
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "="*70)
print("SUPABASE DATABASE INSPECTION - User ID 14")
print("="*70)

# 1. Check total threads
cursor.execute("SELECT COUNT(*) as total FROM sessions.threads WHERE user_id = 14")
total = cursor.fetchone()
print(f"\n1. TOTAL THREADS: {total['total']}")

# 2. Get sample thread data
cursor.execute("""
    SELECT id, thread_slug, name, location, metadata, created_at, updated_at 
    FROM sessions.threads 
    WHERE user_id = 14 
    ORDER BY updated_at DESC 
    LIMIT 3
""")
threads = cursor.fetchall()
print(f"\n2. SAMPLE THREADS (most recent 3):")
for t in threads:
    print(f"\n   Thread: {t['thread_slug']}")
    print(f"   Name: {t['name']}")
    print(f"   Location: {t['location']}")
    print(f"   Created: {t['created_at']}")
    print(f"   Updated: {t['updated_at']}")
    if t['metadata']:
        meta = json.loads(t['metadata']) if isinstance(t['metadata'], str) else t['metadata']
        print(f"   Metadata: {meta}")

# 3. Check messages for first thread
if threads:
    first_thread_id = threads[0]['id']
    cursor.execute("""
        SELECT id, role, content, metadata, created_at
        FROM sessions.messages
        WHERE thread_id = %s
        ORDER BY created_at ASC
        LIMIT 5
    """, (first_thread_id,))
    messages = cursor.fetchall()
    
    print(f"\n3. MESSAGES IN FIRST THREAD ({threads[0]['thread_slug']}):")
    print(f"   Total messages in sample: {len(messages)}")
    
    for i, m in enumerate(messages, 1):
        print(f"\n   Message {i}:")
        print(f"     Role: {m['role']}")
        print(f"     Created: {m['created_at']}")
        
        # Parse content
        content = json.loads(m['content']) if isinstance(m['content'], str) else m['content']
        if isinstance(content, list):
            types = [b.get('type', 'unknown') for b in content]
            print(f"     Content blocks: {types}")
            
            # Show first block details
            if content:
                first_block = content[0]
                print(f"     First block type: {first_block.get('type')}")
                if first_block.get('type') == 'text':
                    text = first_block.get('text', '')
                    print(f"     Text preview: {text[:80]}...")
        else:
            print(f"     Content type: {type(content)}")
            print(f"     Content preview: {str(content)[:80]}...")
        
        # Parse metadata
        if m['metadata']:
            meta = json.loads(m['metadata']) if isinstance(m['metadata'], str) else m['metadata']
            print(f"     Metadata: {meta}")

# 4. Test the EXACT COUNT query from thread_routes.py
print(f"\n4. TESTING THE COUNT QUERY:")
cursor.execute("""
    SELECT 
        t.thread_slug,
        t.name,
        COUNT(m.id) as total_messages,
        COUNT(CASE 
            WHEN m.role = 'user' AND (
                m.metadata IS NULL 
                OR m.metadata::jsonb->>'tool_results' IS NULL 
                OR m.metadata::jsonb->>'tool_results' != 'true'
            ) THEN 1
            WHEN m.role = 'assistant' AND m.content::jsonb::text LIKE '%"type": "text"%' THEN 1
            ELSE NULL
        END) as filtered_count
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON t.id = m.thread_id
    WHERE t.user_id = 14
    GROUP BY t.id, t.thread_slug, t.name
    ORDER BY t.updated_at DESC
    LIMIT 5
""")
results = cursor.fetchall()

print(f"\n   Results:")
for r in results:
    print(f"   {r['thread_slug']}: {r['name']}")
    print(f"     Total messages: {r['total_messages']}")
    print(f"     Filtered count: {r['filtered_count']}")

# 5. Check if RealDictCursor is working
print(f"\n5. CURSOR TYPE CHECK:")
print(f"   Cursor class: {type(cursor)}")
print(f"   Row type: {type(results[0]) if results else 'No results'}")
print(f"   Row has .keys()?: {hasattr(results[0], 'keys') if results else 'N/A'}")
if results:
    print(f"   Row keys: {list(results[0].keys())}")

conn.close()
print("\n" + "="*70)
print("INSPECTION COMPLETE")
print("="*70 + "\n")
