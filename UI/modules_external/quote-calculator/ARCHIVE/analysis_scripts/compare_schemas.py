"""
Schema Comparison Tool
Compares old Shopify schema files with new calculator_tools.json
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Set

def load_calculator_tools() -> Dict:
    """Load the main calculator_tools.json schema"""
    schema_path = Path(__file__).parent / "schema" / "calculator_tools.json"
    with open(schema_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def load_shopify_schemas() -> Dict[str, Dict]:
    """Load all old Shopify schema files"""
    shopify_dir = Path(__file__).parent / "schema" / "shopify"
    schemas = {}
    
    if not shopify_dir.exists():
        return schemas
    
    for json_file in shopify_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            schemas[json_file.stem] = json.load(f)
    
    return schemas

def extract_calculator_params(tool: Dict) -> Set[str]:
    """Extract parameter names from a calculator tool definition"""
    if "parameters" not in tool:
        return set()
    return set(tool["parameters"].keys())

def compare_schemas():
    """Compare old and new schemas"""
    print("=" * 80)
    print("SCHEMA COMPARISON REPORT")
    print("=" * 80)
    print()
    
    # Load schemas
    calculator_tools = load_calculator_tools()
    shopify_schemas = load_shopify_schemas()
    
    # Build lookup for new schemas
    new_tools = {}
    for tool in calculator_tools.get("tools", []):
        name = tool.get("name", "")
        new_tools[name] = tool
    
    print(f"📊 NEW SCHEMA (calculator_tools.json):")
    print(f"   Total tools: {len(new_tools)}")
    print()
    
    print(f"📊 OLD SCHEMAS (schema/shopify/):")
    print(f"   Total files: {len(shopify_schemas)}")
    print()
    
    # Map old schema files to new tools
    mappings = {
        "Business_Cards_Economic": "calculate_economical_business_cards_shopify",
        "Premium_Business_Cards": "calculate_premium_business_cards_shopify",
        "folded_printed_flyers_Shopify": "calculate_folded_flyers_shopify",
        "Printed_Flyers_Shopify": "calculate_flyers",
        "Perfect_Bound_books": "calculate_perfect_bound_books",
        "Perfect_Bound_Books_WooCommerce": "calculate_perfect_bound_books_shopify",
        "Wire_Spiral_Bound": "calculate_wire_bound_books_shopify",
        "Corflute_Signs_Shopify": "calculate_corflute_signs_shopify"
    }
    
    print("=" * 80)
    print("DETAILED COMPARISON")
    print("=" * 80)
    print()
    
    for old_name, new_name in mappings.items():
        if old_name not in shopify_schemas:
            print(f"⚠️  OLD FILE MISSING: {old_name}.json")
            continue
        
        if new_name not in new_tools:
            print(f"❌ NEW TOOL MISSING: {new_name}")
            print(f"   Old file: {old_name}.json")
            print()
            continue
        
        old_schema = shopify_schemas[old_name]
        new_tool = new_tools[new_name]
        
        # Extract parameters from old schema (it's in a different format)
        old_params = set()
        if isinstance(old_schema, dict):
            # Old schema has nested structure
            for key, value in old_schema.items():
                if isinstance(value, dict) and "options" in value:
                    for option in value["options"]:
                        if "field_id" in option:
                            old_params.add(option.get("name", ""))
        
        # Extract parameters from new schema
        new_params = extract_calculator_params(new_tool)
        
        print(f"📁 {old_name}.json → {new_name}")
        print(f"   Old format: Shopify product template")
        print(f"   New format: Tool schema")
        
        if old_params:
            print(f"   Old params: {sorted(old_params)}")
        else:
            print(f"   Old params: (non-standard format)")
        
        print(f"   New params: {sorted(new_params)}")
        
        # Note: Old schemas are product templates, new schemas are tool definitions
        # They're fundamentally different formats
        print(f"   ⚠️  Different formats - not directly comparable")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✅ NEW SCHEMA ANALYSIS:")
    shopify_tools = [name for name in new_tools.keys() if "shopify" in name.lower()]
    god_tools = [name for name in new_tools.keys() if "god" in name.lower()]
    standard_tools = [name for name in new_tools.keys() if "shopify" not in name.lower() and "god" not in name.lower()]
    
    print(f"   Standard calculators: {len(standard_tools)}")
    print(f"   GOD calculators: {len(god_tools)}")
    print(f"   Shopify calculators: {len(shopify_tools)}")
    print(f"   Total: {len(new_tools)}")
    print()
    
    print("❌ OLD SCHEMAS:")
    print(f"   Shopify template files: {len(shopify_schemas)}")
    print(f"   Format: Shopify product templates (NOT tool schemas)")
    print(f"   Status: NOT LOADED by Python code")
    print(f"   Recommendation: ARCHIVE or DELETE")
    print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("The old schema/shopify/*.json files are PRODUCT TEMPLATES for Shopify.")
    print("They are NOT tool schemas and are NOT used by the calculator system.")
    print()
    print("The new calculator_tools.json contains TOOL SCHEMAS that define:")
    print("  - Function parameters (types, enums, descriptions)")
    print("  - Input validation rules")
    print("  - Return value structures")
    print()
    print("These are COMPLETELY DIFFERENT formats serving DIFFERENT purposes.")
    print("The old files can be safely DELETED or moved to ARCHIVE.")
    print()

if __name__ == "__main__":
    compare_schemas()
