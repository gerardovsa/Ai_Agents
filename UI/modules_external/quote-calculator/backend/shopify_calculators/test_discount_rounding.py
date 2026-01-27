"""Test different discount calculation methods"""

subtotal = 560.56

# Method 1: Calculate discount amount, then subtract
discount_amt_1 = round(subtotal * 0.05, 2)
final_1 = round(subtotal - discount_amt_1, 2)
print(f"Method 1 (subtract rounded discount):")
print(f"  Subtotal: ${subtotal:.2f}")
print(f"  Discount: ${discount_amt_1:.2f}")
print(f"  Final: ${final_1:.2f}")
print()

# Method 2: Multiply by 0.95 then round
final_2 = round(subtotal * 0.95, 2)
print(f"Method 2 (multiply 0.95):")
print(f"  Subtotal: ${subtotal:.2f}")
print(f"  Discount: ${round(subtotal * 0.05, 2):.2f}")
print(f"  Final: ${final_2:.2f}")
print()

# Method 3: What if discount is calculated BEFORE rounding eyelet cost?
base = 538.56  # cost_after_custom
eyelet = 22.00
subtotal_unrounded = base + eyelet  # 560.56
discounted = subtotal_unrounded * 0.95  # 532.532
final_3 = round(discounted, 2)
print(f"Method 3 (discount before final round):")
print(f"  Subtotal: ${subtotal_unrounded:.2f}")
print(f"  × 0.95: ${discounted}")
print(f"  Rounded: ${final_3:.2f}")
print()

# Method 4: What if website uses floor/truncate instead of round?
import math
final_4 = math.floor(subtotal * 0.95 * 100) / 100
print(f"Method 4 (floor/truncate):")
print(f"  Subtotal × 0.95: ${subtotal * 0.95}")
print(f"  Floor to cents: ${final_4:.2f}")
