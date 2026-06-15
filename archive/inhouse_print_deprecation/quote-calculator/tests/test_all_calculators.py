"""
Comprehensive Calculator Test Suite - Tests All Working Calculators
Expands as each calculator is fixed to ensure no regressions

Usage: python test_all_calculators.py
"""

import sys
import os

# Add project root to path
# From: ARCHIVE/tests/ -> quote-calculator/ -> modules_external/ -> UI/ -> AI_agents/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.registry_v3 import RegistryV3
import json

def test_calculator(registry, test_config):
    """Test a single calculator through registry"""
    tool_name = test_config['tool_name']
    params = test_config['params']
    expected_min = test_config.get('expected_min', 0)
    
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"Params: {json.dumps(params, indent=2)}")
    
    result = registry.execute_tool(tool_name=tool_name, **params)
    
    if result.get('success'):
        # GOD calculators use 'total_cost_inc_gst', others use 'total_price'
        total_price = result.get('total_price') or result.get('total_cost_inc_gst', 0)
        print(f"✅ PASSED - ${total_price:.2f}")
        
        if total_price < expected_min:
            print(f"⚠️  WARNING: Price ${total_price:.2f} below expected minimum ${expected_min:.2f}")
            return False
        return True
    else:
        print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
        print(f"   Message: {result.get('message', 'N/A')}")
        return False

def main():
    print("\n" + "="*60)
    print("CALCULATOR TEST SUITE - Registry V3 Integration")
    print("="*60)
    
    registry = RegistryV3()
    
    # Test configurations for all working calculators
    tests = [
        # ===== CORE 6 CALCULATORS (VERIFIED WORKING) =====
        {
            'tool_name': 'calculate_business_cards',
            'params': {
                'quantity': 1000,
                'stock_type': 'premium',
                'print_type': 'double_sided'
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_booklets',
            'params': {
                'quantity': 500,
                'total_pages': 16,
                'cover_stock_gsm': 300,
                'internal_stock_gsm': 150
            },
            'expected_min': 1000
        },
        {
            'tool_name': 'calculate_perfect_bound_books',
            'params': {
                'quantity': 100,
                'total_pages': 200,
                'cover_stock_gsm': 300,
                'internal_stock_gsm': 100
            },
            'expected_min': 500
        },
        {
            'tool_name': 'calculate_flyers',
            'params': {
                'quantity': 1000,
                'width': 210,
                'height': 148,  # A5 dimensions
                'stock_gsm': 150
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_letterheads',
            'params': {
                'quantity': 1000,
                'stock': '100GSM Uncoated',
                'colors': 4
            },
            'expected_min': 150
        },
        {
            'tool_name': 'calculate_corflute_signs',
            'params': {
                'quantity': 50,
                'width': 600,
                'height': 900,
                'thickness': '5mm',
                'double_sided': True
            },
            'expected_min': 800
        },
        
        # ===== SHOPIFY CALCULATORS =====
        {
            'tool_name': 'calculate_economical_business_cards_shopify',
            'params': {
                'quantity': 1000,
                'print_sides': 'Double side print',
                'print_type': 'Colour',
                'artworks': 1
            },
            'expected_min': 50
        },
        {
            'tool_name': 'calculate_premium_business_cards_shopify',
            'params': {
                'quantity': 1000,
                'print_sides': 'Double side print',
                'print_type': 'Colour',
                'celloglaze': 'No Cellophane',
                'artworks': 1
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_folded_flyers_shopify',
            'params': {
                'quantity': 1000,
                'size': 'A5',
                'paper_stock': '150GSM Gloss Art',
                'print_sides': 'Double side print',
                'folding': 'No Folding'
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_wire_bound_books_shopify',
            'params': {
                'quantity': 100,
                'pages': 40,
                'size': 'A5',
                'cover_stock': '300GSM Gloss Art',
                'inner_stock': '100GSM Uncoated',
                'cover_cellophane': 'No Cellophane'
            },
            'expected_min': 200
        },
        {
            'tool_name': 'calculate_spiral_bound_books_shopify',
            'params': {
                'quantity': 100,
                'pages': 40,
                'size': 'A5',
                'cover_stock': '300GSM Gloss Art',
                'inner_stock': '100GSM Uncoated',
                'cover_cellophane': 'No Cellophane'
            },
            'expected_min': 200
        },
        
        # ===== GOD VARIANT CALCULATORS (DATABASE-DRIVEN) =====
        {
            'tool_name': 'calculate_flyers_god',
            'params': {
                'quantity': 1000,
                'width': 210,
                'height': 297,
                'gsm': 150,
                'print_side1': 1,  # Colour
                'print_side2': 0   # None
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_letterheads_god',
            'params': {
                'quantity': 1000,
                'width': 210,
                'height': 297,
                'gsm': 100,
                'print_side1': 1,  # Colour
                'print_side2': 0   # None
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_perfect_bound_books_god',
            'params': {
                'quantity': 100,
                'pages': 100,
                'book_width': 210,
                'book_height': 297,
                'cover_gsm': 300,
                'inner_gsm': 100,
                'print_cover_mode': 1,      # 4pp both sides
                'print_inner_mode': 1,      # B&W
                'cello_type': 0,            # None
                'cover_stock_type_id': 20,  # Type 20 has 300GSM available
                'stock_type_id': 29          # Type 29 has 100GSM available
            },
            'expected_min': 500
        },
        {
            'tool_name': 'calculate_corflute_signs_god',
            'params': {
                'quantity': 50,
                'width': 600,
                'height': 900,
                'thickness': 5,
                'print_sides': 'double'
            },
            'expected_min': 800
        },
        
        # ===== SPECIALIZED SHOPIFY CALCULATORS =====
        {
            'tool_name': 'calculate_saddle_stitch_books',
            'params': {
                'quantity': 100,
                'artworks': 1,
                'cover_option': 'Hard Cover',
                'cover_stock': 'Satin 350GSM',
                'cover_print_type': '2 side colour (4pp)',
                'celloglaze': 'None',
                'printed_pages': '20pp',
                'finish_size': 'A5 Portrait',
                'content_print_type': 'Colour',
                'content_stock_type': 'Satin 150GSM'
            },
            'expected_min': 300
        },
        
        # ===== SPECIALIZED SHOPIFY CALCULATORS (SIGNAGE & BOOKMARKS) =====
        {
            'tool_name': 'calculate_bollard_signs',
            'params': {
                'quantity': 100,
                'material': '3mm Corflute',
                'size': '270mm W x 1000mm H - Three Sided',
                'artworks': '1'
            },
            'expected_min': 200
        },
        {
            'tool_name': 'calculate_construction_signs',
            'params': {
                'quantity': 100,
                'eyelets': 'No Eyelets',
                'thickness': '3mm',
                'size': '450mm x 600mm',
                'print_type': 'Colour 1 sided'
            },
            'expected_min': 150
        },
        {
            'tool_name': 'calculate_premium_bookmarks',
            'params': {
                'quantity': '100',
                'celloglaze': 'None',
                'print_type': 'Colour 1 sided',
                'finish_size': '50mm x 150mm',
                'paper_stock_type': 'Satin 350GSM',
                'artworks': 1
            },
            'expected_min': 50
        },
        {
            'tool_name': 'calculate_election_signs',
            'params': {
                'quantity': 100,
                'size': 'A3',
                'thickness': '3mm',
                'print_type': 'Single sided colour',
                'artworks': 1
            },
            'expected_min': 200
        },
        {
            'tool_name': 'calculate_selfie_frames',
            'params': {
                'quantity': 100,
                'size': '1800mm x 1200mm',
                'material': '3mm Corflute'
            },
            'expected_min': 300
        },
        {
            'tool_name': 'calculate_stackable_cubes',
            'params': {
                'quantity': 100,
                'artworks': '1',
                'material': '3mm Corflute',
                'cube_size': 'Small 300mm x 300mm'
            },
            'expected_min': 200
        },
        {
            'tool_name': 'calculate_strut_cards_a3',
            'params': {
                'quantity': 100,
                'stock': '2mm Screenboard',
                'size': 'A3 - 297mm x 420mm',
                'artworks': 1
            },
            'expected_min': 150
        },
        {
            'tool_name': 'calculate_strut_cards_a4',
            'params': {
                'quantity': 100,
                'stock': '2mm Screenboard',
                'size': 'A4 - 210mm x 297mm',
                'artworks': 1
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_notepads_a4',
            'params': {
                'quantity': '100',
                'artworks': 1,
                'leaves_per_pad': '50',
                'finish_size': 'A4 Portrait',
                'print_type': 'Colour 1 sided',
                'stock_type': 'Uncoated Bond 80GSM'
            },
            'expected_min': 150
        },
        {
            'tool_name': 'calculate_custom_poster_printing',
            'params': {
                'quantity': 100,
                'paper_type': '250GSM Satin Poster Paper',
                'size': 'A2 - 420mm x 594mm',
                'artworks': 1
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_custom_vinyl_stickers',
            'params': {
                'quantity': 100,
                'size': '100mm Circle',
                'vinyl_family': 'Standard (Monomeric)',
                'adhesive': 'Permanent',
                'laminate': 'No Lamination',
                'cutting_method': 'Kiss-Cut (Individual)',
                'artworks': 1,
                'labour_rate': 'Trade ($70/hr)'
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_luxury_classic_pull_up_banners',
            'params': {
                'quantity': 100,
                'artworks': '1',
                'base_colour': 'Silver',
                'size': '850mm W x 2000mm H'
            },
            'expected_min': 500
        },
        {
            'tool_name': 'calculate_metal_face_a_frame',
            'params': {
                'quantity': 100,
                'artworks': 1,
                'size': '600mm W x 900mm H'
            },
            'expected_min': 1000
        },
        {
            'tool_name': 'calculate_with_compliments_slips',
            'params': {
                'quantity': '100',
                'print_sides': 'Single side print',
                'print_type': 'Colour',
                'finish_size': 'DL - 99mm x 210mm',
                'paper_stock_type': 'Uncoated Bond 80GSM'
            },
            'expected_min': 50
        },
        {
            'tool_name': 'calculate_notepads_a5',
            'params': {
                'quantity': '100',
                'artworks': 1,
                'finish_size': 'A5 Portrait',
                'leaves_per_pad': '50',
                'print_type': 'Colour 1 sided',
                'stock_type': 'Uncoated Bond 80GSM'
            },
            'expected_min': 100
        },
        {
            'tool_name': 'calculate_notepads_a6',
            'params': {
                'quantity': '100',
                'artworks': 1,
                'finish_size': 'A6 Portrait',
                'leaves_per_pad': '50',
                'print_type': 'Colour 1 sided',
                'stock_type': 'Uncoated Bond 80GSM'
            },
            'expected_min': 80
        },
        {
            'tool_name': 'calculate_corflute_insert_a_frame',
            'params': {
                'quantity': 100,
                'size': '600mm(W) x 900mm(H)',
                'artworks': 1
            },
            'expected_min': 500
        },
        {
            'tool_name': 'calculate_printed_letterheads',
            'params': {
                'quantity': '100',
                'print_sides': 'Single side print',
                'print_type': 'Colour',
                'finish_size': 'A4 - 210mm x 297mm',
                'paper_stock_type': 'Uncoated Bond 80GSM'
            },
            'expected_min': 50
        },
        {
            'tool_name': 'calculate_spiral_bound_books',
            'params': {
                'quantity': 100,
                'artworks': 1,
                'outer_front_cover': 'Clear PVC',
                'printed_front_cover': '300GSM Satin',
                'cover_print_type': '2pp Colour',
                'celloglaze': 'None',
                'outer_back_cover': 'Not Required',
                'printed_back_cover': 'None',
                'pages': '40pp',
                'finish_size': 'A4 Portrait',
                'content_stock': 'Satin 150GSM',
                'content_print_type': 'Colour'
            },
            'expected_min': 300
        },
    ]
    
    # Run all tests
    passed = 0
    failed = 0
    
    for test in tests:
        if test_calculator(registry, test):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"{'='*60}\n")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
