"""
Test inhouse_wrapper.py calculator functions
Tests the FIXED version that uses registry instead of archived calculator
"""
import sys
from pathlib import Path

# Add AI_agents to path
ai_agents_root = Path(__file__).resolve().parent
sys.path.insert(0, str(ai_agents_root))
sys.path.insert(0, str(ai_agents_root / 'AI_infrastructure'))
sys.path.insert(0, str(ai_agents_root / 'tools'))

print("=" * 80)
print("TESTING INHOUSE WRAPPER CALCULATOR FUNCTIONS")
print("=" * 80)

# Test 1: Import the wrapper module
print("\n[TEST 1] Importing inhouse_wrapper...")
try:
    sys.path.insert(0, str(ai_agents_root / 'UI' / 'modules_external' / 'inhouse-print' / 'implementations'))
    from inhouse_wrapper import inhouse_get_calculator_requirements, inhouse_calculate_quote
    print("✅ SUCCESS: inhouse_wrapper imported")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get calculator requirements for flyers
print("\n[TEST 2] Getting calculator requirements for 'flyers'...")
try:
    result = inhouse_get_calculator_requirements("flyers")
    
    if result.get("success"):
        print(f"✅ SUCCESS: Got requirements")
        print(f"   Calculator tool: {result.get('requirements', {}).get('calculator_tool')}")
        print(f"   Parameters: {list(result.get('requirements', {}).get('parameters', {}).keys())[:5]}...")
    else:
        print(f"❌ FAILED: {result.get('error')}")
        print(f"   Details: {result.get('details', 'N/A')}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Get calculator requirements for business_cards
print("\n[TEST 3] Getting calculator requirements for 'business_cards'...")
try:
    result = inhouse_get_calculator_requirements("business_cards")
    
    if result.get("success"):
        print(f"✅ SUCCESS: Got requirements")
        print(f"   Calculator tool: {result.get('requirements', {}).get('calculator_tool')}")
        print(f"   Parameters: {list(result.get('requirements', {}).get('parameters', {}).keys())}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
        print(f"   Details: {result.get('details', 'N/A')}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Calculate quote for business cards (using real parameters from schema)
print("\n[TEST 4] Calculating quote for business cards...")
try:
    parameters = {
        "quantity": 1000,
        "stock_type": "satin_350gsm",
        "print_type": "full_colour_front_and_back",
        "finish_size": "90x55mm",
        "celloglaze": "2_side_matt"
    }
    
    result = inhouse_calculate_quote("business_cards", parameters)
    
    if result.get("success"):
        quote = result.get("quote", {})
        print(f"✅ SUCCESS: Calculated quote")
        print(f"   Cost (ex GST): ${quote.get('cost_ex_gst', 'N/A')}")
        print(f"   Cost (inc GST): ${quote.get('cost_inc_gst', 'N/A')}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
        print(f"   Details: {result.get('details', 'N/A')}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Calculate quote for flyers
print("\n[TEST 5] Calculating quote for folded flyers...")
try:
    # Note: calculate_folded_flyers_shopify has different parameters
    # Let's first check what parameters it needs
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    schema = registry.get_tool("calculate_folded_flyers_shopify")
    
    if schema:
        print(f"   Tool schema found, required params: {schema.get('input_schema', {}).get('required', [])}")
        
        # Use appropriate parameters for folded flyers
        parameters = {
            "quantity": 1000,
            "size": "DL",
            "fold_type": "half_fold",
            "stock": "150gsm_gloss"
        }
        
        result = inhouse_calculate_quote("flyers", parameters)
        
        if result.get("success"):
            quote = result.get("quote", {})
            print(f"✅ SUCCESS: Calculated quote")
            print(f"   Result: {quote}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
    else:
        print(f"⚠️  SKIPPED: calculate_folded_flyers_shopify tool not found in registry")
        
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
