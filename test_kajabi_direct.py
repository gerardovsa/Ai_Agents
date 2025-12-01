"""Test Kajabi directly without registry to isolate the issue"""
from tools.implementations.kajabi import KajabiTools, KajabiError

# New working credentials
client_id = 'oKXzcVFzcFHYTF7AXa5Rc3D5'
client_secret = 'hCfZJ5o6oDT5yJu2Ky4oUkZS'

print("🧪 Testing KajabiTools class directly...")

try:
    # Create fresh instance
    kajabi = KajabiTools()
    
    # Test list_products
    print("\n1️⃣ Testing list_products...")
    result = kajabi.list_products(
        api_key=client_id,
        api_secret=client_secret,
        page=1,
        per_page=5
    )
    
    print(f"✅ SUCCESS! Found {len(result.get('data', []))} products")
    for product in result.get('data', [])[:3]:
        attrs = product.get('attributes', {})
        name = attrs.get('name', 'N/A')
        pid = product.get('id')
        print(f"  - {pid}: {name}")
    
    # Test list_offers
    print("\n2️⃣ Testing list_offers...")
    offers = kajabi.list_offers(
        api_key=client_id,
        api_secret=client_secret,
        page=1,
        per_page=5
    )
    print(f"✅ SUCCESS! Found {len(offers.get('data', []))} offers")
    
    # Test list_members
    print("\n3️⃣ Testing list_members...")
    members = kajabi.list_members(
        api_key=client_id,
        api_secret=client_secret,
        page=1,
        per_page=5
    )
    print(f"✅ SUCCESS! Found {len(members.get('data', []))} members")
    
    print("\n\n🎉 ALL TESTS PASSED!")
    print("✅ KajabiTools class working perfectly")
    print("✅ OAuth 2.0 authentication working")
    print("✅ All API endpoints accessible")
    
except KajabiError as e:
    print(f"❌ Kajabi Error: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
