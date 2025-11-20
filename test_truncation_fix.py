"""
Test Truncation Fix - Verify Meta-Tools and Outlook Parameters

Tests:
1. Meta-tools return full results (no truncation)
2. Unknown tools allow 40KB (not 1KB)
3. Outlook tools have proper date/limit parameters
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import get_registry

def test_meta_tools_no_truncate():
    """Test that meta-tools return full results"""
    print("\n" + "="*70)
    print("TEST 1: Meta-Tools No Truncation")
    print("="*70)
    
    registry = get_registry()
    
    # Test list_platform_tools
    print("\n[1] Testing list_platform_tools...")
    result = registry.execute_tool(tool_name='list_platform_tools', platform='microsoft_365')
    
    if isinstance(result, dict) and 'tools' in result:
        tool_count = len(result['tools'])
        result_size = len(str(result))
        print(f"   Tools returned: {tool_count}")
        print(f"   Result size: {result_size:,} chars")
        print(f"   Status: {'PASS - Full result' if tool_count > 10 else 'FAIL - Truncated'}")
    else:
        print(f"   FAIL: Unexpected result format")
    
    # Test list_available_platforms
    print("\n[2] Testing list_available_platforms...")
    result = registry.execute_tool(tool_name='list_available_platforms')
    
    if isinstance(result, dict) and 'platforms' in result:
        platform_count = len(result['platforms'])
        result_size = len(str(result))
        print(f"   Platforms returned: {platform_count}")
        print(f"   Result size: {result_size:,} chars")
        print(f"   Status: {'PASS - Full result' if platform_count > 5 else 'FAIL - Truncated'}")
    else:
        print(f"   FAIL: Unexpected result format")


def test_outlook_parameters():
    """Test Outlook tools have proper parameters"""
    print("\n" + "="*70)
    print("TEST 2: Outlook Tools Have Date/Limit Parameters")
    print("="*70)
    
    registry = get_registry()
    
    # Check list_messages
    print("\n[1] microsoft_outlook_list_messages parameters:")
    tool = registry.get_tool('microsoft_outlook_list_messages')
    
    if tool and 'parameters' in tool:
        params = tool['parameters'].get('properties', {})
        
        has_max_results = 'max_results' in params
        has_filter = 'filter' in params
        has_search = 'search' in params
        has_unread_only = 'unread_only' in params
        
        print(f"   max_results: {'YES' if has_max_results else 'NO'}")
        print(f"   filter: {'YES' if has_filter else 'NO'}")
        print(f"   search: {'YES' if has_search else 'NO'}")
        print(f"   unread_only: {'YES' if has_unread_only else 'NO'}")
        
        if has_max_results and has_filter:
            print(f"   Status: PASS - Has limit and filter parameters")
        else:
            print(f"   Status: FAIL - Missing parameters")
    else:
        print(f"   FAIL: Tool not found or no parameters")
    
    # Check search_messages
    print("\n[2] microsoft_outlook_search_messages parameters:")
    tool = registry.get_tool('microsoft_outlook_search_messages')
    
    if tool and 'parameters' in tool:
        params = tool['parameters'].get('properties', {})
        
        has_max_results = 'max_results' in params
        has_date_from = 'date_from' in params
        has_date_to = 'date_to' in params
        has_from_email = 'from_email' in params
        
        print(f"   max_results: {'YES' if has_max_results else 'NO'}")
        print(f"   date_from: {'YES' if has_date_from else 'NO'}")
        print(f"   date_to: {'YES' if has_date_to else 'NO'}")
        print(f"   from_email: {'YES' if has_from_email else 'NO'}")
        
        if has_max_results and has_date_from and has_date_to:
            print(f"   Status: PASS - Has all date range parameters")
        else:
            print(f"   Status: FAIL - Missing parameters")
    else:
        print(f"   FAIL: Tool not found or no parameters")


def test_truncation_function():
    """Test smart_truncate_tool_result function"""
    print("\n" + "="*70)
    print("TEST 3: Truncation Function Logic")
    print("="*70)
    
    from AI_infrastructure.core.combined_agent_worker import smart_truncate_tool_result
    
    # Test meta-tool (should not truncate)
    print("\n[1] Testing meta-tool truncation...")
    large_data = {"tools": [{"name": f"tool_{i}"} for i in range(1000)]}
    result = smart_truncate_tool_result(large_data, 'list_platform_tools', max_tokens=100)
    
    # Check if metadata indicates no truncation
    if 'truncated=False' in result and 'type=META_TOOL' in result:
        print(f"   Status: PASS - Meta-tool not truncated")
        print(f"   Result size: {len(result):,} chars")
    else:
        print(f"   Status: FAIL - Meta-tool was truncated")
    
    # Test unknown tool (should allow 40KB)
    print("\n[2] Testing unknown tool limit...")
    small_data = {"data": "x" * 5000}  # 5KB
    result = smart_truncate_tool_result(small_data, 'unknown_custom_tool', max_tokens=100)
    
    # Should not truncate since 5KB < 40KB limit
    if 'truncated=False' in result or 'truncated": false' in result:
        print(f"   Status: PASS - Unknown tool allows large results (40KB limit)")
        print(f"   Result size: {len(result):,} chars")
    else:
        print(f"   Status: FAIL - Unknown tool limit too strict")


def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# TRUNCATION FIX VERIFICATION TESTS")
    print("#"*70)
    
    try:
        test_meta_tools_no_truncate()
        test_outlook_parameters()
        test_truncation_function()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE")
        print("="*70)
        print("\nSummary:")
        print("  1. Meta-tools: Should return full results (no truncation)")
        print("  2. Outlook tools: Should have date/limit parameters")
        print("  3. Truncation function: Should exempt meta-tools and allow 40KB for unknown")
        print("\nIf all tests show PASS, truncation fix is working correctly!")
        
    except Exception as e:
        print(f"\n FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
