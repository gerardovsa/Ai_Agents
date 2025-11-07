"""
Debug: Print actual tool definitions being sent to Claude
"""

import sys
sys.path.insert(0, 'C:\\Users\\gpoli\\GIT\\AI_agents')

from tools.registry import ToolRegistry
import json

registry = ToolRegistry()
all_tools = registry.list_tools()

print("="*70)
print("🔍 Checking Tool Definition Format")
print("="*70)

# Get Google Docs tool as example
google_docs_tools = [t for t in all_tools if 'google_docs' in t.get('name', '').lower()]

if google_docs_tools:
    sample_tool = google_docs_tools[0]
    
    print(f"\n📋 Sample Tool (from registry):")
    print(f"   Name: {sample_tool.get('name')}")
    print(f"   Description: {sample_tool.get('description', '')[:80]}...")
    print(f"   Has parameters: {bool(sample_tool.get('parameters'))}")
    
    print(f"\n🔧 Full Tool Definition:")
    print(json.dumps(sample_tool, indent=2)[:1000])
    
    # Check if it has the right format for Anthropic
    print(f"\n Anthropic Tool Format Requirements:")
    print(f"   ✓ Has 'name': {bool(sample_tool.get('name'))}")
    print(f"   ✓ Has 'description': {bool(sample_tool.get('description'))}")
    print(f"   ✓ Has 'input_schema': {bool(sample_tool.get('input_schema'))}")
    
    if not sample_tool.get('input_schema'):
        print(f"\n PROBLEM: Tool missing 'input_schema' field!")
        print(f"   Claude requires 'input_schema', not 'parameters'")
        print(f"   Current keys: {list(sample_tool.keys())}")
else:
    print(" No Google Docs tools found!")

print("\n" + "="*70)
