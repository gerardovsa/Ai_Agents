"""
Batch fix ALL calculator wrapper functions:
1. Add **kwargs to function signatures that don't have it
2. Add typo validation after docstrings
"""

import re
from pathlib import Path

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

# List of all calculator function names (44 total)
calculator_functions = [
    'calculate_business_cards',
    'calculate_flyers',
    'calculate_booklets',
    'calculate_perfect_bound_books',
    'calculate_letterheads',
    'calculate_flyers_god',
    'calculate_letterheads_god',
    'calculate_perfect_bound_books_god',
    'calculate_corflute_signs_shopify',
    'calculate_economical_business_cards_shopify',
    'calculate_premium_business_cards_shopify',
    'calculate_folded_flyers_shopify',
    'calculate_printed_flyers_shopify',
    'calculate_wire_bound_books_shopify',
    'calculate_spiral_bound_books_shopify',
    'calculate_perfect_bound_books_shopify',
    'calculate_saddle_stitch_books_shopify',
    'calculate_spiral_books_simple_shopify',
    'calculate_saddle_stitch_books',
    'calculate_bollard_signs',
    'calculate_construction_signs',
    'calculate_election_signs',
    'calculate_corflute_insert_a_frame',
    'calculate_metal_face_a_frame',
    'calculate_luxury_classic_pull_up_banners',
    'calculate_premium_pull_up_banners',
    'calculate_selfie_frames',
    'calculate_stackable_cubes',
    'calculate_strut_cards_a3',
    'calculate_strut_cards_a4',
    'calculate_strut_cards_a5',
    'calculate_counter_strut_cards_a3',
    'calculate_counter_strut_cards_a4',
    'calculate_counter_strut_cards_a5',
    'calculate_custom_poster_printing',
    'calculate_custom_vinyl_stickers',
    'calculate_premium_bookmarks',
    'calculate_printed_letterheads',
    'calculate_with_compliments_slips',
    'calculate_notepads_a4',
    'calculate_notepads_a5',
    'calculate_notepads_a6',
    'calculate_spiral_bound_books',  # Last one (line 5211)
]

def fix_function(func_name: str, content: str) -> str:
    """Add **kwargs and validation to one function"""
    
    # Pattern to find the function definition
    pattern = rf'(def {func_name}\([^)]+?)(\) -> Dict\[str, Any\]:)'
    
    def add_kwargs(match):
        params = match.group(1)
        closing = match.group(2)
        
        # Skip if already has **kwargs
        if '**kwargs' in params:
            return match.group(0)
        
        # Add **kwargs
        return params + ',\n    **kwargs  # Absorb internal registry params\n' + closing
    
    content = re.sub(pattern, add_kwargs, content, flags=re.DOTALL)
    
    # Now add validation after docstring
    # Pattern: function def with **kwargs, followed by docstring, then some code (NOT validation)
    pattern2 = rf'(def {func_name}\([^)]*\*\*kwargs[^)]*\) -> Dict\[str, Any\]:\s+"""[^"]*""")\s+([^#\n])'
    
    def add_validation(match):
        header = match.group(1)
        next_char = match.group(2)
        
        # Skip if validation already exists
        if '_validate_no_typos' in header or '_validate_no_typos' in content[match.start():match.start()+500]:
            return match.group(0)
        
        validation = f'''
    # Check for typos in parameter names (unexpected kwargs)
    typo_error = _validate_no_typos(kwargs, "{func_name}")
    if typo_error:
        return typo_error
    
    {next_char}'''
        
        return header + validation
    
    content = re.sub(pattern2, add_validation, content, flags=re.DOTALL)
    
    return content

# Apply fixes to all functions
fixed_count = 0
for func_name in calculator_functions:
    old_content = content
    content = fix_function(func_name, content)
    if content != old_content:
        fixed_count += 1
        print(f"✅ Fixed: {func_name}")

# Save the modified file
wrapper_file.write_text(content, encoding='utf-8')

print(f"\n🎉 COMPLETE: Fixed {fixed_count} calculator functions")
print(f"   Modified: {wrapper_file}")
