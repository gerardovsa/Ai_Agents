"""
Test Agent Coordination Discovery - Simple Version (No Emojis)

Tests meta tool integration for agent coordination platform
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.implementations.meta_tools import list_available_platforms, list_platform_tools, recommend_tools_for_task, get_tool_schema


def test_1_list_platforms():
    """Test 1: Verify advanced_agent_coordination appears in platform list"""
    print("\n" + "="*80)
    print("TEST 1: List Available Platforms")
    print("="*80)
    
    result = list_available_platforms()
    
    # Find agent coordination platform
    agent_platforms = [p for p in result.get('platforms', []) if 'agent' in p['name'].lower()]
    
    print(f"\nTotal Platforms: {result.get('platform_count', 0)}")
    print(f"Total Tools: {result.get('total_tools', 0)}")
    print(f"\nAgent-related platforms found:")
    for p in agent_platforms:
        print(f"  - {p['name']}: {p['count']} tools")
    
    # Check if advanced_agent_coordination exists
    has_agent_coordination = any(p['name'] == 'advanced_agent_coordination' for p in result.get('platforms', []))
    
    if has_agent_coordination:
        print("\n[PASS] advanced_agent_coordination platform found")
        return True
    else:
        print("\n[FAIL] advanced_agent_coordination platform NOT found")
        return False


def test_2_direct_platform_lookup():
    """Test 2: List tools using direct platform name"""
    print("\n" + "="*80)
    print("TEST 2: List Platform Tools (Direct Name)")
    print("="*80)
    
    result = list_platform_tools('advanced_agent_coordination')
    
    if result.get('success'):
        print(f"\nSuccess: {result['success']}")
        print(f"Platform: {result['platform']}")
        print(f"Matched: {result['matched_platform']}")
        print(f"Tool Count: {result['tool_count']}")
        print(f"\nTools:")
        for tool in result.get('tools', []):
            print(f"  - {tool['name']}")
        print("\n[PASS] Direct platform lookup works")
        return True
    else:
        print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
        return False


def test_3_alias_lookup():
    """Test 3: List tools using 'agent' alias"""
    print("\n" + "="*80)
    print("TEST 3: List Platform Tools (Alias 'agent')")
    print("="*80)
    
    result = list_platform_tools('agent')
    
    if result.get('success'):
        print(f"\nSearched for: 'agent'")
        print(f"Matched as: {result['matched_platform']}")
        print(f"Tool Count: {result['tool_count']}")
        
        if 'guidance' in result:
            guidance_preview = result['guidance'][:300] + "..." if len(result['guidance']) > 300 else result['guidance']
            print(f"\nGUIDANCE:")
            print(f"  {guidance_preview}")
        
        print(f"\nTOOLS:")
        for tool in result.get('tools', []):
            print(f"  - {tool['name']}")
        
        print("\n[PASS] Alias lookup works")
        return True
    else:
        print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
        return False


def test_4_task_based_search():
    """Test 4: Search for tools using task description"""
    print("\n" + "="*80)
    print("TEST 4: Task-Based Search")
    print("="*80)
    
    query = "distribute work across multiple agents"
    result = recommend_tools_for_task(query)
    
    print(f"\nQuery: '{query}'")
    print(f"Match Count: {result.get('match_count', 0)}")
    
    if result.get('match_count', 0) > 0:
        print(f"\nTOP TOOLS:")
        for tool in result.get('tools', [])[:5]:
            print(f"  - {tool['name']} ({tool.get('platform', 'unknown')})")
            print(f"    {tool['description'][:100]}...")
        
        # Check if our target tool is in the results
        tool_names = [t['name'] for t in result.get('tools', [])]
        if 'assign_and_activate_agent_with_slugs' in tool_names:
            print("\n[PASS] Target tool found in search results")
            return True
        else:
            print("\n[FAIL] Target tool NOT found in search results")
            print(f"Found tools: {tool_names[:5]}")
            return False
    else:
        print("\n[FAIL] No tools found for query")
        return False


def test_5_get_schema():
    """Test 5: Get detailed schema for agent coordination tool"""
    print("\n" + "="*80)
    print("TEST 5: Get Tool Schema")
    print("="*80)
    
    tool_name = 'assign_and_activate_agent_with_slugs'
    result = get_tool_schema(tool_name)
    
    if result and isinstance(result, dict):
        print(f"\nTool: {tool_name}")
        print(f"Platform: {result.get('platform', 'N/A')}")
        
        if 'description' in result:
            desc = result['description'][:150] + "..." if len(result['description']) > 150 else result['description']
            print(f"Description: {desc}")
        
        if 'parameters' in result:
            params = result['parameters']
            if isinstance(params, dict) and 'properties' in params:
                props = params['properties']
                print(f"\nParameters: {len(props)} total")
                print("Key parameters:")
                for key in list(props.keys())[:5]:
                    print(f"  - {key}")
        
        print("\n[PASS] Schema retrieval works")
        return True
    else:
        print(f"\n[FAIL] Schema not found or invalid")
        return False


def test_6_complete_flow():
    """Test 6: Complete discovery workflow simulation"""
    print("\n" + "="*80)
    print("TEST 6: Complete Discovery Flow")
    print("="*80)
    
    print("\nSCENARIO: User asks 'How can I distribute work to multiple AI agents?'")
    
    # Step 1: Search for tools
    print("\nSTEP 1: Search for relevant tools...")
    search_result = recommend_tools_for_task("distribute work agents")
    
    if search_result.get('match_count', 0) > 0:
        tool_names = [t['name'] for t in search_result.get('tools', [])]
        if 'assign_and_activate_agent_with_slugs' in tool_names:
            print("  assign_and_activate_agent_with_slugs found in search")
            
            # Step 2: Get schema
            print("\nSTEP 2: Get tool schema...")
            schema = get_tool_schema('assign_and_activate_agent_with_slugs')
            if schema:
                print("  Schema retrieved successfully")
                
                # Step 3: Get platform guidance
                print("\nSTEP 3: Get platform guidance...")
                guidance_result = list_platform_tools('agent')
                if guidance_result.get('success'):
                    print("  Platform guidance retrieved successfully")
                    
                    # Step 4: Simulate execution
                    print("\nSTEP 4: AI would now execute the tool with parameters")
                    print("  (Simulated - not actually calling tool)")
                    
                    print("\n[PASS] Complete discovery flow successful")
                    return True
    
    print("\n[FAIL] Discovery flow incomplete")
    return False


def main():
    """Run all tests and report results"""
    print("\n" + "="*80)
    print("AGENT COORDINATION META TOOLS - DISCOVERY TEST SUITE")
    print("="*80)
    
    tests = [
        ("List Available Platforms", test_1_list_platforms),
        ("Direct Platform Lookup", test_2_direct_platform_lookup),
        ("Alias Lookup", test_3_alias_lookup),
        ("Task-Based Search", test_4_task_based_search),
        ("Get Tool Schema", test_5_get_schema),
        ("Complete Discovery Flow", test_6_complete_flow)
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
            print(f"\n[ERROR] Test '{test_name}' raised exception:")
            print(f"  {type(e).__name__}: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
