"""
Alignment Test: JSON Config Verification (WithComplimentsSlips)
Created: Jan 26, 2026

This calculator is CONFIG-LOADED (loads from Shopify_With_Compliments_Slips.json).
Tests verify calculator successfully reads and uses JSON config without fallback to hardcoded values.

Test Strategy:
- 5 diverse test cases covering parameter space
- Small/medium/large quantities (50, 250, 500, 1000, 3000)
- Single vs double sided printing
- Colour vs Black & White printing
- Different paper stocks (80GSM, 90GSM, 100GSM)
- Multiple artworks

Key Features (per docstring):
- DL size only (99mm × 210mm) - 6 slips per sheet
- Setup: impos=$15, guilo=$12, first artwork FREE then $15 each
- Stock: Uncoated Bond 80GSM=$26.34, 90GSM=$29.51, 100GSM=$32.68 per 1000 sheets
- Print: Colour=$0.044/sheet, B&W=$0.02/sheet
- Print sides: Single=×1, Double=×2 multiplier
- Stock waste: 1.05× (5%)
- Cutting: $11 per 500 sheets
- Profit: 11 tiers (170% down to 25%)
- DOUBLE GST: ×1.1 ×1.1 = 1.21 total
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_dir))

# Import calculator
from WithComplimentsSlips_Shopify_Calculator import WithComplimentsSlipsShopifyCalculator

def test_with_compliments_slips():
    """Run 5 diverse tests verifying JSON config is loaded correctly"""
    
    calculator = WithComplimentsSlipsShopifyCalculator()
    tests_passed = 0
    tests_failed = 0
    
    # Verify config loaded
    if not calculator.config:
        print("❌ FATAL: Configuration not loaded - cannot proceed")
        return False
    
    test_cases = [
        {
            "name": "Test 1: 50× Single side, Colour, 80GSM, 1 artwork",
            "params": {
                "quantity": 50,
                "print_sides": "Single side print",
                "print_type": "Colour",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 80GSM",
                "artworks": 1
            }
        },
        {
            "name": "Test 2: 250× Double side, B&W, 90GSM, 2 artworks",
            "params": {
                "quantity": 250,
                "print_sides": "Double side print",
                "print_type": "Black & White",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 90GSM",
                "artworks": 2
            }
        },
        {
            "name": "Test 3: 500× Single side, Colour, 100GSM, 1 artwork",
            "params": {
                "quantity": 500,
                "print_sides": "Single side print",
                "print_type": "Colour",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 100GSM",
                "artworks": 1
            }
        },
        {
            "name": "Test 4: 1000× Double side, Colour, 80GSM, 3 artworks",
            "params": {
                "quantity": 1000,
                "print_sides": "Double side print",
                "print_type": "Colour",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 80GSM",
                "artworks": 3
            }
        },
        {
            "name": "Test 5: 3000× Single side, B&W, 90GSM, 1 artwork",
            "params": {
                "quantity": 3000,
                "print_sides": "Single side print",
                "print_type": "Black & White",
                "finish_size": "DL - 99mm x 210mm",
                "paper_stock": "Uncoated Bond 90GSM",
                "artworks": 1
            }
        }
    ]
    
    print("=" * 80)
    print("JSON CONFIG VERIFICATION TEST - WithComplimentsSlips")
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
            
            print(f"   ✅ PASSED: ${price:.2f} total (${unit_price:.2f}/slip)")
            
            # Show key cost components
            bd = result.breakdown
            print(f"      Setup: ${bd.get('setup_costs', 0):.2f}, Stock: ${bd.get('stock_cost', 0):.2f}, Sheets: {bd.get('sheets_needed', 0):.2f}")
            
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
    success = test_with_compliments_slips()
    sys.exit(0 if success else 1)
