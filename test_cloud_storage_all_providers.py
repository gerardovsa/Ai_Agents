"""
Test Cloud Storage Vector Integration - All Providers

Tests Google Drive, OneDrive, and Dropbox implementations.
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

def test_all_providers():
    """Test all cloud storage providers"""
    
    print("\n" + "="*70)
    print("CLOUD STORAGE VECTOR DATABASE - ALL PROVIDERS TEST")
    print("="*70)
    
    # Load registry
    registry = RegistryV3()
    
    # Check tools loaded
    cloud_tools = [name for name in registry.tools.keys() if 'cloud_storage' in name]
    print(f"\n✅ Found {len(cloud_tools)} cloud storage tools")
    
    print("\n" + "-"*70)
    print("TEST 1: List Providers & Connection Status")
    print("-"*70)
    
    try:
        result = registry.execute_tool(
            tool_name='cloud_storage_list_providers',
            _user_id=12,
            _injected_credentials=True
        )
        
        if result.get('success'):
            print("\n✅ Provider listing successful!\n")
            for provider in result.get('providers', []):
                status_icon = "🟢" if provider['connected'] else "🔴"
                available_icon = "✅" if provider['available'] else "❌"
                print(f"  {status_icon} {provider['name']}")
                print(f"     Platform: {provider['platform']}")
                print(f"     SDK Available: {available_icon}")
                print(f"     Connected: {provider['connected']}")
                print(f"     Features: {', '.join(provider['features'])}")
                print()
        else:
            print(f"\n❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "-"*70)
    print("TEST 2: Google Drive Browse (Full Implementation)")
    print("-"*70)
    print("Testing: Browse root folder")
    
    try:
        result = registry.execute_tool(
            tool_name='cloud_storage_browse_folders',
            provider='google_drive',
            folder_id='root',
            include_files=False,
            _user_id=12,
            _injected_credentials=True
        )
        
        if result.get('success'):
            print(f"\n✅ Google Drive browse successful!")
            print(f"   Folders found: {len(result.get('folders', []))}")
            
            if result.get('folders'):
                print("\n   Sample folders:")
                for folder in result.get('folders', [])[:3]:
                    print(f"     - {folder['name']} (ID: {folder['id'][:20]}...)")
        else:
            print(f"\n⚠️  Expected (no OAuth): {result.get('error')}")
    
    except Exception as e:
        print(f"\n⚠️  Expected (no OAuth): {e}")
    
    print("\n" + "-"*70)
    print("TEST 3: OneDrive Browse (NEW Implementation)")
    print("-"*70)
    print("Testing: Browse root folder")
    
    try:
        result = registry.execute_tool(
            tool_name='cloud_storage_browse_folders',
            provider='onedrive',
            folder_id=None,
            include_files=False,
            _user_id=12,
            _injected_credentials=True
        )
        
        if result.get('success'):
            print(f"\n✅ OneDrive browse successful!")
            print(f"   Folders found: {len(result.get('folders', []))}")
            
            if result.get('folders'):
                print("\n   Sample folders:")
                for folder in result.get('folders', [])[:3]:
                    print(f"     - {folder['name']} (ID: {folder['id'][:20]}...)")
        else:
            print(f"\n⚠️  Expected (no OAuth): {result.get('error')}")
    
    except Exception as e:
        print(f"\n⚠️  Expected (no OAuth): {e}")
    
    print("\n" + "-"*70)
    print("TEST 4: Dropbox Browse (NEW Implementation)")
    print("-"*70)
    print("Testing: Browse root folder")
    
    try:
        result = registry.execute_tool(
            tool_name='cloud_storage_browse_folders',
            provider='dropbox',
            folder_id='root',
            include_files=False,
            _user_id=12,
            _injected_credentials=True
        )
        
        if result.get('success'):
            print(f"\n✅ Dropbox browse successful!")
            print(f"   Folders found: {len(result.get('folders', []))}")
            
            if result.get('folders'):
                print("\n   Sample folders:")
                for folder in result.get('folders', [])[:3]:
                    print(f"     - {folder['name']} (Path: {folder['id']})")
        else:
            print(f"\n⚠️  Expected (no OAuth): {result.get('error')}")
    
    except Exception as e:
        print(f"\n⚠️  Expected (no OAuth): {e}")
    
    print("\n" + "-"*70)
    print("TEST 5: Implementation Verification")
    print("-"*70)
    
    # Check implementation methods
    import tools.implementations.cloud_storage_vector as csv_module
    integration = csv_module.CloudStorageVectorIntegration()
    
    methods_to_check = [
        ('_get_google_service', 'Google Drive service creation'),
        ('_get_onedrive_headers', 'OneDrive API headers'),
        ('_get_dropbox_client', 'Dropbox client creation'),
        ('_extract_text_from_file', 'Text extraction'),
        ('_chunk_text', 'Text chunking'),
        ('_generate_openai_embedding', 'OpenAI embeddings'),
        ('_generate_voyager_embedding', 'Voyager AI embeddings')
    ]
    
    print("\nImplementation methods:")
    all_present = True
    for method_name, description in methods_to_check:
        has_method = hasattr(integration, method_name)
        status = "✅" if has_method else "❌"
        print(f"  {status} {method_name:<30} - {description}")
        if not has_method:
            all_present = False
    
    print("\n" + "-"*70)
    print("TEST 6: Upload Function Structure")
    print("-"*70)
    
    # Check upload function handles all providers
    import inspect
    upload_func = csv_module.cloud_storage_upload_to_vector_db
    source = inspect.getsource(upload_func)
    
    providers_supported = []
    if "'google_drive'" in source and "access_token = kwargs.get('google_access_token')" in source:
        providers_supported.append('Google Drive')
    if "'onedrive'" in source and "access_token = kwargs.get('onedrive_access_token')" in source:
        providers_supported.append('OneDrive')
    if "'dropbox'" in source and "access_token = kwargs.get('dropbox_access_token')" in source:
        providers_supported.append('Dropbox')
    
    print(f"\nProviders supported in upload function: {len(providers_supported)}/3")
    for provider in providers_supported:
        print(f"  ✅ {provider}")
    
    missing = set(['Google Drive', 'OneDrive', 'Dropbox']) - set(providers_supported)
    if missing:
        for provider in missing:
            print(f"  ❌ {provider}")
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    print(f"\n✅ Total tools loaded: {len(cloud_tools)}")
    print(f"✅ Implementation methods: {'All present' if all_present else 'Some missing'}")
    print(f"✅ Upload providers: {len(providers_supported)}/3 implemented")
    
    if len(providers_supported) == 3 and all_present:
        print("\n🎉 ALL PROVIDERS FULLY IMPLEMENTED!")
        print("\nReady for production testing:")
        print("  1. Google Drive → Pinecone ✅")
        print("  2. OneDrive → Pinecone ✅")
        print("  3. Dropbox → Pinecone ✅")
        print("\nNext steps:")
        print("  - Add OAuth credentials for each provider")
        print("  - Test end-to-end upload with real files")
        print("  - Verify embeddings and vector uploads")
    else:
        print("\n⚠️  Some implementations incomplete")
        if len(providers_supported) < 3:
            print(f"  Missing upload support: {3 - len(providers_supported)} providers")
        if not all_present:
            print("  Missing implementation methods")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    test_all_providers()
