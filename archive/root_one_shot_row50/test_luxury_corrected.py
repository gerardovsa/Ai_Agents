"""
Test Luxury Classic Pull Up Banners - CORRECTED FORMULA
Testing exact JSON formula: rate lookup + simple markup
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

wrapper_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'
sys.path.insert(0, str(wrapper_path))

from calculator_wrapper import calculate_luxury_classic_pull_up_banners

def test_production_screenshot_config():
    """Test exact config from user's screenshot: 5 qty, Black, 2 artworks, 850mm W x 2000mm H"""
    print("\n" + "="*70)
    print("🔍 Test: PRODUCTION SCREENSHOT CONFIG")
    print("="*70)
    print("Configuration:")
    print("  Quantity: 5")
    print("  Size: 850mm W x 2000mm H")
    print("  Base Colour: Black")
    print("  Artworks: 2")
    print("\nExpected (from screenshot): $766.72")
    print("\nCalculating with CORRECTED formula...")
    print("-"*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        size="850mm W x 2000mm H",
        base_colour="Black",
        artworks=2
    )
    
    print(f"\n✅ Success: {result.get('success')}")
    if result.get('success'):
        total = result['total_price']
        unit = result['unit_price']
        print(f"📊 Total: ${total:.2f}")
        print(f"📊 Unit: ${unit:.2f}")
        
        # Show formula breakdown
        breakdown = result.get('breakdown', {})
        print(f"\n🔢 Formula Breakdown:")
        print(f"   Rate (qty 5, 2000mm): ${breakdown.get('rate', 0):.2f}")
        print(f"   Subtotal (5 * rate): ${breakdown.get('subtotal', 0):.2f}")
        print(f"   + Artworks field: ${breakdown.get('artworks_added', 0):.2f}")
        print(f"   + Setup: ${breakdown.get('production_setup', 0):.2f}")
        print(f"   = Pre-markup: ${breakdown.get('pre_markup_total', 0):.2f}")
        print(f"   × 1.1 (first): ${breakdown.get('after_first_markup', 0):.2f}")
        print(f"   × 1.1 (final): ${total:.2f}")
        
        # Compare to screenshot
        expected = 766.72
        difference = abs(total - expected)
        match_status = "✅ MATCHES" if difference < 0.05 else f"⚠️ DIFFERS by ${difference:.2f}"
        print(f"\n🎯 Comparison: {match_status}")
        print(f"   Screenshot: ${expected:.2f}")
        print(f"   Calculated: ${total:.2f}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result.get('success') and abs(result['total_price'] - 766.72) < 0.05

def test_manual_formula_verification():
    """Manually calculate using exact JSON formula to verify logic"""
    print("\n" + "="*70)
    print("🧮 MANUAL FORMULA VERIFICATION")
    print("="*70)
    
    F1 = 5  # quantity
    F2 = 2  # artworks
    F4 = "850mm W x 2000mm H"  # size
    
    # Rate lookup for qty=5, size=2000mm
    rate = 123.33
    
    print(f"F1 (quantity): {F1}")
    print(f"F2 (artworks): {F2}")
    print(f"F4 (size): {F4}")
    print(f"\nRate for qty {F1}: ${rate}")
    
    # Formula: var subtotal = {F1}*{rate};
    subtotal = F1 * rate
    print(f"\nStep 1: subtotal = {F1} * {rate} = ${subtotal:.2f}")
    
    # Formula: var total = ({subtotal} + {F2} + 15) * 1.1;
    pre_markup = subtotal + F2 + 15
    print(f"Step 2: pre_markup = ({subtotal:.2f} + {F2} + 15) = ${pre_markup:.2f}")
    
    after_first_markup = pre_markup * 1.1
    print(f"Step 3: after_first_markup = {pre_markup:.2f} * 1.1 = ${after_first_markup:.2f}")
    
    # Formula: {total}*1.1
    final_total = after_first_markup * 1.1
    print(f"Step 4: final_total = {after_first_markup:.2f} * 1.1 = ${final_total:.2f}")
    
    print(f"\n🎯 Manual calculation: ${final_total:.2f}")
    print(f"🎯 Expected (screenshot): $766.72")
    
    return abs(final_total - 766.72) < 0.05

def test_old_formula_for_comparison():
    """Test 5 qty, Silver, 2 artworks - should give different result than old $1143.45"""
    print("\n" + "="*70)
    print("📋 Test: SILVER BASE (Old Test Config)")
    print("="*70)
    print("Configuration: 5 qty, Silver, 2 artworks, 850mm W x 2000mm H")
    print("Old incorrect result: $1143.45")
    print("New correct formula should give: ~$766.72 (same as Black)")
    print("-"*70)
    
    result = calculate_luxury_classic_pull_up_banners(
        quantity=5,
        size="850mm W x 2000mm H",
        base_colour="Silver",
        artworks=2
    )
    
    print(f"\n✅ Success: {result.get('success')}")
    if result.get('success'):
        total = result['total_price']
        print(f"📊 Total: ${total:.2f}")
        print(f"📊 Unit: ${result['unit_price']:.2f}")
        print(f"\n🎯 Base colour does NOT affect price in JSON formula")
        print(f"   Silver and Black should both be: ${total:.2f}")
    
    return result.get('success')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("LUXURY CLASSIC PULL UP BANNERS - CORRECTED FORMULA TEST")
    print("="*70)
    
    test1 = test_manual_formula_verification()
    test2 = test_production_screenshot_config()
    test3 = test_old_formula_for_comparison()
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    
    if test1 and test2:
        print("✅ ALL TESTS PASSED - Formula corrected!")
        print("   Production screenshot config now matches: $766.72")
        print("   Manual formula verification confirmed")
    else:
        print("❌ Some tests failed")
        print(f"   Manual verification: {'PASS' if test1 else 'FAIL'}")
        print(f"   Production config: {'PASS' if test2 else 'FAIL'}")
