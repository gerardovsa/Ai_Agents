"""Test Calculator Fixes - Quick Validation"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'quote-calculator', 'backend'))

from shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
from god_calculators.GOD_flyer_calculator import FlyerCalculatorGOD
from inhouse_modules.db_connector import InHousePrintDB

print("\n" + "="*60)
print("TESTING CALCULATOR FIXES")
print("="*60 + "\n")

# Test 1: Shopify Business Cards (Validation Bug)
print("Test 1: Economical Business Cards (Shopify)")
print("-" * 60)
try:
    calc = EconomicalBusinessCardsShopifyCalculator()
    result = calc.calculate(
        quantity=250,  # This was failing with "Got: 250" error
        print_sides='Double side print',
        print_type='Colour',
        artworks=1
    )
    print(f"✅ SUCCESS!")
    print(f"   Total: ${result.total_price:.2f}")
    print(f"   Unit Price: ${result.unit_price:.2f}")
    print(f"   Cost Per Card: ${result.cost_per_card:.2f}\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 2: GOD Flyer Calculator (Database Config)
print("Test 2: Flyers GOD (Database-Driven)")
print("-" * 60)
try:
    db = InHousePrintDB("UI/modules_external/quote-calculator/config/database-config.json")
    calc = FlyerCalculatorGOD(db)
    result = calc.calculate(
        quantity=1000,
        width=210,
        height=297,
        gsm=250,
        print_side1=1,  # Full color
        print_side2=1,  # Full color
        folding_required=False,
        cello_required=False
    )
    print(f"✅ SUCCESS!")
    print(f"   Total (inc GST): ${result.total_cost_inc_gst:.2f}")
    print(f"   Total (ex GST): ${result.total_cost_ex_gst:.2f}")
    print(f"   Unit Price: ${result.unit_price:.2f}\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

print("="*60)
print("TESTING COMPLETE")
print("="*60 + "\n")
