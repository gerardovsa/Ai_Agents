import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/backend/shopify_calculators')

from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator, Celloglaze, PaperStock, PrintSides, PrintType, FinishSize, FoldType

# Test 3: A5 Budget Single B&W Uncoated with celloglaze=NONE (should PASS with fix)
calc = FoldedFlyersShopifyCalculator()

try:
    result = calc.calculate_quote(
        quantity=250,
        print_sides=PrintSides.SINGLE_SIDE,
        print_type=PrintType.BLACK_WHITE,
        finish_size=FinishSize.A5,
        paper_stock=PaperStock.UNCOATED_100GSM,
        artworks=1,
        fold_type=FoldType.HALF_FOLD_TO_A6,
        celloglaze=Celloglaze.NONE
    )
    print(f"✅ CELLOGLAZE FIX WORKS! Price: {result.final_price}")
except ValueError as e:
    print(f"❌ CELLOGLAZE FIX FAILED: {e}")
    
    # Check the actual source code Python is using
    import inspect
    source_file = inspect.getsourcefile(calc.calculate_quote)
    print(f"\nSource file: {source_file}")
    
    lines = inspect.getsourcelines(calc.calculate_quote)[0]
    print("\nLines 5-10 of calculate_quote (around celloglaze validation):")
    for i, line in enumerate(lines[5:10], start=6):
        print(f"{i}: {line.rstrip()}")
