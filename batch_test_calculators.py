"""Batch test multiple calculators"""
import sys
from pathlib import Path
from decimal import Decimal

backend_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
calculators_dir = backend_dir / 'shopify_calculators'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(calculators_dir))

calculators = [
    ('FoldedFlyers_Shopify_Calculator', 'Shopify_Folded_Flyers.json', [
        ({'quantity': 100, 'finish_size': 'A4 - 210mm x 297mm', 'folding': '1 Fold', 'print_sides': 'Double side print', 'print_type': 'Colour', 'paper_stock': 'Satin 150GSM', 'artworks': 1}, None),
        ({'quantity': 500, 'finish_size': 'DL - 99mm x 210mm', 'folding': '2 Fold', 'print_sides': 'Double side print', 'print_type': 'Colour', 'paper_stock': 'Satin 200GSM', 'artworks': 1}, None)
    ]),
    ('PrintedFlyers_Shopify_Calculator', 'Shopify_Printed_Flyers.json', [
        ({'quantity': 100, 'finish_size': 'A4 - 210mm x 297mm', 'print_sides': 'Single side print', 'print_type': 'Colour', 'paper_stock': 'Satin 150GSM', 'artworks': 1}, None),
        ({'quantity': 500, 'finish_size': 'DL - 99mm x 210mm', 'print_sides': 'Double side print', 'print_type': 'Black & White', 'paper_stock': 'Uncoated Bond 80GSM', 'artworks': 1}, None)
    ])
]

for calc_name, json_name, tests in calculators:
    print(f"\n{'='*80}")
    print(f"Testing: {calc_name}")
    print(f"{'='*80}")
    
    try:
        exec(f"from {calc_name} import {calc_name.replace('_Shopify_Calculator', 'ShopifyCalculator')}")
        calc_class = eval(calc_name.replace('_Shopify_Calculator', 'ShopifyCalculator'))
        
        # Get baseline
        calc_hardcoded = calc_class()
        config_path = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / json_name
        calc_json = calc_class(config_path=str(config_path))
        
        passed = 0
        for i, (params, _) in enumerate(tests, 1):
            baseline = calc_hardcoded.calculate(**params).total_price
            json_result = calc_json.calculate(**params).total_price
            diff = abs(json_result - baseline)
            status = "✅" if diff < Decimal('0.01') else "❌"
            print(f"Test {i}: ${json_result:.2f} vs ${baseline:.2f} - {status}")
            if diff < Decimal('0.01'):
                passed += 1
        
        print(f"Result: {passed}/{len(tests)} passed")
        
    except Exception as e:
        print(f"ERROR: {e}")
