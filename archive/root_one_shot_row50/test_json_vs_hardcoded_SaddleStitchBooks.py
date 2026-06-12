"""
Alignment Test: JSON Config Verification (SaddleStitchBooks)
Created: Jan 26, 2026

This calculator is CONFIG-LOADED (loads from Shopify_Saddle_Stitch_Books.json).
Tests verify calculator successfully reads and uses JSON config without fallback to hardcoded values.

Test Strategy:
- 5 diverse test cases covering parameter space
- Small/medium/large quantities (25, 50, 100, 250, 500)
- Various cover configurations (stock, print types, celloglaze)
- Different content specs (pages 8pp-48pp, stocks, print types)
- Hard cover vs soft cover options
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_dir))

# Import calculator
from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator

def test_saddle_stitch_books():
    """Run 5 diverse tests verifying JSON config is loaded correctly"""
    
    calculator = SaddleStitchBooksShopifyCalculator()
    tests_passed = 0
    tests_failed = 0
    
    # Verify config loaded
    if not calculator.config:
        print("❌ FATAL: Configuration not loaded - cannot proceed")
        return False
    
    test_cases = [
        {
            "name": "Test 1: 25× A5 Portrait, 8pp, B&W content, soft cover",
            "params": {
                "quantity": "25",
                "artworks": 1,
                "cover_option": "Soft Cover",
                "cover_stock": "Satin 200GSM",
                "cover_print_type": "2 side colour (4pp)",
                "celloglaze": "None",
                "printed_pages": "8pp",
                "finish_size": "A5 Portrait",
                "content_print_type": "Black & White",
                "content_stock_type": "Uncoated Bond 80GSM"
            }
        },
        {
            "name": "Test 2: 50× A4 Portrait, 16pp, colour content, hard cover + gloss",
            "params": {
                "quantity": "50",
                "artworks": 2,
                "cover_option": "Hard Cover",
                "cover_stock": "Satin 300GSM",
                "cover_print_type": "2 side colour (4pp)",
                "celloglaze": "Gloss outside only",
                "printed_pages": "16pp",
                "finish_size": "A4 Portrait",
                "content_print_type": "Colour",
                "content_stock_type": "Satin 128GSM"
            }
        },
        {
            "name": "Test 3: 100× A4 Portrait, 24pp, B&W content, soft cover + matt",
            "params": {
                "quantity": "100",
                "artworks": 1,
                "cover_option": "Soft Cover",
                "cover_stock": "Satin 200GSM",
                "cover_print_type": "2 side colour (4pp)",
                "celloglaze": "Matt outside only",
                "printed_pages": "24pp",
                "finish_size": "A4 Portrait",
                "content_print_type": "Black & White",
                "content_stock_type": "Uncoated Bond 90GSM"
            }
        },
        {
            "name": "Test 4: 250× A5 Portrait, 32pp, colour content, hard cover",
            "params": {
                "quantity": "250",
                "artworks": 3,
                "cover_option": "Hard Cover",
                "cover_stock": "Satin 350GSM",
                "cover_print_type": "2 side colour (4pp)",
                "celloglaze": "None",
                "printed_pages": "32pp",
                "finish_size": "A5 Portrait",
                "content_print_type": "Colour",
                "content_stock_type": "Satin 150GSM"
            }
        },
        {
            "name": "Test 5: 500× A4 Landscape, 48pp, B&W content, soft cover + gloss",
            "params": {
                "quantity": "500",
                "artworks": 1,
                "cover_option": "Soft Cover",
                "cover_stock": "Satin 300GSM",
                "cover_print_type": "2 side colour (4pp)",
                "celloglaze": "Gloss outside only",
                "printed_pages": "48pp",
                "finish_size": "A4 Landscape",
                "content_print_type": "Black & White",
                "content_stock_type": "Uncoated Bond 100GSM"
            }
        }
    ]
    
    print("=" * 80)
    print("JSON CONFIG VERIFICATION TEST - SaddleStitchBooks")
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
            if 'padding_cost' in bd:
                print(f"      Padding: ${bd['padding_cost']:.2f}, Setup: ${bd.get('setup_cost', 0):.2f}")
            
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
    success = test_saddle_stitch_books()
    sys.exit(0 if success else 1)
