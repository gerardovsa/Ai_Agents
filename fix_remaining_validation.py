"""
Final comprehensive fix - add **kwargs and validation to ALL remaining functions
"""

from pathlib import Path
import re

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

# Functions that still need fixes (from grep results - those NOT showing _validate_no_typos)
remaining_functions = [
    'calculate_business_cards',  # Has **kwargs but no validation
    'calculate_letterheads',
    'calculate_perfect_bound_books_god',
    'calculate_wire_bound_books_shopify',
    'calculate_spiral_bound_books_shopify',
    'calculate_perfect_bound_books_shopify',
    'calculate_saddle_stitch_books',
    'calculate_printed_flyers_shopify',
    'calculate_custom_vinyl_stickers',
    'calculate_printed_letterheads',
    'calculate_with_compliments_slips',
]

# Add validation to functions that already have **kwargs but missing validation
for func_name in remaining_functions:
    # Pattern: Find function with **kwargs, then its docstring, then first line after
    pattern = rf'(def {func_name}\([^)]*\*\*kwargs[^)]*\)\s*->\s*Dict\[str, Any\]:\s*"""(?:[^"]|"(?!""))*""")\s*\n(\s+)'
    
    def add_validation(match):
        header = match.group(1)
        indent = match.group(2)
        
        # Check if validation already exists in next 200 chars
        next_section = content[match.end():match.end()+200]
        if '_validate_no_typos' in next_section:
            return match.group(0)  # Already has validation
        
        validation = f'''\n{indent}# Check for typos in parameter names (unexpected kwargs)
{indent}typo_error = _validate_no_typos(kwargs, "{func_name}")
{indent}if typo_error:
{indent}    return typo_error
{indent}
{indent}'''
        
        return header + validation
    
    content = re.sub(pattern, add_validation, content, flags=re.DOTALL)

# Save
wrapper_file.write_text(content, encoding='utf-8')
print("✅ Added validation to functions with **kwargs but missing validation")
