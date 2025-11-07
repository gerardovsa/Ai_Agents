"""
Test Microsoft Word Markdown Conversion Smart Tool

Tests the new word_smart_create_from_markdown function that converts
markdown to formatted Word documents.
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

# Test markdown content
TEST_MARKDOWN = """# Q4 Sales Report 2025

## Executive Summary

Our revenue was **$2M**, representing **40% growth** over Q3. This is a *significant milestone* for our company.

## Key Performance Indicators

| Metric | Q3 2025 | Q4 2025 | Change |
|--------|---------|---------|--------|
| Revenue | $1.4M | $2M | +40% |
| Customers | 450 | 680 | +51% |
| MRR | $120K | $175K | +46% |
| Churn Rate | 3.2% | 2.1% | -34% |

## Highlights

### Product Launches
- **Enterprise Plan** - Launched October 15th
- **Mobile App** - Released November 1st
- **API v2** - Beta program started

### Team Growth
1. Hired 12 new engineers
2. Opened Austin office
3. Established customer success team

## Technical Achievements

Our engineering team delivered:

```python
# New API endpoint example
@app.route('/api/v2/analytics')
def get_analytics():
    return {
        'revenue': calculate_revenue(),
        'users': count_active_users()
    }
```

## Customer Feedback

> "The new features have transformed our workflow. We've seen a 3x improvement in productivity."
> - Sarah Chen, Director of Operations at TechCorp

## Strategic Initiatives

### Q1 2026 Goals
- Expand to European markets
- Launch partner program
- Achieve SOC 2 compliance

### Investment Priorities
1. **Product Development** - $500K budget
2. **Marketing** - $300K budget
3. **Infrastructure** - $200K budget

## Conclusion

We're positioned for continued growth with:
- Strong product-market fit
- Expanding customer base
- `Healthy unit economics`
- Talented team

---

*Report prepared by: Finance Team*
*Date: November 7, 2025*
"""

def test_tool_loading():
    """Test 1: Verify tool is loaded in registry"""
    print("\nTest 1: Tool Loading")
    print("=" * 60)
    
    registry = RegistryV3()
    
    # Check if tool exists
    tool_name = 'microsoft_word_smart_create_from_markdown'
    
    if tool_name in registry.tools:
        print(f"SUCCESS: {tool_name} found in registry")
        tool = registry.get_tool(tool_name)
        print(f"  Platform: {tool.get('platform', 'N/A')}")
        print(f"  Category: {tool.get('category', 'N/A')}")
        print(f"  Description: {tool.get('description', 'N/A')[:100]}...")
        return True
    else:
        print(f"FAILED: {tool_name} NOT found in registry")
        print(f"Available Word tools:")
        word_tools = [t for t in registry.tools.keys() if 'word' in t]
        for tool in word_tools:
            print(f"  - {tool}")
        return False


def test_schema_format():
    """Test 2: Verify schema is Anthropic-compatible"""
    print("\nTest 2: Schema Format")
    print("=" * 60)
    
    registry = RegistryV3()
    anthropic_tools = registry.get_anthropic_tools()
    
    # Find our tool
    our_tool = None
    for tool in anthropic_tools:
        if tool['name'] == 'microsoft_word_smart_create_from_markdown':
            our_tool = tool
            break
    
    if not our_tool:
        print("FAILED: Tool not found in Anthropic format")
        return False
    
    # Validate schema structure
    has_input_schema = 'input_schema' in our_tool
    has_type = our_tool.get('input_schema', {}).get('type') == 'object'
    has_props = 'properties' in our_tool.get('input_schema', {})
    has_required = 'required' in our_tool.get('input_schema', {})
    
    print(f"Has input_schema: {has_input_schema}")
    print(f"Has type='object': {has_type}")
    print(f"Has properties: {has_props}")
    print(f"Has required: {has_required}")
    
    if has_props:
        props = our_tool['input_schema']['properties']
        print(f"\nParameters ({len(props)}):")
        for prop_name in props:
            print(f"  - {prop_name}: {props[prop_name].get('type', 'unknown')}")
    
    if has_required:
        required = our_tool['input_schema']['required']
        print(f"\nRequired parameters: {required}")
    
    status = "SUCCESS" if (has_input_schema and has_type and has_props) else "FAILED"
    print(f"\n{status}: Schema format is {'valid' if status == 'SUCCESS' else 'invalid'}")
    
    return status == "SUCCESS"


def test_implementation_exists():
    """Test 3: Verify implementation exists and is callable"""
    print("\nTest 3: Implementation Check")
    print("=" * 60)
    
    try:
        from tools.implementations.microsoft_word_tools import (
            microsoft_word_smart_create_from_markdown,
            MicrosoftWordTools
        )
        
        print("SUCCESS: Import successful")
        
        # Check if method exists on class
        word_tools = MicrosoftWordTools()
        has_method = hasattr(word_tools, 'word_smart_create_from_markdown')
        print(f"Has method on class: {has_method}")
        
        # Check helper methods
        has_parse = hasattr(word_tools, '_parse_markdown_to_docx')
        has_format = hasattr(word_tools, '_add_formatted_text')
        print(f"Has _parse_markdown_to_docx: {has_parse}")
        print(f"Has _add_formatted_text: {has_format}")
        
        return has_method and has_parse and has_format
        
    except ImportError as e:
        print(f"FAILED: Import error - {e}")
        return False
    except Exception as e:
        print(f"FAILED: Unexpected error - {e}")
        return False


def test_markdown_parsing():
    """Test 4: Test markdown parsing without API call"""
    print("\nTest 4: Markdown Parsing (No API)")
    print("=" * 60)
    
    try:
        from tools.implementations.microsoft_word_tools import MicrosoftWordTools
        from docx import Document
        
        word_tools = MicrosoftWordTools()
        
        # Create document and parse markdown
        doc = Document()
        word_tools._parse_markdown_to_docx(doc, TEST_MARKDOWN)
        
        # Count elements
        num_paragraphs = len(doc.paragraphs)
        num_tables = len(doc.tables)
        
        print(f"Parsed markdown successfully")
        print(f"  Paragraphs created: {num_paragraphs}")
        print(f"  Tables created: {num_tables}")
        
        # Check for headings
        headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]
        print(f"  Headings created: {len(headings)}")
        
        # Validate we got expected structures
        has_content = num_paragraphs > 0
        has_tables = num_tables > 0
        has_headings = len(headings) > 0
        
        print(f"\nValidation:")
        print(f"  Has content: {has_content}")
        print(f"  Has tables: {has_tables}")
        print(f"  Has headings: {has_headings}")
        
        status = "SUCCESS" if (has_content and has_tables and has_headings) else "FAILED"
        print(f"\n{status}: Markdown parsing is {'working' if status == 'SUCCESS' else 'broken'}")
        
        return status == "SUCCESS"
        
    except Exception as e:
        print(f"FAILED: Error during parsing - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_python_docx_installed():
    """Test 0: Verify python-docx is installed"""
    print("\nTest 0: python-docx Installation")
    print("=" * 60)
    
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        print("SUCCESS: python-docx is installed")
        
        # Create test document
        doc = Document()
        doc.add_paragraph("Test paragraph")
        
        print("SUCCESS: Can create documents")
        return True
        
    except ImportError as e:
        print(f"FAILED: python-docx not installed - {e}")
        print("\nTo install: pip install python-docx")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Microsoft Word Markdown Conversion - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 0: python-docx installation
    results.append(("python-docx installation", test_python_docx_installed()))
    
    # Test 1: Tool loading
    results.append(("Tool loading", test_tool_loading()))
    
    # Test 2: Schema format
    results.append(("Schema format", test_schema_format()))
    
    # Test 3: Implementation exists
    results.append(("Implementation check", test_implementation_exists()))
    
    # Test 4: Markdown parsing
    results.append(("Markdown parsing", test_markdown_parsing()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nResults: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print("\nALL TESTS PASSED - Tool is ready to use!")
        print("\nNext steps:")
        print("1. Install python-docx: pip install python-docx")
        print("2. Restart AI agent server: BISTART")
        print("3. Test via API: CHAT 'Create a Word document from markdown'")
    else:
        print("\nSOME TESTS FAILED - Review errors above")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
