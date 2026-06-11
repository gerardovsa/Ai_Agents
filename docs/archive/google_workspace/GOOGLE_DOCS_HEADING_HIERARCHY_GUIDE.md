# Google Docs Heading Hierarchy Quick Reference

## Visual Guide - Heading Sizes & Usage

```
# H1 - Main Document Title
Large, bold, black. Used for document title or top-level sections only.

## H2 - Major Section Title  
Large, bold, black. Use for main content sections within document.

### H3 - Sub-Section Title
Medium, bold, black. Use for subdivisions under H2 sections.

#### H4 - List Section Title (11pt, Bold, Black)
Body text size with bold emphasis. Use ONLY for titles directly above bulleted/numbered lists.
    • This is what H4 looks like
    • Same font size as body text
    • But bold for emphasis

##### H5 - Rarely Used
Small, bold, black. Avoid in most documents.

###### H6 - Rarely Used
Smallest, bold, black. Avoid in most documents.
```

---

## Usage Matrix

### When to Use Each Heading

#### Use H1 (#) For:
- ✅ Document title
- ✅ Report name
- ✅ Top-level content divisions
- ❌ NOT for list titles
- ❌ NOT for section headers (use H2)

#### Use H2 (##) For:
- ✅ Main section titles (Introduction, Findings, Conclusion, etc.)
- ✅ Chapter titles
- ✅ Major report sections
- ❌ NOT for list titles (use H4)
- ❌ NOT for sub-sections (use H3)

#### Use H3 (###) For:
- ✅ Sub-section titles under H2 sections
- ✅ Nested content divisions
- ✅ Supporting topic headers
- ❌ NOT for list titles (use H4)

#### Use H4 (####) For:
- ✅ **ONLY** titles directly above bulleted lists
- ✅ **ONLY** titles directly above numbered lists
- ❌ NEVER for regular paragraph sections (use H2/H3)
- ❌ NEVER for document structure (use H1-H3)
- ✅ Is 11pt bold (body text size with emphasis)

#### Use H5 (#####) and H6 (######) For:
- ❌ Rarely use - avoid in most documents
- ⚠️  Only if you have deeply nested content

---

## Correct vs Incorrect Examples

### ✅ CORRECT Pattern

```markdown
# Quarterly Financial Report

## Revenue Analysis
This section covers our revenue trends for Q1 2025.

#### Top Products
- Product A: $150K
- Product B: $120K
- Product C: $95K

More analysis text here discussing the products above.

#### By Region
1. North America: $200K
2. Europe: $180K
3. Asia Pacific: $165K

Regional expansion opportunities outlined below.

## Expense Management
This section analyzes our operational costs.

#### Major Expense Categories
- Salaries and Benefits
- Infrastructure Costs
- Marketing and Sales

### Conclusion
Final summary here.
```

### ❌ INCORRECT Patterns

```markdown
# Quarterly Financial Report

## Revenue Analysis

### Top Products        ← WRONG! H3 should not be list title, use H4
- Product A
- Product B

---

# Main Title
# Another H1         ← WRONG! Should be H2 or H3
- List item
- List item

---

## Section

#### List Title       ← CORRECT H4 for list
- Item 1

#### Another H4       ← WRONG! Not directly above a list
This is body text that doesn't have a list below it.
```

---

## Formatting Applied Automatically

| Element | Format | Details |
|---------|--------|---------|
| **All headings** | Black color | Never colored (even if hex code provided) |
| **H1** | Named Style | Google Docs default H1 size |
| **H2** | Named Style | Google Docs default H2 size |
| **H3** | Named Style | Google Docs default H3 size |
| **H4** | 11pt + Bold + Black | Special formatting (not default H4) |
| **Lists** | 5 PT spacing above first item | Minimal, clean spacing |
| **Body text** | Normal | Default document style |

---

## Real-World Example

### Input Markdown:
```markdown
# Q1 2025 Performance Dashboard

## Sales Overview
Our sales performance exceeded targets in Q1 2025 with strong growth across all regions.

#### Monthly Sales Figures
- January: $450K
- February: $520K
- March: $580K

This growth was driven by new product launches and expanded marketing efforts.

#### Regional Performance
1. North America: 45% of total sales
2. Europe: 35% of total sales
3. Asia Pacific: 20% of total sales

### Expense Analysis
Operational costs remained stable despite increased headcount.

#### Key Expense Items
- Personnel: $380K
- Infrastructure: $120K
- Marketing: $85K

## Strategic Initiatives
Three main initiatives drove our Q1 performance.

## Conclusion
Q1 2025 represents strong progress toward our annual targets.
```

### Output Format:
- **H1**: "Q1 2025 Performance Dashboard" - Large, bold, black
- **H2**: "Sales Overview", "Expense Analysis", "Strategic Initiatives" - Large, bold, black
- **H3**: (None in example) - Would be sub-sections under H2
- **H4**: "Monthly Sales Figures", "Regional Performance", "Key Expense Items" - **11pt bold, black** (body text size with emphasis)
- **Lists**: Minimal 5 PT spacing above first item, compact between items
- **Body text**: Normal paragraph formatting

---

## Key Takeaways

1. **H1, H2, H3**: For document structure and organization
2. **H4 ONLY**: For list section titles (nowhere else!)
3. **H4 Special**: 11pt bold (same size as body text but emphasized)
4. **All black**: Headings never colored
5. **Pattern**: Section heading → content → (H4 if list follows) → list → more content

---

**Last Updated**: November 4, 2025
**Version**: 2.0 (H4 = 11pt bold for list titles)
