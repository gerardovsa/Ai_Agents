"""
Helper functions for Microsoft Word enhanced markdown tool
Based on Stack Overflow research and python-docx best practices

Features:
- Auto-generated Table of Contents with field codes
- Page numbers (center/left/right, Page X, Page X of Y)
- Professional title pages with logo support
- Centered horizontal rules
- Document metadata (author, subject, keywords)
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from datetime import datetime
import re
from typing import Dict, Optional


def add_title_page(doc: Document, options: Dict) -> None:
    """
    Add professional title page with centered content
    
    Based on enhancement plan specification:
    - Logo at top (if provided) - 2-3 inches from top
    - Main title - Large bold font (18-24pt)
    - Subtitle - Medium font (14-16pt), italic
    - Metadata section - Standard font (11-12pt)
    - Page break after
    
    Args:
        doc: python-docx Document object
        options: Dict with title_page_options parameters
    """
    # Logo (if provided)
    if options.get('logo_url'):
        try:
            logo_para = doc.add_paragraph()
            logo_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = logo_para.add_run()
            run.add_picture(options['logo_url'], width=Inches(2.5))
            logo_para.paragraph_format.space_before = Pt(72)  # 1 inch
            logo_para.paragraph_format.space_after = Pt(36)
        except Exception:
            # If logo fails, continue without it
            pass
    
    # Add vertical spacing before title
    if not options.get('logo_url'):
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_before = Pt(144)  # 2 inches
    
    # Main Title
    title_para = doc.add_paragraph(options.get('title', 'Untitled Document'))
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_para.runs[0].font.size = Pt(24)
    title_para.runs[0].font.bold = True
    title_para.paragraph_format.space_after = Pt(12)
    
    # Subtitle
    if options.get('subtitle'):
        subtitle_para = doc.add_paragraph(options['subtitle'])
        subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_para.runs[0].font.size = Pt(16)
        subtitle_para.runs[0].font.italic = True
        subtitle_para.paragraph_format.space_after = Pt(48)
    else:
        # Add spacing if no subtitle
        title_para.paragraph_format.space_after = Pt(96)
    
    # Metadata section (centered, 5 inches from top ideally)
    metadata_fields = []
    
    if options.get('author'):
        metadata_fields.append(f"Author: {options['author']}")
    
    if options.get('company'):
        metadata_fields.append(f"Company: {options['company']}")
    
    if options.get('department'):
        metadata_fields.append(f"Department: {options['department']}")
    
    if options.get('version'):
        metadata_fields.append(f"Version: {options['version']}")
    
    # Date handling
    if options.get('date'):
        if options['date'] == 'auto':
            date_str = datetime.now().strftime('%B %d, %Y')
        else:
            date_str = options['date']
        metadata_fields.append(f"Date: {date_str}")
    
    # Add metadata fields
    for field in metadata_fields:
        meta_para = doc.add_paragraph(field)
        meta_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_para.runs[0].font.size = Pt(12)
        meta_para.paragraph_format.space_after = Pt(6)
    
    # Page break after title page
    doc.add_page_break()


def add_table_of_contents(doc: Document, options: Dict) -> None:
    """
    Add auto-updating Table of Contents using Word TOC field
    
    Based on GitHub issue #36 and Stack Overflow examples:
    - Uses Word TOC field code for auto-updating
    - Supports depth 1-6 for heading levels
    - Includes "Right-click to update field" placeholder
    - Page break after TOC (optional)
    
    Args:
        doc: python-docx Document object
        options: Dict with toc_options parameters
    """
    # TOC Title
    toc_title = options.get('title', 'Table of Contents')
    title_para = doc.add_paragraph(toc_title)
    title_para.style = 'Heading 1'
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Create TOC paragraph
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    
    # Depth (1-6, default 3 for H1, H2, H3)
    depth = options.get('depth', 3)
    if depth < 1:
        depth = 1
    if depth > 6:
        depth = 6
    
    # TOC field code
    # \o "1-3" = outline levels 1-3
    # \h = hyperlinks
    # \z = hide page numbers in web layout
    # \u = use outline levels
    
    # Begin field
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)
    
    # Field instruction
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f'TOC \\o "1-{depth}" \\h \\z \\u'
    run._r.append(instrText)
    
    # Separate
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    run._r.append(fldChar2)
    
    # Placeholder text
    fldChar3 = OxmlElement('w:t')
    fldChar3.text = "Right-click to update field."
    run._r.append(fldChar3)
    
    # End field
    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar4)
    
    # Page break after TOC (if requested)
    if options.get('page_break_after', True):
        doc.add_page_break()


def add_page_numbers(doc: Document, options: Dict, exclude_first_page: bool = False) -> None:
    """
    Add page numbers to document footer
    
    Based on Stack Overflow examples:
    - Supports positions: footer-center, footer-right, footer-left, header-*
    - Formats: 'Page X', 'Page X of Y', 'X', 'X/Y'
    - Can exclude title page
    - Uses Word PAGE and NUMPAGES fields
    
    Args:
        doc: python-docx Document object
        options: Dict with page_number_options parameters
        exclude_first_page: Skip numbering on first page
    """
    # Get options
    position = options.get('position', 'footer-center')
    format_str = options.get('format', 'Page X')
    start_number = options.get('start_number', 1)
    
    # Get section
    section = doc.sections[0]
    
    # Handle different first page
    if exclude_first_page or options.get('exclude_title_page', True):
        section.different_first_page_header_footer = True
        # Set page numbering to start at 0 so page 2 shows as 1
        sectPr = section._sectPr
        pgNumType = OxmlElement('w:pgNumType')
        pgNumType.set(qn('w:start'), str(start_number - 1))
        sectPr.append(pgNumType)
    
    # Determine if header or footer
    if 'header' in position:
        container = section.header
    else:
        container = section.footer
    
    # Get or create paragraph
    if container.paragraphs:
        paragraph = container.paragraphs[0]
    else:
        paragraph = container.add_paragraph()
    
    # Set alignment
    if 'center' in position:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif 'right' in position:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Build page number field
    # Format examples:
    # 'Page X' -> 'Page ' + PAGE
    # 'Page X of Y' -> 'Page ' + PAGE + ' of ' + NUMPAGES
    # 'X' -> PAGE
    # 'X/Y' -> PAGE + '/' + NUMPAGES
    
    if format_str == 'Page X':
        # Add "Page "
        run = paragraph.add_run('Page ')
        # Add PAGE field
        _add_page_field(run)
    
    elif format_str == 'Page X of Y':
        # Add "Page "
        run = paragraph.add_run('Page ')
        # Add PAGE field
        _add_page_field(paragraph.add_run())
        # Add " of "
        run = paragraph.add_run(' of ')
        # Add NUMPAGES field
        _add_numpages_field(paragraph.add_run())
    
    elif format_str == 'X':
        # Just PAGE field
        _add_page_field(paragraph.add_run())
    
    elif format_str == 'X/Y':
        # PAGE field
        _add_page_field(paragraph.add_run())
        # Add "/"
        paragraph.add_run('/')
        # NUMPAGES field
        _add_numpages_field(paragraph.add_run())
    
    else:
        # Default to 'Page X'
        run = paragraph.add_run('Page ')
        _add_page_field(paragraph.add_run())


def _add_page_field(run):
    """Add PAGE field to run"""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    run._r.append(instrText)
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar2)


def _add_numpages_field(run):
    """Add NUMPAGES field to run"""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'NUMPAGES'
    run._r.append(instrText)
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar2)


def add_document_metadata(doc: Document, metadata: Dict) -> None:
    """
    Add document metadata (shows in file properties)
    
    Args:
        doc: python-docx Document object
        metadata: Dict with author, subject, keywords, comments
    """
    core_props = doc.core_properties
    
    if metadata.get('author'):
        core_props.author = metadata['author']
    
    if metadata.get('subject'):
        core_props.subject = metadata['subject']
    
    if metadata.get('keywords'):
        if isinstance(metadata['keywords'], list):
            core_props.keywords = ', '.join(metadata['keywords'])
        else:
            core_props.keywords = metadata['keywords']
    
    if metadata.get('comments'):
        core_props.comments = metadata['comments']


def add_headers_footers(doc: Document, header_text: Optional[str], footer_text: Optional[str],
                        header_align: str = 'left', footer_align: str = 'center') -> None:
    """
    Add custom headers and footers
    
    Args:
        doc: python-docx Document object
        header_text: Text for header
        footer_text: Text for footer
        header_align: Alignment for header ('left', 'center', 'right')
        footer_align: Alignment for footer ('left', 'center', 'right')
    """
    section = doc.sections[0]
    
    # Header
    if header_text:
        header = section.header
        if header.paragraphs:
            para = header.paragraphs[0]
        else:
            para = header.add_paragraph()
        
        para.text = header_text
        if header_align == 'center':
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif header_align == 'right':
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Footer
    if footer_text:
        footer = section.footer
        if footer.paragraphs:
            para = footer.paragraphs[0]
        else:
            para = footer.add_paragraph()
        
        para.text = footer_text
        if footer_align == 'center':
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif footer_align == 'right':
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT


def strip_manual_numbering(markdown: str, strip_enabled: bool = True) -> str:
    """
    Strip manual numbers from markdown headings to prevent double-numbering in TOC
    
    Based on enhancement plan specification:
    - Detects patterns like "# 1. Introduction" or "## 1.2 Overview"
    - Strips the number prefix, keeping just "# Introduction"
    - TOC will auto-number the headings
    
    Args:
        markdown: Markdown content
        strip_enabled: Whether to strip manual numbers (default True)
    
    Returns:
        Cleaned markdown with manual numbers removed from headings
    """
    if not strip_enabled:
        return markdown
    
    # Regex to match headings with manual numbers
    # Pattern: # (1+ spaces) (digits).(optional more digits.) (text)
    pattern = r'^(#{1,6})\s+(\d+\.)+\s+(.+)$'
    
    lines = markdown.split('\n')
    cleaned_lines = []
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            # Found heading with manual number
            hashes, numbers, title = match.group(1), match.group(2), match.group(3)
            # Reconstruct without numbers
            cleaned_lines.append(f"{hashes} {title}")
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def set_document_formatting(doc: Document, formatting_options: Dict) -> None:
    """
    Apply global document formatting options
    
    Args:
        doc: python-docx Document object
        formatting_options: Dict with formatting preferences
    """
    # Get default section
    section = doc.sections[0]
    
    # Margins (in inches)
    if 'margin_inches' in formatting_options:
        margins = formatting_options['margin_inches']
        if 'top' in margins:
            section.top_margin = Inches(margins['top'])
        if 'bottom' in margins:
            section.bottom_margin = Inches(margins['bottom'])
        if 'left' in margins:
            section.left_margin = Inches(margins['left'])
        if 'right' in margins:
            section.right_margin = Inches(margins['right'])
    
    # Font settings (applied to Normal style AND all heading styles)
    if 'default_font' in formatting_options or 'body_font_size' in formatting_options:
        # Apply to Normal style (body text)
        style = doc.styles['Normal']
        font = style.font
        
        if 'default_font' in formatting_options:
            font.name = formatting_options['default_font']
            
            # CRITICAL: Also apply same font to ALL heading styles to ensure consistency
            for i in range(1, 7):
                try:
                    heading_style = doc.styles[f'Heading {i}']
                    heading_style.font.name = formatting_options['default_font']
                    # Remove default blue color from headings
                    heading_style.font.color.rgb = RGBColor(0, 0, 0)  # Black
                except:
                    pass
        
        if 'body_font_size' in formatting_options:
            font.size = Pt(formatting_options['body_font_size'])
    
    # Line spacing (applied to Normal style)
    if 'line_spacing' in formatting_options:
        style = doc.styles['Normal']
        paragraph_format = style.paragraph_format
        paragraph_format.line_spacing = formatting_options['line_spacing']
    
    # Paragraph spacing (before/after)
    if 'paragraph_spacing_before' in formatting_options or 'paragraph_spacing_after' in formatting_options:
        style = doc.styles['Normal']
        paragraph_format = style.paragraph_format
        
        if 'paragraph_spacing_before' in formatting_options:
            paragraph_format.space_before = Pt(formatting_options['paragraph_spacing_before'])
        
        if 'paragraph_spacing_after' in formatting_options:
            paragraph_format.space_after = Pt(formatting_options['paragraph_spacing_after'])

