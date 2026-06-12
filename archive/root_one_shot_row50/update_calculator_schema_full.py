"""
Update Calculator Schema - Add Short Descriptions and Fix Parameter Mismatches

This script:
1. Adds short_description to all 37 calculator tools
2. Fixes parameter name mismatches between schema and backend
3. Maintains all existing enum arrays and descriptions

Date: December 11, 2025
"""

import json
from pathlib import Path

# Schema file path
SCHEMA_PATH = Path("UI/modules_external/quote-calculator/schema/calculator_tools.json")

# Short descriptions for all 37 tools (50-120 characters, action verb + object + key features)
SHORT_DESCRIPTIONS = {
    # GOD Calculators (database-driven)
    "calculate_business_cards": "Calculate business card printing quotes with quantity, stock type, and finishing options",
    "calculate_flyers": "Calculate flyer and leaflet printing quotes with sizing, paper stock, and print side options",
    "calculate_booklets": "Calculate saddle-stitch booklet quotes with page count, cover stock, and binding specifications",
    "calculate_perfect_bound_books": "Calculate perfect bound book quotes with page count, cover and internal stock specifications",
    "calculate_letterheads": "Calculate letterhead printing quotes with quantity, stock weight, and color specifications",
    "calculate_corflute_signs": "Calculate corflute sign quotes with size, thickness, and single or double-sided printing",
    
    # GOD Calculators (GOD suffix)
    "calculate_flyers_god": "Calculate flyer quotes using database-driven GOD calculator with dynamic pricing tiers",
    "calculate_letterheads_god": "Calculate letterhead quotes using database-driven GOD calculator with stock pricing",
    "calculate_perfect_bound_books_god": "Calculate perfect bound book quotes using database-driven GOD calculator with page pricing",
    "calculate_corflute_signs_god": "Calculate corflute sign quotes using database-driven GOD calculator with material pricing",
    
    # Shopify Calculators (hardcoded pricing)
    "calculate_economical_business_cards_shopify": "Calculate economical business card quotes with budget-friendly stock and finishing options",
    "calculate_premium_business_cards_shopify": "Calculate premium business card quotes with high-quality stock and finish selections",
    "calculate_folded_flyers_shopify": "Calculate folded flyer quotes with DL and A4 sizes, fold types, and stock options",
    "calculate_wire_bound_books_shopify": "Calculate wire bound book quotes with coil binding, page count, and cover specifications",
    "calculate_spiral_bound_books_shopify": "Calculate spiral bound book quotes with plastic coil binding and stock options",
    
    # Shopify Sign Calculators
    "calculate_bollard_signs": "Calculate bollard sign quotes with three-sided printing, sizing, and material specifications",
    "calculate_construction_signs": "Calculate construction site sign quotes with sizing, material thickness, and print sides",
    "calculate_corflute_insert_a_frame": "Calculate corflute A-frame insert quotes with standard sizes and printing specifications",
    "calculate_custom_poster_printing": "Calculate custom poster printing quotes with sizing, paper stock, and finishing options",
    "calculate_custom_vinyl_stickers": "Calculate custom vinyl sticker quotes with sizing, quantity breaks, and finish options",
    "calculate_election_signs": "Calculate election campaign sign quotes with sizing, material, and double-sided printing",
    "calculate_luxury_classic_pull_up_banners": "Calculate luxury pull-up banner quotes with premium materials and printing specifications",
    "calculate_metal_face_a_frame": "Calculate metal A-frame sign quotes with durable construction and double-sided printing",
    
    # Shopify Stationery Calculators
    "calculate_notepads_a4": "Calculate A4 notepad quotes with page count, header printing, and binding options",
    "calculate_notepads_a5": "Calculate A5 notepad quotes with page count, header printing, and binding options",
    "calculate_notepads_a6": "Calculate A6 notepad quotes with page count, header printing, and binding options",
    "calculate_premium_bookmarks": "Calculate premium bookmark quotes with custom sizing, stock weight, and finishing",
    "calculate_printed_letterheads": "Calculate printed letterhead quotes with stock options and color specifications",
    "calculate_saddle_stitch_books": "Calculate saddle stitch book quotes with page count, cover stock, and stapled binding",
    "calculate_selfie_frames": "Calculate selfie frame quotes with custom sizing, material specifications, and artwork",
    "calculate_spiral_bound_books": "Calculate spiral bound book quotes with page count, binding, and stock specifications",
    "calculate_stackable_cubes": "Calculate stackable display cube quotes with sizing, material, and printing specifications",
    "calculate_strut_cards_a3": "Calculate A3 strut card quotes with self-standing display and printing options",
    "calculate_strut_cards_a4": "Calculate A4 strut card quotes with self-standing display and printing options",
    "calculate_with_compliments_slips": "Calculate compliments slip quotes with quantity, stock weight, and color options",
    
    # Query Library Tools
    "get_available_queries": "Get list of available pre-built database queries for stock, pricing, and configuration data",
    "execute_query_library": "Execute pre-built database query by name with optional parameters for data retrieval",
    "get_calculator_requirements": "Get detailed parameter requirements and specifications for a specific calculator tool",
    
    # Stock Tool
    "get_stock_list": "Get comprehensive list of available paper stocks with weights, finishes, and pricing details",
}

# Parameter name fixes (schema_name -> backend_name mapping)
PARAMETER_FIXES = {
    "calculate_construction_signs": {
        "print_sides": "sides"  # Schema has print_sides, backend expects sides
    },
    "calculate_election_signs": {
        "print_sides": "sides"  # Schema has print_sides, backend expects sides
    },
    "calculate_spiral_bound_books": {
        "cover_print": "cover_cellophane"  # Schema has cover_print, backend expects cover_cellophane
    }
}

def load_schema():
    """Load the calculator schema"""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schema(schema):
    """Save the updated schema"""
    with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"✅ Schema saved: {SCHEMA_PATH}")

def add_short_descriptions(schema):
    """Add short_description field to all tools"""
    updated_count = 0
    
    for tool in schema['tools']:
        tool_name = tool['name']
        if tool_name in SHORT_DESCRIPTIONS:
            # Add short_description right after name
            short_desc = SHORT_DESCRIPTIONS[tool_name]
            
            # Insert short_description as second field (after name)
            tool_dict = {}
            for key, value in tool.items():
                tool_dict[key] = value
                if key == 'name':
                    tool_dict['short_description'] = short_desc
            
            # Update tool with new order
            tool.clear()
            tool.update(tool_dict)
            
            updated_count += 1
            print(f"  ✅ Added short_description to: {tool_name}")
        else:
            print(f"  ⚠️  No short_description defined for: {tool_name}")
    
    return updated_count

def fix_parameter_names(schema):
    """Fix parameter name mismatches"""
    fixed_count = 0
    
    for tool in schema['tools']:
        tool_name = tool['name']
        
        if tool_name in PARAMETER_FIXES:
            fixes = PARAMETER_FIXES[tool_name]
            
            # Check if parameters exist
            if 'parameters' not in tool:
                print(f"  ⚠️  {tool_name}: No parameters object found")
                continue
            
            params = tool['parameters']
            
            for old_name, new_name in fixes.items():
                if old_name in params:
                    # Rename parameter - preserve order
                    param_items = list(params.items())
                    new_params = {}
                    for key, value in param_items:
                        if key == old_name:
                            new_params[new_name] = value
                            fixed_count += 1
                            print(f"  ✅ Fixed {tool_name}: '{old_name}' → '{new_name}'")
                        else:
                            new_params[key] = value
                    
                    # Update parameters
                    tool['parameters'] = new_params
                else:
                    print(f"  ⚠️  {tool_name}: Parameter '{old_name}' not found in schema")
    
    return fixed_count

def validate_schema(schema):
    """Validate schema structure"""
    issues = []
    
    # Check all tools have short_description
    for tool in schema['tools']:
        if 'short_description' not in tool:
            issues.append(f"Missing short_description: {tool['name']}")
        elif len(tool['short_description']) < 50 or len(tool['short_description']) > 120:
            issues.append(f"Short description length issue ({len(tool['short_description'])} chars): {tool['name']}")
    
    return issues

def main():
    print("=" * 80)
    print("CALCULATOR SCHEMA UPDATE")
    print("=" * 80)
    print()
    
    # Load schema
    print("📖 Loading schema...")
    schema = load_schema()
    print(f"   Loaded {len(schema['tools'])} tools")
    print()
    
    # Add short descriptions
    print("📝 Adding short descriptions...")
    desc_count = add_short_descriptions(schema)
    print(f"   Added short_description to {desc_count} tools")
    print()
    
    # Fix parameter names
    print("🔧 Fixing parameter name mismatches...")
    fix_count = fix_parameter_names(schema)
    print(f"   Fixed {fix_count} parameter names")
    print()
    
    # Validate
    print("✅ Validating schema...")
    issues = validate_schema(schema)
    if issues:
        print("⚠️  Validation issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("   All tools have valid short descriptions!")
    print()
    
    # Save
    print("💾 Saving updated schema...")
    save_schema(schema)
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Short descriptions added: {desc_count}/{len(schema['tools'])}")
    print(f"✅ Parameter names fixed: {fix_count}")
    print(f"✅ Validation issues: {len(issues)}")
    print()
    print("🎉 Schema update complete!")
    print()
    print("Next steps:")
    print("1. Restart server: BISTART")
    print("2. Test tools: python tests/test_all_calculators.py")
    print("3. Verify short descriptions: search_tools('calculate')")

if __name__ == "__main__":
    main()
