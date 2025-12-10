import sys
import traceback
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_agents')

from inhouse_modules.shopify_calculator_wrappers import calculate_wire_bound_books_shopify

print("Testing wire_bound_books_shopify wrapper directly...")
print("="*70)

try:
    result = calculate_wire_bound_books_shopify(
        quantity=3,
        pages=316,
        size="A4"
    )
    print("\nSUCCESS:")
    print(result)
except Exception as e:
    print("\n" + "="*70)
    print("ERROR:", str(e))
    print("="*70)
    print("\nFull traceback:")
    traceback.print_exc()
    print("="*70)
