"""Emergency fix for /api/threads/details endpoint"""
import sqlite3
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

# Check what the endpoint should return
root = Path(__file__).parent
sessions_db = root / 'data' / 'sessions.db'

conn = sqlite3.connect(str(sessions_db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get threads with synergy_card_id
cursor.execute("""
    SELECT id, thread_slug, name, created_at, updated_at, synergy_card_id, location
    FROM threads
    WHERE synergy_card_id IS NOT NULL
    LIMIT 5
""")

threads = cursor.fetchall()

print("="*100)
print("THREADS WITH SYNERGY LINKS:")
print("="*100)

for t in threads:
    print(f"\nThread: {t['name']}")
    print(f"  ID: {t['id']}")
    print(f"  Slug: {t['thread_slug']}")
    print(f"  Synergy: {t['synergy_card_id']}")
    print(f"  Location: {t['location']}")
    print(f"  Created: {t['created_at']}")
    print(f"  Updated: {t['updated_at']}")

conn.close()

# Now check the actual endpoint code
print("\n" + "="*100)
print("CHECKING thread_routes.py CODE:")
print("="*100)

routes_file = root / 'AI_infrastructure' / 'routes' / 'thread_routes.py'
with open(routes_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_threads_details function
import re
match = re.search(r"def get_threads_details\(\):(.*?)(?=\ndef [a-z_]+\(|$)", content, re.DOTALL)

if match:
    func = match.group(1)
    
    # Check critical parts
    issues = []
    
    if 'success_response(result)' in func:
        print("✅ Returns success_response(result)")
    else:
        print("❌ Does NOT return success_response(result)")
        issues.append("Missing success_response")
    
    if 'result = []' in func or 'result.append' in func:
        print("✅ Builds result array")
    else:
        print("❌ Does NOT build result array")
        issues.append("No result array")
    
    if 'for thread in threads:' in func:
        print("✅ Iterates over threads")
    else:
        print("❌ Does NOT iterate over threads")
        issues.append("No thread iteration")
    
    # Check what it returns
    return_match = re.search(r'return\s+(\w+)\(', func)
    if return_match:
        print(f"\n🔍 Returns: {return_match.group(0)}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND: {', '.join(issues)}")
    else:
        print("\n✅ Code structure looks correct")
        
    # Show the last 20 lines (where the return should be)
    lines = func.split('\n')
    print(f"\n📄 Last 20 lines of function:")
    for i, line in enumerate(lines[-20:], len(lines)-19):
        print(f"  {i:3}: {line[:100]}")
else:
    print("❌ Could NOT find get_threads_details function!")

print("\n" + "="*100)
