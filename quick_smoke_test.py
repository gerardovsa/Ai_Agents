"""Quick smoke test for meta tools"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))
sys.path.insert(0, str(project_root / 'tools'))

print("="*70)
print("QUICK SMOKE TEST - Meta Tools & Corflute")
print("="*70)

try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    # Test 1: Check meta tools exist
    print("\n1. Checking meta tools...")
    meta_tools = ["list_platform_tools", "search_tools", "get_tool_schema", "list_available_platforms"]
    for tool in meta_tools:
        status = "✅" if tool in registry.tools else "❌"
        print(f"   {status} {tool}")
    
    # Test 2: Check corflute calculator exists
    print("\n2. Checking corflute calculator...")
    if "calculate_corflute_signs_shopify" in registry.tools:
        print("   ✅ calculate_corflute_signs_shopify EXISTS")
    else:
        print("   ❌ calculate_corflute_signs_shopify NOT FOUND")
    
    # Test 3: Check InHouse tools exist
    print("\n3. Checking InHouse tools...")
    inhouse_tools = ["inhouse_get_calculator_requirements", "inhouse_calculate_quote"]
    for tool in inhouse_tools:
        status = "✅" if tool in registry.tools else "❌"
        print(f"   {status} {tool}")
    
    # Test 4: Quick test list_available_platforms
    print("\n4. Testing list_available_platforms...")
    try:
        result = registry.execute_tool(tool_name="list_available_platforms")
        if result.get("success"):
            print(f"   ✅ SUCCESS - {result['platform_count']} platforms, {result['total_tools']} tools")
        else:
            print(f"   ❌ FAILED - {result.get('error')}")
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
    
    # Test 5: Quick test search_tools
    print("\n5. Testing search_tools('corflute')...")
    try:
        result = registry.execute_tool(tool_name="search_tools", query="corflute")
        if result.get("success"):
            print(f"   ✅ SUCCESS - {result['match_count']} matches found")
            if result['match_count'] > 0:
                print(f"   Top match: {result['matches'][0]['name']}")
        else:
            print(f"   ❌ FAILED - {result.get('error')}")
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
    
    print("\n" + "="*70)
    print("SMOKE TEST COMPLETE")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
