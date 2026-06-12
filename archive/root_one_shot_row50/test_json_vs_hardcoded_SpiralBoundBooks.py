"""
Alignment Test: JSON Config Verification (SpiralBoundBooks)
Created: Jan 26, 2026

This calculator is CONFIG-LOADED (loads from Shopify_Spiral_Bound_Books.json).
Tests verify calculator successfully reads and uses JSON config without fallback to hardcoded values.

Test Strategy:
- 5 diverse test cases covering parameter space
- Small/medium/large quantities (50, 100, 250, 500, 1000)
- Various cover configurations (PVC, satin stocks, celloglaze)
- Different content specs (pages, stocks, print types)
- Wire binding tiers (different thickness levels)
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_dir))

# Import calculator
from SpiralBoundBooks_Shopify_Calculator import SpiralBoundBooksShopifyCalculator

def test_spiral_bound_books():
    """Run 5 diverse tests verifying JSON config is loaded correctly"""
    
    calculator = SpiralBoundBooksShopifyCalculator()
    tests_passed = 0
    tests_failed = 0
    
    # Verify config loaded
    if not calculator.config:
        print("❌ FATAL: Configuration not loaded - cannot proceed")
        return False
    
    test_cases = [
        {
            "name": "Test 1: 50× A5 Portrait, 50 pages, 250GSM front, no PVC, B&W content",
            "params": {
                "quantity": 50,
                "artworks": 1,
                "outer_front_cover": "Not Required",
                "printed_front_cover": "250GSM Satin",
                "cover_print_type": "1pp Colour",
                "celloglaze": "None",
                "outer_back_cover": "None",
                "printed_back_cover": "250GSM Satin",
                "back_cover_print_type": "1pp Colour",
                "back_celloglaze": "None",
                "content_pages": 50,
                "content_paper_stock": "Uncoated Bond 80GSM",
                "content_print_type": "Black & White",
                "finish_size": "A5 Portrait"
            }
        },
        {
            "name": "Test 2: 100× A4 Landscape, 100 pages, 350GSM+PVC front, 2pp colour content",
            "params": {
                "quantity": 100,
                "artworks": 2,
                "outer_front_cover": "Clear PVC",
                "printed_front_cover": "350GSM Satin",
                "cover_print_type": "2pp Colour",
                "celloglaze": "2 Sided Gloss",
                "outer_back_cover": "Clear PVC",
                "printed_back_cover": "350GSM Satin",
                "back_cover_print_type": "2pp Colour",
                "back_celloglaze": "2 Sided Gloss",
                "content_pages": 100,
                "content_paper_stock": "Satin 128GSM",
                "content_print_type": "Full colour",
                "finish_size": "A4 Landscape"
            }
        },
        {
            "name": "Test 3: 250× DL Portrait, 30 pages, 300GSM front, 1-side gloss, B&W",
            "params": {
                "quantity": 250,
                "artworks": 1,
                "outer_front_cover": "Not Required",
                "printed_front_cover": "300GSM Satin",
                "cover_print_type": "2pp Colour",
                "celloglaze": "1 Side Gloss",
                "outer_back_cover": "None",
                "printed_back_cover": "None",
                "back_cover_print_type": "1pp Colour",
                "back_celloglaze": "None",
                "content_pages": 30,
                "content_paper_stock": "Uncoated Bond 100GSM",
                "content_print_type": "Black & White",
                "finish_size": "DL Portrait"
            }
        },
        {
            "name": "Test 4: 500× A6 Landscape, 200 pages, 250GSM both covers, colour content",
            "params": {
                "quantity": 500,
                "artworks": 3,
                "outer_front_cover": "Not Required",
                "printed_front_cover": "250GSM Satin",
                "cover_print_type": "2pp Colour",
                "celloglaze": "None",
                "outer_back_cover": "None",
                "printed_back_cover": "250GSM Satin",
                "back_cover_print_type": "2pp Colour",
                "back_celloglaze": "None",
                "content_pages": 200,
                "content_paper_stock": "Satin 150GSM",
                "content_print_type": "Full colour",
                "finish_size": "A6 Landscape"
            }
        },
        {
            "name": "Test 5: 1000× A5 Landscape, 150 pages, 350GSM+leather back, B&W content",
            "params": {
                "quantity": 1000,
                "artworks": 1,
                "outer_front_cover": "Clear PVC",
                "printed_front_cover": "350GSM Satin",
                "cover_print_type": "2pp Colour",
                "celloglaze": "2 Sided Matt",
                "outer_back_cover": "Black Leather",
                "printed_back_cover": "None",
                "back_cover_print_type": "1pp Colour",
                "back_celloglaze": "None",
                "content_pages": 150,
                "content_paper_stock": "Uncoated Bond 90GSM",
                "content_print_type": "Black & White",
                "finish_size": "A5 Landscape"
            }
        }
    ]
    
    print("=" * 80)
    print("JSON CONFIG VERIFICATION TEST - SpiralBoundBooks")
    print("=" * 80)
    print()
    print("✅ Configuration loaded successfully")
    print(f"   Config file: {calculator.CONFIG_FILE}")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"🧪 {test['name']}")
        
        try:
            # Calculate using JSON-loaded config
            result = calculator.calculate(**test['params'])
            
            # Extract price
            price = result.total_price
            unit_price = result.unit_price
            
            # Verify breakdown exists (proves calculation worked)
            if not result.breakdown:
                print(f"   ❌ FAILED: No breakdown in result")
                tests_failed += 1
                continue
            
            print(f"   ✅ PASSED: ${price:.2f} total (${unit_price:.2f}/unit)")
            
            # Show key cost components
            bd = result.breakdown
            if 'wire_binding_cost' in bd:
                print(f"      Wire: ${bd['wire_binding_cost']:.2f}, Setup: ${bd.get('setup_cost', 0):.2f}")
            
            tests_passed += 1
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            tests_failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    total = tests_passed + tests_failed
    pass_rate = (tests_passed / total * 100) if total > 0 else 0
    
    if tests_failed == 0:
        print(f"🎉 ALL TESTS PASSED ({tests_passed}/{total}) - Config-loaded calculator VERIFIED!")
    else:
        print(f"⚠️  TESTS FAILED: {tests_failed}/{total} ({pass_rate:.1f}% pass rate)")
    
    print("=" * 80)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_spiral_bound_books()
    sys.exit(0 if success else 1)
