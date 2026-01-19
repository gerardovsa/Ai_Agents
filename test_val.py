import sys
sys.path.insert(0, "UI/modules_external/quote-calculator/implementations")
from calculator_wrapper import calculate_economical_business_cards_shopify

print("\n" + "="*60)
print("VALIDATION TESTING")
print("="*60)

# Test invalid print_type
result = calculate_economical_business_cards_shopify(quantity=500, print_type="Rainbow")
print(f"\n1. Invalid print_type: success={result.get('success')}")
print(f"   Error: {result.get('error', 'N/A')}")

# Test invalid celloglaze
result = calculate_economical_business_cards_shopify(quantity=500, celloglaze="Shiny")
print(f"\n2. Invalid celloglaze: success={result.get('success')}")
print(f"   Error: {result.get('error', 'N/A')}")

# Test invalid artworks
result = calculate_economical_business_cards_shopify(quantity=500, artworks=100)
print(f"\n3. Invalid artworks: success={result.get('success')}")
print(f"   Error: {result.get('error', 'N/A')}")

# Test valid call
result = calculate_economical_business_cards_shopify(quantity=500)
print(f"\n4. Valid with defaults: success={result.get('success')}")
if result.get('success'):
    print(f"   Price: ${result.get('total_price'):.2f}")
