"""
Test v2.0 Phase 1: Alignment + Shortened Color Codes
Tests the new compact syntax for Google Sheets formatting
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google_workspace.sheets_markdown_formatter import MarkdownToSheetsFormatter


def test_alignment_parsing():
    """Test alignment parsing (L), (R), (C)"""
    formatter = MarkdownToSheetsFormatter()
    
    # Test left alignment
    clean, fmt = formatter.parse_cell_markdown("(L)Left Text")
    assert clean == "Left Text", f"Expected 'Left Text', got '{clean}'"
    assert 'horizontalAlignment' in fmt, "Missing alignment"
    assert fmt['horizontalAlignment'] == 'LEFT', f"Expected LEFT, got {fmt.get('horizontalAlignment')}"
    
    # Test right alignment
    clean, fmt = formatter.parse_cell_markdown("(R)Right Text")
    assert clean == "Right Text"
    assert fmt['horizontalAlignment'] == 'RIGHT'
    
    # Test center alignment
    clean, fmt = formatter.parse_cell_markdown("(C)Center Text")
    assert clean == "Center Text"
    assert fmt['horizontalAlignment'] == 'CENTER'
    
    print("✅ Test 1: Alignment parsing - PASS")
    return True


def test_shortened_color_codes():
    """Test shortened text color codes [R], [G], [B], [P], [GR], [BK]"""
    formatter = MarkdownToSheetsFormatter()
    
    # Test red
    clean, fmt = formatter.parse_cell_markdown("[R]Red Text")
    assert clean == "Red Text", f"Expected 'Red Text', got '{clean}'"
    assert 'foregroundColor' in fmt, "Missing foreground color"
    assert fmt['foregroundColor']['red'] == 0.9, "Red color not applied"
    
    # Test green
    clean, fmt = formatter.parse_cell_markdown("[G]Green Text")
    assert clean == "Green Text"
    assert fmt['foregroundColor']['green'] == 0.8
    
    # Test blue
    clean, fmt = formatter.parse_cell_markdown("[B]Blue Text")
    assert clean == "Blue Text"
    assert fmt['foregroundColor']['blue'] == 0.9
    
    # Test purple
    clean, fmt = formatter.parse_cell_markdown("[P]Purple Text")
    assert clean == "Purple Text"
    assert fmt['foregroundColor']['red'] == 0.7
    
    # Test gray
    clean, fmt = formatter.parse_cell_markdown("[GR]Gray Text")
    assert clean == "Gray Text"
    assert fmt['foregroundColor']['red'] == 0.5, "Gray color red value wrong"
    assert fmt['foregroundColor']['green'] == 0.5, "Gray color green value wrong"
    assert fmt['foregroundColor']['blue'] == 0.5, "Gray color blue value wrong"
    
    # Test black
    clean, fmt = formatter.parse_cell_markdown("[BK]Black Text")
    assert clean == "Black Text"
    assert fmt['foregroundColor']['red'] == 0.0
    
    print("✅ Test 2: Shortened color codes - PASS")
    return True


def test_shortened_background_codes():
    """Test shortened background codes {LR}, {LG}, {LB}, {LP}, {LGR}"""
    formatter = MarkdownToSheetsFormatter()
    
    # Test light red
    clean, fmt = formatter.parse_cell_markdown("{LR}Light Red BG")
    assert clean == "Light Red BG", f"Expected 'Light Red BG', got '{clean}'"
    assert 'backgroundColor' in fmt, "Missing background color"
    assert fmt['backgroundColor']['red'] == 0.95, "Light red BG not applied"
    
    # Test light green
    clean, fmt = formatter.parse_cell_markdown("{LG}Light Green BG")
    assert clean == "Light Green BG"
    assert fmt['backgroundColor']['green'] == 0.95
    
    # Test light blue
    clean, fmt = formatter.parse_cell_markdown("{LB}Light Blue BG")
    assert clean == "Light Blue BG"
    assert fmt['backgroundColor']['blue'] == 0.95
    
    # Test light purple
    clean, fmt = formatter.parse_cell_markdown("{LP}Light Purple BG")
    assert clean == "Light Purple BG"
    assert fmt['backgroundColor']['red'] == 0.95
    assert fmt['backgroundColor']['blue'] == 0.95
    
    # Test light gray
    clean, fmt = formatter.parse_cell_markdown("{LGR}Light Gray BG")
    assert clean == "Light Gray BG"
    assert fmt['backgroundColor']['red'] == 0.9
    
    print("✅ Test 3: Shortened background codes - PASS")
    return True


def test_stacking_order():
    """Test stacking: (ALIGN)[COLOR]{BG}text"""
    formatter = MarkdownToSheetsFormatter()
    
    # Test alignment + color + background
    clean, fmt = formatter.parse_cell_markdown("(R)[G]{LG}$125K")
    assert clean == "$125K", f"Expected '$125K', got '{clean}'"
    assert 'horizontalAlignment' in fmt, "Missing alignment"
    assert fmt['horizontalAlignment'] == 'RIGHT', "Wrong alignment"
    assert 'foregroundColor' in fmt, "Missing text color"
    assert fmt['foregroundColor']['green'] == 0.8, "Wrong text color"
    assert 'backgroundColor' in fmt, "Missing background color"
    assert fmt['backgroundColor']['green'] == 0.95, "Wrong background color"
    
    # Test alignment + color only
    clean, fmt = formatter.parse_cell_markdown("(L)[R]Critical")
    assert clean == "Critical"
    assert fmt['horizontalAlignment'] == 'LEFT'
    assert fmt['foregroundColor']['red'] == 0.9
    
    # Test color + background only (no alignment)
    clean, fmt = formatter.parse_cell_markdown("[B]{LB}Info")
    assert clean == "Info"
    assert 'horizontalAlignment' not in fmt, "Should not have alignment"
    assert fmt['foregroundColor']['blue'] == 0.9
    assert fmt['backgroundColor']['blue'] == 0.95
    
    print("✅ Test 4: Stacking order - PASS")
    return True


def test_backward_compatibility():
    """Test that old v1.2 syntax still works"""
    formatter = MarkdownToSheetsFormatter()
    
    # Test verbose color with closing tag
    clean, fmt = formatter.parse_cell_markdown("[RED]Red Text[/RED]")
    assert clean == "Red Text", f"Expected 'Red Text', got '{clean}'"
    assert 'foregroundColor' in fmt, "Missing color"
    assert fmt['foregroundColor']['red'] == 0.9, "Red not applied"
    
    # Test verbose background with closing tag
    clean, fmt = formatter.parse_cell_markdown("[BG:LIGHTGREEN]Green BG[/BG]")
    assert clean == "Green BG"
    assert 'backgroundColor' in fmt
    assert fmt['backgroundColor']['green'] == 0.95
    
    # Test bold
    clean, fmt = formatter.parse_cell_markdown("**Bold Text**")
    assert clean == "Bold Text"
    assert fmt.get('bold') == True
    
    # Test header
    clean, fmt = formatter.parse_cell_markdown("# Header")
    assert clean == "Header"
    assert fmt.get('fontSize') == 18
    assert fmt.get('bold') == True
    
    print("✅ Test 5: Backward compatibility (v1.2 syntax still works) - PASS")
    return True


def test_character_savings():
    """Test that v2.0 is actually shorter than v1.2"""
    
    # v1.2 syntax
    v1_text = "[RED]Critical Error[/RED]"
    
    # v2.0 syntax
    v2_text = "[R]Critical Error"
    
    savings = len(v1_text) - len(v2_text)
    percentage = (savings / len(v1_text)) * 100
    
    print(f"✅ Test 6: Character savings")
    print(f"   v1.2: '{v1_text}' ({len(v1_text)} chars)")
    print(f"   v2.0: '{v2_text}' ({len(v2_text)} chars)")
    print(f"   Savings: {savings} chars ({percentage:.1f}% shorter) - PASS")
    
    assert savings > 0, "v2.0 should be shorter"
    assert percentage > 30, f"Should be >30% shorter, got {percentage}%" # Realistic threshold
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("GOOGLE SHEETS v2.0 PHASE 1 TEST SUITE")
    print("Testing: Alignment + Shortened Color Codes")
    print("="*60)
    print()
    
    tests = [
        test_alignment_parsing,
        test_shortened_color_codes,
        test_shortened_background_codes,
        test_stacking_order,
        test_backward_compatibility,
        test_character_savings
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"❌ {test_func.__name__} - FAILED")
            print(f"   Error: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} - ERROR")
            print(f"   Exception: {e}")
            print()
    
    print("="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - v2.0 Phase 1 ready for production!")
    else:
        print(f"❌ {failed} tests failed - need fixes")
    
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
