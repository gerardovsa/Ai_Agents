import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.intelligent_discovery import SemanticToolSearch
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Check what text is being embedded for google_calendar_check_availability
tool_name = 'google_calendar_check_availability'
tool_data = registry.tools.get(tool_name)

if tool_data:
    short_desc = tool_data.get('short_description', '')
    long_desc = tool_data.get('description', '')
    platform = tool_data.get('platform', '')
    category = tool_data.get('category', '')
    
    # This is what SemanticToolSearch embeds
    text = f"{tool_name} {short_desc} {long_desc} {platform} {category}"
    
    print(f'Tool: {tool_name}')
    print(f'\nEmbedded Text:')
    print(f'"{text[:200]}..."')
    print(f'\nLength: {len(text)} characters')
    
    # Now initialize search and check if it has this tool
    search = SemanticToolSearch(registry)
    
    if tool_name in search.tool_embeddings:
        print(f'\n✅ Tool IS in semantic search embeddings')
        metadata = search.tool_metadata.get(tool_name, {})
        print(f'Metadata short_description: {metadata.get("short_description", "MISSING")}')
    else:
        print(f'\n❌ Tool NOT FOUND in semantic search embeddings!')
