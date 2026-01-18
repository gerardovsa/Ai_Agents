"""
Test Meta Tools and Corflute Calculator Discovery
Run this after restarting Flask server to verify fixes
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))
sys.path.insert(0, str(project_root / 'tools'))

from tools.registry_v3 import RegistryV3

def test_meta_tools():
    """Test that meta tools are registered"""
    print("\n" + "="*70)
    print("TEST 1: Meta Tools Registration")
    print("="*70)
    
    registry = RegistryV3()
    
    meta_tools = [
        "list_platform_tools",
        "search_tools",
        "get_tool_schema",
        "list_available_platforms"
    ]
    
    for tool in meta_tools:
        if tool in registry.tools:
            print(f"✅ {tool} - REGISTERED")
        else:
            print(f"❌ {tool} - MISSING")
    
    return all(tool in registry.tools for tool in meta_tools)


def test_list_platforms():
    """Test list_available_platforms"""
    print("\n" + "="*70)
    print("TEST 2: List Available Platforms")
    print("="*70)
    
    registry = RegistryV3()
    
    try:
        result = registry.execute_tool(
            tool_name="list_available_platforms"
        )
        
        if result.get("success"):
            print(f"✅ Found {result['platform_count']} platforms")
            print(f"✅ Total tools: {result['total_tools']}")
            
            # Show top 5 platforms
            print("\nTop platforms:")
            for platform in result['platforms'][:5]:
                print(f"  - {platform['platform']}: {platform['tool_count']} tools")
            
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_search_corflute():
    """Test searching for corflute tools"""
    print("\n" + "="*70)
    print("TEST 3: Search for Corflute Tools")
    print("="*70)
    
    registry = RegistryV3()
    
    try:
        result = registry.execute_tool(
            tool_name="search_tools",
            query="corflute"
        )
        
        if result.get("success"):
            print(f"✅ Found {result['match_count']} matching tools")
            
            for match in result['matches']:
                print(f"\n  Tool: {match['name']}")
                print(f"  Platform: {match['platform']}")
                print(f"  Relevance: {match['relevance_score']}")
                print(f"  Description: {match['description'][:80]}...")
            
            # Check if calculate_corflute_signs_shopify found
            tool_names = [m['name'] for m in result['matches']]
            if 'calculate_corflute_signs_shopify' in tool_names:
                print("\n✅ calculate_corflute_signs_shopify FOUND")
                return True
            else:
                print("\n❌ calculate_corflute_signs_shopify NOT FOUND")
                return False
        else:
            print(f"❌ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_get_corflute_schema():
    """Test getting corflute calculator schema"""
    print("\n" + "="*70)
    print("TEST 4: Get Corflute Calculator Schema")
    print("="*70)
    
    registry = RegistryV3()
    
    try:
        result = registry.execute_tool(
            tool_name="get_tool_schema",
            tool_name="calculate_corflute_signs_shopify"
        )
        
        if result.get("success"):
            print(f"✅ Schema retrieved for {result['name']}")
            print(f"   Platform: {result['platform']}")
            print(f"   Description: {result['short_description'][:100]}...")
            
            # Show parameter count
            params = result.get('parameters', {}).get('properties', {})
            print(f"   Parameters: {len(params)}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            if result.get('similar_tools'):
                print(f"   Similar tools: {result['similar_tools']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_inhouse_corflute_requirements():
    """Test InHouse wrapper corflute support"""
    print("\n" + "="*70)
    print("TEST 5: InHouse Wrapper Corflute Support")
    print("="*70)
    
    registry = RegistryV3()
    
    try:
        result = registry.execute_tool(
            tool_name="inhouse_get_calculator_requirements",
            product_type="corflute_signs"
        )
        
        if result.get("success"):
            reqs = result['requirements']
            print(f"✅ Requirements retrieved for {reqs['product_type']}")
            print(f"   Calculator tool: {reqs['calculator_tool']}")
            print(f"   Parameters: {len(reqs['parameters'])}")
            
            # Check for corflute_signs_shopify
            if reqs['calculator_tool'] == 'calculate_corflute_signs_shopify':
                print(f"✅ Correct calculator mapped: calculate_corflute_signs_shopify")
                return True
            else:
                print(f"❌ Wrong calculator: {reqs['calculator_tool']}")
                return False
        else:
            print(f"❌ Error: {result.get('error')}")
            if result.get('available_types'):
                print(f"   Available types: {result['available_types']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TOOL DISCOVERY SYSTEM VERIFICATION")
    print("="*70)
    
    tests = [
        ("Meta Tools Registration", test_meta_tools),
        ("List Platforms", test_list_platforms),
        ("Search Corflute", test_search_corflute),
        ("Get Corflute Schema", test_get_corflute_schema),
        ("InHouse Corflute Support", test_inhouse_corflute_requirements)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Tool discovery system is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")


if __name__ == "__main__":
    main()
