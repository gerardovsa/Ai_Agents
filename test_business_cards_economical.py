import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from business_card_calculator_shopify import ShopifyBusinessCardCalculator, PrintType, FinishSize, StockTypeStandard
from decimal import Decimal

calc = ShopifyBusinessCardCalculator()

print("="*80)
print("ECONOMICAL BUSINESS CARDS - COMPREHENSIVE VALIDATION TESTS")
print("="*80)
print()

tests = [
    {
        "name": "TEST 1: 500 Single-sided Color (TXT Example 1)",
        "params": {
            "quantity": 500,
            "sides": 1,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 1
        },
        "expected_range": (Decimal('80'), Decimal('120')),
        "description": "Standard single-sided color business cards"
    },
    {
        "name": "TEST 2: 1000 Double-sided Color 3 artworks (TXT Example 2)",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 3
        },
        "expected_range": (Decimal('150'), Decimal('220')),
        "description": "Double-sided color cards with multiple designs"
    },
    {
        "name": "TEST 3: 250 Single-sided B&W (TXT Example 3)",
        "params": {
            "quantity": 250,
            "sides": 1,
            "print_type": PrintType.BLACK_AND_WHITE,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 1
        },
        "expected_range": (Decimal('50'), Decimal('80')),
        "description": "Budget black & white cards"
    },
    {
        "name": "TEST 4: 5000 Double-sided Color (TXT Example 4)",
        "params": {
            "quantity": 5000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 1
        },
        "expected_range": (Decimal('400'), Decimal('600')),
        "description": "High volume order"
    },
    {
        "name": "TEST 5: 1000 Double-sided Color (Common Config)",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 1
        },
        "expected": None,  # Will validate on website
        "expected_range": None,
        "description": "Most common configuration - needs website validation"
    },
    {
        "name": "TEST 6: 2000 Single-sided Color",
        "params": {
            "quantity": 2000,
            "sides": 1,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypeStandard.SATIN_300GSM,
            "artworks": 1
        },
        "expected": None,
        "expected_range": None,
        "description": "Mid-volume single-sided - needs website validation"
    }
]

passed = 0
failed = 0
needs_validation = 0

for test in tests:
    print("-"*80)
    print(test["name"])
    print("-"*80)
    
    result = calc.calculate_standard_business_cards(**test["params"])
    
    print(f'Configuration:')
    print(f'  Quantity: {test["params"]["quantity"]}')
    print(f'  Sides: {test["params"]["sides"]}')
    print(f'  Print: {test["params"]["print_type"].value}')
    print(f'  Stock: {test["params"]["stock_type"].value}')
    print(f'  Artworks: {test["params"]["artworks"]}')
    print()
    
    print(f'Backend Result: ${result.total_inc_gst:.2f}')
    print(f'Cost Breakdown:')
    print(f'  Setup (incl. artwork): ${result.cost_breakdown["setup_cost"]:.2f}')
    print(f'  Paper: ${result.cost_breakdown["paper_cost"]:.2f}')
    print(f'  Clicks: ${result.cost_breakdown["click_cost"]:.2f}')
    print(f'  Cutting: ${result.cost_breakdown["cutting_cost"]:.2f}')
    print(f'  Profit ({result.profit_margin_pct:.0f}%): ${result.cost_breakdown["profit_margin"]:.2f}')
    print(f'  Unit Price: ${result.unit_price_inc_gst:.4f}/card')
    print()
    
    if "expected_range" in test and test["expected_range"] is not None:
        min_price, max_price = test["expected_range"]
        in_range = min_price <= result.total_inc_gst <= max_price
        status = "PASS" if in_range else "FAIL"
        print(f'Expected Range: ${min_price:.2f} - ${max_price:.2f}')
        print(f'Status: {status}')
        
        if status == "PASS":
            passed += 1
        else:
            failed += 1
    elif "expected" in test and test["expected"] is not None:
        diff = abs(result.total_inc_gst - test["expected"])
        status = "PASS" if diff <= Decimal('1.00') else "FAIL"
        print(f'Expected Price: ${test["expected"]:.2f}')
        print(f'Difference: ${diff:.2f}')
        print(f'Status: {status}')
        
        if status == "PASS":
            passed += 1
        else:
            failed += 1
    else:
        print(f'Expected Price: [NEEDS WEBSITE VALIDATION]')
        print(f'Status: PENDING')
        needs_validation += 1
    
    print()

print("="*80)
print("SUMMARY")
print("="*80)
print(f'Tests Passed (in range): {passed}')
print(f'Tests Failed: {failed}')
print(f'Needs Website Validation: {needs_validation}')
print(f'Total Tests: {len(tests)}')
print()

if failed == 0:
    print('✅ All validated tests PASSED!')
if needs_validation > 0:
    print(f'⚠️  {needs_validation} tests need website price validation')
