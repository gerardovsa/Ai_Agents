import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from business_card_calculator_shopify import ShopifyBusinessCardCalculator, PrintType, FinishSize, StockTypePremium, CelloglazePremium
from decimal import Decimal

calc = ShopifyBusinessCardCalculator()

print("="*80)
print("DETAILED CALCULATION BREAKDOWN - PREMIUM BUSINESS CARDS")
print("="*80)
print()

# Configuration
quantity = 1000
sides = 2
print_type = PrintType.COLOR
finish_size = FinishSize.STANDARD_90X55
stock_type = StockTypePremium.KINGKONG_420GSM
celloglaze = CelloglazePremium.TWO_SIDE_GLOSS
artworks = 1

print(f"Configuration:")
print(f"  Quantity: {quantity}")
print(f"  Sides: {sides}")
print(f"  Print Type: {print_type.value}")
print(f"  Finish Size: {finish_size.value}")
print(f"  Stock Type: {stock_type.value}")
print(f"  Celloglaze: {celloglaze.value}")
print(f"  Artworks: {artworks}")
print()

# Calculate cards per sheet
cards_per_sheet = 21  # 90x55mm
sheets_needed = Decimal(quantity) / Decimal(cards_per_sheet)
sheets_with_waste = sheets_needed * Decimal('1.05')

print(f"Sheet Calculations:")
print(f"  Cards per sheet: {cards_per_sheet}")
print(f"  Sheets needed (no waste): {sheets_needed:.2f}")
print(f"  Sheets with 5% waste: {sheets_with_waste:.2f}")
print()

# Setup costs
impos_setup = Decimal('15')
guilo_setup = Decimal('10')
cello_setup = Decimal('17')
setup_cost = impos_setup + guilo_setup + cello_setup

print(f"Setup Costs:")
print(f"  Imposition: ${impos_setup:.2f}")
print(f"  Guillotine: ${guilo_setup:.2f}")
print(f"  Celloglaze: ${cello_setup:.2f}")
print(f"  Total Setup: ${setup_cost:.2f}")
print()

# Paper cost
stock_price = Decimal('300')  # King Kong per 1000
paper_cost = (sheets_with_waste / Decimal('1000')) * stock_price

print(f"Paper Cost:")
print(f"  Stock price: ${stock_price}/1000 sheets")
print(f"  Calculation: {sheets_with_waste:.2f} / 1000 * ${stock_price} = ${paper_cost:.2f}")
print()

# Click cost
click_rate = Decimal('0.048')  # Color rate for premium
click_cost = sheets_with_waste * Decimal(sides) * click_rate

print(f"Click Cost:")
print(f"  Rate: ${click_rate}/sheet (color)")
print(f"  Calculation: {sheets_with_waste:.2f} sheets * {sides} sides * ${click_rate} = ${click_cost:.2f}")
print()

# Cutting cost
cutting_block_size = 500
cutting_block_cost = Decimal('10')
cutting_cost = (sheets_with_waste / Decimal(cutting_block_size)) * cutting_block_cost

print(f"Cutting Cost:")
print(f"  Block size: {cutting_block_size} sheets")
print(f"  Cost per block: ${cutting_block_cost}")
print(f"  Calculation: {sheets_with_waste:.2f} / {cutting_block_size} * ${cutting_block_cost} = ${cutting_cost:.2f}")
print()

# Celloglaze cost
celloglaze_rate = Decimal('0.32')  # 2 Side Gloss
celloglaze_cost = sheets_with_waste * celloglaze_rate

print(f"Celloglaze Cost:")
print(f"  Rate: ${celloglaze_rate}/sheet (2 Side Gloss)")
print(f"  Calculation: {sheets_with_waste:.2f} sheets * ${celloglaze_rate} = ${celloglaze_cost:.2f}")
print()

# Subtotal
subtotal = setup_cost + paper_cost + click_cost + cutting_cost + celloglaze_cost

print(f"Subtotal (before profit): ${subtotal:.2f}")
print()

# Profit margin (with celloglaze - using tiered system)
print(f"Profit Margin (WITH celloglaze - tiered system):")
print(f"  Subtotal: ${subtotal:.2f}")

# Determine profit tier (from backend logic)
if subtotal <= 30:
    profit_pct = Decimal('0.90')
elif subtotal <= 40:
    profit_pct = Decimal('0.80')
elif subtotal <= 50:
    profit_pct = Decimal('0.70')
elif subtotal <= 60:
    profit_pct = Decimal('0.60')
elif subtotal <= 75:
    profit_pct = Decimal('0.55')
elif subtotal <= 90:
    profit_pct = Decimal('0.50')
elif subtotal <= 105:
    profit_pct = Decimal('0.45')
elif subtotal <= 120:
    profit_pct = Decimal('0.40')
elif subtotal <= 140:
    profit_pct = Decimal('0.38')
elif subtotal <= 160:
    profit_pct = Decimal('0.36')
elif subtotal <= 180:
    profit_pct = Decimal('0.34')
elif subtotal <= 200:
    profit_pct = Decimal('0.32')
else:
    profit_pct = Decimal('0.30')

profit = subtotal * profit_pct

print(f"  Profit tier: {int(profit_pct * 100)}%")
print(f"  Profit amount: ${profit:.2f}")
print()

# Total ex GST
total_ex_gst = subtotal + profit

print(f"Total ex GST: ${total_ex_gst:.2f}")
print()

# GST (single application)
gst_multiplier = Decimal('1.1')
total_inc_gst_single = total_ex_gst * gst_multiplier

print(f"Total inc GST (single): ${total_inc_gst_single:.2f}")
print()

# GST (double application - testing TXT mention)
total_inc_gst_double = total_ex_gst * gst_multiplier * gst_multiplier

print(f"Total inc GST (double): ${total_inc_gst_double:.2f}")
print()

print("="*80)
print("COMPARISON TO WEBSITE")
print("="*80)
website_price = Decimal('161.70')
diff_single = abs(total_inc_gst_single - website_price)
diff_double = abs(total_inc_gst_double - website_price)

print(f"Website Price: ${website_price:.2f}")
print(f"Backend (single GST): ${total_inc_gst_single:.2f} - Diff: ${diff_single:.2f}")
print(f"Backend (double GST): ${total_inc_gst_double:.2f} - Diff: ${diff_double:.2f}")
print()
print(f"BEST MATCH: {'Single GST' if diff_single < diff_double else 'Double GST'}")
