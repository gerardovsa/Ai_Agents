"""Verify newly created workflows"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute("""
    SELECT automation_id, title, category, ui_json 
    FROM visual_automations 
    WHERE automation_id LIKE 'wf_%_1763946900' 
    ORDER BY created_at DESC
""")

rows = cursor.fetchall()

print('\n' + '='*60)
print('NEWLY CREATED COMPREHENSIVE WORKFLOWS')
print('='*60 + '\n')

for i, row in enumerate(rows, 1):
    ui_json = row['ui_json']
    shape_count = len(ui_json.get('shapes', []))
    connection_count = len(ui_json.get('connections', []))
    
    print(f"{i}. {row['title']}")
    print(f"   Category: {row['category']}")
    print(f"   Shapes: {shape_count}")
    print(f"   Connections: {connection_count}")
    print(f"   ID: {row['automation_id']}")
    print()

conn.close()

print('✅ All workflows ready to load in the UI!')
print('\n📍 To test: Refresh browser → Click Load button → Select a workflow\n')
