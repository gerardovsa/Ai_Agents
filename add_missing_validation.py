"""
Add validation to all functions that have **kwargs but no validation yet
"""

from pathlib import Path
import re

wrapper_file = Path("UI/modules_external/quote-calculator/implementations/calculator_wrapper.py")
content = wrapper_file.read_text(encoding='utf-8')

# List of calculator functions to find
all_functions = [
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
    'calculate_spiral_bound_books',
]

fixed_count = 0

for func_name in all_functions:
    # Find the function definition
    func_pattern = rf'(def {func_name}\([^)]*\*\*kwargs[^)]*\)\s*->\s*Dict\[str, Any\]:\s*"""(?:[^"]|"(?!""))*?""")\s*\n(\s+)(.{{0,100}})'
    
    matches = list(re.finditer(func_pattern, content, flags=re.DOTALL))
    
    for match in matches:
        header = match.group(1)
        indent = match.group(2)
        next_lines = match.group(3)
        
        # Check if validation already exists
        if f'_validate_no_typos(kwargs, "{func_name}")' in next_lines:
            continue  # Already has validation
        
        # Insert validation
        validation = f'''\n{indent}# Check for typos in parameter names (unexpected kwargs)
{indent}typo_error = _validate_no_typos(kwargs, "{func_name}")
{indent}if typo_error:
{indent}    return typo_error
{indent}
{indent}'''
        
        # Replace
        replacement = header + validation + match.group(3)
        content = content[:match.start()] + replacement + content[match.end():]
        
        fixed_count += 1
        print(f"✅ Added validation to: {func_name}")
        break  # Only fix first occurrence

# Save
wrapper_file.write_text(content, encoding='utf-8')

print(f"\n🎉 COMPLETE: Added validation to {fixed_count} functions")
print(f"   File: {wrapper_file}")
