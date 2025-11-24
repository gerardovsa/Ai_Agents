"""Check what's stored in visual_automations table"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
import json

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute("SELECT automation_id, title, ui_json FROM visual_automations ORDER BY created_at DESC")
rows = cursor.fetchall()

print('\n=== VISUAL AUTOMATIONS DATA ===\n')
for row in rows:
    automation_id = row['automation_id']
    title = row['title']
    ui_json = row['ui_json']
    
    print(f'ID: {automation_id}')
    print(f'Title: {title}')
    print(f'ui_json type: {type(ui_json)}')
    
    if isinstance(ui_json, dict):
        shapes_count = len(ui_json.get("shapes", []))
        connections_count = len(ui_json.get("connections", []))
        print(f'shapes count: {shapes_count}')
        print(f'connections count: {connections_count}')
        
        if shapes_count > 0:
            print(f'✅ HAS SHAPES - Can render on canvas')
            print(f'Preview: {json.dumps(ui_json, indent=2)[:300]}')
        else:
            print(f'❌ EMPTY - No shapes to render')
    else:
        print(f'ui_json: {ui_json}')
    
    print('---\n')

conn.close()
