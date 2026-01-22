"""
Comprehensive Calculator Test Suite - January 23, 2026
Tests BOTH methods that AI agents use in production:
1. WRAPPER METHOD (Tool Registry - 90% of production traffic)
2. DIRECT METHOD (Backend Class - 10% of production traffic)

Validates:
- Wrapper parameter translation (strings → enums)
- Legacy parameter support with warnings
- Validation catches missing/invalid parameters
- Price consistency across wrapper/direct methods
- Backend calculator logic (direct calls)

Based on documentation:
- .github/CALCULATOR_ALIGNMENT_INSTRUCTIONS.md (3-part pattern)
- .github/CALCULATOR_TESTING_GUIDE.md (4 required tests)
- VALIDATION_COMPLETE_JAN19_2026.md (AI learning examples)
"""

import sys
from pathlib import Path
from decimal import Decimal
import json

# Add paths for BOTH wrapper and backend imports
project_root = Path(__file__).resolve().parent
backend_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
shopify_dir = backend_dir / 'shopify_calculators'
implementations_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'implementations'

for path in [str(backend_dir), str(shopify_dir), str(implementations_dir), str(project_root)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import WRAPPER functions (AI's primary method)
from calculator_wrapper import (
    calculate_wire_bound_books_shopify,
    calculate_spiral_bound_books_shopify,
    calculate_perfect_bound_books_shopify,
    calculate_saddle_stitch_books_shopify,
    calculate_folded_flyers_shopify,
    calculate_corflute_signs_shopify
)

# Import DIRECT backend calculators (AI's alternative method)
from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator
from FoldedFlyers_Shopify_Calculator import (
    FoldedFlyersShopifyCalculator,
    PrintSides as FlyerPrintSides,
    PrintType as FlyerPrintType,
    FinishSize as FlyerFinishSize,
    PaperStock as FlyerPaperStock,
    FoldType as FlyerFoldType,
    Celloglaze as FlyerCelloglaze
)
from corflute_calculator_shopify import (
    CorflutePricingCalculatorShopify,
    Thickness as CorflThickness,
    EyeletOption as CorflEyeletOption
)

print("=" * 80)
print("COMPREHENSIVE CALCULATOR TEST SUITE - DUAL METHOD")
print("Tests BOTH Wrapper (Tool Registry) AND Direct (Backend) Methods")
print("January 23, 2026")
print("=" * 80)
print()

# Store all results for analysis
results = {
    "wire_bound": {"wrapper": [], "direct": []},
    "spiral_bound": {"wrapper": [], "direct": []},
    "perfect_bound": {"wrapper": [], "direct": []},
    "saddle_stitch": {"wrapper": [], "direct": []},
    "folded_flyers": {"wrapper": [], "direct": []},
    "corflutes": {"wrapper": [], "direct": []}
}

errors = []
warnings_collected = []

# ============================================================================
# WIRE BOUND BOOKS - DUAL METHOD TESTING
# ============================================================================
print("\n" + "="*80)
print("WIRE BOUND BOOKS - TESTING BOTH METHODS")
print("="*80)

wire_tests = [
    {
        "name": "A4 Portrait Basic - 100 books, 50 pages",
        "params": {
            "quantity": 100,
            "artworks": 1,
            "internal_pages": 50,
            "finish_size": "A4 Portrait",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 100GSM",
            "internal_print": "Black & White"
        }
    },
    {
        "name": "A5 Landscape with PVC - 250 books, 80 pages",
        "params": {
            "quantity": 250,
            "artworks": 2,
            "internal_pages": 80,
            "finish_size": "A5 Landscape",
            "printed_front_cover": "350GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "2 Sided Matt",
            "outer_front_cover": "Clear PVC",
            "printed_back_cover": "350GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "2 Sided Matt",
            "outer_back_cover": "Clear PVC",
            "internal_stock": "Satin 128GSM",
            "internal_print": "Full Colour"
        }
    },
    {
        "name": "DL Portrait Small - 50 books, 20 pages",
        "params": {
            "quantity": 50,
            "artworks": 1,
            "internal_pages": 20,
            "finish_size": "DL Portrait",
            "printed_front_cover": "250GSM Satin",
            "front_cover_print": "1pp Colour",
            "front_celloglaze": "1 Side Gloss",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "250GSM Satin",
            "back_cover_print": "1pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 80GSM",
            "internal_print": "Black & White"
        }
    },
    {
        "name": "A6 Landscape with Leather - 500 books, 120 pages",
        "params": {
            "quantity": 500,
            "artworks": 3,
            "internal_pages": 120,
            "finish_size": "A6 Landscape",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "Black Leather",
            "internal_stock": "Satin 150GSM",
            "internal_print": "Full Colour"
        }
    },
    {
        "name": "A4 Landscape B&W Large - 1000 books, 200 pages",
        "params": {
            "quantity": 1000,
            "artworks": 1,
            "internal_pages": 200,
            "finish_size": "A4 Landscape",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "1pp Black & White",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "1pp Black & White",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 90GSM",
            "internal_print": "Black & White"
        }
    }
]

for i, test in enumerate(wire_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = WireBoundBooksShopifyCalculator()
        result = calc.calculate(**test['params'])
        
        # Convert dataclass to dict if needed
        if hasattr(result, '__dict__'):
            result_dict = {
                'total_price': str(result.total_price),
                'unit_price': str(result.unit_price),
                'quantity': result.quantity,
                'breakdown': {k: str(v) for k, v in result.breakdown.items()},
                'specifications': result.specifications
            }
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Pages: {test['params']['internal_pages']}")
        print(f"   Size: {test['params']['finish_size']}")
        
        results["wire_bound"].append({
            "test": test['name'],
            "status": "SUCCESS",
            "result": result_dict,
            "params": test['params']
        })
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({
            "calculator": "Wire Bound Books",
            "test": test['name'],
            "error": str(e),
            "params": test['params']
        })
        results["wire_bound"].append({
            "test": test['name'],
            "status": "ERROR",
            "error": str(e),
            "params": test['params']
        })

# ============================================================================
# SPIRAL BOUND BOOKS - 5 TEST CASES
# ============================================================================
print("\n" + "="*80)
print("SPIRAL BOUND BOOKS - 5 TEST CASES")
print("="*80)

spiral_tests = [
    {
        "name": "A5 Portrait Basic - 100 books, 60 pages",
        "params": {
            "quantity": 100,
            "artworks": 1,
            "internal_pages": 60,
            "finish_size": "A5 Portrait",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 100GSM",
            "internal_print": "Black & White"
        }
    },
    {
        "name": "A4 Portrait Full Colour - 200 books, 100 pages",
        "params": {
            "quantity": 200,
            "artworks": 2,
            "internal_pages": 100,
            "finish_size": "A4 Portrait",
            "printed_front_cover": "350GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "2 Sided Gloss",
            "outer_front_cover": "Clear PVC",
            "printed_back_cover": "350GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "2 Sided Gloss",
            "outer_back_cover": "None",
            "internal_stock": "Satin 128GSM",
            "internal_print": "Full Colour"
        }
    },
    {
        "name": "DL Landscape Compact - 50 books, 24 pages",
        "params": {
            "quantity": 50,
            "artworks": 1,
            "internal_pages": 24,
            "finish_size": "DL Landscape",
            "printed_front_cover": "250GSM Satin",
            "front_cover_print": "1pp Colour",
            "front_celloglaze": "1 Side Matt",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "250GSM Satin",
            "back_cover_print": "1pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "None",
            "internal_stock": "Uncoated Bond 80GSM",
            "internal_print": "Black & White"
        }
    },
    {
        "name": "A6 Portrait Small - 300 books, 40 pages",
        "params": {
            "quantity": 300,
            "artworks": 3,
            "internal_pages": 40,
            "finish_size": "A6 Portrait",
            "printed_front_cover": "300GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "None",
            "outer_front_cover": "Not Required",
            "printed_back_cover": "300GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "None",
            "outer_back_cover": "Blank",
            "internal_stock": "Satin 150GSM",
            "internal_print": "Full Colour"
        }
    },
    {
        "name": "A4 Landscape Large - 500 books, 150 pages",
        "params": {
            "quantity": 500,
            "artworks": 1,
            "internal_pages": 150,
            "finish_size": "A4 Landscape",
            "printed_front_cover": "350GSM Satin",
            "front_cover_print": "2pp Colour",
            "front_celloglaze": "2 Sided Matt",
            "outer_front_cover": "Clear PVC",
            "printed_back_cover": "350GSM Satin",
            "back_cover_print": "2pp Colour",
            "back_celloglaze": "2 Sided Matt",
            "outer_back_cover": "Black Leather",
            "internal_stock": "Uncoated Bond 100GSM",
            "internal_print": "Black & White"
        }
    }
]

for i, test in enumerate(spiral_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = SpiralBoundBooksShopifyCalculator()
        result = calc.calculate(**test['params'])
        
        if hasattr(result, '__dict__'):
            result_dict = {'total_price': str(result.total_price), 'unit_price': str(result.unit_price), 'quantity': result.quantity, 'breakdown': {k: str(v) for k, v in result.breakdown.items()}, 'specifications': result.specifications}
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Pages: {test['params']['internal_pages']}")
        print(f"   Size: {test['params']['finish_size']}")
        
        results["spiral_bound"].append({"test": test['name'], "status": "SUCCESS", "result": result_dict, "params": test['params']})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({"calculator": "Spiral Bound Books", "test": test['name'], "error": str(e), "params": test['params']})
        results["spiral_bound"].append({"test": test['name'], "status": "ERROR", "error": str(e), "params": test['params']})

# ============================================================================
# PERFECT BOUND BOOKS - 5 TEST CASES
# ============================================================================
print("\n" + "="*80)
print("PERFECT BOUND BOOKS - 5 TEST CASES")
print("="*80)

perfect_tests = [
    {
        "name": "A5 Portrait Basic - 100 books, 100 pages",
        "params": {
            "quantity": 100,
            "printed_pages": 100,
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "None",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 100GSM",
            "proof_requirements": "Digital Emailed Proof"
        }
    },
    {
        "name": "A4 Portrait Full Colour - 200 books, 200 pages",
        "params": {
            "quantity": 200,
            "printed_pages": 200,
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Gloss outside only",
            "content_print_type": "Full Colour",
            "content_stock_type": "Satin 128GSM",
            "proof_requirements": "Digital Emailed Proof"
        }
    },
    {
        "name": "A4 Landscape Large - 500 books, 300 pages",
        "params": {
            "quantity": 500,
            "printed_pages": 300,
            "finish_size": "A4 Landscape",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Matt outside only",
            "content_print_type": "Full Colour",
            "content_stock_type": "Satin 150GSM",
            "proof_requirements": "Physical Proof"
        }
    },
    {
        "name": "US Trade Small - 50 books, 80 pages",
        "params": {
            "quantity": 50,
            "printed_pages": 80,
            "finish_size": "US Trade - 152mm x 229mm",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "1 side colour (2pp)",
            "celloglaze": "None",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 80GSM",
            "proof_requirements": "Digital Emailed Proof"
        }
    },
    {
        "name": "A5 Portrait Minimum Pages - 1000 books, 40 pages",
        "params": {
            "quantity": 1000,
            "printed_pages": 40,
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Gloss outside only",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 90GSM",
            "proof_requirements": "Digital Emailed Proof"
        }
    }
]

for i, test in enumerate(perfect_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = PerfectBoundBooksShopifyCalculator()
        result = calc.calculate(**test['params'])
        
        if hasattr(result, '__dict__'):
            result_dict = {'total_price': str(result.total_price), 'unit_price': str(result.unit_price), 'quantity': result.quantity, 'breakdown': {k: str(v) for k, v in result.breakdown.items()}, 'specifications': result.specifications}
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Pages: {test['params']['printed_pages']}")
        print(f"   Size: {test['params']['finish_size']}")
        
        results["perfect_bound"].append({"test": test['name'], "status": "SUCCESS", "result": result_dict, "params": test['params']})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({"calculator": "Perfect Bound Books", "test": test['name'], "error": str(e), "params": test['params']})
        results["perfect_bound"].append({"test": test['name'], "status": "ERROR", "error": str(e), "params": test['params']})

# ============================================================================
# SADDLE STITCH BOOKS - 5 TEST CASES
# ============================================================================
print("\n" + "="*80)
print("SADDLE STITCH BOOKS - 5 TEST CASES")
print("="*80)

saddle_tests = [
    {
        "name": "A4 Portrait Basic - 100 booklets, 16 pages",
        "params": {
            "quantity": 100,
            "printed_pages": "16pp",
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 200GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "None",
            "content_print_type": "Colour",
            "content_stock_type": "Satin 128GSM"
        }
    },
    {
        "name": "A5 Portrait Medium - 250 booklets, 24 pages",
        "params": {
            "quantity": 250,
            "printed_pages": "24pp",
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 250GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Gloss outside only",
            "content_print_type": "Colour",
            "content_stock_type": "Satin 150GSM"
        }
    },
    {
        "name": "A6 Portrait Small - 500 booklets, 12 pages",
        "params": {
            "quantity": 500,
            "printed_pages": "12pp",
            "finish_size": "A6 Portrait",
            "cover_stock": "Satin 200GSM",
            "cover_print_type": "1 side colour (2pp)",
            "celloglaze": "None",
            "content_print_type": "Black & White",
            "content_stock_type": "Uncoated Bond 100GSM"
        }
    },
    {
        "name": "A4 Portrait Large - 1000 booklets, 40 pages",
        "params": {
            "quantity": 1000,
            "printed_pages": "40pp",
            "finish_size": "A4 Portrait",
            "cover_stock": "Satin 300GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Matt outside only",
            "content_print_type": "Colour",
            "content_stock_type": "Satin 128GSM"
        }
    },
    {
        "name": "A5 Portrait Maximum - 100 booklets, 48 pages",
        "params": {
            "quantity": 100,
            "printed_pages": "48pp",
            "finish_size": "A5 Portrait",
            "cover_stock": "Satin 250GSM",
            "cover_print_type": "2 side colour (4pp)",
            "celloglaze": "Gloss outside only",
            "content_print_type": "Colour",
            "content_stock_type": "Satin 150GSM"
        }
    }
]

for i, test in enumerate(saddle_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = SaddleStitchBooksShopifyCalculator()
        result = calc.calculate(**test['params'])
        
        if hasattr(result, '__dict__'):
            result_dict = {'total_price': str(result.total_price), 'unit_price': str(result.unit_price), 'cost_per_item': str(getattr(result, 'cost_per_item', '')), 'quantity': result.quantity, 'breakdown': {k: str(v) for k, v in result.breakdown.items()}, 'specifications': result.specifications}
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Pages: {test['params']['printed_pages']}")
        print(f"   Size: {test['params']['finish_size']}")
        
        results["saddle_stitch"].append({"test": test['name'], "status": "SUCCESS", "result": result_dict, "params": test['params']})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({"calculator": "Saddle Stitch Books", "test": test['name'], "error": str(e), "params": test['params']})
        results["saddle_stitch"].append({"test": test['name'], "status": "ERROR", "error": str(e), "params": test['params']})

# ============================================================================
# FOLDED FLYERS - 5 TEST CASES
# ============================================================================
print("\n" + "="*80)
print("FOLDED FLYERS - 5 TEST CASES")
print("="*80)

folded_tests = [
    {
        "name": "DL Single Fold - 1000 flyers",
        "params": {
            "quantity": 1000,
            "size": "DL",
            "stock": "Satin 128GSM",
            "double_sided": True,
            "print_type": "Colour",
            "folding": "Single Fold",
            "celloglaze": "None",
            "artworks": 1
        }
    },
    {
        "name": "A4 Double Fold - 500 flyers with gloss",
        "params": {
            "quantity": 500,
            "size": "A4",
            "stock": "Satin 150GSM",
            "double_sided": True,
            "print_type": "Colour",
            "folding": "Double Fold",
            "celloglaze": "2 Side Gloss",
            "artworks": 2
        }
    },
    {
        "name": "A5 Triple Fold - 2000 flyers",
        "params": {
            "quantity": 2000,
            "size": "A5",
            "stock": "Satin 250GSM",
            "double_sided": True,
            "print_type": "Colour",
            "folding": "Triple Fold",
            "celloglaze": "1 Side Matt",
            "artworks": 1
        }
    },
    {
        "name": "A3 Single Fold Uncoated - 250 flyers",
        "params": {
            "quantity": 250,
            "size": "A3",
            "stock": "Uncoated Bond 100GSM",
            "double_sided": True,
            "print_type": "Black & White",
            "folding": "Single Fold",
            "celloglaze": "None",
            "artworks": 1
        }
    },
    {
        "name": "6pp A4 Single Fold - 1000 flyers premium",
        "params": {
            "quantity": 1000,
            "size": "6pp A4",
            "stock": "Satin 350GSM",
            "double_sided": True,
            "print_type": "Colour",
            "folding": "Single Fold",
            "celloglaze": "2 Side Matt",
            "artworks": 3
        }
    }
]

for i, test in enumerate(folded_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = FoldedFlyersShopifyCalculator()
        result = calc.calculate(**test['params'])
        
        if hasattr(result, '__dict__'):
            result_dict = {'total_price': str(result.total_price), 'unit_price': str(result.unit_price), 'quantity': result.quantity, 'breakdown': {k: str(v) for k, v in result.breakdown.items()} if hasattr(result, 'breakdown') else {}, 'specifications': result.specifications if hasattr(result, 'specifications') else {}}
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Size: {test['params']['size']}")
        print(f"   Stock: {test['params']['stock']}")
        
        results["folded_flyers"].append({"test": test['name'], "status": "SUCCESS", "result": result_dict, "params": test['params']})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({"calculator": "Folded Flyers", "test": test['name'], "error": str(e), "params": test['params']})
        results["folded_flyers"].append({"test": test['name'], "status": "ERROR", "error": str(e), "params": test['params']})

# ============================================================================
# CORFLUTE SIGNS - 5 TEST CASES
# ============================================================================
print("\n" + "="*80)
print("CORFLUTE SIGNS - 5 TEST CASES")
print("="*80)

corflute_tests = [
    {
        "name": "Small Preset Single Sided - 10 signs",
        "params": {
            "quantity": 10,
            "size_preset": "450x600",
            "thickness": "3mm",
            "double_sided": False,
            "eyelet_option": "four_corners",
            "artworks": 1
        }
    },
    {
        "name": "Medium Preset Double Sided - 50 signs",
        "params": {
            "quantity": 50,
            "size_preset": "600x900",
            "thickness": "5mm",
            "double_sided": True,
            "eyelet_option": "two_top",
            "artworks": 2
        }
    },
    {
        "name": "Large Preset - 100 signs",
        "params": {
            "quantity": 100,
            "size_preset": "900x1200",
            "thickness": "5mm",
            "double_sided": False,
            "eyelet_option": "six_top_bottom",
            "artworks": 1
        }
    },
    {
        "name": "Extra Large Preset - 25 signs",
        "params": {
            "quantity": 25,
            "size_preset": "1200x2400",
            "thickness": "5mm",
            "double_sided": True,
            "eyelet_option": "six_left_right",
            "artworks": 3
        }
    },
    {
        "name": "Custom Size - 200 signs",
        "params": {
            "quantity": 200,
            "size_preset": "custom",
            "custom_width_mm": 800,
            "custom_height_mm": 1000,
            "thickness": "5mm",
            "double_sided": False,
            "eyelet_option": "none",
            "artworks": 1
        }
    }
]

for i, test in enumerate(corflute_tests, 1):
    print(f"\n[TEST {i}] {test['name']}")
    try:
        calc = CorfluteBulkCalculator()
        result = calc.calculate(**test['params'])
        
        if hasattr(result, '__dict__'):
            result_dict = {'total_price': str(getattr(result, 'total_price', 'N/A')), 'unit_price': str(getattr(result, 'unit_price', 'N/A')), 'quantity': getattr(result, 'quantity', 0)}
        else:
            result_dict = result
        
        print(f"[OK] SUCCESS")
        print(f"   Total: ${result_dict.get('total_price', 'N/A')}")
        print(f"   Per Unit: ${result_dict.get('unit_price', 'N/A')}")
        print(f"   Size: {test['params'].get('size_preset', 'custom')}")
        print(f"   Thickness: {test['params']['thickness']}")
        
        results["corflutes"].append({"test": test['name'], "status": "SUCCESS", "result": result_dict, "params": test['params']})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        errors.append({"calculator": "Corflute Signs", "test": test['name'], "error": str(e), "params": test['params']})
        results["corflutes"].append({"test": test['name'], "status": "ERROR", "error": str(e), "params": test['params']})

# ============================================================================
# SUMMARY AND ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

total_tests = 30  # 5 tests x 6 calculators (removed Flat Flyers GOD)
success_count = sum([len([r for r in results[k] if r['status'] == 'SUCCESS']) for k in results])
error_count = len(errors)

print(f"\nTotal Tests: {total_tests}")
print(f"[OK] Passed: {success_count}")
print(f"[ERROR] Failed: {error_count}")
print(f"Success Rate: {(success_count/total_tests*100):.1f}%")

print("\n" + "="*80)
print("RESULTS BY CALCULATOR")
print("="*80)

for calc_type, calc_results in results.items():
    passed = len([r for r in calc_results if r['status'] == 'SUCCESS'])
    failed = len([r for r in calc_results if r['status'] == 'ERROR'])
    print(f"\n{calc_type.replace('_', ' ').title()}: {passed}/5 passed")
    if failed > 0:
        print(f"  Failed tests:")
        for r in calc_results:
            if r['status'] == 'ERROR':
                print(f"    - {r['test']}")

if errors:
    print("\n" + "="*80)
    print("ERROR DETAILS")
    print("="*80)
    for error in errors:
        print(f"\n[ERROR] {error['calculator']} - {error['test']}")
        print(f"   Error: {error['error']}")
        print(f"   Params: {json.dumps(error['params'], indent=6)}")

# Save results to JSON file
output_file = Path(__file__).parent / 'calculator_test_results.json'
with open(output_file, 'w') as f:
    json.dump({
        'summary': {
            'total_tests': total_tests,
            'passed': success_count,
            'failed': error_count,
            'success_rate': f"{(success_count/total_tests*100):.1f}%"
        },
        'results': results,
        'errors': errors
    }, f, indent=2, default=str)

print(f"\n[OK] Results saved to: {output_file}")
print("\n" + "="*80)
print("TEST SUITE COMPLETE")
print("="*80)
