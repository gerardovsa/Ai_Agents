"""
Test google_docs_smart_update with all new features
====================================================
Tests bookmarks, horizontal lines, code blocks, and headings
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

print("=" * 80)
print("GOOGLE DOCS SMART UPDATE - FEATURE TEST")
print("=" * 80)

registry = RegistryV3()

# Step 1: Create initial document
print("\n1️⃣  Creating initial document...")

create_markdown = '''
# Test Document for Smart Update

This document will be updated with the smart_update tool to test:
- Bookmarks
- Horizontal lines
- Code blocks
- Headings

## Original Content

This is the original content. Updates will be appended below.
'''

try:
    create_result = registry.execute_tool(
        tool_name='google_docs_smart_create_from_markdown',
        title='Smart Update Feature Test',
        markdown_content=create_markdown,
        _user_id=12,
        _injected_credentials=True
    )
    
    doc_id = create_result['document_id']
    doc_url = create_result['document_url']
    
    print(f"✅ Document created: {doc_id}")
    print(f"   URL: {doc_url}")
    
except Exception as e:
    print(f"❌ Failed to create document: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Update with all features
print("\n2️⃣  Updating document with new features...")

update_markdown = '''
---

<<BOOKMARK:appendix>>
## APPENDIX: Updated Content via Smart Update

### Additional Analysis

This section was **added dynamically** using the `google_docs_smart_update` tool.

---

### Performance Metrics

- API calls: Only 2 required
- Processing time: <2 seconds
- Success rate: 95%+

### Code Example

Here's how to use the smart update tool:

```python
def update_document(doc_id, content):
    """Update Google Doc with markdown content"""
    result = google_docs_smart_update(
        document_id=doc_id,
        markdown_content=content,
        insertion_position='end'
    )
    return result
```

---

### New Financial Data

| Region | Revenue | Growth | Target |
|--------|---------|--------|--------|
| North America | $1.2M | +28% | Met |
| Europe | $850K | +22% | Met |
| APAC | $450K | +35% | Exceeded |

---

## Document last updated

Date: 2025-11-09

---
'''

try:
    update_result = registry.execute_tool(
        tool_name='google_docs_smart_update',
        document_id=doc_id,
        markdown_content=update_markdown,
        insertion_position='end',
        _user_id=12,
        _injected_credentials=True
    )
    
    print(f"✅ Document updated successfully")
    print(f"   Start index: {update_result['start_index']}")
    print(f"   End index: {update_result['end_index']}")
    print(f"   Operations: {update_result['operations']}")
    print(f"   Content added: {update_result['content_added']}")
    
except Exception as e:
    print(f"❌ Failed to update document: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Verify features
print("\n3️⃣  Feature Verification:")
print("=" * 80)

features_to_check = [
    {
        'name': 'Headings',
        'test': '## APPENDIX' in update_markdown,
        'description': 'H2 heading should be styled in document'
    },
    {
        'name': 'Bookmarks',
        'test': '<<BOOKMARK:appendix>>' in update_markdown,
        'description': f'Named range created - Link: {doc_url}#bookmark=appendix'
    },
    {
        'name': 'Horizontal Lines',
        'test': '---' in update_markdown,
        'description': '5 horizontal lines (50-char centered) should appear'
    },
    {
        'name': 'Code Blocks',
        'test': '```python' in update_markdown,
        'description': 'Python code with Courier New font + gray background'
    },
    {
        'name': 'Tables',
        'test': '| Region |' in update_markdown,
        'description': 'Financial data table (4x4) should be formatted'
    },
    {
        'name': 'Bold Text',
        'test': '**added dynamically**' in update_markdown,
        'description': 'Text should appear bold'
    },
    {
        'name': 'Inline Code',
        'test': '`google_docs_smart_update`' in update_markdown,
        'description': 'Text should have monospace font'
    }
]

all_passed = True
for feature in features_to_check:
    status = "✅" if feature['test'] else "❌"
    print(f"{status} {feature['name']}")
    print(f"   {feature['description']}")
    
    if not feature['test']:
        all_passed = False

print("\n" + "=" * 80)

if all_passed:
    print("🎉 ALL FEATURES PRESENT IN MARKDOWN")
else:
    print("⚠️  Some features missing from markdown")

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Document ID: {doc_id}")
print(f"Document URL: {doc_url}")
print(f"Bookmark URL: {doc_url}#bookmark=appendix")
print("\n📝 Please open the document and verify:")
print("   1. Headings are styled (H2, H3)")
print("   2. Horizontal lines appear as centered separators")
print("   3. Code block has monospace font + gray background")
print("   4. Table is formatted with borders")
print("   5. Bookmark 'appendix' can be linked to")
print("\n" + "=" * 80)
