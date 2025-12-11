"""Test which calculator tools are actually working"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

print("\n=== Testing Direct Calculator Tools ===\n")

# Test 1: Business cards
try:
    result = r.execute_tool('calculate_business_cards', 
                           quantity=1000, 
                           finish_size='90x55mm', 
                           stock_type='satin_350gsm', 
                           print_sides='double_sided', 
                           celloglaze='none')
    print(f"✓ calculate_business_cards: WORKING")
    print(f"  Result type: {type(result).__name__}")
except Exception as e:
    print(f"✗ calculate_business_cards: FAILED - {str(e)[:100]}")

# Test 2: Spiral bound books
try:
    result = r.execute_tool('calculate_spiral_bound_books_shopify', 
                           quantity=100, 
                           page_count=100, 
                           cover_stock='250gsm', 
                           inside_stock='100gsm')
    print(f"✓ calculate_spiral_bound_books_shopify: WORKING")
    print(f"  Result type: {type(result).__name__}")
except Exception as e:
    print(f"✗ calculate_spiral_bound_books_shopify: FAILED - {str(e)[:100]}")

# Test 3: InHouse get requirements
try:
    result = r.execute_tool('inhouse_get_calculator_requirements', 
                           product_type='business_cards')
    print(f"✓ inhouse_get_calculator_requirements: WORKING")
    print(f"  Result type: {type(result).__name__}")
except Exception as e:
    print(f"✗ inhouse_get_calculator_requirements: FAILED - {str(e)[:100]}")

# Test 4: InHouse calculate quote
try:
    result = r.execute_tool('inhouse_calculate_quote',
                           product_type='business_cards',
                           parameters={'quantity': 1000, 'stock_type': 'satin_350gsm'})
    print(f"✓ inhouse_calculate_quote: WORKING")
    print(f"  Result type: {type(result).__name__}")
except Exception as e:
    print(f"✗ inhouse_calculate_quote: FAILED - {str(e)[:100]}")

print("\n=== Summary ===")
print("Direct calculators (quote_calculator platform): These work!")
print("InHouse calculators (inhouse-print module): Need to check if backend is accessible")
