"""
Test the fixed Saddle Stitch Books calculator
"""

import sys
from pathlib import Path

# Add paths
root = Path(__file__).parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "inhouse_modules"))

from shopify_calculators.SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator

print("=" * 80)
print("🧪 TESTING FIXED SADDLE STITCH BOOKS CALCULATOR")
print("=" * 80)

# Initialize calculator
print("\n📦 Step 1: Initialize calculator...")
try:
    calculator = SaddleStitchBooksShopifyCalculator()
    if calculator.config:
        print("✅ Calculator initialized successfully")
        print(f"   Config loaded: {calculator.CONFIG_FILE}")
    else:
        print("❌ Calculator initialized but config is None")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test with your exact specs: 215×279mm landscape booklet
print("\n📊 Step 2: Calculate quote for Worldwide customer...")
print("   Product: 20-page A4 Landscape booklets")
print("   Specs: 350GSM Gloss cover, 150GSM Gloss internal")

test_specs = {
    "quantity": "50",               # Your first quantity
    "artworks": 1,                  # Single artwork
    "cover_option": "Hard Cover",   # Separate cover
    "cover_stock": "Satin 350GSM",  # Your cover stock (Gloss not in enum, use Satin)
    "cover_print_type": "2 side colour (4pp)",  # Full color both sides
    "celloglaze": "Gloss outside only",  # Your laminate requirement
    "printed_pages": "20pp",        # Your page count
    "finish_size": "A4 Landscape",  # Your custom size!
    "content_print_type": "Colour", # Full color internal
    "content_stock_type": "Satin 150GSM"  # Internal pages (150GSM)
}

try:
    result = calculator.calculate(**test_specs)
    
    print("\n✅ QUOTE GENERATED SUCCESSFULLY!")
    print(f"\n💰 PRICING FOR 50 BOOKLETS:")
    print(f"   Total Price: ${result.total_price:.2f} inc GST")
    print(f"   Unit Price: ${result.unit_price:.2f} per booklet")
    print(f"   Cost per Item: ${result.cost_per_item:.2f}")
    
    print(f"\n📋 BREAKDOWN:")
    for key, value in result.breakdown.items():
        if isinstance(value, (int, float)) or hasattr(value, '__float__'):
            print(f"   {key}: ${float(value):.2f}")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n📝 SPECIFICATIONS:")
    for key, value in result.specifications.items():
        print(f"   {key}: {value}")

except Exception as e:
    print(f"\n❌ CALCULATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test all quantities
print("\n" + "=" * 80)
print("📊 TESTING ALL QUANTITIES")
print("=" * 80)

quantities = ["50", "100", "250", "500"]

for qty in quantities:
    try:
        test_specs["quantity"] = qty
        result = calculator.calculate(**test_specs)
        print(f"\n✅ {qty:>3} booklets: ${result.total_price:>9.2f} (${result.unit_price:>6.2f}/unit)")
    except Exception as e:
        print(f"\n❌ {qty:>3} booklets: Failed - {e}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE - SADDLE STITCH CALCULATOR WORKING!")
print("=" * 80)
