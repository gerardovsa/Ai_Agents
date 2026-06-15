#!/usr/bin/env python3
"""Comprehensive test of all calculators with parameter variations"""
import sys
sys.path.insert(0, 'implementations')
sys.path.insert(0, 'backend')
sys.path.insert(0, 'backend/god_calculators')
sys.path.insert(0, 'backend/shopify_calculators')
sys.path.insert(0, '../inhouse-print')

from calculator_wrapper import (
    calculate_business_cards,
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify,
    calculate_flyers_god,
    calculate_letterheads_god,
    calculate_folded_flyers_shopify,
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_god,
    calculate_corflute_signs_god
)

def print_result(name, result):
    """Print calculator result"""
    if result.get('success'):
        price = result.get('total_price') or result.get('total_cost_inc_gst') or 0
        print(f"   ✅ {name}: ${price:.2f}")
        if 'breakdown' in result:
            cost = result.get('cost_to_business', result.get('breakdown', {}).get('biz_cost', 0))
            if cost:
                print(f"      Cost: ${cost:.2f}")
    else:
        print(f"   ❌ {name}: {result.get('error', 'Unknown error')[:80]}")

print("="*80)
print("🧪 COMPREHENSIVE CALCULATOR TEST - ALL VARIATIONS")
print("="*80)

# ============================================================================
# 1. BUSINESS CARDS (Wrapper - uses Shopify backend)
# ============================================================================
print("\n" + "="*80)
print("1️⃣  BUSINESS CARDS (Shopify Wrapper)")
print("="*80)

print("\nTest 1.1: Premium, 500 qty, double-sided, gloss celloglaze")
result = calculate_business_cards(
    quantity=500,
    stock_type='premium',
    print_type='double_sided',
    celloglaze='gloss'
)
print_result("Premium 500 double gloss", result)

print("\nTest 1.2: Premium, 1000 qty, single-sided, matt celloglaze")
result = calculate_business_cards(
    quantity=1000,
    stock_type='premium',
    print_type='single_sided',
    celloglaze='matt'
)
print_result("Premium 1000 single matt", result)

print("\nTest 1.3: Standard, 250 qty, double-sided, no celloglaze")
result = calculate_business_cards(
    quantity=250,
    stock_type='standard',
    print_type='double_sided',
    celloglaze='none'
)
print_result("Standard 250 double no cello", result)

print("\nTest 1.4: Premium, 2000 qty, double-sided, 2-side gloss")
result = calculate_business_cards(
    quantity=2000,
    stock_type='premium',
    print_type='double_sided',
    celloglaze='2_side_gloss'
)
print_result("Premium 2000 double 2-side gloss", result)

# ============================================================================
# 2. ECONOMICAL BUSINESS CARDS (Pure Shopify)
# ============================================================================
print("\n" + "="*80)
print("2️⃣  ECONOMICAL BUSINESS CARDS (Shopify)")
print("="*80)

print("\nTest 2.1: 500 qty, double-sided, 1 artwork")
result = calculate_economical_business_cards_shopify(
    quantity=500,
    double_sided=True,
    print_type='Colour',
    artworks=1
)
print_result("Economical 500 double 1 art", result)

print("\nTest 2.2: 1000 qty, single-sided, 1 artwork")
result = calculate_economical_business_cards_shopify(
    quantity=1000,
    double_sided=False,
    print_type='Colour',
    artworks=1
)
print_result("Economical 1000 single 1 art", result)

print("\nTest 2.3: 2000 qty, double-sided, 5 artworks")
result = calculate_economical_business_cards_shopify(
    quantity=2000,
    double_sided=True,
    print_type='Colour',
    artworks=5
)
print_result("Economical 2000 double 5 arts", result)

print("\nTest 2.4: 5000 qty, double-sided, Black & White")
result = calculate_economical_business_cards_shopify(
    quantity=5000,
    double_sided=True,
    print_type='Black & White',
    artworks=1
)
print_result("Economical 5000 double B&W", result)

# ============================================================================
# 3. PREMIUM BUSINESS CARDS (Pure Shopify)
# ============================================================================
print("\n" + "="*80)
print("3️⃣  PREMIUM BUSINESS CARDS (Shopify)")
print("="*80)

print("\nTest 3.1: 500 qty, Satin 350GSM, 1 Side Gloss")
result = calculate_premium_business_cards_shopify(
    quantity=500,
    double_sided=True,
    paper_stock='Satin 350GSM',
    celloglaze='1 Side Gloss',
    artworks=1
)
print_result("Premium 500 Satin 1-Gloss", result)

print("\nTest 3.2: 1000 qty, King Kong High Bulk, 2 Side Matt")
result = calculate_premium_business_cards_shopify(
    quantity=1000,
    double_sided=True,
    paper_stock='King Kong High Bulk',
    celloglaze='2 Side Matt',
    artworks=1
)
print_result("Premium 1000 KingKong 2-Matt", result)

print("\nTest 3.3: 2000 qty, EcoStar Uncoated, None")
result = calculate_premium_business_cards_shopify(
    quantity=2000,
    double_sided=False,
    paper_stock='EcoStar 350GSM Uncoated',
    celloglaze='None',
    artworks=3
)
print_result("Premium 2000 EcoStar None", result)

print("\nTest 3.4: 500 qty, Satin, SILK FEEL Matt both sides")
result = calculate_premium_business_cards_shopify(
    quantity=500,
    double_sided=True,
    paper_stock='Satin 350GSM',
    celloglaze='2 Side SILK FEEL Matt',
    artworks=1
)
print_result("Premium 500 Satin SilkMatt", result)

# ============================================================================
# 4. GOD FLYER CALCULATOR
# ============================================================================
print("\n" + "="*80)
print("4️⃣  FLYERS (GOD Database Calculator)")
print("="*80)

print("\nTest 4.1: A4, 1000 qty, 150GSM, colour both sides")
result = calculate_flyers_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=150,
    print_side1=1,  # colour
    print_side2=1   # colour
)
print_result("A4 1000 150GSM colour/colour", result)

print("\nTest 4.2: A5, 500 qty, 250GSM, colour/b&w")
result = calculate_flyers_god(
    quantity=500,
    width=148,
    height=210,
    gsm=250,
    print_side1=1,  # colour
    print_side2=2   # b&w
)
print_result("A5 500 250GSM colour/b&w", result)

print("\nTest 4.3: DL, 2000 qty, 300GSM, single sided with gloss cello")
result = calculate_flyers_god(
    quantity=2000,
    width=99,
    height=210,
    gsm=300,
    print_side1=1,  # colour
    print_side2=0,  # none
    cello_required=True,
    cello_side1=1   # gloss
)
print_result("DL 2000 300GSM colour/none gloss", result)

print("\nTest 4.4: A4, 5000 qty, 200GSM, both colour, with folding")
result = calculate_flyers_god(
    quantity=5000,
    width=210,
    height=297,
    gsm=200,
    print_side1=1,  # colour
    print_side2=1,  # colour
    folding_required=True,
    folding_passes=1  # half fold
)
print_result("A4 5000 200GSM both colour folded", result)

# ============================================================================
# 5. GOD LETTERHEAD CALCULATOR
# ============================================================================
print("\n" + "="*80)
print("5️⃣  LETTERHEADS (GOD Database Calculator)")
print("="*80)

print("\nTest 5.1: A4, 1000 qty, 100GSM, colour single side")
result = calculate_letterheads_god(
    quantity=1000,
    width=210,
    height=297,
    gsm=100,
    print_side1=1,  # colour
    print_side2=0   # none
)
print_result("A4 1000 100GSM colour/none", result)

print("\nTest 5.2: A4, 500 qty, 120GSM, colour both sides")
result = calculate_letterheads_god(
    quantity=500,
    width=210,
    height=297,
    gsm=120,
    print_side1=1,  # colour
    print_side2=1   # colour
)
print_result("A4 500 120GSM colour/colour", result)

print("\nTest 5.3: A4, 2000 qty, 80GSM, b&w single side")
result = calculate_letterheads_god(
    quantity=2000,
    width=210,
    height=297,
    gsm=80,
    print_side1=2,  # b&w
    print_side2=0   # none
)
print_result("A4 2000 80GSM b&w/none", result)

print("\nTest 5.4: A5, 1000 qty, 100GSM, colour/b&w")
result = calculate_letterheads_god(
    quantity=1000,
    width=148,
    height=210,
    gsm=100,
    print_side1=1,  # colour
    print_side2=2   # b&w
)
print_result("A5 1000 100GSM colour/b&w", result)

# ============================================================================
# 6. FOLDED FLYERS (Shopify)
# ============================================================================
print("\n" + "="*80)
print("6️⃣  FOLDED FLYERS (Shopify)")
print("="*80)

print("\nTest 6.1: A4, 500 qty, Satin 150GSM, Single Fold, colour both")
result = calculate_folded_flyers_shopify(
    quantity=500,
    size='A4',
    stock='Satin 150GSM',
    double_sided=True,
    folding='Single Fold',
    print_type='Colour'
)
print_result("A4 500 150GSM Single double", result)

print("\nTest 6.2: A3, 1000 qty, Satin 250GSM, Double Fold, colour both")
result = calculate_folded_flyers_shopify(
    quantity=1000,
    size='A3',
    stock='Satin 250GSM',
    double_sided=True,
    folding='Double Fold',
    print_type='Colour'
)
print_result("A3 1000 250GSM Double double", result)

print("\nTest 6.3: A5, 250 qty, Uncoated Bond 100GSM, Single Fold, single side")
result = calculate_folded_flyers_shopify(
    quantity=250,
    size='A5',
    stock='Uncoated Bond 100GSM',
    double_sided=False,
    folding='Single Fold',
    print_type='Colour'
)
print_result("A5 250 100GSM Single single", result)

print("\nTest 6.4: A4, 2000 qty, Satin 300GSM, Triple Fold, B&W both")
result = calculate_folded_flyers_shopify(
    quantity=2000,
    size='A4',
    stock='Satin 300GSM',
    double_sided=True,
    folding='Triple Fold',
    print_type='Black & White'
)
print_result("A4 2000 300GSM Triple B&W", result)

# ============================================================================
# 7. WIRE BOUND BOOKS (Shopify)
# ============================================================================
print("\n" + "="*80)
print("7️⃣  WIRE BOUND BOOKS (Shopify)")
print("="*80)

print("\nTest 7.1: A4, 100 qty, 40 pages, 300GSM cover, 100GSM internal")
result = calculate_wire_bound_books_shopify(
    quantity=100,
    pages=40,
    size='A4',
    cover_stock='300GSM',
    inner_stock='100GSM'
)
print_result("A4 100qty 40pg 300/100", result)

print("\nTest 7.2: A5, 250 qty, 60 pages, 350GSM cover, 120GSM internal")
result = calculate_wire_bound_books_shopify(
    quantity=250,
    pages=60,
    size='A5',
    cover_stock='350GSM',
    inner_stock='120GSM'
)
print_result("A5 250qty 60pg 350/120", result)

print("\nTest 7.3: A4, 500 qty, 80 pages, 250GSM cover, 80GSM internal, gloss cello")
result = calculate_wire_bound_books_shopify(
    quantity=500,
    pages=80,
    size='A4',
    cover_stock='250GSM',
    inner_stock='80GSM',
    cover_cellophane='Gloss Cellophane'
)
print_result("A4 500qty 80pg 250/80 gloss", result)

print("\nTest 7.4: A4, 1000 qty, 100 pages, 300GSM cover, 100GSM internal, matt cello")
result = calculate_wire_bound_books_shopify(
    quantity=1000,
    pages=100,
    size='A4',
    cover_stock='300GSM',
    inner_stock='100GSM',
    cover_cellophane='Matt Cellophane'
)
print_result("A4 1000qty 100pg 300/100 matt", result)

# ============================================================================
# 8. SPIRAL BOUND BOOKS (Shopify)
# ============================================================================
print("\n" + "="*80)
print("8️⃣  SPIRAL BOUND BOOKS (Shopify)")
print("="*80)

print("\nTest 8.1: A4, 100 qty, 40 pages, 300GSM cover, 100GSM internal")
result = calculate_spiral_bound_books_shopify(
    quantity=100,
    pages=40,
    size='A4',
    cover_stock='300GSM',
    inner_stock='100GSM'
)
print_result("A4 100qty 40pg 300/100", result)

print("\nTest 8.2: A5, 250 qty, 60 pages, 350GSM cover, 120GSM internal")
result = calculate_spiral_bound_books_shopify(
    quantity=250,
    pages=60,
    size='A5',
    cover_stock='350GSM',
    inner_stock='120GSM'
)
print_result("A5 250qty 60pg 350/120", result)

print("\nTest 8.3: A4, 500 qty, 80 pages, 250GSM cover, 80GSM internal, gloss cello")
result = calculate_spiral_bound_books_shopify(
    quantity=500,
    pages=80,
    size='A4',
    cover_stock='250GSM',
    inner_stock='80GSM',
    cover_cellophane='Gloss Cellophane'
)
print_result("A4 500qty 80pg 250/80 gloss", result)

print("\nTest 8.4: A4, 1000 qty, 120 pages, 300GSM cover, 100GSM internal, matt cello")
result = calculate_spiral_bound_books_shopify(
    quantity=1000,
    pages=120,
    size='A4',
    cover_stock='300GSM',
    inner_stock='100GSM',
    cover_cellophane='Matt Cellophane'
)
print_result("A4 1000qty 120pg 300/100 matt", result)

# ============================================================================
# 9. PERFECT BOUND BOOKS (GOD)
# ============================================================================
print("\n" + "="*80)
print("9️⃣  PERFECT BOUND BOOKS (GOD Database Calculator)")
print("="*80)

print("\nTest 9.1: A4, 100 qty, 60 pages, 300GSM cover, 100GSM internal")
result = calculate_perfect_bound_books_god(
    quantity=100,
    pages=60,
    book_width=210,
    book_height=297,
    cover_gsm=300,
    inner_gsm=100,
    print_cover_mode=1,  # both sides
    print_inner_mode=1   # b&w
)
print_result("A4 100qty 60pg 300/100", result)

print("\nTest 9.2: A5, 250 qty, 80 pages, 250GSM cover, 80GSM internal")
result = calculate_perfect_bound_books_god(
    quantity=250,
    pages=80,
    book_width=148,
    book_height=210,
    cover_gsm=250,
    inner_gsm=80,
    print_cover_mode=1,  # both sides
    print_inner_mode=0   # colour
)
print_result("A5 250qty 80pg 250/80", result)

print("\nTest 9.3: A4, 500 qty, 100 pages, 350GSM cover, 120GSM internal, gloss cello")
result = calculate_perfect_bound_books_god(
    quantity=500,
    pages=100,
    book_width=210,
    book_height=297,
    cover_gsm=350,
    inner_gsm=120,
    print_cover_mode=1,  # both sides
    print_inner_mode=0,  # colour
    cello_type=1         # gloss
)
print_result("A4 500qty 100pg 350/120 gloss", result)

print("\nTest 9.4: A4, 1000 qty, 120 pages, 300GSM cover, 100GSM internal, matt cello")
result = calculate_perfect_bound_books_god(
    quantity=1000,
    pages=120,
    book_width=210,
    book_height=297,
    cover_gsm=300,
    inner_gsm=100,
    print_cover_mode=1,  # both sides
    print_inner_mode=1,  # b&w
    cello_type=2         # matt
)
print_result("A4 1000qty 120pg 300/100 matt", result)

# ============================================================================
# 10. CORFLUTE SIGNS (GOD)
# ============================================================================
print("\n" + "="*80)
print("🔟 CORFLUTE SIGNS (GOD Database Calculator)")
print("="*80)

print("\nTest 10.1: 600x600mm, 10 qty, 5mm, single sided")
result = calculate_corflute_signs_god(
    quantity=10,
    width=600,
    height=600,
    thickness=5,
    print_sides='single'
)
print_result("600x600 10qty 5mm single", result)

print("\nTest 10.2: 900x600mm, 25 qty, 5mm, double sided")
result = calculate_corflute_signs_god(
    quantity=25,
    width=900,
    height=600,
    thickness=5,
    print_sides='double'
)
print_result("900x600 25qty 5mm double", result)

print("\nTest 10.3: 1200x900mm, 50 qty, 3mm, single sided")
result = calculate_corflute_signs_god(
    quantity=50,
    width=1200,
    height=900,
    thickness=3,
    print_sides='single'
)
print_result("1200x900 50qty 3mm single", result)

print("\nTest 10.4: 1800x1200mm, 100 qty, 10mm, double sided")
result = calculate_corflute_signs_god(
    quantity=100,
    width=1800,
    height=1200,
    thickness=10,
    print_sides='double'
)
print_result("1800x1200 100qty 10mm double", result)

print("\n" + "="*80)
print("✅ COMPREHENSIVE TEST COMPLETE")
print("="*80)
