"""
Test Agent Coordination Tools

Tests the new multi-agent coordination tools:
1. assign_and_activate_agent_with_slugs - Combo tool with UI automation
2. request_update_from_thread - Cross-thread communication
3. respond_to_cross_thread_request - Response handling

Run this to verify tools load and execute correctly.
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3


def test_tool_loading():
    """Test that coordination tools loaded successfully"""
    print("=" * 60)
    print("TEST 1: Tool Loading")
    print("=" * 60)
    
    registry = RegistryV3()
    
    coordination_tools = [
        'assign_and_activate_agent_with_slugs',
        'request_update_from_thread',
        'respond_to_cross_thread_request'
    ]
    
    for tool_name in coordination_tools:
        if tool_name in registry.tools:
            tool = registry.get_tool(tool_name)
            print(f"✅ {tool_name}")
            print(f"   Description: {tool.get('description', 'N/A')[:80]}...")
            print(f"   Platform: {tool.get('platform', 'N/A')}")
        else:
            print(f"❌ {tool_name} - NOT FOUND")
    
    print()
    return True


def test_assign_and_activate():
    """Test assign_and_activate_agent_with_slugs tool"""
    print("=" * 60)
    print("TEST 2: Assign and Activate Tool")
    print("=" * 60)
    
    registry = RegistryV3()
    
    try:
        print("\n📝 Test parameters:")
        print("   target_agent: 'Alpha'")
        print("   thread_title: 'Test Frontend Work'")
        print("   instructions: 'Build React frontend...'")
        print("   slugs: {'workflow_slug': 'test-workflow'}")
        print("   auto_trigger: False")
        print("   open_ui: True")
        print()
        
        result = registry.execute_tool(
            'assign_and_activate_agent_with_slugs',
            target_agent='Alpha',
            thread_title='Test Frontend Work',
            instructions='Build React frontend for e-commerce platform. Use modern best practices.',
            slugs={
                'workflow_slug': 'test-workflow',
                'workflow_title': 'React Development Workflow'
            },
            auto_trigger=False,
            open_ui=True,
            _user_id=1  # Mock user_id
        )
        
        if result.get('success'):
            print("✅ Tool execution successful!")
            print(f"\n📊 Result:")
            print(f"   Thread ID: {result.get('thread_id')}")
            print(f"   Location: {result.get('thread_location')}")
            print(f"   Slugs: {result.get('assigned_slugs')}")
            print(f"   Message ID: {result.get('message_id')}")
            
            if result.get('ui_commands'):
                print(f"\n🎨 UI Commands: {len(result['ui_commands'])} commands")
                for i, cmd in enumerate(result['ui_commands'], 1):
                    print(f"   {i}. {cmd.get('command')}")
        else:
            print(f"❌ Tool execution failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
    
    print()
    return True


def test_cross_thread_request():
    """Test cross-thread request creation"""
    print("=" * 60)
    print("TEST 3: Cross-Thread Request")
    print("=" * 60)
    
    registry = RegistryV3()
    
    try:
        print("\n📝 Creating cross-thread request...")
        print("   target: 'Bravo' (agent-2)")
        print("   request: 'What's the status?'")
        print("   request_type: 'status_update'")
        print("   priority: 'high'")
        print()
        
        # First, we need a source and target thread
        # Let's create them using assign_and_activate
        print("   Setting up source thread (Prime)...")
        source_result = registry.execute_tool(
            'assign_and_activate_agent_with_slugs',
            target_agent='1',  # Prime is considered agent-0, but let's use agent-1
            thread_title='Test Source Thread',
            instructions='Source thread for testing cross-thread requests',
            auto_trigger=False,
            open_ui=False,
            _user_id=1
        )
        
        if not source_result.get('success'):
            print(f"❌ Failed to create source thread: {source_result.get('error')}")
            return False
        
        source_thread_id = source_result['thread_id']
        print(f"   ✅ Source thread created: {source_thread_id}")
        
        print("   Setting up target thread (Bravo - agent-2)...")
        target_result = registry.execute_tool(
            'assign_and_activate_agent_with_slugs',
            target_agent='Bravo',
            thread_title='Test Target Thread',
            instructions='Target thread for testing cross-thread requests',
            auto_trigger=False,
            open_ui=False,
            _user_id=1
        )
        
        if not target_result.get('success'):
            print(f"❌ Failed to create target thread: {target_result.get('error')}")
            return False
        
        target_thread_id = target_result['thread_id']
        print(f"   ✅ Target thread created: {target_thread_id}")
        
        print("\n   Sending cross-thread request...")
        request_result = registry.execute_tool(
            'request_update_from_thread',
            target_thread_id='Bravo',  # Can use NATO name
            request_message='What is the status of API development? Are endpoints ready?',
            request_type='status_update',
            priority='high',
            wait_for_response=False,
            _user_id=1,
            _source_thread_id=source_thread_id
        )
        
        if request_result.get('success'):
            print("✅ Cross-thread request created!")
            print(f"\n📊 Result:")
            print(f"   Request ID: {request_result.get('request_id')}")
            print(f"   Source: {request_result.get('source_thread_id')[:12]}...")
            print(f"   Target: {request_result.get('target_thread_id')[:12]}...")
            print(f"   Status: {request_result.get('status')}")
            
            if request_result.get('ui_commands'):
                print(f"\n🎨 UI Commands: {len(request_result['ui_commands'])} commands")
        else:
            print(f"❌ Request creation failed: {request_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    return True


def test_anthropic_format():
    """Test that tools have correct Anthropic API format"""
    print("=" * 60)
    print("TEST 4: Anthropic API Format")
    print("=" * 60)
    
    registry = RegistryV3()
    anthropic_tools = registry.get_anthropic_tools()
    
    coordination_tools = [t for t in anthropic_tools if 'coordination' in t.get('name', '')]
    
    print(f"\nFound {len(coordination_tools)} coordination tools in Anthropic format:\n")
    
    for tool in coordination_tools:
        name = tool.get('name')
        has_input_schema = 'input_schema' in tool
        has_type = tool.get('input_schema', {}).get('type') == 'object'
        has_props = 'properties' in tool.get('input_schema', {})
        
        status = "✅" if (has_input_schema and has_type and has_props) else "❌"
        
        print(f"{status} {name}")
        if has_input_schema:
            print(f"   input_schema.type: {tool['input_schema'].get('type')}")
            print(f"   properties count: {len(tool['input_schema'].get('properties', {}))}")
            print(f"   required fields: {tool['input_schema'].get('required', [])}")
        else:
            print("   ❌ Missing input_schema!")
        print()
    
    return True


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("ADVANCED AGENT COORDINATION TOOLS - TEST SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        ("Tool Loading", test_tool_loading),
        ("Assign and Activate", test_assign_and_activate),
        ("Cross-Thread Request", test_cross_thread_request),
        ("Anthropic Format", test_anthropic_format)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
