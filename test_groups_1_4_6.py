"""Test Groups 1, 4, and 6 calculators"""
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/implementations')

from calculator_wrapper import (
    # Group 1
    calculate_economical_business_cards_shopify,
    calculate_premium_business_cards_shopify,
    calculate_folded_flyers_shopify,
    calculate_printed_letterheads,
    calculate_with_compliments_slips,
    # Group 4
    calculate_election_signs,
    calculate_construction_signs,
    calculate_bollard_signs,
    calculate_corflute_insert_a_frame,
    calculate_metal_face_a_frame,
    # Group 6
    calculate_premium_bookmarks,
    calculate_corflute_signs_shopify
)

def test_group_1():
    """Test Group 1: Business Cards, Flyers, Letterheads"""
    print('=' * 80)
    print('TESTING GROUP 1 (Economical/Premium Cards, Folded Flyers, Letterheads)')
    print('=' * 80)
    passed = 0
    failed = 0
    
    # Test 1: Economical Business Cards
    print('\n--- Economical Business Cards ---')
    try:
        result = calculate_economical_business_cards_shopify(
            quantity=500,
            print_type='Colour',
            double_sided=True,
            celloglaze='2 Side Matt',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_economical_business_cards_shopify(quantity=500)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 2: Premium Business Cards
    print('\n--- Premium Business Cards ---')
    try:
        result = calculate_premium_business_cards_shopify(
            quantity=500,
            print_type='Colour',
            paper_stock='Satin 350GSM',
            double_sided=True,
            celloglaze='2 Side Matt',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_premium_business_cards_shopify(quantity=500)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 3: Folded Flyers
    print('\n--- Folded Flyers ---')
    try:
        result = calculate_folded_flyers_shopify(
            quantity=1000,
            size='A5',
            stock='Satin 150GSM',
            folding='Single Fold',
            print_type='Colour',
            double_sided=True,
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_folded_flyers_shopify(quantity=1000)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 4: Printed Letterheads
    print('\n--- Printed Letterheads ---')
    try:
        result = calculate_printed_letterheads(
            quantity=250,
            paper_stock='Bond 100GSM',
            print_type='Colour',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_printed_letterheads(quantity=250)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 5: With Compliments Slips
    print('\n--- With Compliments Slips ---')
    try:
        result = calculate_with_compliments_slips(
            quantity=250,
            paper_stock='Bond 100GSM',
            print_type='Colour',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_with_compliments_slips(quantity=250)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    return passed, failed

def test_group_4():
    """Test Group 4: Signs - Election, Construction, Bollard, A-Frames"""
    print('\n' + '=' * 80)
    print('TESTING GROUP 4 (Signs - Election, Construction, Bollard, A-Frames)')
    print('=' * 80)
    passed = 0
    failed = 0
    
    # Test 1: Election Signs with new params
    print('\n--- Election Signs ---')
    try:
        result = calculate_election_signs(
            quantity=50,
            size='600x450',
            material='Corflute',
            sides='Single',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    # Test 2: Election Signs with defaults
    try:
        result = calculate_election_signs(quantity=50)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 3: Construction Signs with new params
    print('\n--- Construction Signs ---')
    try:
        result = calculate_construction_signs(
            quantity=25,
            size='900x600',
            material='Aluminium Composite',
            sides='Double',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    # Test 4: Construction Signs with defaults
    try:
        result = calculate_construction_signs(quantity=25)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 5: Bollard Signs with new params
    print('\n--- Bollard Signs ---')
    try:
        result = calculate_bollard_signs(
            quantity=10,
            size='300x1200',
            material='Corflute',
            sides='Single',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    # Test 6: Bollard Signs with defaults
    try:
        result = calculate_bollard_signs(quantity=10)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 7: Corflute A-Frame with new params
    print('\n--- Corflute Insert A-Frame ---')
    try:
        result = calculate_corflute_insert_a_frame(
            quantity=5,
            size='600x900',
            sides='Double',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    # Test 8: Corflute A-Frame with defaults
    try:
        result = calculate_corflute_insert_a_frame(quantity=5)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 9: Metal Face A-Frame with new params
    print('\n--- Metal Face A-Frame ---')
    try:
        result = calculate_metal_face_a_frame(
            quantity=3,
            size='A1',
            sides='Double',
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    # Test 10: Metal Face A-Frame with defaults
    try:
        result = calculate_metal_face_a_frame(quantity=3)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    return passed, failed

def test_group_6():
    """Test Group 6: Premium Bookmarks, Corflute Signs"""
    print('\n' + '=' * 80)
    print('TESTING GROUP 6 (Premium Bookmarks, Corflute Signs)')
    print('=' * 80)
    passed = 0
    failed = 0
    
    # Test 1: Premium Bookmarks
    print('\n--- Premium Bookmarks ---')
    try:
        result = calculate_premium_bookmarks(
            quantity=100,
            width_mm=55,
            height_mm=200,
            paper_stock='350gsm',
            lamination='Matte'
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_premium_bookmarks(quantity=100)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 2: Corflute Signs Shopify
    print('\n--- Corflute Signs Shopify ---')
    try:
        result = calculate_corflute_signs_shopify(
            quantity=20,
            size_preset='600x900',
            thickness='5mm',
            double_sided=True,
            artworks=1
        )
        if result['success']:
            print(f'✅ New params: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ New params failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ New params exception: {e}')
        failed += 1
    
    try:
        result = calculate_corflute_signs_shopify(quantity=20)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    return passed, failed

if __name__ == '__main__':
    total_passed = 0
    total_failed = 0
    
    p1, f1 = test_group_1()
    total_passed += p1
    total_failed += f1
    
    p4, f4 = test_group_4()
    total_passed += p4
    total_failed += f4
    
    p6, f6 = test_group_6()
    total_passed += p6
    total_failed += f6
    
    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Group 1: {p1}/{p1+f1} tests passed {"✅" if f1 == 0 else "❌"}')
    print(f'Group 4: {p4}/{p4+f4} tests passed {"✅" if f4 == 0 else "❌"}')
    print(f'Group 6: {p6}/{p6+f6} tests passed {"✅" if f6 == 0 else "❌"}')
    print(f'Total: {total_passed}/{total_passed+total_failed} tests passed ({100*total_passed/(total_passed+total_failed):.0f}%)')
    
    if total_failed == 0:
        print('\n🎉 ALL TESTS PASSED!')
    else:
        print(f'\n⚠️ {total_failed} tests failed')
