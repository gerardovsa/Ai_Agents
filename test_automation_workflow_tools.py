"""
Test Automation Workflow Tools
================================

Tests all 11 automation_workflow_* tools with Supabase backend.

Tests:
1. Tool registry loading (11 tools)
2. Create workflow
3. List workflows
4. Get workflow by ID and slug
5. Update workflow
6. Execute workflow
7. Update execution
8. Get execution history
9. List templates
10. Clone template
11. Create schedule
12. Delete workflow
"""

import sys
from pathlib import Path

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.registry_v3 import RegistryV3
import json


def test_tool_registry():
    """Test that all automation_workflow tools are loaded"""
    print("\n TEST 1: Tool Registry Loading")
    print("=" * 60)
    
    registry = RegistryV3()
    automation_tools = [t for t in registry.tools if 'automation_workflow' in t]
    
    print(f" Loaded {len(automation_tools)} automation_workflow tools:")
    for tool in sorted(automation_tools):
        print(f"    {tool}")
    
    expected_tools = [
        'automation_workflow_create',
        'automation_workflow_list',
        'automation_workflow_get',
        'automation_workflow_update',
        'automation_workflow_delete',
        'automation_workflow_execute',
        'automation_workflow_execution_update',
        'automation_workflow_execution_history',
        'automation_workflow_template_list',
        'automation_workflow_template_clone',
        'automation_workflow_schedule_create'
    ]
    
    missing = set(expected_tools) - set(automation_tools)
    if missing:
        print(f"\n Missing tools: {missing}")
        return False
    
    print(f"\n[OK] All {len(expected_tools)} tools loaded successfully")
    return True


def test_workflow_crud():
    """Test workflow CRUD operations"""
    print("\n TEST 2: Workflow CRUD Operations")
    print("=" * 60)
    
    registry = RegistryV3()
    
    # Test data
    workflow_json = json.dumps({
        "trigger": {"type": "email_received", "platform": "gmail"},
        "nodes": [
            {
                "id": "node_1",
                "type": "ai_agent",
                "position": {"x": 100, "y": 100},
                "config": {"role": "email_handler"}
            },
            {
                "id": "node_2",
                "type": "action",
                "position": {"x": 300, "y": 100},
                "config": {"action": "send_email"}
            }
        ]
    })
    
    canvas_data = json.dumps({"zoom": 1.0, "pan": {"x": 0, "y": 0}})
    
    try:
        # CREATE
        print("\n Creating workflow...")
        result = registry.execute_tool(
            tool_name='automation_workflow_create',
            user_id=1,
            name='Test Email Handler',
            workflow_json=workflow_json,
            description='Test workflow for email handling',
            category='email',
            canvas_data=canvas_data
        )
        
        if not result.get('success'):
            print(f" Create failed: {result}")
            return False
        
        workflow_id = result['workflow_id']
        slug = result['slug']
        print(f" Created workflow: {workflow_id}")
        print(f"   Slug: {slug}")
        
        # LIST
        print("\n Listing workflows...")
        result = registry.execute_tool(tool_name='automation_workflow_list',
            user_id=1
        )
        
        if not result.get('success'):
            print(f" List failed: {result}")
            return False
        
        count = result['count']
        print(f" Found {count} workflows")
        
        # GET by ID
        print(f"\n Getting workflow by ID: {workflow_id}")
        result = registry.execute_tool(tool_name='automation_workflow_get',
            workflow_id=workflow_id
        )
        
        if not result.get('success'):
            print(f" Get failed: {result}")
            return False
        
        workflow = result['workflow']
        print(f" Retrieved: {workflow['name']}")
        
        # GET by slug
        print(f"\n Getting workflow by slug: {slug}")
        result = registry.execute_tool(tool_name='automation_workflow_get',
            slug=slug
        )
        
        if not result.get('success'):
            print(f" Get by slug failed: {result}")
            return False
        
        print(f" Retrieved by slug: {result['workflow']['name']}")
        
        # UPDATE
        print("\n  Updating workflow...")
        result = registry.execute_tool(tool_name='automation_workflow_update',
            workflow_id=workflow_id,
            updates={'enabled': False, 'description': 'Updated description'}
        )
        
        if not result.get('success'):
            print(f" Update failed: {result}")
            return False
        
        print(f" Updated workflow (enabled: {result['workflow']['enabled']})")
        
        # DELETE
        print(f"\n  Deleting workflow: {workflow_id}")
        result = registry.execute_tool(tool_name='automation_workflow_delete',
            workflow_id=workflow_id
        )
        
        if not result.get('success'):
            print(f" Delete failed: {result}")
            return False
        
        print(" Workflow deleted successfully")
        
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execution_tracking():
    """Test execution tracking"""
    print("\n TEST 3: Execution Tracking")
    print("=" * 60)
    
    registry = RegistryV3()
    
    try:
        # Create test workflow first
        workflow_json = json.dumps({"trigger": {"type": "manual"}})
        
        result = registry.execute_tool(tool_name='automation_workflow_create',
            user_id=1,
            name='Test Execution Workflow',
            workflow_json=workflow_json
        )
        
        workflow_id = result['workflow_id']
        print(f" Created test workflow: {workflow_id}")
        
        # START EXECUTION
        print("\n  Starting execution...")
        trigger_data = json.dumps({"triggered_by": "test_script"})
        
        result = registry.execute_tool(tool_name='automation_workflow_execute',
            workflow_id=workflow_id,
            trigger_data=trigger_data,
            executed_by=1
        )
        
        if not result.get('success'):
            print(f" Execute failed: {result}")
            return False
        
        execution_id = result['execution_id']
        print(f" Started execution: {execution_id}")
        
        # UPDATE EXECUTION
        print("\n Updating execution status...")
        execution_state = json.dumps({"node_1": {"result": "success"}})
        
        result = registry.execute_tool(tool_name='automation_workflow_execution_update',
            execution_id=execution_id,
            status='completed',
            execution_state=execution_state,
            duration_ms=1500
        )
        
        if not result.get('success'):
            print(f" Update execution failed: {result}")
            return False
        
        print(" Execution updated to: completed")
        
        # GET HISTORY
        print("\n Getting execution history...")
        result = registry.execute_tool(tool_name='automation_workflow_execution_history',
            workflow_id=workflow_id,
            limit=10
        )
        
        if not result.get('success'):
            print(f" Get history failed: {result}")
            return False
        
        count = result['count']
        print(f" Found {count} executions")
        
        if result['executions']:
            exec_data = result['executions'][0]
            print(f"   Latest: {exec_data['status']} (duration: {exec_data.get('duration_ms')}ms)")
        
        # Cleanup
        registry.execute_tool(tool_name='automation_workflow_delete', workflow_id=workflow_id)
        
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_templates():
    """Test template operations"""
    print("\n TEST 4: Template Operations")
    print("=" * 60)
    
    registry = RegistryV3()
    
    try:
        # LIST TEMPLATES
        print("\n Listing templates...")
        result = registry.execute_tool(tool_name='automation_workflow_template_list')
        
        if not result.get('success'):
            print(f" List templates failed: {result}")
            return False
        
        count = result['count']
        print(f" Found {count} templates")
        
        if count == 0:
            print("  No templates found - run seed script to add templates")
            return True
        
        # Get first template
        template = result['templates'][0]
        template_id = template['template_id']
        print(f"   Template: {template['name']}")
        
        # CLONE TEMPLATE
        print(f"\n Cloning template: {template_id}")
        result = registry.execute_tool(tool_name='automation_workflow_template_clone',
            template_id=template_id,
            user_id=1,
            name='Cloned Test Workflow'
        )
        
        if not result.get('success'):
            print(f" Clone template failed: {result}")
            return False
        
        workflow = result['workflow']
        print(f" Cloned to workflow: {workflow['name']}")
        print(f"   Workflow ID: {workflow['workflow_id']}")
        
        # Cleanup
        registry.execute_tool(tool_name='automation_workflow_delete', workflow_id=workflow['workflow_id'])
        
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schedules():
    """Test schedule creation"""
    print("\n TEST 5: Schedule Creation")
    print("=" * 60)
    
    registry = RegistryV3()
    
    try:
        # Create test workflow
        workflow_json = json.dumps({"trigger": {"type": "schedule"}})
        
        result = registry.execute_tool(tool_name='automation_workflow_create',
            user_id=1,
            name='Scheduled Workflow',
            workflow_json=workflow_json
        )
        
        workflow_id = result['workflow_id']
        print(f" Created workflow: {workflow_id}")
        
        # CREATE CRON SCHEDULE
        print("\n Creating cron schedule (daily at 8am)...")
        result = registry.execute_tool(tool_name='automation_workflow_schedule_create',
            workflow_id=workflow_id,
            schedule_type='cron',
            cron_expression='0 8 * * *',
            timezone='UTC'
        )
        
        if not result.get('success'):
            print(f" Create schedule failed: {result}")
            return False
        
        schedule = result['schedule']
        print(f" Created schedule: {schedule['schedule_type']}")
        print(f"   Cron: {schedule['cron_expression']}")
        
        # CREATE INTERVAL SCHEDULE
        print("\n Creating interval schedule (every 2 hours)...")
        result = registry.execute_tool(tool_name='automation_workflow_schedule_create',
            workflow_id=workflow_id,
            schedule_type='interval',
            interval_minutes=120
        )
        
        if not result.get('success'):
            print(f" Create interval schedule failed: {result}")
            return False
        
        print(f" Created interval schedule: every 120 minutes")
        
        # Cleanup
        registry.execute_tool(tool_name='automation_workflow_delete', workflow_id=workflow_id)
        
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print(" AUTOMATION WORKFLOW TOOLS TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Tool Registry", test_tool_registry),
        ("Workflow CRUD", test_workflow_crud),
        ("Execution Tracking", test_execution_tracking),
        ("Templates", test_templates),
        ("Schedules", test_schedules)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All tests passed!")
    else:
        print("  Some tests failed")
    
    print("=" * 60)


if __name__ == '__main__':
    main()

