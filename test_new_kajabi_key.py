"""Test new Kajabi API key with proper permissions"""
import requests
import json
import base64

# New credentials
client_id = 'oKXzcVFzcFHYTF7AXa5Rc3D5'
client_secret = 'hCfZJ5o6oDT5yJu2Ky4oUkZS'

print("🔐 Testing Kajabi OAuth with new API key...")

# Step 1: Get OAuth token
token_response = requests.post(
    'https://api.kajabi.com/v1/oauth/token',
    data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
)

print(f"OAuth Status: {token_response.status_code}")

if token_response.status_code == 200:
    token_data = token_response.json()
    access_token = token_data['access_token']
    
    # Decode JWT to check scope
    parts = access_token.split('.')
    payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    
    print(f"✅ Token obtained successfully")
    print(f"📋 Scope: {decoded['scope']}")
    print(f"👤 User ID: {decoded['user_id']}")
    print(f"🏢 Account ID: {decoded['account_id']}")
    
    # Step 2: Test products endpoint
    print("\n📦 Testing products endpoint...")
    products_response = requests.get(
        'https://api.kajabi.com/v1/products?per_page=3',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print(f"Products Status: {products_response.status_code}")
    
    if products_response.status_code == 200:
        products_data = products_response.json()
        print(f"✅ SUCCESS! Found {len(products_data.get('data', []))} products")
        print("\nProducts:")
        for product in products_data.get('data', [])[:3]:
            name = product.get('attributes', {}).get('name', 'N/A')
            product_id = product.get('id')
            print(f"  - {product_id}: {name}")
    else:
        print(f"❌ Failed: {products_response.status_code}")
        print(products_response.text[:500])
        
    # Step 3: Test via tool registry
    print("\n🛠️ Testing via Tool Registry...")
    from tools.registry_v3 import RegistryV3
    
    registry = RegistryV3()
    result = registry.execute_tool(
        tool_name='kajabi_list_products',
        api_key=client_id,
        api_secret=client_secret,
        page=1,
        per_page=5
    )
    
    print(f"✅ Tool execution successful!")
    print(f"Found {len(result.get('data', []))} products via registry")
    
else:
    print(f"❌ OAuth failed: {token_response.status_code}")
    print(token_response.text)
