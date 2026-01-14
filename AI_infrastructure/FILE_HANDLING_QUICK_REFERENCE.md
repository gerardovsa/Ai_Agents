# 📄 File Handling Quick Reference

## TL;DR

**Smart two-tier strategy**: Try PDF (visual analysis) → fall back to markdown (efficiency) automatically.

## Quick Decision Tree

```
Office Document Upload
    ├─ Small (<100KB spreadsheet or <500KB doc)
    │   ├─ Try PDF conversion
    │   ├─ Check token estimate
    │   └─ If >2000 tokens → Use markdown ✅
    │
    └─ Large (>100KB spreadsheet or >500KB doc)
        └─ Extract to markdown immediately ✅
```

## Token Costs

| File Type | Method | Cost | Best For |
|-----------|--------|------|----------|
| 1-page DOCX | PDF | 3,000 tokens | Documents with images/charts |
| 1-page DOCX | Markdown | ~50 tokens | Text-only documents |
| 10-page PDF | PDF | 30,000 tokens | Visual presentations |
| 100-row spreadsheet | PDF | 3,000 tokens | Simple tables |
| 500-row spreadsheet | Markdown | ~10,000 tokens | Large datasets |
| PNG image (2MB) | Direct | 1,600 tokens | All images |

## API Usage

### Default (Smart Auto)
```javascript
formData.append('session_id', 'session-123');
formData.append('files', file);
// Auto: PDF first, markdown fallback
```

### Force Markdown (Efficient)
```javascript
formData.append('convert_pref', 'extract');
// Always markdown, skip visual
```

### Force PDF (Visual)
```javascript
formData.append('convert_pref', 'pdf');
// PDF preferred, still falls back if >2000 tokens
```

## When to Use What

✅ **Use PDF (auto/pdf mode):**
- Documents with important images, charts, diagrams
- Presentations with visual layouts
- Small spreadsheets with formatting

✅ **Use Markdown (extract mode):**
- Large spreadsheets (>100KB)
- Text-heavy documents (>500KB)
- Data reports without visuals
- When token budget is limited

## Response Check

```javascript
const response = await fetch('/api/chat/upload', {...});
const result = await response.json();

if (result.success) {
  result.files.forEach(file => {
    console.log(`Method: ${file.method}`);  // 'convert_pdf' or 'extract'
    console.log(`Tokens: ${file.metadata.token_estimate}`);
    
    if (file.content.type === 'document') {
      console.log('✅ PDF - Visual analysis available');
    } else if (file.content.type === 'text') {
      console.log('✅ Markdown - Text extracted');
    }
  });
}
```

## Troubleshooting

**"My file was converted to markdown instead of PDF"**
- Check file size: >100KB spreadsheet or >500KB doc triggers markdown
- Check console: Token estimate >2000 triggers fallback
- This is **correct behavior** - saving you tokens!

**"I want to force PDF even for large files"**
```javascript
formData.append('convert_pref', 'pdf');
// Will still fall back if >2000 tokens
```

**"I always want markdown, never PDF"**
```javascript
formData.append('convert_pref', 'extract');
// Always extracts text, never converts
```

## Size Thresholds

| Threshold | Trigger | Action |
|-----------|---------|--------|
| >100KB | Spreadsheet (XLSX/CSV) | Extract to markdown |
| >500KB | Document (DOCX/PPTX) | Extract to markdown |
| >2000 tokens | Post-conversion check | Retry with markdown |
| >32MB | Request size limit | Use Files API (future) |

---

**See Also:** `FILE_HANDLING_TWO_TIER_STRATEGY.md` for full documentation
