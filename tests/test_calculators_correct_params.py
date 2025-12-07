"""
Final test with CORRECT parameter names discovered from function signatures.
This will prove the calculators work when called correctly.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'inhouse_modules'))

from decimal import Decimal
from inhouse_modules.db_connector import InHousePrintDB
from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator

def main():
    print("\n" + "="*80)
    print("TESTING CALCULATORS WITH CORRECT PARAMETERS")
    print("="*80)
    
    # Connect to database
    config_path = r"c:\Users\gpoli\GIT\In_House_SQL\config\database-config.json"
    db = InHousePrintDB(config_path)
    calc = ComprehensiveQuoteCalculator(db)
    
    print("\n[OK] Database connected and calculator initialized")
    print("-"*80)
    
    # Test 1: Business Cards (CORRECT PARAMETERS)
    print("\n1. BUSINESS CARDS")
    print("   Method: calculate_business_cards()")
    print("   Parameters: quantity=500, stock_type='satin_350gsm', sides=2")
    
    try:
        result = calc.calculate_business_cards(
            quantity=500,
            stock_type="satin_350gsm",
            sides=2,
            print_type="color",
            finish_size="standard",
            celloglaze="none",
            artworks=1
        )
        print(f"   [PASS] Result type: {type(result)}")
        print(f"   Cost: {result}")  # Will print the QuoteResult object
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
    
    # Test 2: Flyers (CORRECT PARAMETERS)
    print("\n2. FLYERS - A5 Single Sided")
    print("   Method: calculate_flyers()")
    print("   Parameters: quantity=1000, width=148, height=210, gsm=170")
    
    try:
        result = calc.calculate_flyers(
            quantity=1000,
            width=148,
            height=210,
            gsm=170,
            print_side1=2,  # Color
            print_side2=0,  # No back printing
            folding_required=False,
            cello_required=False,
            discount=Decimal('0')
        )
        print(f"   [PASS] Result type: {type(result)}")
        print(f"   Cost: {result}")
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
    
    # Test 3: Perfect Bound Book (CORRECT PARAMETERS)
    print("\n3. PERFECT BOUND BOOK - A5, 200 pages")
    print("   Method: calculate_perfect_bound_book()")
    print("   Parameters: quantity=100, book_width=148, book_height=210, pages=200")
    
    try:
        result = calc.calculate_perfect_bound_book(
            quantity=100,
            book_width=148,
            book_height=210,
            pages=200,
            stock_type_id=1,
            internal_stock_gsm=100,
            internal_print_mode=1,  # Color
            cover_stock_type_id=1,
            cover_stock_gsm=300,
            cover_print_mode=1,
            cello_type=1,  # Gloss
            is_scored=False,
            colour_pages=0,
            colour_insert_type=0,
            binding_type="Perfect Bound",
            artworks=1,
            discount=Decimal('0')
        )
        print(f"   [PASS] Result type: {type(result)}")
        print(f"   Cost: {result}")
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
    
    # Test 4: Booklets (CORRECT PARAMETERS)
    print("\n4. BOOKLETS - A5, 24 pages")
    print("   Method: calculate_booklets()")
    print("   Parameters: quantity=200, width=148, height=210, pages=24")
    
    try:
        result = calc.calculate_booklets(
            quantity=200,
            width=148,
            height=210,
            pages=Decimal('24'),
            stock_type_id=1,
            stock_gsm=100,
            print_mode=1,  # Color
            staple_required=True,
            fold_required=True,
            is_scored=False,
            colour_pages=0,
            discount=Decimal('0')
        )
        print(f"   [PASS] Result type: {type(result)}")
        print(f"   Cost: {result}")
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
    
    # Test 5: Letterheads (CORRECT PARAMETERS)
    print("\n5. LETTERHEADS - A4")
    print("   Method: calculate_letterheads()")
    print("   Parameters: quantity=500, width=210, height=297, gsm=100")
    
    try:
        result = calc.calculate_letterheads(
            quantity=500,
            width=210,
            height=297,
            gsm=100,
            print_side1=2,  # Color
            print_side2=0,  # Blank back
            discount=Decimal('0')
        )
        print(f"   [PASS] Result type: {type(result)}")
        print(f"   Cost: {result}")
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
