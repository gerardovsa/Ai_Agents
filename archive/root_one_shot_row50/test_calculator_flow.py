#!/usr/bin/env python3
"""Quick test of calculator tool flow"""
import sys
import os
from pathlib import Path

# Set up environment
os.chdir(Path(__file__).parent)

print("="*80)
print("CALCULATOR TOOL FLOW TEST")
print("="*80)

# Add all required paths
root = Path(__file__).parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "AI_infrastructure"))
sys.path.insert(0, str(root / "tools"))
sys.path.insert(0, str(root / "UI" / "modules_external" / "inhouse-print"))

print(f"\nWorking directory: {os.getcwd()}")
print(f"Python paths added:")
for p in sys.path[:5]:
    print(f"   - {p}")

# Test 1: Import InHouse wrapper
print("\n[TEST 1] Importing InHouse wrapper...")
try:
    from implementations.inhouse_wrapper import (
        inhouse_get_calculator_requirements,
        inhouse_calculate_quote
    )
    print("PASS: Functions imported")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get requirements for business cards
print("\n[TEST 2] Getting calculator requirements for 'business_cards'...")
try:
    result = inhouse_get_calculator_requirements("business_cards")
    
    if result.get("success"):
        print("PASS: Got requirements")
        print(f"   Product type: {result.get('product_type')}")
        print(f"   Calculator tool: {result.get('calculator_tool')}")
        
        params = result.get('requirements', {}).get('parameters', {})
        if params:
            print(f"   Parameters found: {len(params)}")
            print(f"   Sample params: {list(params.keys())[:5]}")
        else:
            print("   WARNING: No parameters returned")
    else:
        print(f"FAIL: {result.get('error')}")
        sys.exit(1)
        
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Calculate business cards quote
print("\n[TEST 3] Calculating business cards quote...")
try:
    params = {
        "quantity": 1000,
        "finish_size": "90x55mm",
        "stock_type": "satin_350gsm",
        "print_type": "double_sided",
        "celloglaze": "2_side_matt",
        "artworks": 1
    }
    
    result = inhouse_calculate_quote("business_cards", params)
    
    if result.get("success"):
        print("✅ PASS: Quote calculated")
        quote = result.get('quote', {})
        
        if isinstance(quote, dict) and 'total_price' in quote:
            print(f"   Total price: ${quote['total_price']:.2f}")
            print(f"   Unit price: ${quote.get('unit_price', 0):.4f}")
        else:
            print(f"   Quote result: {quote}")
    else:
        print(f"❌ FAIL: {result.get('error')}")
        if 'details' in result:
            print(f"   Details: {result['details'][:200]}...")
        sys.exit(1)
        
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Calculate folded flyers quote
print("\n[TEST 4] Calculating folded flyers quote...")
try:
    params = {
        "quantity": 1000,
        "finish_size": "A4",
        "stock_type": "satin_350gsm",
        "folds": "half_fold",
        "print_type": "double_sided",
        "celloglaze": "2_side_matt",
        "artworks": 1
    }
    
    result = inhouse_calculate_quote("folded_flyers", params)
    
    if result.get("success"):
        print("✅ PASS: Quote calculated")
        quote = result.get('quote', {})
        
        if isinstance(quote, dict) and 'total_price' in quote:
            print(f"   Total price: ${quote['total_price']:.2f}")
            print(f"   Unit price: ${quote.get('unit_price', 0):.4f}")
        else:
            print(f"   Quote result: {quote}")
    else:
        print(f"❌ FAIL: {result.get('error')}")
        if 'details' in result:
            print(f"   Details: {result['details'][:200]}...")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("ALL TESTS PASSED")
print("="*80)
print("\nCalculator tool flow is working correctly!")
print("Ready for production deployment")
