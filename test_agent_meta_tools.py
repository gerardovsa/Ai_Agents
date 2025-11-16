"""
Test Agent Coordination Meta Tools Integration

Tests that the meta tools properly discover and guide users to agent coordination tools.
Shows the complete discovery flow: platforms → tools → schemas → usage
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3


def test_list_available_platforms():
    """Test 1: Check if advanced_agent_coordination appears in platforms list"""
    print("=" * 70)
    print("TEST 1: List Available Platforms")
    print("=" * 70)
    
    registry = RegistryV3()
    
    # Simulate calling list_available_platforms()
    from tools.implementations.meta_tools import list_available_platforms
    
    result = list_available_platforms()
    
    if result.get('success'):
        platforms = result.get('platforms', [])
        
        # Check if agent coordination is in the list
        agent_platforms = [p for p in platforms if 'agent' in p.lower() or 'coordination' in p.lower()]
        
        print(f"\n Total Platforms: {result.get('platform_count')}")
        print(f" Total Tools: {result.get('total_tools')}")
        print(f"\n Agent-related platforms found:")
        
        if agent_platforms:
            for platform in agent_platforms:
                tool_count = result.get('tool_counts', {}).get(platform, 0)
                print(f"   - {platform}: {tool_count} tools")
        else:
            print("   ❌ No agent coordination platforms found!")
        
        return bool(agent_platforms)
    else:
        print(f" ❌ Failed: {result.get('error')}")
        return False


def test_list_platform_tools_direct():
    """Test 2: List tools using exact platform name"""
    print("\n" + "=" * 70)
    print("TEST 2: List Platform Tools (Direct)")
    print("=" * 70)
    
    from tools.implementations.meta_tools import list_platform_tools
    
    result = list_platform_tools(platform='advanced_agent_coordination')
    
    if result.get('success'):
        print(f"\n Platform: {result.get('platform')}")
        print(f" Tool Count: {result.get('tool_count')}")
        
        if result.get('guidance'):
            print(f"\n GUIDANCE PROVIDED:")
            print(f"{result.get('guidance')}")
        
        print(f"\n TOOLS:")
        for tool in result.get('tools', []):
            print(f"\n   {tool['name']}")
            print(f"   {tool['description'][:100]}...")
        
        return True
    else:
        print(f" ❌ Failed: {result.get('error')}")
        return False


def test_list_platform_tools_alias():
    """Test 3: List tools using alias 'agent'"""
    print("\n" + "=" * 70)
    print("TEST 3: List Platform Tools (Alias 'agent')")
    print("=" * 70)
    
    from tools.implementations.meta_tools import list_platform_tools
    
    result = list_platform_tools(platform='agent')
    
    if result.get('success'):
        print(f"\n Searched for: 'agent'")
        print(f" Matched as: {result.get('matched_as')}")
        print(f" Tool Count: {result.get('tool_count')}")
        
        if result.get('guidance'):
            print(f"\n GUIDANCE:")
            guidance_lines = result.get('guidance').split('\n')[:15]  # First 15 lines
            for line in guidance_lines:
                print(f"   {line}")
            print("   ...")
        
        print(f"\n TOOLS:")
        for tool in result.get('tools', [])[:3]:  # First 3 tools
            print(f"   - {tool['name']}")
        
        return True
    else:
        print(f" ❌ Failed: {result.get('error')}")
        return False


def test_search_tools():
    """Test 4: Search for agent coordination using search_tools"""
    print("\n" + "=" * 70)
    print("TEST 4: Search Tools (recommend_tools_for_task)")
    print("=" * 70)
    
    from tools.implementations.meta_tools import recommend_tools_for_task
    
    result = recommend_tools_for_task(task_description='distribute work across multiple agents')
    
    if result.get('success'):
        print(f"\n Query: 'distribute work across multiple agents'")
        print(f" Matches: {result.get('match_count')}")
        
        if result.get('guidance'):
            print(f"\n GUIDANCE:")
            guidance_lines = result.get('guidance').split('\n')[:10]
            for line in guidance_lines:
                print(f"   {line}")
        
        print(f"\n TOP TOOLS:")
        for tool in result.get('tools', [])[:5]:
            print(f"\n   {tool['name']}")
            print(f"   Platform: {tool['platform']}")
            print(f"   {tool['description'][:80]}...")
        
        return True
    else:
        print(f" ❌ Failed: {result.get('error')}")
        return False


def test_get_tool_schema():
    """Test 5: Get detailed schema for assign_and_activate_agent_with_slugs"""
    print("\n" + "=" * 70)
    print("TEST 5: Get Tool Schema")
    print("=" * 70)
    
    from tools.implementations.meta_tools import get_tool_schema
    
    result = get_tool_schema(tool_name='assign_and_activate_agent_with_slugs')
    
    if result.get('success'):
        schema = result.get('schema', {})
        print(f"\n Tool: {result.get('tool_name')}")
        print(f" Platform: {schema.get('platform')}")
        print(f" Description: {schema.get('description')[:100]}...")
        
        params = schema.get('parameters', {}).get('properties', {})
        print(f"\n PARAMETERS ({len(params)} total):")
        
        for param_name, param_info in list(params.items())[:3]:
            print(f"\n   {param_name}:")
            print(f"     Type: {param_info.get('type')}")
            print(f"     Description: {param_info.get('description', '')[:80]}...")
        
        print("\n   ... (more parameters)")
        
        required = schema.get('parameters', {}).get('required', [])
        print(f"\n REQUIRED: {', '.join(required)}")
        
        return True
    else:
        print(f" ❌ Failed: {result.get('error')}")
        return False


def test_complete_discovery_flow():
    """Test 6: Complete discovery flow from query to usage"""
    print("\n" + "=" * 70)
    print("TEST 6: Complete Discovery Flow")
    print("=" * 70)
    
    print("\n SCENARIO: User asks 'How can I distribute work to multiple AI agents?'")
    print("\n STEP 1: Search for relevant tools...")
    
    from tools.implementations.meta_tools import recommend_tools_for_task
    
    result = recommend_tools_for_task(task_description='distribute work multiple agents')
    
    if not result.get('success'):
        print(" ❌ Search failed")
        return False
    
    # Find assign_and_activate tool
    tools = result.get('tools', [])
    agent_tool = next((t for t in tools if 'assign_and_activate' in t['name']), None)
    
    if not agent_tool:
        print(" ❌ assign_and_activate_agent_with_slugs not found in search results")
        return False
    
    print(f" Found: {agent_tool['name']}")
    
    print("\n STEP 2: Get detailed schema...")
    
    from tools.implementations.meta_tools import get_tool_schema
    
    schema_result = get_tool_schema(tool_name=agent_tool['name'])
    
    if not schema_result.get('success'):
        print(" ❌ Schema fetch failed")
        return False
    
    print(f" Got schema with {len(schema_result['schema'].get('parameters', {}).get('properties', {}))} parameters")
    
    print("\n STEP 3: Review guidance...")
    
    from tools.implementations.meta_tools import list_platform_tools
    
    guidance_result = list_platform_tools(platform='agent')
    
    if guidance_result.get('guidance'):
        print(" Guidance available")
        guidance_preview = guidance_result['guidance'].split('\n')[:5]
        for line in guidance_preview:
            print(f"   {line}")
        print("   ...")
    
    print("\n STEP 4: Execute tool (simulation)...")
    print(f"   registry.execute_tool(")
    print(f"       '{agent_tool['name']}',")
    print(f"       target_agent='Alpha',")
    print(f"       thread_title='Test Work',")
    print(f"       instructions='Do something...',")
    print(f"       auto_trigger=True")
    print(f"   )")
    
    print("\n ✅ COMPLETE DISCOVERY FLOW SUCCESSFUL!")
    return True


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("AGENT COORDINATION META TOOLS - DISCOVERY TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("List Available Platforms", test_list_available_platforms),
        ("List Platform Tools (Direct)", test_list_platform_tools_direct),
        ("List Platform Tools (Alias)", test_list_platform_tools_alias),
        ("Search Tools", test_search_tools),
        ("Get Tool Schema", test_get_tool_schema),
        ("Complete Discovery Flow", test_complete_discovery_flow)
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
            print(f"\n❌ TEST EXCEPTION: {test_name}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED! Agent coordination is fully discoverable!")
    
    print()
