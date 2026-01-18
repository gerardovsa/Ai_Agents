from AI_infrastructure.shared.database_utils import execute_query
import json

try:
    # First check if any credentials exist
    all_creds = execute_query(
        'SELECT id, user_id, platform FROM ai_infrastructure.user_platform_credentials',
        fetch_mode='all'
    )
    
    print('All Platform Credentials:')
    for cred in all_creds:
        print(f'  ID: {cred["id"]}, User: {cred["user_id"]}, Platform: {cred["platform"]}')
    
    print('\nSearching for Shopify credentials...')
    creds = execute_query(
        'SELECT user_id, platform, credentials FROM ai_infrastructure.user_platform_credentials WHERE platform = %s',
        ('shopify',),
        fetch_mode='one'
    )
    
    if not creds:
        print('❌ No Shopify credentials found!')
        exit(1)
    
    print('\nShopify Credentials:')
    print(f'User ID: {creds["user_id"]}')
    print(f'Platform: {creds["platform"]}')
    
    cred_data = creds["credentials"]
    if isinstance(cred_data, str):
        cred_data = json.loads(cred_data)
    print(f'Shop Name: {cred_data.get("shop_name", "N/A")}')
    print(f'Shop Domain: {cred_data.get("shop_domain", "N/A")}')
    print(f'API Version: {cred_data.get("api_version", "N/A")}')
    
    access_token = cred_data.get('access_token', '')
    if access_token:
        print(f'Access Token: {access_token[:20]}... (length: {len(access_token)})')
    else:
        print('Access Token: MISSING')
        
    # Test Shopify API connection
    print('\nTesting Shopify API connection...')
    import shopify
    
    shop_url = f"{cred_data['shop_domain']}"
    api_version = cred_data.get('api_version', '2025-10')
    
    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)
    
    # Try to fetch shop info
    shop = shopify.Shop.current()
    print(f'✅ Connected to: {shop.name}')
    print(f'   Email: {shop.email}')
    print(f'   Currency: {shop.currency}')
    
    shopify.ShopifyResource.clear_session()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
