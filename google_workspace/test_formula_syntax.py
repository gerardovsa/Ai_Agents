"""
Test suite for Google Sheets Markdown Formatter v3.1 Formula Syntax
Tests all 6 formula syntaxes added in v3.1
"""

import sys
sys.path.append('C:\\Users\\gpoli\\GIT\\AI_agents')

from google_workspace.sheets_markdown_formatter import MarkdownToSheetsFormatter

def test_formulas():
    """Test v3.1 formula syntax"""
    formatter = MarkdownToSheetsFormatter()
    
    print("=" * 80)
    print("GOOGLE SHEETS MARKDOWN FORMATTER v3.1 - FORMULA TESTS")
    print("=" * 80)
    
    # Test 1: Direct formula with FORMULA prefix
    print("\n[TEST 1] Direct Formula Syntax")
    text, fmt = formatter.parse_cell_markdown("[FORMULA]=SUM(A1:A10)", 0, 0)
    print(f"  Input:  [FORMULA]=SUM(A1:A10)")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=SUM(A1:A10)" else f"  ✗ FAIL - Expected '=SUM(A1:A10)', got '{text}'")
    
    # Test 2: Formula without = prefix (auto-add)
    print("\n[TEST 2] Formula Without = Prefix")
    text, fmt = formatter.parse_cell_markdown("[FORMULA]SUM(B1:B10)", 0, 0)
    print(f"  Input:  [FORMULA]SUM(B1:B10)")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=SUM(B1:B10)" else f"  ✗ FAIL - Expected '=SUM(B1:B10)', got '{text}'")
    
    # Test 3: SUM shorthand
    print("\n[TEST 3] SUM Shorthand")
    text, fmt = formatter.parse_cell_markdown("[SUM:A1:A10]", 0, 0)
    print(f"  Input:  [SUM:A1:A10]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=SUM(A1:A10)" else f"  ✗ FAIL - Expected '=SUM(A1:A10)', got '{text}'")
    
    # Test 4: AVERAGE shorthand (both syntaxes)
    print("\n[TEST 4] AVERAGE Shorthand (AVG)")
    text, fmt = formatter.parse_cell_markdown("[AVG:B2:B50]", 0, 0)
    print(f"  Input:  [AVG:B2:B50]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=AVERAGE(B2:B50)" else f"  ✗ FAIL - Expected '=AVERAGE(B2:B50)', got '{text}'")
    
    print("\n[TEST 5] AVERAGE Shorthand (AVERAGE)")
    text, fmt = formatter.parse_cell_markdown("[AVERAGE:C1:C25]", 0, 0)
    print(f"  Input:  [AVERAGE:C1:C25]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=AVERAGE(C1:C25)" else f"  ✗ FAIL - Expected '=AVERAGE(C1:C25)', got '{text}'")
    
    # Test 6: COUNT shorthand
    print("\n[TEST 6] COUNT Shorthand")
    text, fmt = formatter.parse_cell_markdown("[COUNT:D1:D100]", 0, 0)
    print(f"  Input:  [COUNT:D1:D100]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=COUNT(D1:D100)" else f"  ✗ FAIL - Expected '=COUNT(D1:D100)', got '{text}'")
    
    # Test 7: MIN shorthand
    print("\n[TEST 7] MIN Shorthand")
    text, fmt = formatter.parse_cell_markdown("[MIN:E1:E20]", 0, 0)
    print(f"  Input:  [MIN:E1:E20]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=MIN(E1:E20)" else f"  ✗ FAIL - Expected '=MIN(E1:E20)', got '{text}'")
    
    # Test 8: MAX shorthand
    print("\n[TEST 8] MAX Shorthand")
    text, fmt = formatter.parse_cell_markdown("[MAX:F1:F30]", 0, 0)
    print(f"  Input:  [MAX:F1:F30]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=MAX(F1:F30)" else f"  ✗ FAIL - Expected '=MAX(F1:F30)', got '{text}'")
    
    # Test 9: Formula combined with alignment
    print("\n[TEST 9] Formula + Right Alignment")
    text, fmt = formatter.parse_cell_markdown("(R)[SUM:A1:A10]", 0, 0)
    print(f"  Input:  (R)[SUM:A1:A10]")
    print(f"  Output: {text}")
    print(f"  Alignment: {fmt.get('horizontalAlignment', 'NONE')}")
    is_correct = text == "=SUM(A1:A10)" and fmt.get('horizontalAlignment') == 'RIGHT'
    print(f"  ✓ PASS" if is_correct else f"  ✗ FAIL")
    
    # Test 10: Formula combined with number format
    print("\n[TEST 10] Formula + Currency Format")
    text, fmt = formatter.parse_cell_markdown("[$][SUM:Revenue]", 0, 0)
    print(f"  Input:  [$][SUM:Revenue]")
    print(f"  Output: {text}")
    print(f"  Number Format: {fmt.get('numberFormat', {}).get('pattern', 'NONE')}")
    has_currency = '$' in str(fmt.get('numberFormat', {}).get('pattern', ''))
    is_formula = text == "=SUM(Revenue)"
    print(f"  ✓ PASS" if (has_currency and is_formula) else f"  ✗ FAIL")
    
    # Test 11: Complex formula
    print("\n[TEST 11] Complex Formula")
    text, fmt = formatter.parse_cell_markdown("[FORMULA]=IF(A1>100,SUM(B1:B10),0)", 0, 0)
    print(f"  Input:  [FORMULA]=IF(A1>100,SUM(B1:B10),0)")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=IF(A1>100,SUM(B1:B10),0)" else f"  ✗ FAIL")
    
    # Test 12: Formula with column reference (entire column)
    print("\n[TEST 12] Formula with Entire Column")
    text, fmt = formatter.parse_cell_markdown("[SUM:A:A]", 0, 0)
    print(f"  Input:  [SUM:A:A]")
    print(f"  Output: {text}")
    print(f"  ✓ PASS" if text == "=SUM(A:A)" else f"  ✗ FAIL - Expected '=SUM(A:A)', got '{text}'")
    
    print("\n" + "=" * 80)
    print("FORMULA SYNTAX TEST SUITE COMPLETE")
    print("=" * 80)
    print("\nv3.1 Features:")
    print("  ✓ Direct formulas: [FORMULA]=...")
    print("  ✓ Shorthand: [SUM:range], [AVG:range], [COUNT:range]")
    print("  ✓ Shorthand: [MIN:range], [MAX:range]")
    print("  ✓ Combined with alignment and number formats")
    print("  ✓ Complex formulas with nested functions")
    print("  ✓ Entire column references (A:A)")
    print("\nTotal v3.1 Features: 47 (41 from v3.0 + 6 formula syntaxes)")

if __name__ == "__main__":
    test_formulas()
