"""Check if workflows are visible in UI"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
import json

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# Get the new workflows
cursor.execute("""
    SELECT automation_id, title, slug, ui_json->>'shapes' as shapes_json
    FROM visual_automations 
    WHERE automation_id LIKE 'wf_%_1763946900'
    ORDER BY created_at DESC
""")

rows = cursor.fetchall()

print('\n' + '='*70)
print('NEW WORKFLOWS - UI VISIBILITY CHECK')
print('='*70 + '\n')

for i, row in enumerate(rows, 1):
    shapes = json.loads(row['shapes_json']) if row['shapes_json'] else []
    
    print(f"{i}. {row['title']}")
    print(f"   automation_id: {row['automation_id']}")
    print(f"   slug: {row['slug']}")
    print(f"   shapes: {len(shapes)} shapes")
    
    if len(shapes) > 0:
        print(f"   First shape: {shapes[0].get('text', 'No text')}")
    
    print()

# Now check what the API would return
cursor.execute("""
    SELECT automation_id, slug, title 
    FROM visual_automations 
    WHERE user_id = 1
    ORDER BY created_at DESC
    LIMIT 5
""")

api_rows = cursor.fetchall()

print('='*70)
print('TOP 5 WORKFLOWS IN API ORDER (what UI should see)')
print('='*70 + '\n')

for i, row in enumerate(api_rows, 1):
    print(f"{i}. {row['title']}")
    print(f"   ID: {row['automation_id']}")
    print(f"   Slug: {row['slug']}")
    print()

conn.close()

print('✅ If you refresh browser, these should appear in Load panel!')
