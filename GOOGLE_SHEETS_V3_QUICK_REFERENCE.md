# Google Sheets Markdown v3.0 - Quick Reference Card 📋

## 🎨 Text Formatting

| Syntax | Result |
|--------|--------|
| `**bold**` | **Bold** |
| `*italic*` | *Italic* |
| `~~strike~~` | ~~Strike~~ |
| `__underline__` | <u>Underline</u> |
| `# Header` | 18pt bold + gray bg |
| `## Header` | 16pt bold + gray bg |
| `[SIZE:20]text` | Custom 20pt |

## 💰 Number Formatting

| Syntax | Input | Output |
|--------|-------|--------|
| `[$]` | `[$]1500` | $1,500.00 |
| `[%]` | `[%]15` | 15.00% |
| `[#]` | `[#]1234.5` | 1,234.50 |
| `[INT]` | `[INT]9876` | 9,876 |
| `[DATE]` | `[DATE]2025-12-16` | Dec 16, 2025 |

## 🎨 Colors

| Text | Background |
|------|------------|
| `[R]text` | `{LR}text` |
| `[G]text` | `{LG}text` |
| `[B]text` | `{LB}text` |
| `[P]text` | `{LP}text` |
| `[GR]text` | `{LGR}text` |

## 📐 Alignment

| Syntax | Result |
|--------|--------|
| `(L)text` | Left |
| `(C)text` | Center |
| `(R)text` | Right |

## 🔧 Advanced

| Feature | Syntax | Example |
|---------|--------|---------|
| **Merge** | `[MERGE:3]text` | Span 3 cells |
| **Wrap** | `[WRAP]text` | Text wraps |
| **No Wrap** | `[NOWRAP]text` | Overflow |
| **Dropdown** | `[DROPDOWN:A,B]A` | Select from list |
| **Conditional** | `[IF>100:RED]125` | Red if >100 |

## ⚡ Usage

```python
# Enable v3.0 features
google_sheets_create(
    title="My Report",
    headers=["# Name", "**Price**", "**Status**"],
    data=[
        ["Product A", "[$]1500", "[IF>1000:GREEN]1500"],
        ["Product B", "[$]800", "[DROPDOWN:Active,Inactive]Active"]
    ],
    parse_markdown=True,
    auto_resize_columns=True  # Auto-size!
)
```

## 🎯 Pro Tips

✅ **Combine features**: `(R)[$]1500` = Right-aligned currency  
✅ **Merge headers**: `[MERGE:3]Q4 Report` for section titles  
✅ **Use dropdowns**: Better than free-text data entry  
✅ **Conditional colors**: Instant visual insights  
✅ **Auto-resize**: Let AI calculate perfect widths  

## 📚 Full Docs

See `GOOGLE_SHEETS_FORMATTER_V3_COMPLETE.md` for complete guide
