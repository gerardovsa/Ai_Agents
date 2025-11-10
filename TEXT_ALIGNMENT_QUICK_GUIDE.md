# Google Docs Text Alignment - Quick Reference

## New Feature: Text Alignment via Markdown Syntax

**Added**: November 9, 2025  
**Works in**: `google_docs_smart_create_from_markdown`, `google_docs_smart_update`

---

## Alignment Syntax

```
<text<      → Left aligned paragraph
>text<      → Center aligned paragraph  
>text>      → Right aligned paragraph
```

---

## Examples

### Basic Alignment

```markdown
<This is left aligned<

>This is centered<

>This is right aligned>
```

### With Formatting

```markdown
<**Bold left text**<

>*Italic centered text*<

>**Bold right text**>
```

### Document Headers

```markdown
>**CONFIDENTIAL REPORT**<
>*Internal Use Only*<

---

# Document Title

Regular body text starts here...
```

### Signatures

```markdown
---

>Best regards,>
>John Smith>
>CEO, Acme Corp>
```

### Mixed Content

```markdown
# Sales Report Q4

>**EXECUTIVE SUMMARY**<

Our Q4 results exceeded expectations:

- Revenue: **$1.5M**
- Growth: **+25%**
- Customers: **520**

>*Analysis continues below*<

## Detailed Metrics

| Metric | Value | Change |
|--------|-------|--------|
| Revenue | $1.5M | +25% |
| Profit | $400K | +18% |

---

>Report generated: November 9, 2025>
>Prepared by: Finance Team>
```

---

## Rules

1. **Start and end markers must match direction**:
   - ✅ `<text<` (both point left)
   - ✅ `>text<` (points inward = center)
   - ✅ `>text>` (both point right)
   - ❌ `<text>` (mixed directions = won't work)

2. **Applies to entire paragraph**:
   - One line = one paragraph
   - Alignment affects the whole line
   - Empty lines create separate paragraphs

3. **Works with all markdown formatting**:
   - **Bold**: `>**Centered bold text**<`
   - *Italic*: `>*Centered italic*<`
   - `Code`: `><code>center code</code><`
   - Links: `>[Click here](url)<`

4. **Does NOT work with**:
   - Headings (use native Google Docs heading alignment)
   - Tables (use table column alignment)
   - Lists (use list paragraph alignment)
   - Code blocks (fixed left alignment)

---

## Visual Examples

### Left Aligned (<text<)
```
<This text is left aligned<
```
**Result**:
```
This text is left aligned
```

### Center Aligned (>text<)
```
>This text is centered<
```
**Result**:
```
        This text is centered
```

### Right Aligned (>text>)
```
>This text is right aligned>
```
**Result**:
```
                    This text is right aligned
```

---

## Common Use Cases

### 1. Document Headers
```markdown
>**QUARTERLY BUSINESS REVIEW**<
>*Q4 2024*<
>---<
```

### 2. Cover Pages
```markdown
>**COMPANY NAME**<

>Annual Report<
>2024<

---

>Prepared by: Executive Team>
>Date: December 31, 2024>
```

### 3. Section Dividers
```markdown
>---<
>**PART 2: FINANCIAL ANALYSIS**<
>---<
```

### 4. Quotes
```markdown
>"Success is not final, failure is not fatal"<
>- Winston Churchill<
```

### 5. Signatures
```markdown
>Sincerely,>

>John Smith>
>CEO>
>john@company.com>
```

---

## API Usage

### Python Example
```python
from tools.registry_v3 import RegistryV3
registry = RegistryV3()

markdown = '''
>**PROJECT PROPOSAL**<
>*Confidential*<

# Overview

This proposal outlines our Q1 initiative.

## Goals

1. Increase revenue by 20%
2. Launch new product line
3. Expand to 3 new markets

---

>Submitted by: Product Team>
>Date: November 9, 2025>
'''

result = registry.execute_tool(
    tool_name='google_docs_smart_create_from_markdown',
    title='Q1 Project Proposal',
    markdown_content=markdown,
    _user_id=12,
    _injected_credentials=True
)

print(f"Created: {result['document_url']}")
```

### JavaScript Example
```javascript
const markdown = `
>**MEETING NOTES**<
>*Board Meeting - November 9, 2025*<

# Attendees

- John Smith (CEO)
- Jane Doe (CFO)
- Bob Johnson (CTO)

# Decisions

1. Approved Q1 budget
2. Hired 5 new engineers
3. Launched marketing campaign

---

>Next meeting: December 15, 2025>
`;

const result = await executeAITool({
  tool_name: 'google_docs_smart_create_from_markdown',
  title: 'Board Meeting Notes',
  markdown_content: markdown
});

console.log(`Created: ${result.document_url}`);
```

---

## Comparison with Other Tools

| Tool | Text Alignment Support |
|------|------------------------|
| **Smart Create (API)** | ✅ <text<, >text<, >text> |
| **Smart Update (API)** | ✅ <text<, >text<, >text> |
| **DOCX V2 (Conversion)** | ❌ Not supported (yet) |
| **Standard Create** | ❌ No markdown support |

---

## Tips & Best Practices

### DO:
- ✅ Use alignment for visual hierarchy
- ✅ Center headers and titles
- ✅ Right-align signatures and dates
- ✅ Keep alignment syntax on its own line
- ✅ Combine with other markdown formatting

### DON'T:
- ❌ Mix alignment markers (e.g., `<text>`)
- ❌ Try to align tables (use table alignment instead)
- ❌ Forget the closing marker
- ❌ Use alignment for long paragraphs (reduces readability)
- ❌ Overuse center/right alignment (mostly left is best)

---

## Troubleshooting

### Alignment Not Working?

**Check**:
1. Start and end markers match the pattern?
   - Left: `<text<`
   - Center: `>text<`
   - Right: `>text>`

2. Syntax on its own line?
   ```markdown
   # Good
   >Centered text<
   
   # Bad (won't work)
   This is normal text >with centered part< in the middle
   ```

3. Using correct tool?
   - ✅ `google_docs_smart_create_from_markdown`
   - ✅ `google_docs_smart_update`
   - ❌ `google_docs_smart_create_from_markdown_v2` (not supported)

4. Flask server restarted?
   - Run `BISTART` to load updated code

---

## Testing Your Alignment

**Quick Test**:
```python
test_markdown = '''
<Left aligned text<

>Center aligned text<

>Right aligned text>

Regular text (default left)
'''

result = registry.execute_tool(
    tool_name='google_docs_smart_create_from_markdown',
    title='Alignment Test',
    markdown_content=test_markdown,
    _user_id=12,
    _injected_credentials=True
)

# Open document and verify:
# - Line 1: Left aligned
# - Line 2: Center aligned  
# - Line 3: Right aligned
# - Line 4: Left aligned (default)
```

---

## FAQ

**Q: Can I align headings?**  
A: No, use Google Docs native heading alignment instead. This syntax is for regular paragraphs.

**Q: Can I mix alignment with other markdown?**  
A: Yes! Example: `>**Bold centered text**<`

**Q: What if I forget the closing marker?**  
A: The text will be treated as literal (< and > will appear in document).

**Q: Can I align multiple lines at once?**  
A: No, each line needs its own alignment markers. Each line is a separate paragraph.

**Q: Does this work in DOCX v2?**  
A: Not yet. Currently only in Smart Create/Update (API-based methods).

**Q: Can I left-align without markers?**  
A: Yes, left is the default. Only use `<text<` if you want to explicitly show it's left-aligned.

---

## Summary

**Syntax**:
- `<text<` = Left
- `>text<` = Center
- `>text>` = Right

**Works in**:
- `google_docs_smart_create_from_markdown` ✅
- `google_docs_smart_update` ✅

**Best for**:
- Headers, titles, signatures
- Visual hierarchy
- Professional document layout

**Simple, intuitive, powerful!**

---

*Last Updated: November 9, 2025*  
*Feature Added: Text Alignment via Markdown Syntax*
