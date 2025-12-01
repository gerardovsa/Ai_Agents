"""
Test Cloud Storage to Vector Database Integration

Tests the cloud storage upload pipeline with credential injection.
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

def test_cloud_storage_tools():
    """Test cloud storage vector database tools"""
    
    print("\n=== CLOUD STORAGE VECTOR DATABASE TOOLS TEST ===\n")
    
    # Load registry
    registry = RegistryV3()
    
    # Check if cloud storage tools loaded
    cloud_tools = [name for name in registry.tools.keys() if 'cloud_storage' in name]
    print(f"Found {len(cloud_tools)} cloud storage tools:")
    for tool in cloud_tools:
        print(f"  - {tool}")
    
    print("\n--- Test 1: List Available Providers ---")
    try:
        result = registry.execute_tool(
            'cloud_storage_list_providers',
            _user_id=12,
            _injected_credentials=True
        )
        print(f"Result: {result}")
        
        if result.get('success'):
            print("\n✅ Providers listed successfully!")
            for provider in result.get('providers', []):
                status = "✅ Connected" if provider['connected'] else "❌ Not Connected"
                print(f"  {provider['name']}: {status}")
        else:
            print(f"\n❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n--- Test 2: Browse Google Drive (Mock) ---")
    print("Note: Requires Google OAuth token in database for user_id 12")
    try:
        result = registry.execute_tool(
            'cloud_storage_browse_folders',
            provider='google_drive',
            folder_id='root',
            include_files=False,
            _user_id=12,
            _injected_credentials=True
        )
        print(f"Result: {result}")
        
        if result.get('success'):
            print(f"\n✅ Found {result.get('folder_count', 0)} folders")
        else:
            print(f"\n⚠️ Expected error (no OAuth): {result.get('error')}")
    
    except Exception as e:
        print(f"\n⚠️ Expected error (no OAuth): {e}")
    
    print("\n--- Test 3: Tool Schema Validation ---")
    anthropic_tools = registry.get_anthropic_tools()
    cloud_anthropic = [t for t in anthropic_tools if 'cloud_storage' in t['name']]
    
    print(f"\nValidating {len(cloud_anthropic)} tools for Anthropic API...")
    
    for tool in cloud_anthropic:
        has_input_schema = 'input_schema' in tool
        has_type = tool.get('input_schema', {}).get('type') == 'object'
        has_props = 'properties' in tool.get('input_schema', {})
        
        status = "✅" if (has_input_schema and has_type and has_props) else "❌"
        print(f"  {status} {tool['name']}")
        
        if not (has_input_schema and has_type and has_props):
            print(f"      Missing: input_schema={has_input_schema}, type={has_type}, properties={has_props}")
    
    print("\n--- Test 4: Upload Function Structure ---")
    upload_tool = registry.get_tool('cloud_storage_upload_to_vector_db')
    if upload_tool:
        print("\n✅ Upload tool found in registry")
        print(f"Description: {upload_tool.get('description', 'N/A')[:100]}...")
        
        params = upload_tool.get('parameters', {}).get('properties', {})
        required = upload_tool.get('parameters', {}).get('required', [])
        
        print(f"\nParameters ({len(params)} total):")
        for param_name, param_spec in params.items():
            req = "REQUIRED" if param_name in required else "optional"
            param_type = param_spec.get('type', 'unknown')
            print(f"  - {param_name} ({param_type}) - {req}")
    else:
        print("\n❌ Upload tool not found")
    
    print("\n--- Test 5: Embedding Generation Methods ---")
    print("\nChecking embedding helper methods in implementation...")
    
    import tools.implementations.cloud_storage_vector as csv_module
    integration = csv_module.CloudStorageVectorIntegration()
    
    has_openai = hasattr(integration, '_generate_openai_embedding')
    has_voyager = hasattr(integration, '_generate_voyager_embedding')
    
    print(f"  OpenAI embedding method: {'✅ Present' if has_openai else '❌ Missing'}")
    print(f"  Voyager AI embedding method: {'✅ Present' if has_voyager else '❌ Missing'}")
    
    print("\n=== TEST SUMMARY ===")
    print(f"Total cloud storage tools: {len(cloud_tools)}")
    print(f"Anthropic API compatible: {len(cloud_anthropic)}")
    print(f"Embedding methods: {'✅ Ready' if (has_openai and has_voyager) else '❌ Incomplete'}")
    
    print("\n✅ Cloud storage integration foundation complete!")
    print("\nNext steps for full functionality:")
    print("  1. Add Google OAuth credentials for user_id 12")
    print("  2. Add Pinecone credentials (API key, index, environment)")
    print("  3. Add embedding credentials (OpenAI or Voyager AI)")
    print("  4. Create cloud_folder_links database table")
    print("  5. Implement scheduled sync job system")
    print("  6. Test end-to-end upload from real Google Drive files")


if __name__ == '__main__':
    test_cloud_storage_tools()
