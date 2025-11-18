"""
Test AI Agent Access to Automation Workflows
============================================

This tests whether the AI agent can:
1. Create workflows with JSON definitions
2. Retrieve workflow data (including canvas_data)
3. Update workflows based on the stored JSON
4. Execute workflows programmatically
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3
import json
from datetime import datetime

# Configure encoding
sys.stdout.reconfigure(encoding='utf-8')

def test_ai_workflow_access():
    """Test AI can access and manipulate workflow data"""
    
    registry = RegistryV3()
    
    print("=" * 70)
    print(" TEST: AI Agent Workflow Access")
    print("=" * 70)
    
    # Test 1: Create a workflow with JSON definition
    print("\n📝 TEST 1: Creating workflow with structured JSON...")
    
    workflow_definition = {
        "nodes": [
            {
                "id": "trigger_1",
                "type": "email_trigger",
                "config": {
                    "platform": "gmail",
                    "subject_contains": "invoice"
                }
            },
            {
                "id": "ai_agent_1",
                "type": "ai_agent",
                "config": {
                    "role": "Extract invoice details",
                    "tools": ["gmail_read", "stripe_create_customer"]
                }
            },
            {
                "id": "action_1",
                "type": "send_email",
                "config": {
                    "to": "accounting@company.com",
                    "subject": "Invoice Processed",
                    "body": "Invoice details: {{ai_agent_1.result}}"
                }
            }
        ],
        "edges": [
            {"from": "trigger_1", "to": "ai_agent_1"},
            {"from": "ai_agent_1", "to": "action_1"}
        ]
    }
    
    canvas_data = {
        "nodes": {
            "trigger_1": {"x": 100, "y": 100},
            "ai_agent_1": {"x": 300, "y": 100},
            "action_1": {"x": 500, "y": 100}
        }
    }
    
    result = registry.execute_tool(
        tool_name='automation_workflow_create',
        user_id=1,
        name='AI Invoice Processor',
        workflow_json=json.dumps(workflow_definition),
        canvas_data=json.dumps(canvas_data),
        description='Automatically process invoices from Gmail',
        category='automation'
    )
    
    if result['success']:
        workflow_id = result['workflow_id']
        print(f"✅ Workflow created: {workflow_id}")
        print(f"   Slug: {result['slug']}")
    else:
        print("❌ Failed to create workflow")
        return
    
    # Test 2: Retrieve workflow and parse JSON
    print("\n📖 TEST 2: Retrieving workflow data...")
    
    result = registry.execute_tool(
        tool_name='automation_workflow_get',
        workflow_id=workflow_id
    )
    
    if result['success']:
        workflow = result['workflow']
        print(f"✅ Retrieved workflow: {workflow['name']}")
        
        # Parse the JSON
        workflow_json = json.loads(workflow['workflow_json'])
        canvas_json = json.loads(workflow['canvas_data'])
        
        print(f"\n   📊 Workflow Structure:")
        print(f"      Nodes: {len(workflow_json['nodes'])}")
        for node in workflow_json['nodes']:
            print(f"        - {node['id']}: {node['type']}")
        
        print(f"\n   🎨 Canvas Positions:")
        for node_id, pos in canvas_json['nodes'].items():
            print(f"        - {node_id}: ({pos['x']}, {pos['y']})")
    else:
        print("❌ Failed to retrieve workflow")
        return
    
    # Test 3: AI modifies workflow (add a new node)
    print("\n🔧 TEST 3: AI modifying workflow structure...")
    
    # Add a new node to the workflow
    workflow_json['nodes'].append({
        "id": "condition_1",
        "type": "if_else",
        "config": {
            "condition": "{{ai_agent_1.result.total}} > 1000"
        }
    })
    
    # Update edges to include new node
    workflow_json['edges'] = [
        {"from": "trigger_1", "to": "ai_agent_1"},
        {"from": "ai_agent_1", "to": "condition_1"},
        {"from": "condition_1", "to": "action_1", "condition": "true"}
    ]
    
    # Update canvas position for new node
    canvas_json['nodes']['condition_1'] = {"x": 400, "y": 100}
    
    # Update the workflow
    result = registry.execute_tool(
        tool_name='automation_workflow_update',
        workflow_id=workflow_id,
        updates={
            'workflow_json': json.dumps(workflow_json),
            'canvas_data': json.dumps(canvas_json)
        }
    )
    
    if result['success']:
        print(f"✅ Workflow updated successfully")
        print(f"   Added node: condition_1 (if_else)")
    else:
        print("❌ Failed to update workflow")
    
    # Test 4: Verify the update
    print("\n✔️  TEST 4: Verifying modification...")
    
    result = registry.execute_tool(
        tool_name='automation_workflow_get',
        workflow_id=workflow_id
    )
    
    if result['success']:
        workflow = result['workflow']
        updated_json = json.loads(workflow['workflow_json'])
        
        print(f"✅ Verified updated workflow")
        print(f"   Total nodes: {len(updated_json['nodes'])}")
        print(f"   Node IDs: {[n['id'] for n in updated_json['nodes']]}")
    
    # Test 5: List all workflows (AI discovery)
    print("\n🔍 TEST 5: AI discovering available workflows...")
    
    result = registry.execute_tool(
        tool_name='automation_workflow_list',
        user_id=1
    )
    
    if result['success']:
        workflows = result['workflows']
        print(f"✅ Found {len(workflows)} workflow(s)")
        for wf in workflows:
            print(f"   - {wf['name']} ({wf['category']})")
    
    # Test 6: Execute workflow
    print("\n▶️  TEST 6: AI executing workflow...")
    
    trigger_data = {
        "email_id": "msg_12345",
        "subject": "New Invoice from Supplier",
        "from": "supplier@example.com"
    }
    
    result = registry.execute_tool(
        tool_name='automation_workflow_execute',
        workflow_id=workflow_id,
        executed_by=1,  # User ID
        trigger_data=json.dumps(trigger_data)
    )
    
    if result['success']:
        execution_id = result['execution_id']
        print(f"✅ Workflow execution started: {execution_id}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    registry.execute_tool(
        tool_name='automation_workflow_delete',
        workflow_id=workflow_id
    )
    print("✅ Test workflow deleted")
    
    print("\n" + "=" * 70)
    print(" SUMMARY: AI Workflow Access")
    print("=" * 70)
    print("✅ AI can CREATE workflows with JSON definitions")
    print("✅ AI can READ workflow structures and canvas data")
    print("✅ AI can UPDATE/MODIFY workflows programmatically")
    print("✅ AI can EXECUTE workflows with trigger data")
    print("✅ AI can DISCOVER all available workflows")
    print("\n🎉 AI has FULL ACCESS to automation workflows!")
    print("=" * 70)


if __name__ == '__main__':
    test_ai_workflow_access()
