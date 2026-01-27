"""
Debug Spiral Bound Books - Line by Line Comparison
Trace exactly what backend calculates vs what website should calculate
"""

from decimal import Decimal, ROUND_HALF_UP

# Test 1 Configuration
qty = 100
artworks = 1
content_pages = 40
finish_size = "A5 Portrait"
outer_front_cover = "Not Required"
printed_front_cover = "300GSM Satin"
cover_print_type = "1pp Colour"
celloglaze = "None"
outer_back_cover = "None"
printed_back_cover = "None"
back_cover_print_type = "1pp Colour"
back_celloglaze = "None"
content_paper_stock = "Uncoated Bond 80GSM"
content_print_type = "Black & White"

# Constants from TXT
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
cello_setup = Decimal('0')  # Both None

# Field prices from JSON
outer_front_price = 0  # "Not Required"
printed_front_stock_price = 0.14  # 300GSM Satin
cover_print_price = 0.04  # 1pp Colour
cello_price = 0  # None

outer_back_price = 0  # None
printed_back_stock_price = 0  # None
back_print_price = 0.04  # 1pp Colour
back_cello_price = 0  # None

content_stock_price = 26.34  # Uncoated Bond 80GSM per 1000 sheets
content_print_price = 0.02  # Black & White per sheet
finish_sheets_per_sra3 = 4  # A5 Portrait

print("=" * 80)
print("SPIRAL BOUND BOOKS - DETAILED CALCULATION TRACE")
print("=" * 80)
print(f"\nConfiguration: {qty} books, A5, {content_pages}pp, {content_paper_stock}")
print()

# Line by line calculation
print("FRONT COVER CALCULATIONS:")
print("-" * 80)

# TXT Line 3889: outFront = ({F3.price} * {F1})
out_front = Decimal(str(outer_front_price)) * Decimal(str(qty))
print(f"outFront = {outer_front_price} * {qty} = ${out_front:.2f}")

# TXT Line 3890: totalFrontCoverSheets
if printed_front_cover == "None":
    total_front_cover_sheets = Decimal('0')
else:
    total_front_cover_sheets = (Decimal(str(qty)) / Decimal(str(finish_sheets_per_sra3))) * stock_waste
print(f"totalFrontCoverSheets = ({qty} / {finish_sheets_per_sra3}) * {stock_waste} = {total_front_cover_sheets:.2f}")

# TXT Line 3891: coverClickCost
cover_click_cost = Decimal(str(cover_print_price)) * total_front_cover_sheets
print(f"coverClickCost = {cover_print_price} * {total_front_cover_sheets:.2f} = ${cover_click_cost:.2f}")

# TXT Line 3892: totalFrontCoverCost
total_front_cover_cost = (total_front_cover_sheets * Decimal(str(printed_front_stock_price))) + cover_click_cost
print(f"totalFrontCoverCost = ({total_front_cover_sheets:.2f} * {printed_front_stock_price}) + {cover_click_cost:.2f} = ${total_front_cover_cost:.2f}")

# TXT Line 3893: FrontcelloCost
front_cello_cost = Decimal('0')
print(f"FrontcelloCost = ${front_cello_cost:.2f}")

print("\nBACK COVER CALCULATIONS:")
print("-" * 80)

# TXT Line 3895: outBack
out_back = Decimal(str(outer_back_price)) * Decimal(str(qty))
print(f"outBack = {outer_back_price} * {qty} = ${out_back:.2f}")

# TXT Line 3896: totalBackCoverSheets
total_back_cover_sheets = Decimal('0')
print(f"totalBackCoverSheets = ${total_back_cover_sheets:.2f}")

# TXT Line 3897: coverClickCostBack
cover_click_cost_back = Decimal('0')
print(f"coverClickCostBack = ${cover_click_cost_back:.2f}")

# TXT Line 3898: totalBackCoverCost
total_back_cover_cost = Decimal('0')
print(f"totalBackCoverCost = ${total_back_cover_cost:.2f}")

# TXT Line 3899: BackcelloCost
back_cello_cost = Decimal('0')
print(f"BackcelloCost = ${back_cello_cost:.2f}")

print("\nCONTENT CALCULATIONS:")
print("-" * 80)

# TXT Line 3901: totalContentSheets
total_content_sheets = (((Decimal(str(qty)) * Decimal(str(content_pages))) / Decimal('2')) / Decimal(str(finish_sheets_per_sra3))) * stock_waste
print(f"totalContentSheets = ((({qty} * {content_pages}) / 2) / {finish_sheets_per_sra3}) * {stock_waste}")
print(f"                  = ((4000 / 2) / 4) * 1.05")
print(f"                  = (2000 / 4) * 1.05")
print(f"                  = 500 * 1.05")
print(f"                  = {total_content_sheets:.2f}")

# TXT Line 3902: contentClickCost
content_click_cost = total_content_sheets * Decimal(str(content_print_price))
print(f"contentClickCost = {total_content_sheets:.2f} * {content_print_price} = ${content_click_cost:.2f}")

# TXT Line 3903: totalContentCost
# CRITICAL: Check if we should divide by 1000
print(f"\nCRITICAL: Content stock price = {content_stock_price} (JSON says 'per_1000_sheets')")
print(f"Option 1 (with /1000): {total_content_sheets:.2f} * {content_stock_price} / 1000 = ${(total_content_sheets * Decimal(str(content_stock_price)) / Decimal('1000')):.2f}")
print(f"Option 2 (without /1000): {total_content_sheets:.2f} * {content_stock_price} = ${(total_content_sheets * Decimal(str(content_stock_price))):.2f}")

total_content_cost_v1 = (total_content_sheets * Decimal(str(content_stock_price)) / Decimal('1000')) + content_click_cost
total_content_cost_v2 = (total_content_sheets * Decimal(str(content_stock_price))) + content_click_cost

print(f"totalContentCost (with /1000) = ${total_content_cost_v1:.2f}")
print(f"totalContentCost (without /1000) = ${total_content_cost_v2:.2f}")

# Use the /1000 version (current backend)
total_content_cost = total_content_cost_v1

print("\nTOTAL PRINT COST:")
print("-" * 80)

# TXT Line 3905: totalPrintCost
total_print_cost = total_front_cover_cost + total_back_cover_cost + front_cello_cost + back_cello_cost + out_front + out_back + total_content_cost
print(f"totalPrintCost = {total_front_cover_cost:.2f} + {total_back_cover_cost:.2f} + {front_cello_cost:.2f} + {back_cello_cost:.2f} + {out_front:.2f} + {out_back:.2f} + {total_content_cost:.2f}")
print(f"               = ${total_print_cost:.2f}")

print("\nSETUP COSTS:")
print("-" * 80)

# TXT Line 3906: totalSetupCosts
_a = Decimal(str(artworks)) * extra_arts
_a2 = Decimal('0') if _a <= extra_arts else (_a - extra_arts)
total_setup_costs = guilo_setup + impos_setup + punch_setup + cello_setup + _a2
print(f"_a = {artworks} * {extra_arts} = {_a:.2f}")
print(f"_a2 = 0 (since {_a:.2f} <= {extra_arts})")
print(f"totalSetupCosts = {guilo_setup} + {impos_setup} + {punch_setup} + {cello_setup} + {_a2:.2f} = ${total_setup_costs:.2f}")

print("\nBOOK THICKNESS & WIRE PRICING:")
print("-" * 80)

# TXT Line 3908: bookSheets
book_sheets = Decimal(str(content_pages)) / Decimal('2')
print(f"bookSheets = {content_pages} / 2 = {book_sheets:.2f}")

# TXT Line 3909-3916: contentSheetThickness (NON-TRADE - 7 types)
content_sheet_thickness = Decimal('0.1')  # Uncoated Bond 80GSM
print(f"contentSheetThickness = 0.1 (Uncoated Bond 80GSM)")

# TXT Line 3917: bookThickness
book_thickness = book_sheets * content_sheet_thickness
print(f"bookThickness = {book_sheets:.2f} * {content_sheet_thickness} = {book_thickness:.2f}mm")

# TXT Line 3919-3936: pricePerRing (NON-TRADE - 18 tiers)
if book_thickness <= 8:
    price_per_ring = Decimal('0.13065')
else:
    price_per_ring = Decimal('0.157')  # For 2mm, should be 0.13065
print(f"pricePerRing = 0.13065 (thickness {book_thickness:.2f}mm <= 8mm)")

# TXT Line 3938-3940: priceofwire
small_formats = ['A6 Portrait', 'A6 Landscape', 'DL Landscape', 'A5 Landscape']
if finish_size in small_formats:
    price_of_wire = (price_per_ring * Decimal(str(qty))) / Decimal('2')
else:
    price_of_wire = price_per_ring * Decimal(str(qty))
print(f"priceofwire = {price_per_ring} * {qty} = ${price_of_wire:.2f} (A5 Portrait NOT halved)")

print("\nPUNCH & CUTTING:")
print("-" * 80)

# TXT Line 3943-3947: punch calculations
base_value = (Decimal(str(qty)) * Decimal(str(content_pages))) / Decimal('2')
additional_f8 = Decimal('0')  # printed_back_cover == "None"
additional_f4 = Decimal(str(qty))  # printed_front_cover != "None"
total_punch = base_value + additional_f8 + additional_f4
sheets_to_punch = total_punch * stock_waste

print(f"baseValue = ({qty} * {content_pages}) / 2 = {base_value:.2f}")
print(f"additionalF8 = 0 (no back cover)")
print(f"additionalF4 = {qty} (has front cover)")
print(f"totalPunch = {base_value:.2f} + 0 + {qty} = {total_punch:.2f}")
print(f"sheetsToPunch = {total_punch:.2f} * {stock_waste} = {sheets_to_punch:.2f}")

# TXT Line 3949: punchPrice
punch_price = (sheets_to_punch / punch_sheets_hour) * bindery_labor
print(f"punchPrice = ({sheets_to_punch:.2f} / {punch_sheets_hour}) * {bindery_labor} = ${punch_price:.2f}")

# TXT Line 3951: cuttingCost
cutting_cost = ((total_content_sheets + total_front_cover_sheets + total_back_cover_sheets) / cutting_blk) * cut_cost
print(f"cuttingCost = (({total_content_sheets:.2f} + {total_front_cover_sheets:.2f} + 0) / {cutting_blk}) * {cut_cost}")
print(f"            = ${cutting_cost:.2f}")

print("\nBIZCOST CALCULATION:")
print("-" * 80)

# TXT Line 3953: BizCost
biz_cost = total_print_cost + total_setup_costs + price_of_wire + punch_price + cutting_cost + (Decimal(str(qty)) * wirebind_per_book)
print(f"BizCost = {total_print_cost:.2f} + {total_setup_costs:.2f} + {price_of_wire:.2f} + {punch_price:.2f} + {cutting_cost:.2f} + ({qty} * {wirebind_per_book})")
print(f"        = {total_print_cost:.2f} + {total_setup_costs:.2f} + {price_of_wire:.2f} + {punch_price:.2f} + {cutting_cost:.2f} + {Decimal(str(qty)) * wirebind_per_book:.2f}")
print(f"        = ${biz_cost:.2f}")

print("\nPROFIT MARGIN & FINAL PRICE:")
print("-" * 80)

# Profit margin (90% for BizCost <= 500)
profit_margin = Decimal('0.9')
print(f"profitMargin = 0.9 (90% since BizCost {biz_cost:.2f} <= 500)")

# TXT Line 3969: subTotal
sub_total = biz_cost * (Decimal('1') + profit_margin)
print(f"subTotal = {biz_cost:.2f} * 1.9 = ${sub_total:.2f}")

# NON-TRADE: var total = {subTotal} * 1.15
total_with_gst = sub_total * Decimal('1.15')
print(f"total (after GST) = {sub_total:.2f} * 1.15 = ${total_with_gst:.2f}")

# Add $44
total_final = total_with_gst + Decimal('44')
print(f"FINAL TOTAL = {total_with_gst:.2f} + 44 = ${total_final:.2f}")

print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
print(f"Backend calculated: ${total_final:.2f}")
print(f"Website shows:      $640.69")
print(f"Difference:         ${Decimal('640.69') - total_final:.2f}")

print("\n" + "=" * 80)
print("WORKING BACKWARDS FROM WEBSITE:")
print("=" * 80)
website_price = Decimal('640.69')
website_before_surcharge = website_price - Decimal('44')
website_subtotal = website_before_surcharge / Decimal('1.15')
website_bizcost = website_subtotal / Decimal('1.9')

print(f"Website price: ${website_price:.2f}")
print(f"Minus $44 surcharge: ${website_before_surcharge:.2f}")
print(f"Divide by 1.15 (GST): ${website_subtotal:.2f}")
print(f"Divide by 1.9 (90% margin): ${website_bizcost:.2f}")
print(f"\nImplied website BizCost: ${website_bizcost:.2f}")
print(f"Backend BizCost: ${biz_cost:.2f}")
print(f"Missing in backend: ${website_bizcost - biz_cost:.2f}")
