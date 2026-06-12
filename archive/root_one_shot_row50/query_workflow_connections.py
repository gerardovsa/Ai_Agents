"""
Query Visual Automation Workflows to Analyze Connection Data Structure
=======================================================================
This script queries the Supabase visual_automations table to examine
how connections/arrows are stored in the ui_json field.

Purpose: Debug why arrows don't render when loading stored workflows
"""

import sys
import json
from pathlib import Path

# Add path for shared imports
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection

def analyze_workflow_connections():
    """Query and analyze connection data structure in stored workflows"""
    print("\n" + "="*80)
    print("VISUAL AUTOMATION WORKFLOW CONNECTION ANALYSIS")
    print("="*80 + "\n")
    
    try:
        # Get database connection
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query visual automations with non-null ui_json
        query = """
            SELECT 
                slug,
                title,
                description,
                ui_json,
                created_at,
                updated_at
            FROM visual_automations
            WHERE ui_json IS NOT NULL
            ORDER BY updated_at DESC
            LIMIT 10
        """
        
        print("Executing query...")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ No visual automations found with ui_json data")
            return
        
        print(f"✅ Found {len(rows)} visual automations with UI data\n")
        print("-"*80 + "\n")
        
        # Analyze each workflow
        for i, row in enumerate(rows, 1):
            # Handle both dict and tuple results
            if isinstance(row, dict):
                slug = row['slug']
                title = row['title']
                description = row['description']
                ui_json = row['ui_json']
            else:
                slug = row[0]
                title = row[1]
                description = row[2]
                ui_json = row[3]
            
            print(f"\n{'='*80}")
            print(f"WORKFLOW {i}: {title}")
            print(f"{'='*80}")
            print(f"Slug: {slug}")
            print(f"Description: {description}")
            
            # Parse ui_json
            try:
                if isinstance(ui_json, str):
                    ui_data = json.loads(ui_json)
                else:
                    ui_data = ui_json
                
                # Extract shapes
                shapes = ui_data.get('shapes', [])
                connections = ui_data.get('connections', [])
                
                print(f"\n📊 SHAPES: {len(shapes)} total")
                if shapes:
                    print("\nShape IDs:")
                    for shape in shapes:
                        shape_id = shape.get('id', 'NO_ID')
                        shape_type = shape.get('type', 'unknown')
                        shape_text = shape.get('text', '')
                        print(f"  - {shape_id} ({shape_type}): {shape_text}")
                
                print(f"\n🔗 CONNECTIONS: {len(connections)} total")
                if connections:
                    print("\nConnection Structure Analysis:")
                    for j, conn in enumerate(connections, 1):
                        print(f"\n  Connection {j}:")
                        print(f"    Raw data: {json.dumps(conn, indent=6)}")
                        
                        # Check for different possible field names
                        conn_id = conn.get('id', 'NO_ID')
                        from_field = conn.get('from') or conn.get('source') or conn.get('fromId')
                        to_field = conn.get('to') or conn.get('target') or conn.get('toId')
                        
                        print(f"\n    Parsed fields:")
                        print(f"      ID: {conn_id}")
                        print(f"      FROM: {from_field}")
                        print(f"      TO: {to_field}")
                        
                        # Verify shape IDs exist
                        from_exists = any(s.get('id') == from_field for s in shapes)
                        to_exists = any(s.get('id') == to_field for s in shapes)
                        
                        print(f"\n    Validation:")
                        print(f"      FROM shape exists: {'✅ YES' if from_exists else '❌ NO'}")
                        print(f"      TO shape exists: {'✅ YES' if to_exists else '❌ NO'}")
                else:
                    print("  ⚠️ NO CONNECTIONS - This workflow has no arrows defined")
                
                # Check for other ui_json fields
                other_fields = [k for k in ui_data.keys() if k not in ['shapes', 'connections']]
                if other_fields:
                    print(f"\n📋 OTHER UI_JSON FIELDS: {', '.join(other_fields)}")
                
            except json.JSONDecodeError as e:
                print(f"❌ ERROR parsing ui_json: {e}")
                print(f"Raw ui_json: {ui_json}")
            
            print("\n" + "-"*80)
        
        # Summary
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)
        
        total_workflows = len(rows)
        workflows_with_connections = 0
        total_connections = 0
        
        for row in rows:
            # Handle both dict and tuple results
            if isinstance(row, dict):
                ui_json = row['ui_json']
            else:
                ui_json = row[3]
            
            if isinstance(ui_json, str):
                ui_data = json.loads(ui_json)
            else:
                ui_data = ui_json
            
            connections = ui_data.get('connections', [])
            if connections:
                workflows_with_connections += 1
                total_connections += len(connections)
        
        print(f"\nTotal workflows analyzed: {total_workflows}")
        print(f"Workflows with connections: {workflows_with_connections}")
        print(f"Total connections across all workflows: {total_connections}")
        
        if total_connections > 0:
            print("\n✅ Connections data exists - analyze structure above to debug rendering")
        else:
            print("\n⚠️ NO CONNECTIONS found in any workflow - arrows may not have been saved")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_workflow_connections()
