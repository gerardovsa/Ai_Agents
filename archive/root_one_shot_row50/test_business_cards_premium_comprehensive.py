import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from business_card_calculator_shopify import ShopifyBusinessCardCalculator, PrintType, FinishSize, StockTypePremium, CelloglazePremium
from decimal import Decimal

calc = ShopifyBusinessCardCalculator()

print("="*80)
print("PREMIUM BUSINESS CARDS - COMPREHENSIVE VALIDATION TESTS")
print("="*80)
print()

tests = [
    {
        "name": "TEST 1: Website Config - 1000 King Kong Double Gloss",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.KINGKONG_420GSM,
            "celloglaze": CelloglazePremium.TWO_SIDE_GLOSS,
            "artworks": 1
        },
        "expected": Decimal('161.70'),
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 2: 500 Satin 350GSM Single Side Matt",
        "params": {
            "quantity": 500,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.SATIN_350GSM,
            "celloglaze": CelloglazePremium.ONE_SIDE_MATT,
            "artworks": 1
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 3: 1000 EcoStar 350GSM Double Silk",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.ECOSTAR_350GSM,
            "celloglaze": CelloglazePremium.TWO_SIDE_SILK,
            "artworks": 1
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 4: 250 Satin NO celloglaze (high margin test)",
        "params": {
            "quantity": 250,
            "sides": 1,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.SATIN_350GSM,
            "celloglaze": CelloglazePremium.NONE,
            "artworks": 1
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 5: 1000 Satin B&W Double Side (lower click cost)",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.BLACK_AND_WHITE,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.SATIN_350GSM,
            "celloglaze": CelloglazePremium.TWO_SIDE_GLOSS,
            "artworks": 1
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 6: 1000 small size 90x45 (30 cards/sheet)",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.SMALL_90X45,
            "stock_type": StockTypePremium.SATIN_350GSM,
            "celloglaze": CelloglazePremium.TWO_SIDE_GLOSS,
            "artworks": 1
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    },
    {
        "name": "TEST 7: Multiple artworks (3) - extra cost test",
        "params": {
            "quantity": 1000,
            "sides": 2,
            "print_type": PrintType.COLOR,
            "finish_size": FinishSize.STANDARD_90X55,
            "stock_type": StockTypePremium.SATIN_350GSM,
            "celloglaze": CelloglazePremium.TWO_SIDE_GLOSS,
            "artworks": 3
        },
        "expected": None,  # Need website validation
        "tolerance": Decimal('1.00')
    }
]

passed = 0
failed = 0
needs_validation = 0

for test in tests:
    print("-"*80)
    print(test["name"])
    print("-"*80)
    
    result = calc.calculate_premium_business_cards(**test["params"])
    
    print(f'Configuration:')
    print(f'  Quantity: {test["params"]["quantity"]}')
    print(f'  Sides: {test["params"]["sides"]}')
    print(f'  Print: {test["params"]["print_type"].value}')
    print(f'  Size: {test["params"]["finish_size"].value}')
    print(f'  Stock: {test["params"]["stock_type"].value}')
    print(f'  Celloglaze: {test["params"]["celloglaze"].value}')
    print(f'  Artworks: {test["params"]["artworks"]}')
    print()
    
    print(f'Backend Result: ${result.total_inc_gst:.2f}')
    print(f'Cost Breakdown:')
    print(f'  Setup: ${result.cost_breakdown["setup_cost"]:.2f}')
    print(f'  Paper: ${result.cost_breakdown["paper_cost"]:.2f}')
    print(f'  Clicks: ${result.cost_breakdown["click_cost"]:.2f}')
    print(f'  Cutting: ${result.cost_breakdown["cutting_cost"]:.2f}')
    print(f'  Celloglaze: ${result.cost_breakdown["celloglaze_cost"]:.2f}')
    print(f'  Artwork Extra: ${result.cost_breakdown["artwork_extra"]:.2f}')
    print(f'  Profit ({result.profit_margin_pct:.0f}%): ${result.cost_breakdown["profit_margin"]:.2f}')
    print(f'  Unit Price: ${result.unit_price_inc_gst:.4f}/card')
    print()
    
    if test["expected"] is not None:
        diff = abs(result.total_inc_gst - test["expected"])
        status = "PASS" if diff <= test["tolerance"] else "FAIL"
        print(f'Website Price: ${test["expected"]:.2f}')
        print(f'Difference: ${diff:.2f}')
        print(f'Status: {status}')
        
        if status == "PASS":
            passed += 1
        else:
            failed += 1
    else:
        print(f'Website Price: [NEEDS VALIDATION]')
        print(f'Status: PENDING')
        needs_validation += 1
    
    print()

print("="*80)
print("SUMMARY")
print("="*80)
print(f'Tests Passed: {passed}')
print(f'Tests Failed: {failed}')
print(f'Needs Website Validation: {needs_validation}')
print(f'Total Tests: {len(tests)}')
print()

if failed == 0 and passed > 0:
    print('✅ All validated tests PASSED!')
if needs_validation > 0:
    print(f'⚠️  {needs_validation} tests need website price validation')
