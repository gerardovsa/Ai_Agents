"""
Test Premium Business Cards Calculator - All 6 Tests
Run directly to bypass AI execution layer
"""

import sys
from pathlib import Path

# Add paths
backend_dir = Path(__file__).parent / "UI" / "modules_external" / "quote-calculator" / "backend" / "shopify_calculators"
sys.path.insert(0, str(backend_dir))

from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator

def test_premium_cards():
    calc = PremiumBusinessCardsShopifyCalculator()
    
    tests = [
        {
            "name": "TEST 1 - Premium KingKong ($161.70)",
            "expected": 161.70,
            "params": {
                "quantity": 1000,
                "paper_stock": "King Kong High Bulk",
                "finish_size": "90mm x 55mm",
                "print_type": "Colour",
                "print_sides": "Double side print",
                "celloglaze": "2 Side Gloss",
                "artworks": 1
            }
        },
        {
            "name": "TEST 2 - Standard Satin No Celloglaze ($85.80)",
            "expected": 85.80,
            "params": {
                "quantity": 500,
                "paper_stock": "Satin 350GSM",
                "finish_size": "90mm x 55mm",
                "print_type": "Colour",
                "print_sides": "Double side print",
                "celloglaze": "None",
                "artworks": 1
            }
        },
        {
            "name": "TEST 3 - Eco-Friendly EcoStar ($135.30)",
            "expected": 135.30,
            "params": {
                "quantity": 1000,
                "paper_stock": "EcoStar 350GSM Uncoated",
                "finish_size": "90mm x 55mm",
                "print_type": "Colour",
                "print_sides": "Single side print",
                "celloglaze": "None",
                "artworks": 1
            }
        },
        {
            "name": "TEST 4 - Budget Small Quantity ($85.80)",
            "expected": 85.80,
            "params": {
                "quantity": 250,
                "paper_stock": "Satin 350GSM",
                "finish_size": "90mm x 55mm",
                "print_type": "Colour",
                "print_sides": "Single side print",
                "celloglaze": "1 Side Matt",
                "artworks": 1
            }
        },
        {
            "name": "TEST 5 - High Volume SILK FEEL ($518.10)",
            "expected": 518.10,
            "params": {
                "quantity": 5000,
                "paper_stock": "King Kong High Bulk",
                "finish_size": "90mm x 55mm",
                "print_type": "Colour",
                "print_sides": "Double side print",
                "celloglaze": "2 Side SILK FEEL Matt",
                "artworks": 1
            }
        },
        {
            "name": "TEST 6 - B&W Economy ($95.70)",
            "expected": 95.70,
            "params": {
                "quantity": 1000,
                "paper_stock": "Satin 350GSM",
                "finish_size": "90mm x 55mm",
                "print_type": "Black & White",
                "print_sides": "Single side print",
                "celloglaze": "None",
                "artworks": 1
            }
        }
    ]
    
    print("="*80)
    print("PREMIUM BUSINESS CARDS - SHOPIFY CALCULATOR TEST")
    print("="*80)
    
    for i, test in enumerate(tests, 1):
        print(f"\n{test['name']}")
        print("-"*80)
        
        try:
            result = calc.calculate(**test['params'])
            actual = float(result.total_price)
            expected = test['expected']
            diff = actual - expected
            diff_pct = (diff / expected * 100) if expected else 0
            
            status = "✅ PASS" if abs(diff_pct) < 1.0 else "❌ FAIL"
            
            print(f"Expected: ${expected:.2f}")
            print(f"Actual:   ${actual:.2f}")
            print(f"Diff:     ${diff:+.2f} ({diff_pct:+.2f}%)")
            print(f"Status:   {status}")
            
            # Show breakdown for failures
            if abs(diff_pct) >= 1.0:
                print(f"\nBreakdown:")
                print(f"  BizCost: ${result.breakdown['biz_cost']:.2f}")
                print(f"  Profit: ${result.breakdown['profit_amount']:.2f} ({result.breakdown['profit_margin_rate']*100:.0f}%)")
                print(f"  Artwork: ${result.breakdown['artwork_setup_cost']:.2f}")
                print(f"  Subtotal: ${result.breakdown['subtotal']:.2f}")
                print(f"  GST: ${result.breakdown['total_gst_amount']:.2f}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_premium_cards()
