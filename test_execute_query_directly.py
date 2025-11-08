"""Test execute_sqlite_query directly to see what exception it raises"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from utils.database_helpers import execute_sqlite_query, get_sessions_database_path

print("="*100)
print("Testing execute_sqlite_query with the same query from get_threads_details")
print("="*100)

thread_ids = ["2", "3", "4", "6", "8"]

db_path = get_sessions_database_path()
print(f"\nDatabase path: {db_path}")

placeholders = ','.join(['?' for _ in thread_ids])
query = f"""
    SELECT 
        t.id,
        t.thread_slug,
        t.name,
        t.created_at,
        t.updated_at,
        t.synergy_card_id,
        t.location
    FROM threads t
    WHERE t.id IN ({placeholders}) OR t.thread_slug IN ({placeholders})
    ORDER BY t.updated_at DESC
"""

params = thread_ids + thread_ids

print(f"\nQuery:")
print(query)
print(f"\nParams: {params}")

try:
    print("\nExecuting query...")
    threads = execute_sqlite_query(db_path, query, params)
    
    print(f"✅ SUCCESS! Got {len(threads)} threads")
    
    for t in threads:
        print(f"\n  Thread {t['id']}:")
        print(f"    Name: {t['name']}")
        print(f"    Slug: {t['thread_slug']}")
        print(f"    Location: {t['location']}")
        print(f"    Synergy: {t['synergy_card_id']}")
        
except Exception as e:
    print(f"\n❌ ERROR!")
    print(f"  Type: {type(e).__name__}")
    print(f"  Value: {e}")
    print(f"  Str: {str(e)}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*100)
