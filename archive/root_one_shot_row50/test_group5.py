"""Test Group 5: Promotional Products calculators"""
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/implementations')

from calculator_wrapper import (
    calculate_luxury_classic_pull_up_banners,
    calculate_selfie_frames,
    calculate_stackable_cubes,
    calculate_strut_cards_a3,
    calculate_strut_cards_a4
)

def test_group_5():
    """Test Group 5: Pull Up Banners, Selfie Frames, Cubes, Strut Cards"""
    print('=' * 80)
    print('TESTING GROUP 5 (Promotional Products)')
    print('=' * 80)
    passed = 0
    failed = 0
    
    # Test 1: Luxury Classic Pull Up Banners
    print('\n--- Luxury Classic Pull Up Banners ---')
    try:
        result = calculate_luxury_classic_pull_up_banners(
            quantity=5,
            width_mm=850,
            height_mm=2000,
            material='Premium Vinyl'
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
        result = calculate_luxury_classic_pull_up_banners(quantity=5)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 2: Selfie Frames
    print('\n--- Selfie Frames ---')
    try:
        result = calculate_selfie_frames(
            quantity=10,
            width_mm=600,
            height_mm=600,
            material='Foam Core',
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
        result = calculate_selfie_frames(quantity=10)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 3: Stackable Cubes
    print('\n--- Stackable Cubes ---')
    try:
        result = calculate_stackable_cubes(
            quantity=5,
            size='300',
            material='Corrugated'
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
        result = calculate_stackable_cubes(quantity=5)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 4: Strut Cards A3
    print('\n--- Strut Cards A3 ---')
    try:
        result = calculate_strut_cards_a3(
            quantity=50,
            size='297x420',
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
    
    try:
        result = calculate_strut_cards_a3(quantity=50)
        if result['success']:
            print(f'✅ Defaults: total=${result.get("total_price", 0):.2f}')
            passed += 1
        else:
            print(f'❌ Defaults failed: {result.get("error")}')
            failed += 1
    except Exception as e:
        print(f'❌ Defaults exception: {e}')
        failed += 1
    
    # Test 5: Strut Cards A4
    print('\n--- Strut Cards A4 ---')
    try:
        result = calculate_strut_cards_a4(
            quantity=50,
            size='210x297',
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
    
    try:
        result = calculate_strut_cards_a4(quantity=50)
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
    passed, failed = test_group_5()
    
    print('\n' + '=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Group 5: {passed}/{passed+failed} tests passed {"✅" if failed == 0 else "❌"}')
    print(f'Total: {passed}/{passed+failed} tests passed ({100*passed/(passed+failed):.0f}%)')
    
    if failed == 0:
        print('\n🎉 ALL TESTS PASSED!')
    else:
        print(f'\n⚠️ {failed} tests failed')
