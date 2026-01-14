#!/usr/bin/env python3
"""Test all calculator types"""
import sys
sys.path.insert(0, 'implementations')
sys.path.insert(0, 'backend')
sys.path.insert(0, 'backend/god_calculators')
sys.path.insert(0, '../inhouse-print')

from calculator_wrapper import (
    calculate_flyers_god,
    calculate_letterheads_god,
    calculate_economical_business_cards_shopify,
    calculate_business_cards
)

print("🧪 TESTING ALL CALCULATOR TYPES:\n")
print("="*70)

# Test 1: Shopify wrapper (uses Shopify backend)
print("\n1️⃣  Business Cards (Shopify Premium via wrapper):")
r1 = calculate_business_cards(quantity=500, stock_type='premium', print_type='double_sided')
print(f"   Success: {r1.get('success')}")
if r1.get('success'):
    print(f"   Price: ${r1.get('total_price', 0):.2f}")
else:
    print(f"   Error: {r1.get('error', 'Unknown')[:80]}")

# Test 2: Pure Shopify calculator
print("\n2️⃣  Economical Business Cards (Pure Shopify):")
r2 = calculate_economical_business_cards_shopify(quantity=1000, double_sided=True)
print(f"   Success: {r2.get('success')}")
if r2.get('success'):
    print(f"   Price: ${r2.get('total_price', 0):.2f}")
else:
    print(f"   Error: {r2.get('error', 'Unknown')[:80]}")

# Test 3: GOD Flyer Calculator
print("\n3️⃣  Flyers (GOD Calculator - Database):")
r3 = calculate_flyers_god(quantity=1000, width=210, height=297, gsm=150, print_side1=1, print_side2=1)
print(f"   Success: {r3.get('success')}")
if r3.get('success'):
    print(f"   Price: ${r3.get('total_cost_inc_gst', 0):.2f}")
else:
    print(f"   Error: {r3.get('error', 'Unknown')[:100]}")

# Test 4: GOD Letterhead Calculator  
print("\n4️⃣  Letterheads (GOD Calculator - Database):")
r4 = calculate_letterheads_god(quantity=1000, width=210, height=297, gsm=100)
print(f"   Success: {r4.get('success')}")
if r4.get('success'):
    print(f"   Price: ${r4.get('total_cost_inc_gst', 0):.2f}")
else:
    print(f"   Error: {r4.get('error', 'Unknown')[:100]}")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
