"""
Quick test of Wire Bound calculator wrapper for Pacific Partnerships quotes
"""

import sys
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_agents\\inhouse_modules')

from shopify_calculator_wrappers import calculate_wire_bound_books_shopify

# Pacific Partnerships specs:
# - A4 Portrait
# - Clear Acetate front (250mic)
# - 350GSM Black Satin back
# - 100GSM Uncoated internals, full colour
# - 3 copies each

jobs = [
    {"name": "Job 1", "pages": 316},
    {"name": "Job 2", "pages": 372},
    {"name": "Job 3", "pages": 392},
    {"name": "Job 4", "pages": 372},
    {"name": "Job 5", "pages": 360}
]

print("\n" + "="*80)
print("PACIFIC PARTNERSHIPS - WIRE BOUND BOOKS QUOTES")
print("="*80)

for job in jobs:
    print(f"\n{job['name']}: {job['pages']} pages")
    print("-" * 40)
    
    try:
        result = calculate_wire_bound_books_shopify(
            quantity=3,
            pages=job['pages'],
            size="A4",
            cover_stock="350GSM Satin",
            inner_stock="100GSM Uncoated",
            cover_cellophane="No Cellophane",
            front_cover_pvc=True
        )
        
        print(f"  Total Price: ${result['total_price']:.2f}")
        print(f"  Unit Price:  ${result['unit_price']:.2f}")
        print(f"  Quantity:    {result['quantity']} books")
        
        if 'breakdown' in result and result['breakdown']:
            print(f"\n  Cost Breakdown:")
            for item, cost in result['breakdown'].items():
                print(f"    {item}: ${cost:.2f}")
                
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("Testing complete!")
print("="*80 + "\n")
