"""Check which tools have intelligence layers added"""
import json
from pathlib import Path

def check_intelligence_layers():
    """Report on intelligence layer completion"""
    schemas_dir = Path("tools/schemas")
    
    total_files = 0
    total_tools = 0
    tools_with_intelligence = 0
    tools_with_memory = 0
    
    for schema_file in schemas_dir.glob("*.json"):
        total_files += 1
        with open(schema_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for tool in data.get('tools', []):
            total_tools += 1
            
            if 'tool_intelligence' in tool:
                tools_with_intelligence += 1
            
            if 'memory_context' in tool:
                tools_with_memory += 1
    
    print(f"Intelligence Layer Status")
    print(f"  Total files: {total_files}")
    print(f"  Total tools: {total_tools}")
    print(f"  Tools with intelligence: {tools_with_intelligence} ({tools_with_intelligence/total_tools*100:.1f}%)")
    print(f"  Tools with memory: {tools_with_memory} ({tools_with_memory/total_tools*100:.1f}%)")
    
    completion = (tools_with_intelligence + tools_with_memory) / (total_tools * 2) * 100
    print(f"\nOverall completion: {completion:.1f}%")

if __name__ == "__main__":
    check_intelligence_layers()
