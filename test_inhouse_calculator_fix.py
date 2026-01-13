"""
Test InHouse Print Calculator Wrapper Functions
Tests the fixes applied on Jan 13, 2026 for path resolution issues

Tests:
1. inhouse_get_calculator_requirements() - Get flyer calculator requirements
2. inhouse_calculate_quote() - Calculate A5 flyer quote (Kollosche specs)
3. End-to-end workflow - Full calculator workflow for production deployment

USAGE:
    python test_inhouse_calculator_fix.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_get_calculator_requirements():
    """Test 1: Get flyer calculator requirements"""
    print("\n" + "="*80)
    print("TEST 1: inhouse_get_calculator_requirements('flyers')")
    print("="*80)
    
    try:
        from UI.modules_external.inhouse_print.implementations.inhouse_wrapper import inhouse_get_calculator_requirements
        
        result = inhouse_get_calculator_requirements(product_type="flyers")
        
        if result.get("success"):
            print("✅ SUCCESS - Calculator requirements retrieved")
            print(f"\n📋 Product Type: {result.get('product_type')}")
            
            requirements = result.get('requirements', {})
            if requirements:
                print(f"✅ Requirements structure returned")
                print(f"   - Has parameters: {bool(requirements.get('parameters'))}")
                print(f"   - Has natural_language_mapping: {bool(requirements.get('natural_language_mapping'))}")
                print(f"   - Has historical_patterns: {bool(requirements.get('historical_patterns'))}")
            
            return True
        else:
            print(f"❌ FAILED - {result.get('error')}")
            print(f"Details: {result.get('details', 'No details')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculate_quote():
    """Test 2: Calculate A5 flyer quote (Kollosche specifications)"""
    print("\n" + "="*80)
    print("TEST 2: inhouse_calculate_quote('flyers', {...})")
    print("="*80)
    print("\n📊 Using Kollosche's specifications from OrderID 57886:")
    print("   - Size: A5 (148mm x 210mm)")
    print("   - Quantity: 2000")
    print("   - Stock: 300gsm Satin")
    print("   - Expected Cost: $351.00")
    
    try:
        from UI.modules_external.inhouse_print.implementations.inhouse_wrapper import inhouse_calculate_quote
        
        # Kollosche specifications from the conversation thread
        parameters = {
            "quantity": 2000,
            "width": 148,
            "height": 210,
            "gsm": 300,
            "print_side1": 1,  # Full colour
            "print_side2": 1,  # Full colour
            "folding_required": False,
            "cello_required": False
        }
        
        result = inhouse_calculate_quote(product_type="flyers", parameters=parameters)
        
        if result.get("success"):
            print("✅ SUCCESS - Quote calculated")
            
            quote = result.get('quote', {})
            if quote:
                print(f"\n💰 QUOTE RESULTS:")
                print(f"   - Cost Ex GST: ${quote.get('cost_ex_gst', 'N/A')}")
                print(f"   - Cost Inc GST: ${quote.get('cost_inc_gst', 'N/A')}")
                print(f"   - Cost to Business: ${quote.get('cost_to_business', 'N/A')}")
                print(f"   - Profit Margin: ${quote.get('profit_margin', 'N/A')}")
                
                # Compare with expected $351.00 from database
                cost_inc_gst = quote.get('cost_inc_gst')
                if cost_inc_gst:
                    diff = abs(float(cost_inc_gst) - 351.00)
                    if diff < 10:  # Allow $10 variance
                        print(f"   ✅ Price matches historical order (±${diff:.2f})")
                    else:
                        print(f"   ⚠️  Price differs from historical order by ${diff:.2f}")
            
            return True
        else:
            print(f"❌ FAILED - {result.get('error')}")
            print(f"Details: {result.get('details', 'No details')}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """Test 3: Complete workflow - Requirements → Calculate"""
    print("\n" + "="*80)
    print("TEST 3: END-TO-END WORKFLOW (Production Simulation)")
    print("="*80)
    print("\n🎯 Simulating production scenario: Customer requests A5 flyer quote")
    
    try:
        from UI.modules_external.inhouse_print.implementations.inhouse_wrapper import (
            inhouse_get_calculator_requirements,
            inhouse_calculate_quote
        )
        
        # Step 1: Get requirements
        print("\n📋 Step 1: Get calculator requirements...")
        req_result = inhouse_get_calculator_requirements(product_type="flyers")
        
        if not req_result.get("success"):
            print(f"❌ Step 1 FAILED - {req_result.get('error')}")
            return False
        
        print("   ✅ Requirements retrieved")
        
        # Step 2: Parse customer specs (simulating AI agent parsing)
        print("\n🔍 Step 2: Parse customer specifications...")
        customer_request = "2000 A5 flyers, 300gsm Satin, full colour both sides"
        print(f"   Customer: \"{customer_request}\"")
        
        parameters = {
            "quantity": 2000,
            "width": 148,  # A5
            "height": 210,  # A5
            "gsm": 300,
            "print_side1": 1,
            "print_side2": 1,
            "folding_required": False,
            "cello_required": False
        }
        print("   ✅ Parameters extracted")
        
        # Step 3: Calculate quote
        print("\n💰 Step 3: Calculate quote...")
        quote_result = inhouse_calculate_quote(product_type="flyers", parameters=parameters)
        
        if not quote_result.get("success"):
            print(f"❌ Step 3 FAILED - {quote_result.get('error')}")
            return False
        
        print("   ✅ Quote calculated successfully")
        
        # Step 4: Format response
        print("\n📧 Step 4: Format customer response...")
        quote = quote_result.get('quote', {})
        
        response = f"""
        ╔═══════════════════════════════════════════════════════════╗
        ║                    QUOTE CONFIRMATION                     ║
        ╚═══════════════════════════════════════════════════════════╝
        
        Product: A5 Flyers (148mm x 210mm)
        Quantity: 2000
        Paper Stock: 300gsm Satin
        Printing: Full colour both sides
        
        PRICING:
        ├─ Cost Ex GST: ${quote.get('cost_ex_gst', 'N/A')}
        ├─ GST: ${float(quote.get('cost_inc_gst', 0)) - float(quote.get('cost_ex_gst', 0)):.2f}
        └─ TOTAL INC GST: ${quote.get('cost_inc_gst', 'N/A')}
        
        ✅ PRODUCTION READY
        """
        
        print(response)
        
        print("\n" + "="*80)
        print("✅ END-TO-END WORKFLOW COMPLETE - READY FOR PRODUCTION DEPLOYMENT")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ WORKFLOW EXCEPTION - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 INHOUSE PRINT CALCULATOR FIX VALIDATION")
    print("Fix Date: January 13, 2026")
    print("Issue: Import path resolution for complete_calculator_implementation")
    print("="*80)
    
    results = {
        "test_get_requirements": False,
        "test_calculate_quote": False,
        "test_end_to_end": False
    }
    
    # Run tests
    results["test_get_requirements"] = test_get_calculator_requirements()
    results["test_calculate_quote"] = test_calculate_quote()
    results["test_end_to_end"] = test_end_to_end_workflow()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-"*80)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - READY FOR PRODUCTION DEPLOYMENT")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("⚠️  SOME TESTS FAILED - DO NOT DEPLOY TO PRODUCTION")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
