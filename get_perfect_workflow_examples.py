"""
Query Perfect Workflow Examples from Database
==============================================
Retrieves well-structured workflows to use as templates/examples
"""

import sys
import json
from pathlib import Path

# Add path for shared imports
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection

def get_perfect_workflows():
    """Query workflows with proper structure"""
    print("\n" + "="*100)
    print("PERFECT WORKFLOW EXAMPLES - REFERENCE TEMPLATES")
    print("="*100 + "\n")
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Query workflows with non-empty ui_json and string IDs
    query = """
        SELECT 
            automation_id,
            slug,
            title,
            description,
            category,
            ui_json,
            execution_json,
            status,
            schedule_cron,
            timezone
        FROM visual_automations
        WHERE ui_json IS NOT NULL 
        AND ui_json::text != '{}'
        AND ui_json::text LIKE '%"trigger_%'
        ORDER BY updated_at DESC
        LIMIT 5
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("No perfect workflows found")
        return
    
    print(f"Found {len(rows)} well-structured workflows\n")
    print("="*100 + "\n")
    
    for idx, row in enumerate(rows, 1):
        if isinstance(row, dict):
            automation_id = row['automation_id']
            slug = row['slug']
            title = row['title']
            description = row['description']
            category = row['category']
            ui_json = row['ui_json']
            execution_json = row['execution_json']
            status = row['status']
            schedule_cron = row['schedule_cron']
            timezone = row['timezone']
        else:
            automation_id = row[0]
            slug = row[1]
            title = row[2]
            description = row[3]
            category = row[4]
            ui_json = row[5]
            execution_json = row[6]
            status = row[7]
            schedule_cron = row[8]
            timezone = row[9]
        
        print(f"{'='*100}")
        print(f"EXAMPLE {idx}: {title}")
        print(f"{'='*100}\n")
        
        print(f"Automation ID: {automation_id}")
        print(f"Slug: {slug}")
        print(f"Category: {category}")
        print(f"Status: {status}")
        print(f"Description: {description}\n")
        
        # Parse ui_json
        if isinstance(ui_json, str):
            ui_data = json.loads(ui_json)
        else:
            ui_data = ui_json
        
        shapes = ui_data.get('shapes', [])
        connections = ui_data.get('connections', [])
        
        print(f"VISUAL STRUCTURE:")
        print(f"  Shapes: {len(shapes)}")
        print(f"  Connections: {len(connections)}\n")
        
        # Show shape structure
        if shapes:
            print(f"  Shape IDs (showing first 5):")
            for shape in shapes[:5]:
                shape_id = shape.get('id')
                shape_type = shape.get('type')
                text = shape.get('text', shape.get('label', 'No label'))
                print(f"    - {shape_id} ({shape_type}): {text[:40]}")
            if len(shapes) > 5:
                print(f"    ... and {len(shapes) - 5} more shapes")
        
        # Show connection structure
        if connections:
            print(f"\n  Connections (showing first 5):")
            for conn in connections[:5]:
                from_id = conn.get('from')
                to_id = conn.get('to')
                label = conn.get('label', '')
                label_str = f" [{label}]" if label else ""
                print(f"    - {from_id} → {to_id}{label_str}")
            if len(connections) > 5:
                print(f"    ... and {len(connections) - 5} more connections")
        
        # Parse execution_json
        if isinstance(execution_json, str):
            exec_data = json.loads(execution_json) if execution_json and execution_json != '{}' else {}
        else:
            exec_data = execution_json if execution_json else {}
        
        actions = exec_data.get('actions', [])
        trigger = exec_data.get('trigger', {})
        
        print(f"\nAUTOMATION LOGIC:")
        if not actions and not trigger:
            print(f"  Status: Empty (draft workflow)")
        else:
            print(f"  Actions: {len(actions)}")
            if trigger:
                print(f"  Trigger Type: {trigger.get('type', 'Not set')}")
                if trigger.get('schedule_cron'):
                    print(f"  Schedule: {trigger.get('schedule_cron')} ({trigger.get('timezone', 'UTC')})")
        
        # Export as JSON template
        print(f"\nJSON STRUCTURE (formatted for copying):")
        print("-"*100)
        
        template = {
            "automation_id": automation_id,
            "title": title,
            "description": description,
            "category": category,
            "ui_json": ui_data,
            "execution_json": exec_data,
            "status": status
        }
        
        print(json.dumps(template, indent=2, ensure_ascii=False))
        print("-"*100 + "\n\n")
    
    cursor.close()
    conn.close()
    
    # Create reference guide
    print("\n" + "="*100)
    print("STRUCTURE PATTERNS - BEST PRACTICES")
    print("="*100 + "\n")
    
    print("✅ CORRECT ID FORMAT:")
    print('  - Use string IDs: "trigger_1", "action_1", "action_2"')
    print('  - NOT numeric: 1, 2, 3')
    print('  - NOT string numbers: "1", "2", "3"\n')
    
    print("✅ SHAPE STRUCTURE:")
    print('  {')
    print('    "id": "trigger_1",')
    print('    "type": "trigger",')
    print('    "x": 120,')
    print('    "y": 80,')
    print('    "width": 240,')
    print('    "height": 100,')
    print('    "text": "Schedule Trigger\\nDaily 9am",  // OR use "label"')
    print('    "color": "#10B981"')
    print('  }\n')
    
    print("✅ CONNECTION STRUCTURE:")
    print('  {')
    print('    "from": "trigger_1",  // Must match shape ID exactly')
    print('    "to": "action_1",     // Must match shape ID exactly')
    print('    "label": "optional label"  // Optional')
    print('  }\n')
    
    print("✅ EXECUTION JSON STRUCTURE:")
    print('  {')
    print('    "trigger": {')
    print('      "type": "schedule",')
    print('      "schedule_cron": "0 9 * * *",')
    print('      "timezone": "Australia/Sydney"')
    print('    },')
    print('    "actions": [')
    print('      {')
    print('        "id": "action_1",')
    print('        "tool": "gmail_list_messages",')
    print('        "parameters": {')
    print('          "max_results": 50,')
    print('          "query": "is:unread"')
    print('        }')
    print('      }')
    print('    ]')
    print('  }\n')
    
    print("="*100)
    print("VALIDATION CHECKLIST")
    print("="*100 + "\n")
    
    print("Before saving a workflow, verify:")
    print("  [ ] ui_json is NOT empty (not '{}')")
    print("  [ ] All shape IDs are strings (not numbers)")
    print("  [ ] All connection from/to match existing shape IDs")
    print("  [ ] Shapes have 'text' or 'label' field")
    print("  [ ] execution_json has 'trigger' object")
    print("  [ ] execution_json has 'actions' array")
    print("  [ ] Cron schedule has 5 parts (if scheduled)")
    print("  [ ] Timezone is set (if scheduled)\n")

if __name__ == "__main__":
    get_perfect_workflows()
