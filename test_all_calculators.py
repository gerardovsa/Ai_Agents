"""Test all 37 calculator tools in registry_v3"""
from tools.registry_v3 import RegistryV3
import sys

def test_all_calculators():
    """Test execution of all calculator tools"""
    print("\n" + "="*80)
    print("CALCULATOR EXECUTION TEST - ALL 37 CALCULATORS")
    print("="*80 + "\n")
    
    r = RegistryV3()
    
    # Get all calculator tools
    tools = r.get_anthropic_tools()
    calc_tools = [t for t in tools if 'calculate_' in t.get('name', '')]
    
    print(f"[FOUND] {len(calc_tools)} calculator tools\n")
    
    # Test data for each calculator type
    test_params = {
        'calculate_business_cards': {
            'quantity': 500,
            'finish_size': '90x55',
            'stock_type': '350gsm Silk',
            'print_type': '4/0 (Full Colour Front Only)'
        },
        'calculate_flyers': {
            'quantity': 1000,
            'finish_size': 'A5',
            'stock_type': '150gsm Gloss',
            'print_type': '4/4 (Full Colour Both Sides)'
        },
        'calculate_booklets': {
            'quantity': 100,
            'pages': 12,
            'finish_size': 'A4',
            'cover_stock': '250gsm Gloss',
            'inner_stock': '150gsm Gloss'
        },
        'calculate_perfect_bound_books': {
            'quantity': 50,
            'pages': 48,
            'finish_size': 'A5',
            'cover_stock': '300gsm Gloss',
            'inner_stock': '150gsm Offset'
        },
        'calculate_letterheads': {
            'quantity': 500,
            'stock_type': '100gsm Laser',
            'print_type': '4/0 (Full Colour Front Only)'
        },
        'calculate_corflute_signs': {
            'quantity': 10,
            'size': 'A2',
            'thickness': '5mm'
        }
    }
    
    # Default minimal params for unknown calculators
    default_params = {'quantity': 100}
    
    results = []
    passed = 0
    failed = 0
    
    for i, tool in enumerate(calc_tools, 1):
        tool_name = tool['name']
        params = test_params.get(tool_name, default_params)
        
        try:
            # Execute with kwargs
            result = r.execute_tool(tool_name=tool_name, **params)
            
            # Check if successful
            if result.get('success') or result.get('total_price') or result.get('price'):
                price = result.get('total_price') or result.get('price') or 'N/A'
                status = '[OK]'
                passed += 1
                results.append((tool_name, status, f'${price}'))
                print(f"{i:2}. {status} {tool_name:<50} ${price}")
            else:
                status = '[FAIL]'
                failed += 1
                error_msg = result.get('error', result.get('message', 'Unknown'))[:40]
                results.append((tool_name, status, error_msg))
                print(f"{i:2}. {status} {tool_name:<50} {error_msg}")
                
        except Exception as e:
            status = '[ERROR]'
            failed += 1
            error_msg = str(e)[:40]
            results.append((tool_name, status, error_msg))
            print(f"{i:2}. {status} {tool_name:<50} {error_msg}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total calculators: {len(calc_tools)}")
    print(f"Passed:            {passed} ({passed/len(calc_tools)*100:.1f}%)")
    print(f"Failed:            {failed} ({failed/len(calc_tools)*100:.1f}%)")
    print("="*80 + "\n")
    
    # Return exit code
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(test_all_calculators())
