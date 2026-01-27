from decimal import Decimal, ROUND_HALF_UP

# Test 1: 100 books, A5, 40pp, Bond 80GSM, B&W, 300GSM Satin front, 1pp Color
# Website: $640.69 Inc GST

qty = Decimal('100')
pages = Decimal('40')
artworks = 1

# Constants from TXT lines 3865-3875
guilo_setup = Decimal('12')
impos_setup = Decimal('15')
stock_waste = Decimal('1.05')
extra_arts = Decimal('15')
cutting_blk = Decimal('500')
cut_cost = Decimal('11')
punch_setup = Decimal('15')
wirebind_per_book = Decimal('1.16')
bindery_labor = Decimal('70')
punch_sheets_hour = Decimal('15000')

# Extra artwork calculation
_a = Decimal(str(artworks)) * extra_arts
_a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)
print(f'Extra artwork charge: ${_a2}')

# Front cover - TXT 3889-3893
outer_front_price = Decimal('0')  # Not Required
front_stock_price = Decimal('0.14')  # 300GSM Satin
cover_print_price = Decimal('0.04')  # 1pp Color
finish_imp = Decimal('8')  # A5 Portrait = 8 books per sheet

out_front = outer_front_price * qty
print(f'outFront: ${out_front}')

total_front_cover_sheets = (qty / finish_imp) * stock_waste
print(f'totalFrontCoverSheets: {total_front_cover_sheets}')

cover_click_cost = cover_print_price * total_front_cover_sheets
print(f'coverClickCost: ${cover_click_cost}')

total_front_cover_cost = (total_front_cover_sheets * front_stock_price) + cover_click_cost
print(f'totalFrontCoverCost: ${total_front_cover_cost}')

# Back cover - None
out_back = Decimal('0')
total_back_cover_sheets = Decimal('0')
total_back_cover_cost = Decimal('0')
print(f'Back cover costs: $0')

# Content - TXT 3901-3903
content_stock_price = Decimal('26.34')  # Bond 80GSM per 1000 sheets
content_print_price = Decimal('0.015')  # B&W per sheet

total_content_sheets = (((qty * pages) / Decimal('2')) / finish_imp) * stock_waste
print(f'\ntotalContentSheets: {total_content_sheets}')

content_click_cost = total_content_sheets * content_print_price
print(f'contentClickCost: ${content_click_cost}')

# TXT LINE 3903: totalContentCost = ({totalContentSheets} * {F12.price}) + {contentClickCost}
# This is the KEY line - is F12.price used directly or divided?
total_content_cost = (total_content_sheets * content_stock_price) + content_click_cost
print(f'totalContentCost (using {content_stock_price} directly): ${total_content_cost}')

total_content_cost_divided = (total_content_sheets * content_stock_price / Decimal('1000')) + content_click_cost
print(f'totalContentCost (dividing by 1000): ${total_content_cost_divided}')

# Let me use the DIVIDED version (as backend currently does)
total_content_cost = total_content_cost_divided

# Celloglaze costs
front_cello_cost = Decimal('0')
back_cello_cost = Decimal('0')

# Total print cost
total_print_cost = total_front_cover_cost + total_back_cover_cost + front_cello_cost + back_cello_cost + out_front + out_back + total_content_cost
print(f'\ntotalPrintCost: ${total_print_cost:.2f}')

# Setup costs
cello_setup = Decimal('0')  # No celloglaze
total_setup = guilo_setup + impos_setup + punch_setup + cello_setup + _a2
print(f'totalSetupCosts: ${total_setup}')

# Wire cost - TXT 3908-3940
book_sheets = pages / Decimal('2')
content_thickness = Decimal('0.1')  # Bond 80GSM
book_thickness = book_sheets * content_thickness
print(f'\nbookThickness: {book_thickness}mm')

price_per_ring = Decimal('0.13065')  # <= 8mm tier
print(f'pricePerRing: ${price_per_ring}')

# A5 Portrait NOT in small formats list (only A6/DL/A5 Landscape)
price_of_wire = price_per_ring * qty
print(f'priceOfWire: ${price_of_wire}')

# Punch - TXT 3943-3949
base_value = (qty * pages) / Decimal('2')
additional_f8 = Decimal('0')  # No printed back cover
additional_f4 = qty  # Has printed front cover
total_punch = base_value + additional_f8 + additional_f4
sheets_to_punch = total_punch * stock_waste
print(f'\nsheetsToPunch: {sheets_to_punch}')

punch_price = (sheets_to_punch / punch_sheets_hour) * bindery_labor
print(f'punchPrice: ${punch_price:.2f}')

# Cutting
cutting_cost = ((total_content_sheets + total_front_cover_sheets + total_back_cover_sheets) / cutting_blk) * cut_cost
print(f'cuttingCost: ${cutting_cost:.2f}')

# BizCost - TXT 3953
biz_cost = total_print_cost + total_setup + price_of_wire + punch_price + cutting_cost + (qty * wirebind_per_book)
print(f'\nBizCost: ${biz_cost:.2f}')

# Profit margin - 90% for <=500
profit_margin = Decimal('0.9')
print(f'profitMargin: {profit_margin * 100}%')

# Subtotal
sub_total = biz_cost + (biz_cost * profit_margin)
print(f'subTotal: ${sub_total:.2f}')

# GST + Surcharge - TXT 3971-3972
total_gst = sub_total * Decimal('1.15')
print(f'\ntotal (15% GST): ${total_gst:.2f}')

total_final = total_gst + Decimal('44')
print(f'FINAL (+ $44 surcharge): ${total_final:.2f}')

print(f'\n' + '='*50)
print(f'Website shows: $640.69')
print(f'Backend calculated: ${total_final:.2f}')
print(f'Difference: ${Decimal("640.69") - total_final:.2f}')
print(f'Percentage off: {((Decimal("640.69") - total_final) / Decimal("640.69") * 100):.1f}%')
