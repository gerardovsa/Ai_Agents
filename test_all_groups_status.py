"""
Quick status check for all calculator groups (1-6)
Tests one calculator per group to verify pattern implementation
"""

import sys
from pathlib import Path

# Add paths
wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import (
    # Group 1: Business Cards & Flyers
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify,
    calculate_folded_flyers_shopify,
    calculate_printed_letterheads,
    calculate_with_compliments_slips,
    
    # Group 2: Bound Books
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_spiral_books_simple_shopify,
    
    # Group 3: Notepads & Printing
    calculate_notepads_a4,
    calculate_notepads_a5,
    calculate_notepads_a6,
    calculate_custom_poster_printing,
    calculate_custom_vinyl_stickers,
    
    # Group 4: Signs & Displays
    calculate_election_signs,
    calculate_construction_signs,
    calculate_bollard_signs,
    calculate_corflute_insert_a_frame,
    calculate_metal_face_a_frame,
    
    # Group 5: Promotional Products
    calculate_luxury_classic_pull_up_banners,
    calculate_selfie_frames,
    calculate_stackable_cubes,
    calculate_strut_cards_a3,
    calculate_strut_cards_a4,
    
    # Group 6: Specialty & Remaining
    calculate_premium_bookmarks,
    calculate_corflute_signs_shopify,
)

def check_function_signature(func):
    """Check if function follows proper pattern (None defaults, validation)"""
    import inspect
    
    sig = inspect.signature(func)
    params = sig.parameters
    
    # Check for **kwargs (bad pattern)
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    
    # Check for None defaults on optional params
    none_defaults = [name for name, p in params.items() 
                     if p.default is None and name != 'kwargs']
    
    # Check source for validation
    source = inspect.getsource(func)
    has_validation = 'is None:' in source and 'return {"error"' in source
    
    return {
        'has_kwargs': has_kwargs,
        'none_defaults': none_defaults,
        'has_validation': has_validation,
        'pattern_score': (0 if has_kwargs else 1) + (1 if none_defaults else 0) + (1 if has_validation else 0)
    }

def test_group(group_name, calculators):
    """Test pattern implementation for a group"""
    print(f"\n{'='*70}")
    print(f"GROUP: {group_name}")
    print(f"{'='*70}")
    
    results = []
    for calc_name, calc_func in calculators:
        info = check_function_signature(calc_func)
        status = '✅' if info['pattern_score'] >= 2 else '⚠️' if info['pattern_score'] == 1 else '❌'
        
        print(f"\n{status} {calc_name}")
        print(f"   Pattern Score: {info['pattern_score']}/3")
        print(f"   Has kwargs: {info['has_kwargs']}")
        print(f"   None defaults: {len(info['none_defaults'])} params")
        print(f"   Has validation: {info['has_validation']}")
        
        results.append(info['pattern_score'])
    
    avg_score = sum(results) / len(results) if results else 0
    total_possible = len(results) * 3
    total_actual = sum(results)
    
    print(f"\n{'-'*70}")
    print(f"GROUP SUMMARY: {total_actual}/{total_possible} ({avg_score:.1f}/3.0 avg)")
    
    if avg_score >= 2.5:
        print("Status: ✅ EXCELLENT - Proper pattern implemented")
    elif avg_score >= 2.0:
        print("Status: ✅ GOOD - Mostly proper pattern")
    elif avg_score >= 1.0:
        print("Status: ⚠️ NEEDS WORK - Partial implementation")
    else:
        print("Status: ❌ NOT STARTED - Old pattern still in use")
    
    return avg_score

# Test all groups
print("="*70)
print("CALCULATOR PATTERN IMPLEMENTATION STATUS CHECK")
print("="*70)

group_scores = []

# Group 1
score = test_group("GROUP 1: Business Cards & Flyers", [
    ('Economical Business Cards', calculate_economical_business_cards_shopify),
    ('Premium Business Cards', calculate_premium_business_cards_shopify),
    ('Folded Flyers', calculate_folded_flyers_shopify),
    ('Printed Letterheads', calculate_printed_letterheads),
    ('With Compliments Slips', calculate_with_compliments_slips),
])
group_scores.append(('Group 1', score))

# Group 2
score = test_group("GROUP 2: Bound Books", [
    ('Wire Bound Books', calculate_wire_bound_books_shopify),
    ('Spiral Bound Books', calculate_spiral_bound_books_shopify),
    ('Perfect Bound Books', calculate_perfect_bound_books_shopify),
    ('Saddle Stitch Books', calculate_saddle_stitch_books_shopify),
    ('Spiral Books Simple', calculate_spiral_books_simple_shopify),
])
group_scores.append(('Group 2', score))

# Group 3
score = test_group("GROUP 3: Notepads & Printing", [
    ('Notepads A4', calculate_notepads_a4),
    ('Notepads A5', calculate_notepads_a5),
    ('Notepads A6', calculate_notepads_a6),
    ('Custom Poster Printing', calculate_custom_poster_printing),
    ('Custom Vinyl Stickers', calculate_custom_vinyl_stickers),
])
group_scores.append(('Group 3', score))

# Group 4
score = test_group("GROUP 4: Signs & Displays", [
    ('Election Signs', calculate_election_signs),
    ('Construction Signs', calculate_construction_signs),
    ('Bollard Signs', calculate_bollard_signs),
    ('Corflute Insert A-Frame', calculate_corflute_insert_a_frame),
    ('Metal Face A-Frame', calculate_metal_face_a_frame),
])
group_scores.append(('Group 4', score))

# Group 5
score = test_group("GROUP 5: Promotional Products", [
    ('Luxury Classic Pull Up Banners', calculate_luxury_classic_pull_up_banners),
    ('Selfie Frames', calculate_selfie_frames),
    ('Stackable Cubes', calculate_stackable_cubes),
    ('Strut Cards A3', calculate_strut_cards_a3),
    ('Strut Cards A4', calculate_strut_cards_a4),
])
group_scores.append(('Group 5', score))

# Group 6
score = test_group("GROUP 6: Specialty & Remaining", [
    ('Premium Bookmarks', calculate_premium_bookmarks),
    ('Corflute Signs Shopify', calculate_corflute_signs_shopify),
])
group_scores.append(('Group 6', score))

# Overall summary
print(f"\n{'='*70}")
print("OVERALL SUMMARY")
print(f"{'='*70}")

for group_name, score in group_scores:
    status = '✅' if score >= 2.5 else '⚠️' if score >= 2.0 else '❌'
    print(f"{status} {group_name}: {score:.1f}/3.0")

overall_avg = sum(score for _, score in group_scores) / len(group_scores)
print(f"\n📊 Overall Average: {overall_avg:.1f}/3.0")

if overall_avg >= 2.5:
    print("🎉 EXCELLENT: All groups properly implemented!")
elif overall_avg >= 2.0:
    print("✅ GOOD: Most groups properly implemented")
elif overall_avg >= 1.0:
    print("⚠️ IN PROGRESS: Significant work remaining")
else:
    print("❌ NOT STARTED: Major work needed")
