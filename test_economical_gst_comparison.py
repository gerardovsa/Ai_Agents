import sys
sys.path.insert(0, 'C:/Users/gpoli/GIT/AI_Agents_V11/AI_agents/UI/modules_external/quote-calculator/backend/shopify_calculators')
from decimal import Decimal

# Manual calculation test to verify if double GST is needed

print("="*80)
print("ECONOMICAL BUSINESS CARDS - SINGLE GST vs DOUBLE GST COMPARISON")
print("="*80)
print()

# TEST 1: 500 Single-sided Color
print("TEST 1: 500 Single-sided Color")
print("-"*80)
quantity = 500
sides = 1
print_rate = Decimal('0.044')  # Color

# Setup
impos = Decimal('15')
guilo = Decimal('12')
artwork = Decimal('0')  # 1 artwork = no extra
setup = impos + guilo + artwork
print(f"Setup: ${setup:.2f}")

# Sheets
cards_per_sheet = 21
sheets = Decimal(quantity) / Decimal(cards_per_sheet) * Decimal('1.05')  # with waste
print(f"Sheets: {sheets:.2f}")

# Paper
paper = (sheets / Decimal('1000')) * Decimal('126')
print(f"Paper: ${paper:.2f}")

# Clicks
clicks = sheets * Decimal(sides) * print_rate
print(f"Clicks: ${clicks:.2f}")

# Cutting
cutting = (sheets / Decimal('500')) * Decimal('11')
print(f"Cutting: ${cutting:.2f}")

# Subtotal
bizcost = setup + paper + clicks + cutting
print(f"BizCost: ${bizcost:.2f}")

# Profit (65% for low cost jobs)
profit = bizcost * Decimal('0.65')
print(f"Profit (65%): ${profit:.2f}")

# Total ex GST
total_ex = bizcost + profit
print(f"Total Ex GST: ${total_ex:.2f}")

# Single GST
single_gst = total_ex * Decimal('1.1')
print(f"Single GST: ${single_gst:.2f}")

# Double GST
double_gst = total_ex * Decimal('1.1') * Decimal('1.1')
print(f"Double GST: ${double_gst:.2f}")

print(f"\nExpected Range: $80-$120")
print(f"Single GST fits: {Decimal('80') <= single_gst <= Decimal('120')}")
print(f"Double GST fits: {Decimal('80') <= double_gst <= Decimal('120')}")
print()

# TEST 2: 1000 Double-sided Color, 3 artworks
print()
print("TEST 2: 1000 Double-sided Color, 3 artworks")
print("-"*80)
quantity = 1000
sides = 2
artworks_count = 3

# Setup
artwork = (Decimal(artworks_count) * Decimal('15')) - Decimal('15')  # Extra artworks
setup = impos + guilo + artwork
print(f"Setup (with {artworks_count} artworks): ${setup:.2f}")

# Sheets
sheets = Decimal(quantity) / Decimal(cards_per_sheet) * Decimal('1.05')
print(f"Sheets: {sheets:.2f}")

# Paper
paper = (sheets / Decimal('1000')) * Decimal('126')
print(f"Paper: ${paper:.2f}")

# Clicks
clicks = sheets * Decimal(sides) * print_rate
print(f"Clicks: ${clicks:.2f}")

# Cutting
cutting = (sheets / Decimal('500')) * Decimal('11')
print(f"Cutting: ${cutting:.2f}")

# Subtotal
bizcost = setup + paper + clicks + cutting
print(f"BizCost: ${bizcost:.2f}")

# Profit (60% tier)
profit = bizcost * Decimal('0.60')
print(f"Profit (60%): ${profit:.2f}")

# Total ex GST
total_ex = bizcost + profit
print(f"Total Ex GST: ${total_ex:.2f}")

# Single GST
single_gst = total_ex * Decimal('1.1')
print(f"Single GST: ${single_gst:.2f}")

# Double GST
double_gst = total_ex * Decimal('1.1') * Decimal('1.1')
print(f"Double GST: ${double_gst:.2f}")

print(f"\nExpected Range: $150-$220")
print(f"Single GST fits: {Decimal('150') <= single_gst <= Decimal('220')}")
print(f"Double GST fits: {Decimal('150') <= double_gst <= Decimal('220')}")
print()

# TEST 4: 5000 Double-sided Color
print()
print("TEST 4: 5000 Double-sided Color")
print("-"*80)
quantity = 5000
sides = 2
artwork = Decimal('0')

# Setup
setup = impos + guilo + artwork
print(f"Setup: ${setup:.2f}")

# Sheets
sheets = Decimal(quantity) / Decimal(cards_per_sheet) * Decimal('1.05')
print(f"Sheets: {sheets:.2f}")

# Paper
paper = (sheets / Decimal('1000')) * Decimal('126')
print(f"Paper: ${paper:.2f}")

# Clicks
clicks = sheets * Decimal(sides) * print_rate
print(f"Clicks: ${clicks:.2f}")

# Cutting
cutting = (sheets / Decimal('500')) * Decimal('11')
print(f"Cutting: ${cutting:.2f}")

# Subtotal
bizcost = setup + paper + clicks + cutting
print(f"BizCost: ${bizcost:.2f}")

# Profit (60% tier for bizcost ~86)
profit = bizcost * Decimal('0.60')
print(f"Profit (60%): ${profit:.2f}")

# Total ex GST
total_ex = bizcost + profit
print(f"Total Ex GST: ${total_ex:.2f}")

# Single GST
single_gst = total_ex * Decimal('1.1')
print(f"Single GST: ${single_gst:.2f}")

# Double GST
double_gst = total_ex * Decimal('1.1') * Decimal('1.1')
print(f"Double GST: ${double_gst:.2f}")

print(f"\nExpected Range: $400-$600")
print(f"Single GST fits: {Decimal('400') <= single_gst <= Decimal('600')}")
print(f"Double GST fits: {Decimal('400') <= double_gst <= Decimal('600')}")
