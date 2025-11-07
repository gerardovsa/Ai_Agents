"""
Test Google Sheets Markdown Formatting Feature

Tests the new parse_markdown parameter in google_sheets_create()
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'AI_infrastructure'))

from tools.registry_v3 import RegistryV3


def test_markdown_formatter():
    """Test the markdown formatter module directly"""
    print("\n" + "="*60)
    print("TEST 1: Markdown Formatter Module")
    print("="*60)
    
    try:
        from google_workspace.sheets_markdown_formatter import MarkdownToSheetsFormatter, format_data_with_markdown
        
        formatter = MarkdownToSheetsFormatter()
        
        # Test 1a: Bold text
        text, fmt = formatter.parse_cell_markdown("**Bold text**")
        assert text == "Bold text", f"Expected 'Bold text', got '{text}'"
        assert fmt.get('bold') == True, f"Expected bold=True, got {fmt}"
        print(f"✅ Test 1a: Bold parsing - PASS")
        print(f"   Input: '**Bold text**' → Output: '{text}' + {fmt}")
        
        # Test 1b: Italic text
        text, fmt = formatter.parse_cell_markdown("*Italic text*")
        assert text == "Italic text", f"Expected 'Italic text', got '{text}'"
        assert fmt.get('italic') == True, f"Expected italic=True, got {fmt}"
        print(f"✅ Test 1b: Italic parsing - PASS")
        print(f"   Input: '*Italic text*' → Output: '{text}' + {fmt}")
        
        # Test 1c: Header
        text, fmt = formatter.parse_cell_markdown("# Header 1")
        assert text == "Header 1", f"Expected 'Header 1', got '{text}'"
        assert fmt.get('bold') == True, f"Expected bold=True for header"
        assert fmt.get('fontSize') == 18, f"Expected fontSize=18, got {fmt.get('fontSize')}"
        print(f"✅ Test 1c: Header parsing - PASS")
        print(f"   Input: '# Header 1' → Output: '{text}' + {fmt}")
        
        # Test 1d: Color tags
        text, fmt = formatter.parse_cell_markdown("[RED]Critical[/RED]")
        assert text == "Critical", f"Expected 'Critical', got '{text}'"
        assert 'foregroundColor' in fmt, f"Expected color in format: {fmt}"
        print(f"✅ Test 1d: Color parsing - PASS")
        print(f"   Input: '[RED]Critical[/RED]' → Output: '{text}' + {fmt}")
        
        # Test 1e: Full data array
        data = [
            ["**John**", "*30*", "NYC"],
            ["Jane", "[GREEN]Active[/GREEN]", "LA"]
        ]
        headers = ["# Name", "**Age**", "City"]
        
        clean_data, format_requests = format_data_with_markdown(data, headers)
        
        assert len(clean_data) == 2, f"Expected 2 data rows, got {len(clean_data)}"
        assert len(format_requests) > 0, f"Expected format requests, got {len(format_requests)}"
        print(f"✅ Test 1e: Full data array - PASS")
        print(f"   Input: 2 rows with markdown → Output: {len(format_requests)} format rules")
        
        return True
        
    except Exception as e:
        print(f"❌ Test 1: Markdown formatter - FAIL")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sheets_create_without_markdown():
    """Test google_sheets_create WITHOUT markdown (baseline)"""
    print("\n" + "="*60)
    print("TEST 2: Create Sheet WITHOUT Markdown (Baseline)")
    print("="*60)
    
    try:
        registry = RegistryV3()
        user_id = 1
        
        result = registry.execute_tool(
            'google_sheets_create',
            title='Test Sheet - No Markdown',
            headers=['Name', 'Age', 'Status'],
            data=[
                ['**John**', 25, '[RED]Critical[/RED]'],
                ['Jane', 30, '*Pending*']
            ],
            parse_markdown=False,  # Explicitly False
            _user_id=user_id,
            _injected_credentials=True
        )
        
        assert 'spreadsheet_id' in result, f"Missing spreadsheet_id in result"
        assert 'url' in result, f"Missing url in result"
        assert result.get('markdown_parsed') == False, f"Expected markdown_parsed=False"
        
        print(f"✅ Test 2: Create without markdown - PASS")
        print(f"   Spreadsheet ID: {result['spreadsheet_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Rows written: {result.get('rows_written', 0)}")
        print(f"   Markdown parsed: {result.get('markdown_parsed', False)}")
        print(f"   📝 Check URL - should see literal markdown syntax (**bold**, [RED], etc.)")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 2: Create without markdown - FAIL")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_sheets_create_with_markdown():
    """Test google_sheets_create WITH markdown (NEW FEATURE)"""
    print("\n" + "="*60)
    print("TEST 3: Create Sheet WITH Markdown (NEW FEATURE)")
    print("="*60)
    
    try:
        registry = RegistryV3()
        user_id = 1
        
        result = registry.execute_tool(
            'google_sheets_create',
            title='Test Sheet - With Markdown',
            headers=['# Patient Name', '**Status**', '**Priority**'],
            data=[
                ['**Dr. John Smith**', '[GREEN]Stable[/GREEN]', 'Low'],
                ['Jane Doe', '[RED]Critical[/RED]', '**High**'],
                ['Bob Johnson', '[YELLOW]Observation[/YELLOW]', '*Medium*']
            ],
            parse_markdown=True,  # ✨ NEW PARAMETER
            _user_id=user_id,
            _injected_credentials=True
        )
        
        assert 'spreadsheet_id' in result, f"Missing spreadsheet_id in result"
        assert 'url' in result, f"Missing url in result"
        assert result.get('markdown_parsed') == True, f"Expected markdown_parsed=True, got {result.get('markdown_parsed')}"
        
        print(f"✅ Test 3: Create with markdown - PASS")
        print(f"   Spreadsheet ID: {result['spreadsheet_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Rows written: {result.get('rows_written', 0)}")
        print(f"   Markdown parsed: {result.get('markdown_parsed', False)}")
        print(f"\n   ✨ Expected formatting:")
        print(f"      - Header row: Larger font (18pt), bold, gray background")
        print(f"      - 'Dr. John Smith': Bold text")
        print(f"      - 'Stable': Green text")
        print(f"      - 'Critical': Red text")
        print(f"      - 'Observation': Yellow text")
        print(f"      - 'High': Bold text")
        print(f"      - 'Medium': Italic text")
        print(f"      - All cells: Bordered")
        print(f"\n   📝 CHECK URL - Should see professional formatting, NO markdown syntax!")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 3: Create with markdown - FAIL")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_complex_markdown_scenario():
    """Test complex real-world scenario with markdown"""
    print("\n" + "="*60)
    print("TEST 4: Complex Real-World Scenario")
    print("="*60)
    
    try:
        registry = RegistryV3()
        user_id = 1
        
        # Business report with markdown formatting
        result = registry.execute_tool(
            'google_sheets_create',
            title='Q4 Sales Report - Markdown Formatted',
            headers=['# Product Category', '**Q3 Sales**', '**Q4 Sales**', '**Status**', '**Action Required**'],
            data=[
                ['**Premium Widgets**', '$125,000', '$145,000', '[GREEN]+16%[/GREEN]', '*Maintain inventory*'],
                ['Economy Widgets', '$85,000', '$78,000', '[RED]-8%[/RED]', '**Investigate decline**'],
                ['**Accessories**', '$42,000', '$51,000', '[GREEN]+21%[/GREEN]', '*Increase marketing*'],
                ['Services', '$38,000', '$39,000', '[YELLOW]+3%[/YELLOW]', 'Monitor trends']
            ],
            parse_markdown=True,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        assert 'spreadsheet_id' in result, f"Missing spreadsheet_id"
        assert result.get('markdown_parsed') == True, f"Expected markdown_parsed=True"
        assert result.get('rows_written', 0) > 0, f"No rows written"
        
        print(f"✅ Test 4: Complex scenario - PASS")
        print(f"   Spreadsheet ID: {result['spreadsheet_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Rows written: {result.get('rows_written', 0)}")
        print(f"\n   ✨ This demonstrates:")
        print(f"      - Professional business report formatting")
        print(f"      - Color-coded performance indicators (green=good, red=bad)")
        print(f"      - Bold for emphasis on key products")
        print(f"      - Italic for action items")
        print(f"      - Headers with visual hierarchy")
        print(f"\n   📝 CHECK URL - Should look like a professional dashboard!")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Test 4: Complex scenario - FAIL")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


if __name__ == '__main__':
    print("\n" + "="*70)
    print("GOOGLE SHEETS MARKDOWN FORMATTING TEST SUITE")
    print("="*70)
    print("Testing new parse_markdown parameter in google_sheets_create()")
    print()
    
    results = []
    
    # Test 1: Markdown formatter module
    results.append(('Markdown Formatter Module', test_markdown_formatter()))
    
    # Test 2: Baseline (no markdown)
    success, result = test_sheets_create_without_markdown()
    results.append(('Create Sheet WITHOUT Markdown', success))
    
    # Test 3: With markdown
    success, result = test_sheets_create_with_markdown()
    results.append(('Create Sheet WITH Markdown', success))
    
    # Test 4: Complex scenario
    success, result = test_complex_markdown_scenario()
    results.append(('Complex Business Report', success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for name, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 SUCCESS! All markdown formatting tests passed!")
        print("\n📝 NEXT STEPS:")
        print("   1. Open the test sheet URLs above")
        print("   2. Verify formatting looks professional")
        print("   3. Compare WITH/WITHOUT markdown versions")
        print("   4. Check that colors, bold, italic all render correctly")
        print("\n✨ MARKDOWN FEATURE READY FOR PRODUCTION!")
    else:
        print(f"\n⚠️ WARNING: {total - passed} test(s) failed")
        print("   Review error messages above")
