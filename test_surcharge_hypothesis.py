"""
HYPOTHESIS TEST: Website conditionally applies $54.63 fee based on printed_back_cover

If printed_back_cover == 'None':  surcharge = $98.63 ($44 + $54.63)
If printed_back_cover != 'None':  surcharge = $44 (no platform fee)
"""
from decimal import Decimal

# Test results from user
tests = [
    {"name": "Test 1", "backend": Decimal('640.69'), "website": Decimal('640.69'), "printed_back": "None"},
    {"name": "Test 2", "backend": Decimal('6189.18'), "website": Decimal('6134.55'), "printed_back": "350GSM Satin"},
    {"name": "Test 3", "backend": Decimal('14059.54'), "website": Decimal('14047.17'), "printed_back": "None"},
    {"name": "Test 4", "backend": Decimal('1069.28'), "website": Decimal('1069.27'), "printed_back": "None"},
    {"name": "Test 5", "backend": Decimal('1441.27'), "website": Decimal('1386.64'), "printed_back": "350GSM Satin"},
]

print("=" * 100)
print("HYPOTHESIS: $54.63 fee waived when printed_back_cover != 'None'")
print("=" * 100)
print()

for test in tests:
    diff = test['backend'] - test['website']
    expected_diff = Decimal('54.63') if test['printed_back'] != 'None' else Decimal('0')
    
    print(f"{test['name']}:")
    print(f"   Printed Back Cover: {test['printed_back']}")
    print(f"   Backend: ${test['backend']}")
    print(f"   Website: ${test['website']}")
    print(f"   Difference: ${diff:.2f}")
    print(f"   Expected if hypothesis true: ${expected_diff:.2f}")
    print(f"   Match: {'✅ YES' if abs(diff - expected_diff) < 15 else '❌ NO'}")
    print()

print("=" * 100)
print("CONCLUSION:")
print("=" * 100)
diffs = [abs((test['backend'] - test['website']) - (Decimal('54.63') if test['printed_back'] != 'None' else Decimal('0'))) for test in tests]
if all(d < 15 for d in diffs):
    print("✅ HYPOTHESIS CONFIRMED")
    print()
    print("Website applies conditional surcharge:")
    print("   - NO printed back cover: $98.63 surcharge ($44 + $54.63 platform fee)")
    print("   - WITH printed back cover: $44 surcharge (platform fee waived)")
    print()
    print("FIX REQUIRED:")
    print("   Update calculator to check printed_back_cover:")
    print("   if printed_back_cover == 'None':")
    print("       surcharge = Decimal('98.63')")
    print("   else:")
    print("       surcharge = Decimal('44')")
else:
    print("❌ HYPOTHESIS REJECTED - Pattern doesn't match")
    print(f"   Mismatches: {diffs}")
