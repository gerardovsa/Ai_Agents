"""
Test: Verify meta-tools work without duplicate wrapper
Date: January 19, 2026
Purpose: Confirm AI can access all 8 meta-tools through Registry V3 after deleting quote-calculator/meta_tools_wrapper.py
"""

def test_registry_loads_core_meta_tools():
    """Test 1: Verify Registry V3 loads all 8 core meta-tools"""
    print("\n" + "="*70)
    print("TEST 1: Registry V3 Loads Core Meta-Tools")
    print("="*70)
    
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    
    expected_meta_tools = [
        "search_tools",
        "list_platform_tools", 
        "get_tool_schema",
        "list_available_platforms",
        "execute_tool",
        "get_platform_guide",
        "recommend_tools_for_task",
        "get_workflow_steps"
    ]
    
    print(f"\n📊 Total tools in registry: {len(registry.tools)}")
    print(f"🎯 Expected meta-tools: {len(expected_meta_tools)}")
    
    missing = []
    found = []
    
    for tool_name in expected_meta_tools:
        if tool_name in registry.tools:
            found.append(tool_name)
            print(f"   ✅ {tool_name}")
        else:
            missing.append(tool_name)
            print(f"   ❌ {tool_name} - MISSING!")
    
    print(f"\n📈 Results: {len(found)}/{len(expected_meta_tools)} meta-tools found")
    
    if missing:
        print(f"⚠️ MISSING: {missing}")
        return False
    else:
        print("✅ SUCCESS: All core meta-tools loaded correctly")
        return True


def test_meta_tools_source():
    """Test 2: Verify meta-tools come from core implementation, not module wrapper"""
    print("\n" + "="*70)
    print("TEST 2: Meta-Tools Source Verification")
    print("="*70)
    
    from tools.registry_v3 import RegistryV3
    import inspect
    
    registry = RegistryV3()
    
    # Check search_tools source file
    if 'search_tools' in registry.tools:
        tool_func = registry.tools['search_tools']['function']
        source_file = inspect.getfile(tool_func)
        
        print(f"\n🔍 search_tools() source:")
        print(f"   {source_file}")
        
        # Should be in tools/implementations/meta_tools.py, NOT quote-calculator module
        if 'tools\\implementations\\meta_tools.py' in source_file or 'tools/implementations/meta_tools.py' in source_file:
            print("   ✅ Loaded from CORE implementation (correct)")
            return True
        elif 'quote-calculator' in source_file:
            print("   ❌ Loaded from quote-calculator module (WRONG - wrapper still active)")
            return False
        else:
            print(f"   ⚠️ Unexpected source location")
            return False
    else:
        print("❌ search_tools not found in registry")
        return False


def test_search_tools_execution():
    """Test 3: Execute search_tools() without ToolUseAgent dependency"""
    print("\n" + "="*70)
    print("TEST 3: search_tools() Execution (No ToolUseAgent)")
    print("="*70)
    
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    
    try:
        # Execute search_tools directly through registry
        result = registry.execute_tool(
            tool_name='search_tools',
            query='shopify products'
        )
        
        print(f"\n🔧 Executed: search_tools(query='shopify products')")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Tools found: {result.get('total_results', 0)}")
        
        if result.get('success') and result.get('total_results', 0) > 0:
            print(f"\n📋 Sample results:")
            for tool in result.get('tools', [])[:3]:
                print(f"   - {tool.get('name')}: {tool.get('short_description', 'N/A')[:60]}...")
            
            print("\n✅ SUCCESS: search_tools() executed without ToolUseAgent")
            return True
        else:
            print(f"\n⚠️ PARTIAL: Executed but returned no results")
            print(f"   Result: {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_platform_tools_execution():
    """Test 4: Execute list_platform_tools() for quote_calculator"""
    print("\n" + "="*70)
    print("TEST 4: list_platform_tools() Execution")
    print("="*70)
    
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    
    try:
        # Execute list_platform_tools for quote_calculator
        result = registry.execute_tool(
            tool_name='list_platform_tools',
            platform='quote_calculator'
        )
        
        print(f"\n🔧 Executed: list_platform_tools(platform='quote_calculator')")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Tools found: {len(result.get('tools', []))}")
        
        if result.get('success') and len(result.get('tools', [])) > 0:
            print(f"\n📋 Sample tools:")
            for tool in result.get('tools', [])[:5]:
                print(f"   - {tool.get('name')}")
            
            print("\n✅ SUCCESS: list_platform_tools() executed correctly")
            return True
        else:
            print(f"\n⚠️ WARNING: No tools found for quote_calculator platform")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_agent_tool_loading():
    """Test 5: Simulate AI agent tool loading (agent_routes_v4.py pattern)"""
    print("\n" + "="*70)
    print("TEST 5: AI Agent Tool Loading Simulation")
    print("="*70)
    
    from tools.registry_v3 import get_registry
    
    # Simulate agent_routes_v4.py lines 1078-1091
    registry = get_registry()
    
    meta_tool_names = [
        'list_available_platforms',
        'list_platform_tools',
        'get_tool_schema',
        'search_tools',
        'get_platform_guide',
        'recommend_tools_for_task',
        'get_workflow_steps',
        'execute_tool'
    ]
    
    all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
    tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
    
    print(f"\n🤖 Simulated AI agent tool loading:")
    print(f"   Requested meta-tools: {len(meta_tool_names)}")
    print(f"   Loaded from registry: {len(tools)}")
    
    if len(tools) == len(meta_tool_names):
        print(f"\n✅ SUCCESS: All {len(tools)} meta-tools available to AI")
        print(f"   Tools: {[t['name'] for t in tools]}")
        return True
    else:
        missing = set(meta_tool_names) - {t['name'] for t in tools}
        print(f"\n❌ FAILED: Missing {len(missing)} tools")
        print(f"   Missing: {missing}")
        return False


def run_all_tests():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("META-TOOLS VERIFICATION SUITE")
    print("Testing Registry V3 after deleting duplicate meta_tools_wrapper.py")
    print("="*70)
    
    tests = [
        ("Registry Loads Core Meta-Tools", test_registry_loads_core_meta_tools),
        ("Meta-Tools Source Verification", test_meta_tools_source),
        ("search_tools() Execution", test_search_tools_execution),
        ("list_platform_tools() Execution", test_list_platform_tools_execution),
        ("AI Agent Tool Loading", test_ai_agent_tool_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {test_name}")
            print(f"   Error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - Meta-tools work without ToolUseAgent wrapper!")
        print("   AI agents can discover and execute tools through Registry V3")
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed - investigation needed")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
