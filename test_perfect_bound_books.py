import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from decimal import Decimal

calc = PerfectBoundShopifyCalculator()

print("="*80)
print("PERFECT BOUND BOOKS - VALIDATION TESTS")
print("="*80)
print()

# Test 1: Standard B&W Novel (from backend example)
print("-"*80)
print("TEST 1: Standard B&W Novel")
print("-"*80)
result = calc.calculate(
    quantity=500,
    printed_pages=200,
    proof_requirements="Digital Emailed Proof",
    cover_stock="Satin 300GSM",
    cover_print_type="2 side colour (4pp)",
    celloglaze="Matt outside only",
    finish_size="A5 Portrait",
    content_print_type="Black & White",
    content_stock_type="Uncoated Bond 100GSM"
)

print(f"Configuration:")
print(f"  Quantity: {result.specifications['quantity']}")
print(f"  Pages: {result.specifications['printed_pages']}")
print(f"  Size: {result.specifications['finish_size']}")
print(f"  Cover: {result.specifications['cover_stock']} - {result.specifications['cover_print_type']}")
print(f"  Celloglaze: {result.specifications['celloglaze']}")
print(f"  Content: {result.specifications['content_stock_type']} - {result.specifications['content_print_type']}")
print(f"  Proof: {result.specifications['proof_requirements']}")
print()

print(f"Backend Result: ${result.total_price:,.2f}")
print(f"Unit Price: ${result.unit_price:.4f}/book")
print()

print(f"Cost Breakdown:")
print(f"  Setup: ${result.breakdown['setup_costs']:.2f}")
print(f"  Proof: ${result.breakdown['proof_cost']:.2f}")
print(f"  Cover: ${result.breakdown['cover_cost']:.2f}")
print(f"  Content: ${result.breakdown['content_cost']:.2f}")
print(f"  Celloglaze: ${result.breakdown['cello_cost']:.2f}")
print(f"  Cutting: ${result.breakdown['cutting_cost']:.2f}")
print(f"  Binding: ${result.breakdown['binding_cost']:.2f}")
print(f"  BizCost: ${result.breakdown['biz_cost']:.2f}")
print(f"  Profit ({result.breakdown['profit_margin_rate']*100:.0f}%): ${result.breakdown['profit_amount']:.2f}")
print(f"  Subtotal: ${result.breakdown['subtotal']:.2f}")
print(f"  Overs ({result.breakdown['extra_books_qty']:.0f} books): ${result.breakdown['overs_cost']:.2f}")
print(f"  Subtotal + Overs: ${result.breakdown['subtotal_with_overs']:.2f}")
print(f"  GST (double): ${result.breakdown['gst_amount']:.2f}")
print(f"  Final: ${result.total_price:.2f}")
print()
print(f"Website Price: [NEEDS VALIDATION]")
print()

# Test 2: Full Color Magazine
print("-"*80)
print("TEST 2: Full Color Magazine with Physical Proof")
print("-"*80)
result2 = calc.calculate(
    quantity=250,
    printed_pages=48,
    proof_requirements="Physical Unbound Proof",
    cover_stock="Satin 300GSM",
    cover_print_type="2 side colour (4pp)",
    celloglaze="Gloss outside only",
    finish_size="A4 Portrait",
    content_print_type="Full Colour",
    content_stock_type="Satin 128GSM"
)

print(f"Backend Result: ${result2.total_price:,.2f}")
print(f"Unit Price: ${result2.unit_price:.4f}/book")
print(f"BizCost: ${result2.breakdown['biz_cost']:.2f}")
print(f"Profit ({result2.breakdown['profit_margin_rate']*100:.0f}%): ${result2.breakdown['profit_amount']:.2f}")
print(f"Includes: {result2.specifications['extra_books_included']} extra books + Physical Proof ($40)")
print(f"Website Price: [NEEDS VALIDATION]")
print()

# Test 3: Small A5 Book (minimal config)
print("-"*80)
print("TEST 3: Small A5 Book (40 pages, B&W)")
print("-"*80)
result3 = calc.calculate(
    quantity=100,
    printed_pages=40,  # Minimum pages
    proof_requirements="Digital Emailed Proof",
    cover_stock="Satin 300GSM",
    cover_print_type="2 side colour (4pp)",
    celloglaze="None",
    finish_size="A5 Portrait",
    content_print_type="Black & White",
    content_stock_type="Uncoated Bond 80GSM"  # Cheapest stock
)

print(f"Backend Result: ${result3.total_price:,.2f}")
print(f"Unit Price: ${result3.unit_price:.4f}/book")
print(f"BizCost: ${result3.breakdown['biz_cost']:.2f}")
print(f"Profit ({result3.breakdown['profit_margin_rate']*100:.0f}%): ${result3.breakdown['profit_amount']:.2f}")
print(f"Bind cost/book: ${result3.specifications['bind_cost_per_book']:.2f}")
print(f"Website Price: [NEEDS VALIDATION]")
print()

# Test 4: Large Volume Order
print("-"*80)
print("TEST 4: Large Volume Order (5000 books)")
print("-"*80)
result4 = calc.calculate(
    quantity=5000,
    printed_pages=100,
    proof_requirements="Digital Emailed Proof",
    cover_stock="Satin 300GSM",
    cover_print_type="2 side colour (4pp)",
    celloglaze="None",
    finish_size="A4 Portrait",
    content_print_type="Black & White",
    content_stock_type="Uncoated Bond 100GSM"
)

print(f"Backend Result: ${result4.total_price:,.2f}")
print(f"Unit Price: ${result4.unit_price:.4f}/book")
print(f"BizCost: ${result4.breakdown['biz_cost']:.2f}")
print(f"Profit ({result4.breakdown['profit_margin_rate']*100:.0f}%): ${result4.breakdown['profit_amount']:.2f}")
print(f"Bind cost/book: ${result4.specifications['bind_cost_per_book']:.2f} (volume discount)")
print(f"Website Price: [NEEDS VALIDATION]")
print()

# Test 5: US Trade Size
print("-"*80)
print("TEST 5: US Trade Size (152mm x 229mm)")
print("-"*80)
result5 = calc.calculate(
    quantity=1000,
    printed_pages=200,
    proof_requirements="Digital Emailed Proof",
    cover_stock="Satin 300GSM",
    cover_print_type="1 side colour (2pp)",  # Front only
    celloglaze="None",
    finish_size="US Trade - 152mm x 229mm",
    content_print_type="Black & White",
    content_stock_type="Uncoated Bond 90GSM"
)

print(f"Backend Result: ${result5.total_price:,.2f}")
print(f"Unit Price: ${result5.unit_price:.4f}/book")
print(f"Website Price: [NEEDS VALIDATION]")
print()

print("="*80)
print("SUMMARY")
print("="*80)
print("All tests completed. Prices use DOUBLE GST (×1.1 ×1.1 = ×1.21)")
print("Need website validation to confirm formula accuracy.")
print()
print("Key Formula Features:")
print("  ✓ Quantity-based binding costs (8 tiers)")
print("  ✓ BizCost-based profit margins (12 tiers)")
print("  ✓ Extra books (overs) included in price")
print("  ✓ Double GST application (like Premium Business Cards)")
print("  ✓ No surcharge ($0)")
print("  ✓ No price increase (0%)")
