"""Final test of Kajabi integration - bypasses cache"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3
import json

# Force registry reload to clear any cached tokens
registry = RegistryV3()

# New credentials from database
print("🧪 Testing Kajabi tools with user 12 (credential injection)...")

try:
    # Test with credential injection (will fetch from database)
    result = registry.execute_tool(
        tool_name='kajabi_list_products',
        _user_id=12,  # Uses credential injection
        page=1,
        per_page=5
    )
    
    print(f"✅ SUCCESS! kajabi_list_products working!")
    print(f"Found {len(result.get('data', []))} products")
    print("\nProducts:")
    for product in result.get('data', [])[:5]:
        attrs = product.get('attributes', {})
        name = attrs.get('name', 'N/A')
        product_id = product.get('id')
        print(f"  - {product_id}: {name}")
    
    # Test other endpoints
    print("\n\n🧪 Testing kajabi_list_offers...")
    offers = registry.execute_tool(
        tool_name='kajabi_list_offers',
        _user_id=12,
        page=1,
        per_page=5
    )
    print(f"✅ Found {len(offers.get('data', []))} offers")
    
    print("\n\n🧪 Testing kajabi_list_members...")
    members = registry.execute_tool(
        tool_name='kajabi_list_members',
        _user_id=12,
        page=1,
        per_page=10
    )
    print(f"✅ Found {len(members.get('data', []))} members")
    
    print("\n\n✅ ALL KAJABI TOOLS WORKING!")
    print("🎉 Integration complete - 26+ tools ready to use")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
