import sys
import traceback
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_agents')

from tools.implementations.shopify_quote_calculator import calculate_shopify_quote

try:
    result = calculate_shopify_quote('wire_bound_books_shopify', quantity=3, pages=316, size='A4')
    print("SUCCESS:", result)
except Exception as e:
    print("\n" + "="*70)
    print("ERROR:", str(e))
    print("="*70)
    traceback.print_exc()
    print("="*70)
