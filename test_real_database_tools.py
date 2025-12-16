"""
Test Script for REAL InHouse Database Query Tools
December 16, 2025

This script tests the WORKING database tools (not the STUB tools).

WORKING Tools:
- get_available_queries (module plugin: quote-calculator)
- execute_query_library (module plugin: quote-calculator)
- inhouse_query_guide (module plugin: inhouse-print)
- inhouse_execute_query (module plugin: inhouse-print)
- inhouse_database_guide (module plugin: inhouse-print)

STUB Tools (DO NOT USE):
- db_execute_query (core tools: sql_database.py)
- db_get_available_queries (core tools: sql_database.py)
- db_calculate_quote (core tools: sql_database.py)
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

def test_tool_discovery():
    """Test that we can find the real tools"""
    print("\n" + "="*80)
    print("TEST 1: TOOL DISCOVERY")
    print("="*80)
    
    registry = RegistryV3()
    
    # Find inhouse query tools
    inhouse_query_tools = [name for name in registry.tools.keys() 
                          if 'query' in name.lower() and 'inhouse' in name.lower()]
    
    print(f"\n✅ Found {len(inhouse_query_tools)} InHouse query tools:")
    for tool in sorted(inhouse_query_tools):
        tool_data = registry.get_tool(tool)
        platform = tool_data.get('platform', 'unknown')
        print(f"   - {tool} (platform: {platform})")
    
    # Find query library tools
    query_lib_tools = [name for name in registry.tools.keys() 
                       if 'available_queries' in name.lower() or 'execute_query_library' in name.lower()]
    
    print(f"\n✅ Found {len(query_lib_tools)} Query Library tools:")
    for tool in sorted(query_lib_tools):
        tool_data = registry.get_tool(tool)
        platform = tool_data.get('platform', 'unknown')
        print(f"   - {tool} (platform: {platform})")
    
    return registry, inhouse_query_tools, query_lib_tools


def test_query_library_discovery(registry):
    """Test get_available_queries tool"""
    print("\n" + "="*80)
    print("TEST 2: QUERY LIBRARY DISCOVERY")
    print("="*80)
    
    try:
        # Get the tool function
        func = registry.get_tool_function('get_available_queries')
        
        if not func:
            print("❌ Tool function not found")
            return False
        
        print("✅ Tool function found")
        
        # Execute with no category (get all queries)
        print("\n📋 Getting all available queries...")
        result = func(category="all")
        
        print(f"\nResult:")
        print(f"   Success: {result.get('success')}")
        print(f"   Category: {result.get('category')}")
        print(f"   Query Count: {result.get('query_count')}")
        
        if result.get('success'):
            queries = result.get('queries', [])
            print(f"\n📊 Sample queries (first 5):")
            for i, query in enumerate(queries[:5], 1):
                print(f"   {i}. {query.get('name')}")
                print(f"      Category: {query.get('category')}")
                print(f"      Description: {query.get('description', '')[:60]}...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing query library: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_guide(registry):
    """Test inhouse_query_guide tool"""
    print("\n" + "="*80)
    print("TEST 3: INHOUSE QUERY GUIDE")
    print("="*80)
    
    try:
        # Get the tool function
        func = registry.get_tool_function('inhouse_query_guide')
        
        if not func:
            print("❌ Tool function not found")
            return False
        
        print("✅ Tool function found")
        
        # Execute guide
        print("\n📖 Getting query guide...")
        result = func()
        
        print(f"\nResult:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            # Print first 500 chars of guide
            guide_text = result.get('guide', '')
            print(f"\n📝 Guide preview (first 500 chars):")
            print(guide_text[:500] + "...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing query guide: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_guide(registry):
    """Test inhouse_database_guide tool"""
    print("\n" + "="*80)
    print("TEST 4: INHOUSE DATABASE GUIDE")
    print("="*80)
    
    try:
        # Get the tool function
        func = registry.get_tool_function('inhouse_database_guide')
        
        if not func:
            print("❌ Tool function not found")
            return False
        
        print("✅ Tool function found")
        
        # Execute guide
        print("\n📖 Getting database schema guide...")
        result = func()
        
        print(f"\nResult:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            # Print first 500 chars of guide
            guide_text = result.get('guide', '')
            print(f"\n📝 Schema guide preview (first 500 chars):")
            print(guide_text[:500] + "...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing database guide: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_execution(registry):
    """Test execute_query_library tool"""
    print("\n" + "="*80)
    print("TEST 5: QUERY EXECUTION")
    print("="*80)
    
    try:
        # Get the tool function
        func = registry.get_tool_function('execute_query_library')
        
        if not func:
            print("❌ Tool function not found")
            return False
        
        print("✅ Tool function found")
        
        # Try executing a simple query (monthly revenue trend)
        print("\n💰 Executing query: monthly_revenue_trend (last 3 months)...")
        result = func(
            query_name="monthly_revenue_trend",
            parameters={"months": 3}
        )
        
        print(f"\nResult:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            data = result.get('data', [])
            print(f"   Rows returned: {len(data)}")
            if data:
                print(f"\n📊 Sample data (first row):")
                print(f"   {data[0]}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing query execution: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("INHOUSE DATABASE TOOLS - COMPREHENSIVE TEST")
    print("="*80)
    print("\nTesting REAL tools (module plugins), NOT stub tools")
    print("")
    
    # Test 1: Discovery
    registry, inhouse_tools, query_lib_tools = test_tool_discovery()
    
    if not inhouse_tools and not query_lib_tools:
        print("\n❌ FAIL: No tools found! Check registry loading.")
        return
    
    # Test 2: Query Library Discovery
    test_query_library_discovery(registry)
    
    # Test 3: Query Guide
    test_query_guide(registry)
    
    # Test 4: Database Guide
    test_database_guide(registry)
    
    # Test 5: Query Execution (might fail if DB not accessible)
    test_query_execution(registry)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\n✅ Tool discovery completed")
    print("✅ If guides returned data, tools are working")
    print("⚠️  Query execution may fail if database credentials not configured")
    print("\nNext Steps:")
    print("1. Check database-config.json in config/ folder")
    print("2. Verify InHousePrintDB connection settings")
    print("3. Test with actual client data once DB is accessible")


if __name__ == "__main__":
    main()
