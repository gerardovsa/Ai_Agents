"""
Compare JSON config vs Hardcoded enum values for FoldedFlyers
"""
import sys
import json
from pathlib import Path
from decimal import Decimal

# Add paths
backend_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
sys.path.insert(0, str(backend_path))
shopify_path = backend_path / 'shopify_calculators'
sys.path.insert(0, str(shopify_path))

from FoldedFlyers_Shopify_Calculator import (
    PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
)

# Load JSON config
config_path = Path(__file__).parent / 'UI' / 'modules_external' / 'quote-calculator' / 'config' / 'shopify' / 'folded_printed_flyers_Shopify.json'
with open(config_path, 'r') as f:
    json_config = json.load(f)['shopify_folded_printed_flyers']

print("\n" + "="*80)
print("JSON vs HARDCODED ENUM COMPARISON - FoldedFlyers")
print("="*80 + "\n")

mismatches = []

# Check Print Type (F3)
print("🔍 Checking Print Type (F3)...")
json_print_options = {opt['title']: opt['price'] for opt in json_config['options'][2]['options']}
hardcoded_print = {
    'Colour': float(PrintType.COLOUR.cost_per_sheet),
    'Black & White': float(PrintType.BLACK_WHITE.cost_per_sheet)
}

for title, json_price in json_print_options.items():
    hardcoded_price = hardcoded_print.get(title)
    if hardcoded_price == json_price:
        print(f"  ✅ {title}: ${json_price} (match)")
    else:
        print(f"  ❌ {title}: JSON=${json_price}, Hardcoded=${hardcoded_price}")
        mismatches.append(f"Print Type - {title}")

# Check Paper Stock (F5)
print("\n🔍 Checking Paper Stock (F5)...")
json_stock_options = {opt['title']: opt['price'] for opt in json_config['options'][4]['options']}
hardcoded_stock = {
    'Satin 128GSM': float(PaperStock.SATIN_128GSM.cost_per_1000),
    'Satin 150GSM': float(PaperStock.SATIN_150GSM.cost_per_1000),
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

# Check Celloglaze (F8)
print("\n🔍 Checking Celloglaze (F8)...")
json_cello_options = {opt['title']: {'price': opt['price'], 'setup': opt.get('setup_cost', 0)} 
                      for opt in json_config['options'][7]['options']}
hardcoded_cello = {
    'None': {'price': float(Celloglaze.NONE.cost_per_sheet), 'setup': float(Celloglaze.NONE.setup_cost)},
    '1 Side Gloss': {'price': float(Celloglaze.ONE_SIDE_GLOSS.cost_per_sheet), 'setup': float(Celloglaze.ONE_SIDE_GLOSS.setup_cost)},
    '2 Side Gloss': {'price': float(Celloglaze.TWO_SIDE_GLOSS.cost_per_sheet), 'setup': float(Celloglaze.TWO_SIDE_GLOSS.setup_cost)},
    '1 Side Matt': {'price': float(Celloglaze.ONE_SIDE_MATT.cost_per_sheet), 'setup': float(Celloglaze.ONE_SIDE_MATT.setup_cost)},
    '2 Side Matt': {'price': float(Celloglaze.TWO_SIDE_MATT.cost_per_sheet), 'setup': float(Celloglaze.TWO_SIDE_MATT.setup_cost)},
}

for title, json_vals in json_cello_options.items():
    hardcoded_vals = hardcoded_cello.get(title)
    if hardcoded_vals:
        if (abs(hardcoded_vals['price'] - json_vals['price']) < 0.01 and 
            abs(hardcoded_vals['setup'] - json_vals['setup']) < 0.01):
            print(f"  ✅ {title}: price=${json_vals['price']}, setup=${json_vals['setup']} (match)")
        else:
            print(f"  ❌ {title}: JSON price=${json_vals['price']}/setup=${json_vals['setup']}, Hardcoded price=${hardcoded_vals['price']}/setup=${hardcoded_vals['setup']}")
            mismatches.append(f"Celloglaze - {title}")

# Check Constants
print("\n🔍 Checking Constants...")
json_constants = json_config.get('production_constants', {})
from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
calc = FoldedFlyersShopifyCalculator()

constant_checks = [
    ('Impos Setup', json_constants.get('impos_setup', 0), float(calc.IMPOS_SETUP)),
    ('Guilo Setup', json_constants.get('guilo_setup', 0), float(calc.GUILO_SETUP)),
    ('Folder Setup', json_constants.get('folder_setup', 0), float(calc.FOLDER_SETUP)),
    ('Extra Arts', json_constants.get('extra_arts', 0), float(calc.EXTRA_ARTS)),
    ('Stock Waste', json_constants.get('stock_waste', 0), float(calc.STOCK_WASTE)),
    ('Cutting Block', json_constants.get('cutting_block', 0), float(calc.CUTTING_BLOCK)),
    ('Cut Cost', json_constants.get('cut_cost', 0), float(calc.CUT_COST)),
    ('Fold Per Thousand', json_constants.get('fold_per_thousand', 0), float(calc.FOLD_PER_THOUSAND)),
    ('GST Rate', json_constants.get('gst_rate', 0), float(calc.GST_RATE)),
]

for name, json_val, hardcoded_val in constant_checks:
    if json_val and abs(json_val - hardcoded_val) < 0.01:
        print(f"  ✅ {name}: ${json_val} (match)")
    elif not json_val:
        print(f"  ⚠️  {name}: Not in JSON (hardcoded=${hardcoded_val})")
    else:
        print(f"  ❌ {name}: JSON=${json_val}, Hardcoded=${hardcoded_val}")
        mismatches.append(f"Constant - {name}")

print("\n" + "="*80)
if mismatches:
    print(f"❌ FAILED: {len(mismatches)} mismatches found")
    for mismatch in mismatches:
        print(f"  - {mismatch}")
else:
    print("🎉 ALL VALUES MATCH - JSON and Hardcoded enums are aligned!")
print("="*80)
