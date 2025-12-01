"""Debug Kajabi API calls to see what's different"""
import requests

client_id = 'oKXzcVFzcFHYTF7AXa5Rc3D5'
client_secret = 'hCfZJ5o6oDT5yJu2Ky4oUkZS'

print("🔍 Debugging Kajabi API calls...")

# Step 1: Get OAuth token (this works)
print("\n1️⃣ Getting OAuth token...")
token_response = requests.post(
    'https://api.kajabi.com/v1/oauth/token',
    data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    },
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
print(f"OAuth Status: {token_response.status_code}")

if token_response.status_code == 200:
    access_token = token_response.json()['access_token']
    print(f"✅ Token obtained: {access_token[:20]}...")
    
    # Step 2: Try products endpoint with exact same headers as working test
    print("\n2️⃣ Testing products endpoint (simple approach)...")
    products_response = requests.get(
        'https://api.kajabi.com/v1/products?per_page=3',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    print(f"Products Status: {products_response.status_code}")
    
    if products_response.status_code == 200:
        products = products_response.json()
        print(f"✅ Found {len(products.get('data', []))} products")
    else:
        print(f"❌ Error: {products_response.text}")
    
    # Step 3: Try with additional headers (like KajabiTools class uses)
    print("\n3️⃣ Testing products endpoint (with Content-Type + Accept headers)...")
    products_response2 = requests.get(
        'https://api.kajabi.com/v1/products?per_page=3',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    print(f"Products Status: {products_response2.status_code}")
    
    if products_response2.status_code == 200:
        products = products_response2.json()
        print(f"✅ Found {len(products.get('data', []))} products")
    else:
        print(f"❌ Error: {products_response2.text}")
        
    # Step 4: Try with params dict (like _make_request uses)
    print("\n4️⃣ Testing products endpoint (with params dict)...")
    products_response3 = requests.get(
        'https://api.kajabi.com/v1/products',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        params={'page': 1, 'per_page': 5}
    )
    print(f"Products Status: {products_response3.status_code}")
    
    if products_response3.status_code == 200:
        products = products_response3.json()
        print(f"✅ Found {len(products.get('data', []))} products")
    else:
        print(f"❌ Error: {products_response3.text}")

else:
    print(f"❌ OAuth failed: {token_response.text}")
