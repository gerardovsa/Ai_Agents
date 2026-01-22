"""
Dual Method Calculator Test Suite - January 23, 2026
Tests BOTH methods that AI agents use for quote calculations:

METHOD 1: WRAPPER (Tool Registry) - 90% of production traffic
  - Uses calculator_wrapper functions
  - Parameter translation (strings → enums)
  - Legacy parameter support with warnings
  - Validation returns structured errors

METHOD 2: DIRECT (Backend Class) - 10% of production traffic  
  - Direct backend calculator instantiation
  - Requires enum parameters
  - No parameter translation
  - Raw backend validation

Based on:
- .github/CALCULATOR_ALIGNMENT_INSTRUCTIONS.md
- .github/CALCULATOR_TESTING_GUIDE.md
- VALIDATION_COMPLETE_JAN19_2026.md
"""

import sys
from pathlib import Path
from decimal import Decimal
import json

# Add paths
project_root = Path(__file__).resolve().parent
backend_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
shopify_dir = backend_dir / 'shopify_calculators'
implementations_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'

for path in [str(backend_dir), str(shopify_dir), str(implementations_dir), str(project_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import WRAPPER functions
try:
    from calculator_wrapper import (
        calculate_folded_flyers_shopify,
        calculate_corflute_signs_shopify,
        calculate_wire_bound_books_shopify,
        calculate_spiral_bound_books_shopify,
        calculate_perfect_bound_books_shopify,
        calculate_saddle_stitch_books_shopify
    )
    WRAPPER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Could not import wrapper functions: {e}")
    WRAPPER_AVAILABLE = False

# Import DIRECT backend calculators
from FoldedFlyers_Shopify_Calculator import (
    FoldedFlyersShopifyCalculator,
    PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
)
from corflute_calculator_shopify import (
    CorflutePricingCalculatorShopify,
    CorfiuteThickness, EyeletOption, CorfluteSizePreset  # Note: Typo in original - "Corfiute"
)
from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator

print("=" * 80)
print("DUAL METHOD CALCULATOR TEST SUITE")
print("Testing: Folded Flyers & Corflute Signs")
print("January 23, 2026")
print("=" * 80)
print()

# Test results storage
results = {
    "folded_flyers": {"wrapper": [], "direct": []},
    "corflutes": {"wrapper": [], "direct": []},
    "wire_bound": {"wrapper": [], "direct": []},
    "spiral_bound": {"wrapper": [], "direct": []},
    "perfect_bound": {"wrapper": [], "direct": []},
    "saddle_stitch": {"wrapper": [], "direct": []}
}

# ============================================================================
# FOLDED FLYERS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("FOLDED FLYERS CALCULATOR - BOTH METHODS")
print("="*80)

# Test case 1: DL Single Fold
test_name = "DL Single Fold - 1000 flyers"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER (AI's Primary Method) =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")
print("   Route: AI → wrapper function → backend calculator")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_folded_flyers_shopify(
            quantity=1000,
            size="DL",
            stock="Satin 128GSM",
            double_sided=True,
            print_type="Colour",
            folding="Single Fold",
            celloglaze="None",
            artworks=1
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price', 'N/A')}")
            print(f"   Unit Price: ${wrapper_result.get('unit_price', 'N/A')}")
            print(f"   Product Type: {wrapper_result.get('product_type', 'N/A')}")
            
            if 'warnings' in wrapper_result:
                print(f"   ⚠️  Warnings: {len(wrapper_result['warnings'])}")
                for w in wrapper_result['warnings']:
                    print(f"      - {w.get('deprecated')} → {w.get('use_instead')}")
            
            results["folded_flyers"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price'),
                "warnings": wrapper_result.get('warnings', [])
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["folded_flyers"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["folded_flyers"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT (AI's Alternative Method) =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")
print("   Route: AI → backend calculator (with enums)")

try:
    calc = FoldedFlyersShopifyCalculator()
    direct_result = calc.calculate_quote(
        quantity=1000,
        print_sides=PrintSides.DOUBLE_SIDE,
        print_type=PrintType.COLOUR,
        finish_size=FinishSize.DL,
        paper_stock=PaperStock.SATIN_128GSM,
        artworks=1,
        fold_type=FoldType.SINGLE_FOLD,
        celloglaze=Celloglaze.NONE
    )
    
    print(f"   ✅ SUCCESS")
    print(f"   Total Price: ${float(direct_result.final_price):.2f}")
    unit_price = float(direct_result.final_price) / direct_result.quantity
    print(f"   Unit Price: ${unit_price:.4f}")
    print(f"   Quantity: {direct_result.quantity}")
    
    results["folded_flyers"]["direct"].append({
        "test": test_name,
        "status": "SUCCESS",
        "price": float(direct_result.final_price)
    })
    
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["folded_flyers"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ===== PRICE CONSISTENCY CHECK =====
if WRAPPER_AVAILABLE:
    if (results["folded_flyers"]["wrapper"][-1]["status"] == "SUCCESS" and 
        results["folded_flyers"]["direct"][-1]["status"] == "SUCCESS"):
        
        wrapper_price = results["folded_flyers"]["wrapper"][-1]["price"]
        direct_price = results["folded_flyers"]["direct"][-1]["price"]
        
        print(f"\n💰 PRICE CONSISTENCY CHECK:")
        print(f"   Wrapper: ${wrapper_price}")
        print(f"   Direct:  ${direct_price}")
        
        if abs(wrapper_price - direct_price) < 0.01:
            print(f"   ✅ MATCH - Prices consistent across methods")
        else:
            print(f"   ❌ MISMATCH - Price difference: ${abs(wrapper_price - direct_price):.2f}")

# ===== TEST VALIDATION (Missing Parameters) =====
print(f"\n🔍 VALIDATION TEST: Missing Required Parameters")
print("   Testing if wrapper catches missing params...")

if WRAPPER_AVAILABLE:
    try:
        validation_result = calculate_folded_flyers_shopify(
            quantity=1000
            # Intentionally omit required params
        )
        
        if validation_result.get('success') == False:
            print(f"   ✅ CORRECTLY REJECTED")
            print(f"   Error: {validation_result.get('error')}")
        else:
            print(f"   ❌ VALIDATION FAILED - Should have rejected missing params")
            
    except Exception as e:
        print(f"   ⚠️  Exception raised (backend validation): {str(e)}")

# ============================================================================
# CORFLUTE SIGNS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("CORFLUTE SIGNS CALCULATOR - BOTH METHODS")
print("="*80)

# Test case: Small preset
test_name = "Small Preset - 10 signs (450x600mm)"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_corflute_signs_shopify(
            quantity=10,
            size_preset="450x600",
            thickness="3mm",
            double_sided=False,
            eyelet_option="four_corners",
            artworks=1
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price', 'N/A')}")
            print(f"   Unit Price: ${wrapper_result.get('unit_price', 'N/A')}")
            
            results["corflutes"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price')
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["corflutes"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["corflutes"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")

try:
    calc = CorflutePricingCalculatorShopify()
    # Check if calculate_quote method exists
    if hasattr(calc, 'calculate_quote'):
        direct_result = calc.calculate_quote(
            quantity=10,
            size_preset=CorfluteSizePreset.SIZE_450x600,  # Fixed: Use enum not string
            thickness=CorfiuteThickness.MM_3,  # Fixed: MM_3 not THREE_MM (backend typo)
            double_sided=False,
            eyelet_option=EyeletOption.FOUR_CORNERS,
            artworks=1
        )
        
        print(f"   ✅ SUCCESS")
        # Corflute returns dict, not dataclass
        if isinstance(direct_result, dict):
            # Check various possible price key names
            total_price = direct_result.get('total_price', 
                            direct_result.get('final_price', 
                            direct_result.get('grand_total_inc_gst', 
                            direct_result.get('total', 0))))
            unit_price = direct_result.get('unit_price', 
                           direct_result.get('price_per_unit', 
                           direct_result.get('per_unit', 0)))
        else:
            total_price = direct_result.final_price
            unit_price = direct_result.unit_price
            
        print(f"   Total Price: ${float(total_price):.2f}")
        print(f"   Unit Price: ${float(unit_price):.2f}")
        
        results["corflutes"]["direct"].append({
            "test": test_name,
            "status": "SUCCESS",
            "price": float(total_price)
        })
    else:
        print(f"   ❌ METHOD NOT FOUND: calculate_quote() doesn't exist")
        print(f"   Available methods: {[m for m in dir(calc) if not m.startswith('_')]}")
        results["corflutes"]["direct"].append({
            "test": test_name,
            "status": "ERROR",
            "error": "calculate_quote method not found"
        })
        
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["corflutes"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ============================================================================
# WIRE BOUND BOOKS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("WIRE BOUND BOOKS CALCULATOR - BOTH METHODS")
print("="*80)

test_name = "A5 Portrait - 100 pages - 100 books"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_wire_bound_books_shopify(
            quantity=100,
            internal_pages=100,
            finish_size="A5 Portrait",
            printed_front_cover="300GSM Satin",
            front_cover_print="2pp Colour",
            front_celloglaze="None",
            outer_front_cover="Not Required",
            printed_back_cover="300GSM Satin",
            back_cover_print="2pp Colour",
            back_celloglaze="None",
            outer_back_cover="None",
            internal_stock="Uncoated Bond 100GSM",
            internal_print="Black & White",
            artworks=1
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price')}")
            
            results["wire_bound"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price')
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["wire_bound"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["wire_bound"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")

try:
    calc = WireBoundShopifyCalculator()
    direct_result = calc.calculate(
        quantity=100,
        internal_pages=100,
        finish_size="A5 Portrait",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Black & White",
        artworks=1
    )
    
    print(f"   ✅ SUCCESS")
    print(f"   Total Price: ${float(direct_result.total_price):.2f}")
    print(f"   Unit Price: ${float(direct_result.unit_price):.2f}")
    
    results["wire_bound"]["direct"].append({
        "test": test_name,
        "status": "SUCCESS",
        "price": float(direct_result.total_price)
    })
    
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["wire_bound"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ============================================================================
# SPIRAL BOUND BOOKS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("SPIRAL BOUND BOOKS CALCULATOR - BOTH METHODS")
print("="*80)

test_name = "A4 Landscape - 200 pages - 50 books"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_spiral_bound_books_shopify(
            quantity=50,
            internal_pages=200,
            finish_size="A4 Landscape",
            printed_front_cover="300GSM Satin",
            front_cover_print="2pp Colour",
            front_celloglaze="None",
            outer_front_cover="Not Required",
            printed_back_cover="300GSM Satin",
            back_cover_print="2pp Colour",
            back_celloglaze="None",
            outer_back_cover="None",
            internal_stock="Uncoated Bond 100GSM",
            internal_print="Full Colour",
            artworks=1
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price')}")
            
            results["spiral_bound"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price')
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["spiral_bound"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["spiral_bound"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")

try:
    calc = SpiralBoundShopifyCalculator()
    direct_result = calc.calculate(
        quantity=50,
        internal_pages=200,
        finish_size="A4 Landscape",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Full Colour",
        artworks=1
    )
    
    print(f"   ✅ SUCCESS")
    print(f"   Total Price: ${float(direct_result.total_price):.2f}")
    print(f"   Unit Price: ${float(direct_result.unit_price):.2f}")
    
    results["spiral_bound"]["direct"].append({
        "test": test_name,
        "status": "SUCCESS",
        "price": float(direct_result.total_price)
    })
    
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["spiral_bound"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ============================================================================
# PERFECT BOUND BOOKS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("PERFECT BOUND BOOKS CALCULATOR - BOTH METHODS")
print("="*80)

test_name = "A5 Portrait - 152 pages - 200 books"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_perfect_bound_books_shopify(
            quantity=200,
            printed_pages=152,
            finish_size="A5 Portrait",
            cover_stock="Satin 300GSM",
            cover_print_type="4pp Colour",
            celloglaze="None",
            content_stock_type="Satin 128GSM",
            content_print_type="Full Colour"
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price')}")
            
            results["perfect_bound"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price')
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["perfect_bound"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["perfect_bound"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")

try:
    calc = PerfectBoundShopifyCalculator()
    direct_result = calc.calculate(
        quantity=200,
        printed_pages=152,
        finish_size="A5 Portrait",
        cover_stock="Satin 300GSM",
        cover_print_type="4pp Colour",
        celloglaze="None",
        content_stock_type="Satin 128GSM",
        content_print_type="Full Colour"
    )
    
    print(f"   ✅ SUCCESS")
    print(f"   Total Price: ${float(direct_result.total_price):.2f}")
    print(f"   Unit Price: ${float(direct_result.unit_price):.2f}")
    
    results["perfect_bound"]["direct"].append({
        "test": test_name,
        "status": "SUCCESS",
        "price": float(direct_result.total_price)
    })
    
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["perfect_bound"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ============================================================================
# SADDLE STITCH BOOKS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("SADDLE STITCH BOOKS CALCULATOR - BOTH METHODS")
print("="*80)

test_name = "A5 Portrait - 24 pages - 500 books"
print(f"\n{'─'*80}")
print(f"TEST: {test_name}")
print(f"{'─'*80}")

# ===== METHOD 1: WRAPPER =====
print("\n🔧 METHOD 1: WRAPPER (Tool Registry)")

if WRAPPER_AVAILABLE:
    try:
        wrapper_result = calculate_saddle_stitch_books_shopify(
            quantity=500,
            printed_pages="24pp",
            finish_size="A5 Portrait",
            cover_stock="Satin 200GSM",
            cover_print_type="2 side colour (4pp)",
            celloglaze="None",
            content_stock_type="Satin 128GSM",
            content_print_type="Colour",
            cover_option="Self Cover",
            artworks=1
        )
        
        if wrapper_result.get('success'):
            print(f"   ✅ SUCCESS")
            print(f"   Total Price: ${wrapper_result.get('total_price')}")
            
            results["saddle_stitch"]["wrapper"].append({
                "test": test_name,
                "status": "SUCCESS",
                "price": wrapper_result.get('total_price')
            })
        else:
            print(f"   ❌ FAILED: {wrapper_result.get('error')}")
            results["saddle_stitch"]["wrapper"].append({
                "test": test_name,
                "status": "ERROR",
                "error": wrapper_result.get('error')
            })
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results["saddle_stitch"]["wrapper"].append({
            "test": test_name,
            "status": "EXCEPTION",
            "error": str(e)
        })
else:
    print("   ⚠️  SKIPPED - Wrapper not available")

# ===== METHOD 2: DIRECT =====
print("\n🔧 METHOD 2: DIRECT (Backend Class)")

try:
    calc = SaddleStitchBooksShopifyCalculator()
    direct_result = calc.calculate(
        quantity=500,
        printed_pages="24pp",
        finish_size="A5 Portrait",
        cover_stock="Satin 200GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="None",
        content_stock_type="Satin 128GSM",
        content_print_type="Colour",
        cover_option="Self Cover",
        artworks=1
    )
    
    print(f"   ✅ SUCCESS")
    print(f"   Total Price: ${float(direct_result.total_price):.2f}")
    print(f"   Unit Price: ${float(direct_result.unit_price):.2f}")
    
    results["saddle_stitch"]["direct"].append({
        "test": test_name,
        "status": "SUCCESS",
        "price": float(direct_result.total_price)
    })
    
except Exception as e:
    print(f"   ❌ EXCEPTION: {str(e)}")
    results["saddle_stitch"]["direct"].append({
        "test": test_name,
        "status": "EXCEPTION",
        "error": str(e)
    })

# ============================================================================
# SUMMARY REPORT
# ============================================================================
print("\n" + "="*80)
print("TEST SUMMARY - DUAL METHOD COMPARISON")
print("="*80)

for product, methods in results.items():
    print(f"\n{product.upper().replace('_', ' ')}:")
    
    for method, tests in methods.items():
        if not tests:
            print(f"  {method.upper()}: No tests run")
            continue
            
        success_count = len([t for t in tests if t['status'] == 'SUCCESS'])
        error_count = len([t for t in tests if t['status'] in ['ERROR', 'EXCEPTION']])
        
        print(f"  {method.upper()}: {success_count}/{len(tests)} passed", end="")
        if error_count > 0:
            print(f" ({error_count} failed)")
        else:
            print()
        
        # Show prices if available
        successful_tests = [t for t in tests if t['status'] == 'SUCCESS' and 'price' in t]
        if successful_tests:
            for t in successful_tests:
                print(f"     - {t['test']}: ${t['price']:.2f}")

# Save detailed results
output_file = Path(__file__).parent / 'dual_method_test_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n📄 Detailed results saved to: {output_file}")

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)
print("""
1. WRAPPER METHOD (Primary - 90% of AI traffic)
   - Uses string parameters (no enums needed)
   - Automatic parameter translation
   - Returns structured validation errors
   - Supports legacy parameters with warnings
   
2. DIRECT METHOD (Alternative - 10% of AI traffic)
   - Requires backend enum parameters
   - No parameter translation
   - Direct backend validation
   - Used in schema-only mode

3. BOTH METHODS REQUIRED FOR COMPLETE TESTING
   - AI agents use BOTH methods in production
   - Wrapper = primary path via tool registry
   - Direct = alternative path for direct calculator access
   - Test suite must validate BOTH pathways

4. VALIDATION LAYER (Added Jan 19, 2026)
   - Catches missing/invalid parameters
   - Returns structured error messages
   - Enables AI learning through iteration
   - Critical for production reliability
""")

print("=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)
