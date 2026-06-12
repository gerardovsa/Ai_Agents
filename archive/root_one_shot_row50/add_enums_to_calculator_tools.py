"""
Add enum guidance to calculator_tools.json parameters
This fixes the Requirements test by adding enum arrays based on parameter descriptions
"""

import json
import re
from pathlib import Path

# Load the JSON file
json_path = Path("tools/schemas/calculator_tools.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Common enum mappings based on parameter names and descriptions
ENUM_MAPPINGS = {
    # Print modes
    "print_mode": ["single_sided", "double_sided", "no_print"],
    "print_type": ["single_sided", "double_sided"],
    "cover_print_mode": ["single_sided", "double_sided"],
    "internal_print_mode": ["single_sided", "double_sided", "black_white", "mixed"],
    
    # Cellophane/finish types
    "cello_type": ["none", "gloss_both_sides", "matt_both_sides", "gloss_front_only", "matt_front_only"],
    "celloglaze": ["none", "gloss", "matt", "1_side_gloss", "2_side_gloss", "1_side_matt", "2_side_matt"],
    "cover_cellophane": ["No Cellophane", "Gloss Cellophane", "Matt Cellophane"],
    "cellophane": ["None", "Gloss", "Matt"],
    "cover_lamination": ["none", "gloss", "matt"],
    "finish": ["none", "gloss", "matt", "uncoated"],
    
    # Stock types
    "stock_type": ["standard", "premium", "satin", "uncoated"],
    "cover_stock": ["350GSM Satin", "300GSM Satin", "250GSM Satin"],
    "inner_stock": ["100GSM Uncoated", "100GSM Satin", "80GSM Uncoated", "80GSM Satin"],
    "stock": ["Satin 150GSM", "Satin 300GSM", "Uncoated Bond 80GSM", "Satin 128GSM", "Satin 250GSM", "Satin 350GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"],
    
    # Sizes
    "finish_size": ["90x55mm", "90x50mm", "85x55mm", "A4", "A5", "A6", "DL"],
    "size": ["A4", "A5", "A6", "DL", "A3", "6pp A4"],
    
    # Fold types
    "fold_type": ["Single Fold", "Double Fold", "Triple Fold"],
    
    # Common GSM values (integers)
    "stock_gsm": [128, 150, 170, 200, 250, 300, 350, 400],
    "cover_stock_gsm": [250, 300, 350, 400],
    "internal_stock_gsm": [80, 100, 128, 150, 170],
    
    # Quantity ranges (common values)
    "quantity": [100, 250, 500, 1000, 2000, 5000, 10000],
    
    # Orientation
    "orientation": ["portrait", "landscape"],
    
    # Colors
    "colour": [True, False],
    "color": [True, False],
    "double_sided": [True, False],
    "front_cover_pvc": [True, False],
}

# Function to extract enum values from description text
def extract_enums_from_description(param_type, description):
    """Extract potential enum values from parameter description"""
    if not description:
        return None
    
    # Look for quoted values like 'value1', 'value2'
    quoted_pattern = r"'([^']+)'"
    matches = re.findall(quoted_pattern, description)
    if matches and len(matches) > 1:
        return matches
    
    # Look for values after colons like "Options: A, B, C"
    colon_pattern = r":\s*([A-Za-z0-9_,\s-]+)"
    colon_match = re.search(colon_pattern, description)
    if colon_match:
        values_str = colon_match.group(1)
        # Split by comma and clean
        values = [v.strip() for v in values_str.split(',') if v.strip()]
        if len(values) > 1:
            return values
    
    return None

# Process each tool
modified_count = 0
param_count = 0

for tool in data["tools"]:
    tool_name = tool.get("name", "unknown")
    parameters = tool.get("parameters", {})
    
    for param_name, param_def in parameters.items():
        param_type = param_def.get("type")
        description = param_def.get("description", "")
        
        # Skip if already has enum
        if "enum" in param_def:
            continue
        
        param_count += 1
        enum_values = None
        
        # 1. Check if param_name matches common mappings
        if param_name in ENUM_MAPPINGS:
            enum_values = ENUM_MAPPINGS[param_name]
        
        # 2. Try to extract from description
        elif param_type in ["string", "integer"]:
            enum_values = extract_enums_from_description(param_type, description)
        
        # Add enum if found
        if enum_values:
            param_def["enum"] = enum_values
            modified_count += 1
            print(f"✓ {tool_name}.{param_name}: Added enum with {len(enum_values)} values")

# Save updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Total parameters checked: {param_count}")
print(f"  Parameters with enums added: {modified_count}")
print(f"  Updated file: {json_path}")
print(f"{'='*60}")
