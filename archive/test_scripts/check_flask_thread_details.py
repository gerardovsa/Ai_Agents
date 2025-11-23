"""Check what's wrong with /api/threads/details"""
import sqlite3
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

root = Path(__file__).parent
db_path = root / 'data' / 'sessions.db'

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Test the exact query that should be in thread_routes.py
thread_ids = ["1762530418975", "1762531251405", "1762533505022"]

print("="*100)
print("TESTING THREAD DETAILS QUERY DIRECTLY")
print("="*100)

# Build placeholders
placeholders = ', '.join(['?' for _ in thread_ids])

# The query from thread_routes.py (FIXED VERSION)
query = f"""
    SELECT 
        t.id,
        t.thread_slug,
        t.name,
        t.created_at,
        t.updated_at,
        t.synergy_card_id,
        t.location AS agent_id
    FROM threads t
    WHERE t.thread_slug IN ({placeholders})
       OR t.id IN ({placeholders})
"""

print(f"\nQuery:\n{query}")
print(f"\nParameters: {thread_ids + thread_ids}")

try:
    cursor.execute(query, thread_ids + thread_ids)
    rows = cursor.fetchall()
    
    print(f"\n✅ Query executed successfully!")
    print(f"Rows returned: {len(rows)}")
    
    for row in rows:
        print(f"\n  Thread:")
        print(f"    id: {row['id']}")
        print(f"    thread_slug: {row['thread_slug']}")
        print(f"    name: {row['name']}")
        print(f"    created_at: {row['created_at']}")
        print(f"    updated_at: {row['updated_at']}")
        print(f"    synergy_card_id: {row['synergy_card_id']}")
        print(f"    agent_id (location): {row['agent_id']}")
        
except Exception as e:
    print(f"\n❌ Query failed: {e}")
    import traceback
    traceback.print_exc()

conn.close()

print("\n" + "="*100)
print("Now checking what thread_routes.py actually has...")
print("="*100)

# Read the actual file
routes_file = root / 'AI_infrastructure' / 'routes' / 'thread_routes.py'
with open(routes_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_threads_details function
import re
match = re.search(r'@thread_bp\.route\(\'/details\', methods=\[\'POST\'\]\)(.*?)(?=@thread_bp\.route|def [a-z_]+\(|$)', content, re.DOTALL)

if match:
    func_content = match.group(1)
    print("\nFound /details endpoint:")
    
    # Check for the query
    if 't.created_at' in func_content:
        print("  ✅ Uses t.created_at (CORRECT)")
    else:
        print("  ❌ Does NOT use t.created_at (WRONG - still has t.created)")
        
    if 't.updated_at' in func_content:
        print("  ✅ Uses t.updated_at (CORRECT)")
    else:
        print("  ❌ Does NOT use t.updated_at (WRONG - still has t.updated)")
        
    if 'synergy_card_name' in func_content:
        print("  ❌ Still trying to fetch synergy_card_name (WRONG - doesn't exist)")
    else:
        print("  ✅ Does NOT fetch synergy_card_name (CORRECT)")
        
    if 't.location' in func_content:
        print("  ✅ Uses t.location for agent (CORRECT)")
    else:
        print("  ⚠️  Does NOT use t.location (may be using join)")
        
    # Show a snippet of the query
    query_match = re.search(r'query = f?["\']""(.*?)"""', func_content, re.DOTALL)
    if query_match:
        print(f"\nQuery snippet:\n{query_match.group(1)[:500]}...")
else:
    print("\n❌ Could not find /details endpoint in thread_routes.py")

print("\n" + "="*100)
