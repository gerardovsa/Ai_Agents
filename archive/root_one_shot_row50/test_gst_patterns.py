from decimal import Decimal

# My subtotal: $381.20
sub = Decimal('381.20')

# Test different GST patterns
gst_10_double = sub * Decimal('1.1') * Decimal('1.1')
gst_15_plus_44 = (sub * Decimal('1.15')) + Decimal('44')
gst_10_single = sub * Decimal('1.1')

print(f'Subtotal: ${sub}')
print(f'')
print(f'Option 1 - 10% double GST (×1.21): ${gst_10_double:.2f}')
print(f'Option 2 - 15% GST + $44: ${gst_15_plus_44:.2f}')
print(f'Option 3 - 10% single GST: ${gst_10_single:.2f}')
print(f'')
print(f'Website shows: $640.69')
print(f'')

# Work backwards from website
website = Decimal('640.69')
backward_div_121 = website / Decimal('1.21')
backward_div_115_minus_44 = (website - Decimal('44')) / Decimal('1.15')
backward_div_11 = website / Decimal('1.1')

print(f'If 10% double GST, subtotal would be: ${backward_div_121:.2f}')
print(f'If 15% GST + $44, subtotal would be: ${backward_div_115_minus_44:.2f}')
print(f'If 10% single GST, subtotal would be: ${backward_div_11:.2f}')
print(f'')
print(f'My calculated subtotal: ${sub}')
print(f'')

# Maybe BizCost is wrong?
# Calculate what BizCost should be if website is correct
bizcost_if_90margin_10double = (website / Decimal('1.21')) / Decimal('1.9')
bizcost_if_90margin_15plus44 = ((website - Decimal('44')) / Decimal('1.15')) / Decimal('1.9')

print(f'If 10% double GST + 90% margin, BizCost should be: ${bizcost_if_90margin_10double:.2f}')
print(f'If 15% GST + $44 + 90% margin, BizCost should be: ${bizcost_if_90margin_15plus44:.2f}')
print(f'My calculated BizCost: $200.63')
