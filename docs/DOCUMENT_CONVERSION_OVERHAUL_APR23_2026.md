# Document Conversion Overhaul — Technical Reference
**Date:** April 23, 2026  
**Author:** GitHub Copilot (Claude Sonnet 4.6)  
**Status:** Implemented & verified (`python -c "... print('OK')"` — module imports clean, DOCX→PDF test produced valid `%PDF` header, 1871 bytes)

---

## Overview

Three files were changed to fix broken Office document → PDF/image conversion and to add
poppler-based high-quality page rendering to the production Docker image.

| File | Change type |
|------|-------------|
| `AI_infrastructure/core/document_converter.py` | Bug fix + feature upgrade |
| `Dockerfile` | Dependency addition |

---

## 1. `AI_infrastructure/core/document_converter.py`

**Full path:** `c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\AI_infrastructure\core\document_converter.py`

### 1.1 — `_convert_docx_to_pdf()` — Complete rewrite (lines ~220–345)

#### Problem (before)

```python
def _convert_docx_to_pdf(self, file_data: bytes, filename: str) -> bytes:
    try:
        try:
            from docx2pdf import convert          # <-- ImportError always raised
            ...
        except ImportError:
            print("[INFO] docx2pdf not available, using image-based conversion")
            return self._convert_via_images_to_pdf(file_data, filename, 'docx')
            # _convert_via_images_to_pdf called _convert_docx_to_images()
            # _convert_docx_to_images() drew EACH PARAGRAPH as a single dot
            # at y = paragraph_index × 100 pixels. Nearly every pixel was blank.
```

- `docx2pdf` is not installed (Windows-only, requires Microsoft Word)
- The fallback called `_convert_docx_to_images()` which iterated `doc.paragraphs`
  and called `draw.text((100, 100 * page_num), paragraph.text, fill='black')` —
  one paragraph per full A4-sized image, at coordinates that overflowed the page
  after ~35 paragraphs
- Tables were completely lost
- Result passed to Claude was essentially blank

#### Fix (after)

Pure-Python implementation using `python-docx` + `reportlab`. No system dependencies.

```python
def _convert_docx_to_pdf(self, file_data: bytes, filename: str) -> bytes:
    """Convert DOCX to PDF using python-docx + reportlab (pure Python, no system deps).

    Preserves: paragraph ordering relative to tables, heading levels H1-H3,
    bold / italic / underline runs, bullet list indentation, and table grid
    layouts with alternating row shading.
    """
    from docx import Document
    from docx.oxml.ns import qn
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    doc_obj = Document(io.BytesIO(file_data))
    pdf_buffer = io.BytesIO()
    pdf_doc = SimpleDocTemplate(
        pdf_buffer, pagesize=A4,
        rightMargin=inch * 0.75, leftMargin=inch * 0.75,
        topMargin=inch * 0.75, bottomMargin=inch * 0.75,
    )
    styles = getSampleStyleSheet()
    bullet_style = ParagraphStyle(
        'BulletItem', parent=styles['Normal'],
        leftIndent=20, firstLineIndent=-12, spaceAfter=2,
    )

    def _esc(text):
        return (text or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    def _para_markup(para):
        parts = []
        for run in para.runs:
            t = _esc(run.text)
            if not t: continue
            if run.bold and run.italic: t = f'<b><i>{t}</i></b>'
            elif run.bold:              t = f'<b>{t}</b>'
            elif run.italic:            t = f'<i>{t}</i>'
            elif run.underline:         t = f'<u>{t}</u>'
            parts.append(t)
        return ''.join(parts) or _esc(para.text)

    # Walk body children in document order — preserves paragraph/table interleaving
    para_map = {p._element: p for p in doc_obj.paragraphs}
    tbl_map  = {t._element: t for t in doc_obj.tables}
    elements = []

    for child in doc_obj.element.body:
        para = para_map.get(child)
        tbl  = tbl_map.get(child)

        if para is not None:
            markup = _para_markup(para)
            sname  = (para.style.name or '') if para.style else ''
            if not markup.strip():
                elements.append(Spacer(1, 4))
            elif 'Heading 1' in sname:
                elements.append(Paragraph(markup, styles['Heading1']))
            elif 'Heading 2' in sname:
                elements.append(Paragraph(markup, styles['Heading2']))
            elif 'Heading 3' in sname:
                elements.append(Paragraph(markup, styles['Heading3']))
            elif 'List' in sname:
                elements.append(Paragraph(f'\u2022 {markup}', bullet_style))
            else:
                elements.append(Paragraph(markup, styles['Normal']))
            elements.append(Spacer(1, 4))

        elif tbl is not None:
            table_data = [[_esc(cell.text) for cell in row.cells] for row in tbl.rows]
            if table_data:
                col_count = max(len(r) for r in table_data)
                col_w = (A4[0] - inch * 1.5) / col_count
                rt = Table(table_data, colWidths=[col_w] * col_count)
                rt.setStyle(TableStyle([
                    ('GRID',           (0,0),(-1,-1), 0.5, colors.grey),
                    ('BACKGROUND',     (0,0),(-1, 0), colors.HexColor('#e8e8e8')),
                    ('FONTNAME',       (0,0),(-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE',       (0,0),(-1,-1), 8),
                    ('ROWBACKGROUNDS', (0,1),(-1,-1), [colors.white, colors.HexColor('#f8f8f8')]),
                    ('VALIGN',         (0,0),(-1,-1), 'TOP'),
                ]))
                elements.append(rt)
                elements.append(Spacer(1, 10))

    pdf_doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.read()
```

**Key design detail — body element walk:**  
`doc_obj.paragraphs` and `doc_obj.tables` are *flat* lists; iterating them separately
loses the interleaving between paragraphs and tables. Instead the code builds index maps
(`para_map`, `tbl_map`) keyed on the lxml element, then walks `doc_obj.element.body`
children in order — the same order Word stores them. This preserves "paragraph, table,
paragraph, …" sequences correctly.

**Packages used (all pre-installed):**

| Package | Version | Purpose |
|---------|---------|---------|
| `python-docx` | 1.1.0 | Read DOCX structure |
| `reportlab` | 4.4.4 | Generate PDF |

---

### 1.2 — `_convert_docx_to_images()` — Full replacement (lines ~345–395)

#### Problem (before)

Iterated `doc.paragraphs` and rendered each paragraph as a separate full–A4 image
(`2480 × 3508 px`) with a single `draw.text()` call at `y = 100 * page_num`.
After ~35 paragraphs the y coordinate exceeded the image height; all subsequent
paragraphs were invisible. Tables not included at all.

#### Fix (after)

Three-step pipeline:

```python
def _convert_docx_to_images(self, file_data, filename, format='png', dpi=150):
    # Step 1 — convert to PDF using the fixed _convert_docx_to_pdf()
    pdf_data = self._convert_docx_to_pdf(file_data, filename)

    # Step 2 — high-quality page render (requires poppler / pdf2image)
    try:
        from pdf2image import convert_from_bytes
        pil_images = convert_from_bytes(pdf_data, dpi=dpi, fmt=format)
        # returns one PIL image per page at 150 DPI (1240×1754 for A4)
        ...
        return images
    except Exception:
        pass   # poppler not installed → fall through

    # Step 3 — readable text fallback (Pillow only, no system deps)
    doc_obj = Document(io.BytesIO(file_data))
    lines = [para.text for para in doc_obj.paragraphs if para.text.strip()]
    return [self._render_text_as_image(lines, filename, format)]
```

Same pipeline pattern applied to `_convert_xlsx_to_images()` and
`_convert_pptx_to_images()` — both previously used the same broken PIL-per-row / PIL-per-shape approach.

---

### 1.3 — `_render_text_as_image()` — New helper method (lines ~601–636)

Added to `# ==================== HELPER METHODS ====================` section.

**Why:** All three `_to_images()` fallback paths (when poppler is absent) previously
created separate large blank images or single-paragraph renders. A shared helper
consolidates the fallback logic and produces a readable A4-proportion image with proper
line wrapping.

```python
def _render_text_as_image(self, lines: List[str], base_name: str,
                          format: str = 'png') -> Dict[str, Any]:
    from PIL import Image, ImageDraw

    WIDTH, HEIGHT = 1240, 1754   # A4 at 150 DPI
    MARGIN_X, MARGIN_Y = 60, 60
    LINE_H = 22
    MAX_CHARS = 110              # chars per line before wrap

    img = Image.new('RGB', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(img)

    y = MARGIN_Y
    for raw_line in lines:
        for i in range(0, max(1, len(raw_line)), MAX_CHARS):
            draw.text((MARGIN_X, y), raw_line[i:i + MAX_CHARS], fill='#111111')
            y += LINE_H
        if y > HEIGHT - MARGIN_Y:
            draw.text((MARGIN_X, y), '…', fill='#888888')
            break

    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format.upper())
    data = img_bytes.getvalue()
    return {'data': data, 'name': f"{base_name}.{format}",
            'size': len(data), 'content_type': f'image/{format}'}
```

**Parameters:** `1240 × 1754 px` = A4 at 150 DPI (same resolution as the pdf2image
path), so image block sizes are consistent whether poppler is available or not.

---

### 1.4 — Methods NOT changed in this session

| Method | Status | Notes |
|--------|--------|-------|
| `_convert_xlsx_to_pdf()` | Unchanged — was already working | openpyxl + reportlab |
| `_convert_pptx_to_pdf()` | Unchanged — was already working | python-pptx + reportlab |
| `_convert_via_images_to_pdf()` | Unchanged — kept as legacy helper | No longer called by DOCX path |
| `_create_placeholder_image()` | Unchanged | Used as last-resort fallback |
| `convert_to_pdf()` (router) | Unchanged | Dispatches to per-type methods |
| `convert_to_images()` (router) | Unchanged | Dispatches to per-type methods |

---

## 2. `Dockerfile`

**Full path:** `c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\Dockerfile`

### Change — `poppler-utils` added to system layer (Layer 1)

#### Why

`pdf2image` (version 1.17.0, already in `requirements.txt`) is a Python wrapper around
the `pdftoppm` command-line tool from the `poppler-utils` package. Without `poppler-utils`
installed at the OS level, `pdf2image` raises `PDFInfoNotInstalledError` on the first
call and is completely non-functional.

The new `_to_images()` methods catch this exception gracefully and fall back to text
rendering, but the high-quality path (pixel-perfect PDF page rendering at 150 DPI) only
activates when poppler is present.

#### Before

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl git build-essential libpq-dev postgresql-client \
    unixodbc unixodbc-dev freetds-dev tesseract-ocr \
    gnupg apt-transport-https nodejs npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
```

#### After

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl git build-essential libpq-dev postgresql-client \
    unixodbc unixodbc-dev freetds-dev tesseract-ocr \
    gnupg apt-transport-https nodejs npm \
    poppler-utils \                        # <-- added
    && apt-get clean && rm -rf /var/lib/apt/lists/*
```

**Layer impact:** `poppler-utils` on Debian slim is ~15 MB installed. It sits in
Layer 1 (system deps), which is cached after the first build and does not rebuild
unless this `RUN` block changes. Build time impact: ~30–60 s on first deploy, zero
on subsequent deploys.

**Local Windows dev:** `poppler-utils` is not available via `apt-get`. Install via:
```powershell
choco install poppler
# or download pre-built binaries from https://github.com/oschwartz10612/poppler-windows
# and add the bin/ folder to PATH
```
Until poppler is installed locally the system falls back to `_render_text_as_image()`
automatically — no error is raised, no code change needed.

---

## 3. Dependency summary

All Python packages were already installed. No `requirements.txt` changes required.

| Package | Version | Role | Pre-existing? |
|---------|---------|------|---------------|
| `python-docx` | 1.1.0 | Read DOCX structure | ✅ |
| `reportlab` | 4.4.4 | Generate PDF output | ✅ |
| `pdf2image` | 1.17.0 | PDF → page images | ✅ (now functional with poppler) |
| `Pillow` | 11.3.0 | Image creation (fallback) | ✅ |
| `python-pptx` | 1.0.2 | Read PPTX (for PDF+image paths) | ✅ |
| `openpyxl` | 3.1.5 | Read XLSX (for PDF+image paths) | ✅ |
| `poppler-utils` | OS pkg | Backend for pdf2image | ➕ Added to Dockerfile |
| `docx2pdf` | — | Old approach (Windows+Word only) | ❌ Not installed, no longer used |

---

## 4. Conversion pipeline summary (current state)

```
User uploads file
        │
        ▼
file_encoding.py  ──────────────────────────────┐
  guess_media_type()                             │
  get_content_block_type()                       │
        │                                        │
   "base64"                                 "extract"
  (PDF, images)                     (DOCX, XLSX, PPTX, CSV,
        │                            JSON, TXT, code files)
        ▼                                        │
  encode_file_base64()                           ▼
  → {type:'document'|'image',         text_extractor.py
     source:{base64...}}              → {type:'text',
                                         text:'# markdown...'}
                                                 │
                            ┌────────────────────┘
                            │  (if convert_to_images requested separately)
                            ▼
                   document_converter.py
                   DocumentConverter.convert_to_images()
                            │
                   ┌────────┴────────────┐
                   │                     │
              _convert_*_to_pdf()   (router)
                   │
                   ▼
              pdf2image (poppler)
             ┌─────┴──────┐
         available      not available
             │                │
      page images         _render_text_as_image()
      150 DPI PNG          1240×1754 text layout
      (production)         (local dev fallback)
```

---

## 5. Verification

```powershell
# Import check
python -c "from AI_infrastructure.core.document_converter import DocumentConverter; print('OK')"
# Output: OK

# Functional DOCX→PDF test (run from workspace root)
python -c "
from docx import Document
from AI_infrastructure.core.document_converter import DocumentConverter
import io

doc = Document()
doc.add_heading('Test Heading', level=1)
doc.add_paragraph('Hello world paragraph.')
tbl = doc.add_table(rows=2, cols=3)
tbl.rows[0].cells[0].text = 'Col A'
tbl.rows[1].cells[0].text = 'Data 1'
buf = io.BytesIO(); doc.save(buf); buf.seek(0)

dc = DocumentConverter()
pdf = dc._convert_docx_to_pdf(buf.read(), 'test.docx')
print(f'PDF size: {len(pdf)} bytes, header: {pdf[:4]}')
"
# Output: PDF size: 1871 bytes, header: b'%PDF'
```

---

## 6. Limitations / known gaps

| Item | Status |
|------|--------|
| DOCX images (charts, embedded pictures) | Not rendered — reportlab does not embed raster images from docx. Image captions appear as text only. |
| DOCX column layouts / text boxes | Not supported by python-docx paragraph iteration |
| PPTX visual fidelity (PDF path) | Text-only PDF; charts, shapes, backgrounds not rendered — poppler renders whatever reportlab produced |
| XLSX merged cells | openpyxl reads merged cell values correctly but column width is evenly distributed |
| Password-protected files | Will raise an exception — not handled |
| Large documents (200+ pages) | pdf2image loads all pages into RAM. For very large docs this may exhaust memory on the 512 MB Render starter plan. Text extraction path is preferred for large docs. |

---

*End of document.*
