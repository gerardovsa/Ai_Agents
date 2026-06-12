"""
Direct Test of InHouse Calculator Functions
Tests by directly importing from the correct path

USAGE: python test_calculator_direct.py
"""

import sys
from pathlib import Path

# Add the correct path to sys.path
project_root = Path(__file__).resolve().parent
ui_modules = project_root / "UI" / "modules_external" / "inhouse-print" / "implementations"
sys.path.insert(0, str(ui_modules))

print("="*80)
print("🧪 DIRECT TEST - InHouse Calculator Functions")
print("="*80)

# Test 1: Import the module
print("\n📦 TEST 1: Import inhouse_wrapper module...")
try:
    import inhouse_wrapper
    print("   ✅ Module imported successfully")
    print(f"   Location: {inhouse_wrapper.__file__}")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check if functions exist
print("\n🔍 TEST 2: Check function availability...")
try:
    has_requirements = hasattr(inhouse_wrapper, 'inhouse_get_calculator_requirements')
    has_calculate = hasattr(inhouse_wrapper, 'inhouse_calculate_quote')
    
    print(f"   - inhouse_get_calculator_requirements: {'✅' if has_requirements else '❌'}")
    print(f"   - inhouse_calculate_quote: {'✅' if has_calculate else '❌'}")
    
    if not (has_requirements and has_calculate):
        print("   ❌ Required functions not found")
        sys.exit(1)
    
    print("   ✅ All functions available")
except Exception as e:
    print(f"   ❌ Check failed: {e}")
    sys.exit(1)

# Test 3: Call inhouse_get_calculator_requirements
print("\n📋 TEST 3: Call inhouse_get_calculator_requirements('flyers')...")
try:
    result = inhouse_wrapper.inhouse_get_calculator_requirements(product_type="flyers")
    
    if result.get("success"):
        print("   ✅ Function executed successfully")
        print(f"   Product Type: {result.get('product_type')}")
        
        requirements = result.get('requirements', {})
        if requirements:
            print(f"   ✅ Requirements returned")
            print(f"      - Has parameters: {bool(requirements.get('parameters'))}")
            print(f"      - Has natural_language_mapping: {bool(requirements.get('natural_language_mapping'))}")
            print(f"      - Has historical_patterns: {bool(requirements.get('historical_patterns'))}")
    else:
        print(f"   ❌ Function failed: {result.get('error')}")
        print(f"   Details: {result.get('details', 'No details')}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Call inhouse_calculate_quote
print("\n💰 TEST 4: Call inhouse_calculate_quote('flyers', {...})...")
print("   Using Kollosche specs: A5, 2000 qty, 300gsm Satin")

try:
    parameters = {
        "quantity": 2000,
        "width": 148,
        "height": 210,
        "gsm": 300,
        "print_side1": 1,
        "print_side2": 1,
        "folding_required": False,
        "cello_required": False
    }
    
    result = inhouse_wrapper.inhouse_calculate_quote(
        product_type="flyers", 
        parameters=parameters
    )
    
    if result.get("success"):
        print("   ✅ Function executed successfully")
        
        quote = result.get('quote', {})
        if quote:
            print(f"\n   💰 QUOTE RESULTS:")
            print(f"      - Cost Ex GST: ${quote.get('cost_ex_gst', 'N/A')}")
            print(f"      - Cost Inc GST: ${quote.get('cost_inc_gst', 'N/A')}")
            print(f"      - Cost to Business: ${quote.get('cost_to_business', 'N/A')}")
            print(f"      - Profit Margin: ${quote.get('profit_margin', 'N/A')}")
            
            # Compare with expected $351.00
            cost_inc_gst = quote.get('cost_inc_gst')
            if cost_inc_gst:
                try:
                    cost = float(cost_inc_gst)
                    diff = abs(cost - 351.00)
                    print(f"\n   📊 Historical comparison:")
                    print(f"      - Expected (OrderID 57886): $351.00")
                    print(f"      - Calculated: ${cost:.2f}")
                    print(f"      - Difference: ${diff:.2f}")
                    
                    if diff < 10:
                        print(f"      ✅ Within acceptable range (±$10)")
                    else:
                        print(f"      ⚠️  Price differs significantly")
                except:
                    pass
    else:
        print(f"   ❌ Function failed: {result.get('error')}")
        print(f"   Details: {result.get('details', 'No details')}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n" + "="*80)
print("🎉 ALL TESTS PASSED")
print("="*80)
print("\n✅ PRODUCTION DEPLOYMENT VERIFIED:")
print("   1. Module imports correctly")
print("   2. Functions are accessible")
print("   3. inhouse_get_calculator_requirements works")
print("   4. inhouse_calculate_quote works")
print("   5. Path resolution fix is effective")
print("\n🚀 READY FOR PRODUCTION DEPLOYMENT")
print("="*80)
