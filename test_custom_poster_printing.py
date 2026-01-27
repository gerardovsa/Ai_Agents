"""
Test Custom Poster Printing Shopify Calculator (Jan 26, 2026)
All 5 tests validated against Shopify website
Note: Backend only has 250GSM Satin and 200GSM Yuppo options
"""
import sys
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend' / 'shopify_calculators'
sys.path.insert(0, str(backend_path))

from CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator

def test_custom_poster_printing():
    """Test all 5 Custom Poster Printing configurations"""
    calculator = CustomPosterPrintingShopifyCalculator()
    
    tests = [
        {
            'name': 'Test 1: A3 Size - Small Quantity (250GSM Satin)',
            'params': {
                'quantity': 10,
                'width_mm': 297,
                'height_mm': 420,
                'paper_stock': '250GSM Satin Poster Paper',
                'artworks': 1
            },
            'expected': 132.00
        },
        {
            'name': 'Test 1B: A3 Size - Small Quantity (200GSM Yuppo)',
            'params': {
                'quantity': 10,
                'width_mm': 297,
                'height_mm': 420,
                'paper_stock': '200GSM Yuppo Synthetic Paper',
                'artworks': 1
            },
            'expected': 132.00
        },
        {
            'name': 'Test 2: A2 Size - Standard Quantity (250GSM Satin)',
            'params': {
                'quantity': 50,
                'width_mm': 420,
                'height_mm': 594,
                'paper_stock': '250GSM Satin Poster Paper',
                'artworks': 1,
                'size': 'A2 - 420mm x 594mm'  # Standard size, NOT custom
            },
            'expected': 171.84
        },
        {
            'name': 'Test 2B: A2 Size - Standard Quantity (200GSM Yuppo)',
            'params': {
                'quantity': 50,
                'width_mm': 420,
                'height_mm': 594,
                'paper_stock': '200GSM Yuppo Synthetic Paper',
                'artworks': 1,
                'size': 'A2 - 420mm x 594mm'  # Standard size, NOT custom
            },
            'expected': 245.11
        },
        {
            'name': 'Test 3: A1 Size - Medium Volume (250GSM Satin)',
            'params': {
                'quantity': 100,
                'width_mm': 594,
                'height_mm': 841,
                'paper_stock': '250GSM Satin Poster Paper',
                'artworks': 2,
                'size': 'A1 - 594mm x 841mm'  # Standard size, NOT custom
            },
            'expected': 583.20
        },
        {
            'name': 'Test 3B: A1 Size - Medium Volume (200GSM Yuppo)',
            'params': {
                'quantity': 100,
                'width_mm': 594,
                'height_mm': 841,
                'paper_stock': '200GSM Yuppo Synthetic Paper',
                'artworks': 2,
                'size': 'A1 - 594mm x 841mm'  # Standard size, NOT custom
            },
            'expected': 845.86
        },
        {
            'name': 'Test 4: A0 Size - Large Order (250GSM Satin)',
            'params': {
                'quantity': 250,
                'width_mm': 841,
                'height_mm': 1189,
                'paper_stock': '250GSM Satin Poster Paper',
                'artworks': 2,
                'size': 'A0 - 841mm x 1189mm'  # Standard size, NOT custom
            },
            'expected': 2577.87
        },
        {
            'name': 'Test 5: Custom Size - High Volume (250GSM Satin)',
            'params': {
                'quantity': 500,
                'width_mm': 1000,
                'height_mm': 1400,
                'paper_stock': '250GSM Satin Poster Paper',
                'artworks': 3,
                'size': 'Custom'  # Custom size
            },
            'expected': 7903.10
        },
        {
            'name': 'Test 5B: Custom Size - High Volume (200GSM Yuppo)',
            'params': {
                'quantity': 500,
                'width_mm': 1000,
                'height_mm': 1400,
                'paper_stock': '200GSM Yuppo Synthetic Paper',
                'artworks': 3,
                'size': 'Custom'  # Custom size
            },
            'expected': 11570.61
        }
    ]
    
    print("=" * 80)
    print("CUSTOM POSTER PRINTING SHOPIFY CALCULATOR TESTS")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test['name']}")
        print("-" * 80)
        
        if test['expected'] is None:
            print("⚠️ SKIPPING - Need website price")
            continue
        
        try:
            result = calculator.calculate(**test['params'])
            backend_price = float(result.total_price)
            expected_price = test['expected']
            difference = backend_price - expected_price
            percent_diff = (difference / expected_price) * 100
            
            print(f"Backend:  ${backend_price:.2f}")
            print(f"Expected: ${expected_price:.2f}")
            print(f"Difference: ${difference:.2f} ({percent_diff:+.2f}%)")
            
            if abs(percent_diff) < 0.5:
                print("✅ PASS")
                passed += 1
            else:
                print("❌ FAIL - Difference exceeds 0.5%")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

if __name__ == '__main__':
    test_custom_poster_printing()
