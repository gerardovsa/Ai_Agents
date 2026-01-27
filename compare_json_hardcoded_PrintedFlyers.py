"""
Compare JSON config vs Hardcoded enum values for PrintedFlyers
"""
import sys
import json
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from PrintedFlyers_Shopify_Calculator import (
    PrintSides, PrintType, FinishSize, PaperStock, PrintedFlyersShopifyCalculator
)

# Load JSON config
config_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'printed_flyers_Shopify.json'
with open(config_path, 'r') as f:
    json_config = json.load(f)

print("\n" + "="*80)
print("JSON vs HARDCODED ENUM COMPARISON - PrintedFlyers")
print("="*80 + "\n")

mismatches = []

# Check Print Type (F3)
print("🔍 Checking Print Type (F3)...")
json_print_options = {opt['label']: opt['price_per_sheet'] for opt in json_config['fields']['F3']['options']}
hardcoded_print = {
    'Colour': float(PrintType.COLOUR.cost_per_sheet),
    'Black & White': float(PrintType.BLACK_WHITE.cost_per_sheet)
}

for label, json_price in json_print_options.items():
    hardcoded_price = hardcoded_print.get(label)
    if hardcoded_price and abs(hardcoded_price - json_price) < 0.001:
        print(f"  ✅ {label}: ${json_price} (match)")
    else:
        print(f"  ❌ {label}: JSON=${json_price}, Hardcoded=${hardcoded_price}")
        mismatches.append(f"Print Type - {label}")

# Check Paper Stock (F5)
print("\n🔍 Checking Paper Stock (F5)...")
json_stock_options = {opt['label']: opt['price_per_1000_sheets'] for opt in json_config['fields']['F5']['options']}
hardcoded_stock = {
    'Satin 128GSM': float(PaperStock.SATIN_128GSM.cost_per_1000),
    'Satin 150GSM': float(PaperStock.SATIN_150GSM.cost_per_1000),
    'Satin 170GSM': float(PaperStock.SATIN_170GSM.cost_per_1000),
    'Satin 250GSM': float(PaperStock.SATIN_250GSM.cost_per_1000),
    'Satin 300GSM': float(PaperStock.SATIN_300GSM.cost_per_1000),
    'Satin 350GSM': float(PaperStock.SATIN_350GSM.cost_per_1000),
    'Uncoated Bond 80GSM': float(PaperStock.UNCOATED_80GSM.cost_per_1000),
    'Uncoated Bond 90GSM': float(PaperStock.UNCOATED_90GSM.cost_per_1000),
    'Uncoated Bond 100GSM': float(PaperStock.UNCOATED_100GSM.cost_per_1000),
}

for title, json_price in json_stock_options.items():
    hardcoded_price = hardcoded_stock.get(title)
    if hardcoded_price and abs(hardcoded_price - json_price) < 0.01:
        print(f"  ✅ {title}: ${json_price} (match)")
    else:
        print(f"  ❌ {title}: JSON=${json_price}, Hardcoded=${hardcoded_price}")
        mismatches.append(f"Paper Stock - {title}")

# Check Constants
print("\n🔍 Checking Constants...")
calc = PrintedFlyersShopifyCalculator()

constant_checks = [
    ('Impos Setup', 15, float(calc.IMPOSITION_SETUP)),
    ('Guilo Setup', 12, float(calc.GUILLOTINE_SETUP)),
    ('Extra Arts', 15, float(calc.EXTRA_ARTWORK_COST)),
    ('Stock Waste', 1.05, float(calc.STOCK_WASTE_FACTOR)),
    ('Cutting Block', 500, float(calc.CUTTING_BLOCK_SIZE)),
    ('Cut Cost', 11, float(calc.CUTTING_COST_PER_BLOCK)),
    ('GST Rate', 1.1, float(calc.GST_RATE)),
]

for name, expected, hardcoded_val in constant_checks:
    if abs(expected - hardcoded_val) < 0.01:
        print(f"  ✅ {name}: ${expected} (match)")
    else:
        print(f"  ❌ {name}: Expected=${expected}, Hardcoded=${hardcoded_val}")
        mismatches.append(f"Constant - {name}")

print("\n" + "="*80)
if mismatches:
    print(f"❌ FAILED: {len(mismatches)} mismatches found")
    for mismatch in mismatches:
        print(f"  - {mismatch}")
else:
    print("🎉 ALL VALUES MATCH - JSON and Hardcoded enums are aligned!")
print("="*80)
