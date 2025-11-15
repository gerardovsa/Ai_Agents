"""
Check which smart tools have integrated instructions in their schemas
"""

import os
import json
from pathlib import Path

def check_smart_tools_instructions():
    """Scan all schema files for smart tools and check if they have instructions"""
    
    schemas_dir = Path(r'C:\Users\gpoli\GIT\AI_agents\tools\schemas')
    results = []
    
    for schema_file in schemas_dir.glob('*.json'):
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
                
            tools = schema_data.get('tools', [])
            
            for tool in tools:
                tool_name = tool.get('name', '')
                
                # Check if it's a smart tool
                if 'smart_' in tool_name.lower():
                    has_instructions = 'instructions' in tool
                    results.append({
                        'schema_file': schema_file.name,
                        'tool_name': tool_name,
                        'has_instructions': has_instructions,
                        'description': tool.get('description', '')[:100]
                    })
        
        except Exception as e:
            print(f"Error loading {schema_file.name}: {e}")
            continue
    
    # Print results
    print("\n" + "="*100)
    print("SMART TOOLS INSTRUCTIONS CHECK")
    print("="*100 + "\n")
    
    print(f"{'STATUS':<6} | {'SCHEMA FILE':<40} | {'TOOL NAME':<50}")
    print("-"*100)
    
    for result in sorted(results, key=lambda x: (not x['has_instructions'], x['schema_file'])):
        status = "✅ YES" if result['has_instructions'] else "❌ NO"
        print(f"{status:<6} | {result['schema_file']:<40} | {result['tool_name']:<50}")
    
    # Summary
    with_instructions = len([r for r in results if r['has_instructions']])
    without_instructions = len([r for r in results if not r['has_instructions']])
    
    print("\n" + "="*100)
    print("SUMMARY:")
    print("="*100)
    print(f"  ✅ With integrated instructions: {with_instructions}")
    print(f"  ❌ Without instructions: {without_instructions}")
    print(f"  📊 Total smart tools found: {len(results)}")
    print(f"  📈 Completion rate: {with_instructions/len(results)*100:.1f}%")
    
    # List tools without instructions
    if without_instructions > 0:
        print("\n" + "="*100)
        print("TOOLS NEEDING INSTRUCTIONS:")
        print("="*100)
        
        for result in [r for r in results if not r['has_instructions']]:
            print(f"\n📋 {result['tool_name']}")
            print(f"   File: {result['schema_file']}")
            print(f"   Description: {result['description']}...")

if __name__ == "__main__":
    check_smart_tools_instructions()
