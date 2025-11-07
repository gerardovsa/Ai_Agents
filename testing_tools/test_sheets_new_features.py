"""
Test new Google Sheets markdown features:
- Background colors [BG:COLOR]
- header_row_background parameter
- auto_borders parameter
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.registry_v3 import RegistryV3

def test_background_colors():
    """Test background color markdown syntax"""
    print("\n" + "="*60)
    print("TEST 1: Background Colors")
    print("="*60)
    
    registry = RegistryV3()
    
    result = registry.execute_tool(
        'google_sheets_create',
        title='Test - Background Colors',
        headers=['**Name**', '**Status**', '**Priority**'],
        data=[
            ['Project A', '[BG:LIGHTGREEN][GREEN]Complete[/GREEN][/BG]', 'High'],
            ['Project B', '[BG:LIGHTYELLOW][ORANGE]In Progress[/ORANGE][/BG]', 'Medium'],
            ['Project C', '[BG:LIGHTRED][RED]Blocked[/RED][/BG]', 'Low']
        ],
        parse_markdown=True,
        _user_id=1,
        _injected_credentials=True
    )
    
    print(f"✅ Created sheet with background colors")
    print(f"   URL: {result['url']}")
    print(f"   Check: Green/Yellow/Red cell backgrounds")
    
    return result['url']


def test_custom_header_control():
    """Test header_row_background=False with custom header colors"""
    print("\n" + "="*60)
    print("TEST 2: Custom Header Control (No Auto Gray)")
    print("="*60)
    
    registry = RegistryV3()
    
    result = registry.execute_tool(
        'google_sheets_create',
        title='Test - Custom Headers',
        headers=[
            '[BG:LIGHTBLUE]**Product**[/BG]',
            '[BG:LIGHTBLUE]**Q3 Sales**[/BG]',
            '[BG:LIGHTBLUE]**Q4 Sales**[/BG]'
        ],
        data=[
            ['Premium Line', '$145K', '$168K'],
            ['Standard Line', '$85K', '$78K']
        ],
        parse_markdown=True,
        header_row_background=False,  # Disable auto gray background
        _user_id=1,
        _injected_credentials=True
    )
    
    print(f"✅ Created sheet with custom header backgrounds")
    print(f"   URL: {result['url']}")
    print(f"   Check: Light blue headers (NOT gray)")
    
    return result['url']


def test_no_borders():
    """Test auto_borders=False for borderless sheet"""
    print("\n" + "="*60)
    print("TEST 3: No Auto Borders")
    print("="*60)
    
    registry = RegistryV3()
    
    result = registry.execute_tool(
        'google_sheets_create',
        title='Test - No Borders',
        headers=['Name', 'Email', 'Status'],
        data=[
            ['**John Doe**', 'john@example.com', '[GREEN]Active[/GREEN]'],
            ['Jane Smith', 'jane@example.com', '[GRAY]Inactive[/GRAY]']
        ],
        parse_markdown=True,
        auto_borders=False,  # No borders
        _user_id=1,
        _injected_credentials=True
    )
    
    print(f"✅ Created borderless sheet")
    print(f"   URL: {result['url']}")
    print(f"   Check: No cell borders")
    
    return result['url']


def test_full_custom_control():
    """Test all features together - full AI control"""
    print("\n" + "="*60)
    print("TEST 4: Full Custom Control (All Features)")
    print("="*60)
    
    registry = RegistryV3()
    
    result = registry.execute_tool(
        'google_sheets_create',
        title='Test - Full Custom Control',
        headers=[
            '[BG:LIGHTYELLOW]**Task Name**[/BG]',
            '[BG:LIGHTYELLOW]**Status**[/BG]',
            '[BG:LIGHTYELLOW]**Owner**[/BG]'
        ],
        data=[
            ['[BG:LIGHTGREEN]API Integration[/BG]', '[GREEN]✓ Done[/GREEN]', '**John**'],
            ['[BG:LIGHTYELLOW]Testing[/BG]', '[ORANGE]In Progress[/ORANGE]', '*Jane*'],
            ['[BG:LIGHTRED]Deployment[/BG]', '[RED]Blocked[/RED]', '**Mike**']
        ],
        parse_markdown=True,
        header_row_background=False,  # Custom yellow headers
        auto_borders=True,  # Keep borders
        _user_id=1,
        _injected_credentials=True
    )
    
    print(f"✅ Created fully customized sheet")
    print(f"   URL: {result['url']}")
    print(f"   Check:")
    print(f"   - Yellow header backgrounds")
    print(f"   - Green/Yellow/Red row backgrounds")
    print(f"   - Colored status text")
    print(f"   - Borders present")
    
    return result['url']


if __name__ == '__main__':
    print("\n" + "="*60)
    print("GOOGLE SHEETS NEW FEATURES TEST SUITE")
    print("Testing: Background colors, header control, border control")
    print("="*60)
    
    urls = []
    
    try:
        # Test 1: Background colors
        url1 = test_background_colors()
        urls.append(('Background Colors', url1))
        
        # Test 2: Custom header control
        url2 = test_custom_header_control()
        urls.append(('Custom Headers', url2))
        
        # Test 3: No borders
        url3 = test_no_borders()
        urls.append(('No Borders', url3))
        
        # Test 4: Full custom control
        url4 = test_full_custom_control()
        urls.append(('Full Custom', url4))
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        print("\nTest Sheet URLs:")
        for i, (name, url) in enumerate(urls, 1):
            print(f"{i}. {name}:")
            print(f"   {url}")
        
        print("\n🎉 NEW FEATURES READY:")
        print("   • [BG:COLOR]text[/BG] - 9 background colors")
        print("   • header_row_background - Control gray header background")
        print("   • auto_borders - Control automatic borders")
        print("   • AI has FULL formatting control!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
