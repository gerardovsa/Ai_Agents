"""Test Group 3 calculators"""
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/implementations')

from calculator_wrapper import (
    calculate_notepads_a4,
    calculate_notepads_a5,
    calculate_notepads_a6,
    calculate_custom_poster_printing,
    calculate_custom_vinyl_stickers
)

print("\n" + "="*60)
print("GROUP 3: NOTEPADS & PRINTING CALCULATORS - TEST")
print("="*60)

tests = [
    ("Notepads A4", calculate_notepads_a4, {}),
    ("Notepads A5", calculate_notepads_a5, {}),
    ("Notepads A6", calculate_notepads_a6, {}),
    ("Custom Poster Printing", calculate_custom_poster_printing, {}),
    ("Custom Vinyl Stickers", calculate_custom_vinyl_stickers, {})
]

passed = 0
failed = 0

for name, func, params in tests:
    print(f"\n{name}:")
    print(f"  Test 1 (defaults): ", end="")
    try:
        result = func(quantity=500, **params)
        if result.get("success"):
            price = result.get("total_price", 0)
            print(f"✅ ${price:.2f}")
            passed += 1
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            failed += 1
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        failed += 1
    
    print(f"  Test 2 (with params): ", end="")
    try:
        # Custom Poster and Vinyl Stickers don't support artworks (backend limitation)
        if "Poster" in name or "Stickers" in name:
            result = func(quantity=1000, width_mm=300, height_mm=400)
        else:
            result = func(quantity=1000, artworks=2)
        if result.get("success"):
            price = result.get("total_price", 0)
            print(f"✅ ${price:.2f}")
            passed += 1
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            failed += 1
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        failed += 1

print("\n" + "="*60)
print(f"RESULTS: {passed}/10 tests passing ({passed*10}%)")
print("="*60)

if passed == 10:
    print("🎉 ALL GROUP 3 TESTS PASSING!")
else:
    print(f"⚠️  {failed} tests still failing")
