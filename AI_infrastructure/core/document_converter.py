"""
DOCUMENT CONVERTER - Convert Office Documents to PDF/Images
============================================================

Converts DOCX, XLSX, PPTX, and other documents to PDF or images for visual
processing by AI models. Provides multiple conversion strategies:

1. **PDF Conversion**: Convert documents to PDF (preserves formatting)
2. **Image Conversion**: Convert documents/pages to images (visual analysis)
3. **Hybrid Mode**: Extract text + generate image/PDF for dual processing

Supported Input Types:
- DOCX, DOC → PDF or Images
- XLSX, XLS → PDF or Images (per sheet)
- PPTX, PPT → PDF or Images (per slide)
- CSV → PDF table
- Any document → PDF or PNG/JPEG

Output Formats:
- PDF (single or multi-page)
- PNG images (high resolution)
- JPEG images (compressed)

Usage:
    from AI_infrastructure.core.document_converter import DocumentConverter
    
    converter = DocumentConverter()
    
    # Convert DOCX to PDF
    result = converter.convert_to_pdf(
        file_data=docx_bytes,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename='document.docx'
    )
    
    # Convert XLSX to images (one per sheet)
    result = converter.convert_to_images(
        file_data=xlsx_bytes,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename='spreadsheet.xlsx',
        format='png'
    )
    
    # Returns:
    {
        'success': True,
        'format': 'pdf' | 'png' | 'jpeg',
        'files': [
            {'data': bytes, 'name': 'document.pdf', 'size': 12345},
            {'data': bytes, 'name': 'sheet1.png', 'size': 45678}
        ],
        'metadata': {
            'original_filename': 'document.docx',
            'pages': 5,
            'conversion_method': 'docx2pdf'
        }
    }
"""

import io
import os
import tempfile
from typing import Dict, Any, List, Optional, Union, Literal
from pathlib import Path


class DocumentConverterError(Exception):
    """Custom exception for document conversion errors"""
    pass


class DocumentConverter:
    """
    Convert office documents to PDF or images for AI visual processing
    """
    
    # Supported input types
    DOCX_TYPES = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    ]
    
    XLSX_TYPES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/csv'
    ]
    
    PPTX_TYPES = [
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint'
    ]
    
    
    def __init__(self):
        """Initialize document converter"""
        self.conversion_methods = {
            'docx_to_pdf': self._convert_docx_to_pdf,
            'xlsx_to_pdf': self._convert_xlsx_to_pdf,
            'pptx_to_pdf': self._convert_pptx_to_pdf,
            'docx_to_images': self._convert_docx_to_images,
            'xlsx_to_images': self._convert_xlsx_to_images,
            'pptx_to_images': self._convert_pptx_to_images
        }
    
    
    def convert_to_pdf(self,
                      file_data: bytes,
                      content_type: str,
                      filename: str) -> Dict[str, Any]:
        """
        Convert document to PDF format
        
        Args:
            file_data: Raw file bytes
            content_type: MIME type
            filename: Original filename
        
        Returns:
            Conversion result with PDF bytes
        """
        try:
            # Determine conversion method
            if content_type in self.DOCX_TYPES:
                method = self._convert_docx_to_pdf
            elif content_type in self.XLSX_TYPES:
                method = self._convert_xlsx_to_pdf
            elif content_type in self.PPTX_TYPES:
                method = self._convert_pptx_to_pdf
            else:
                return {
                    'success': False,
                    'error': f'PDF conversion not supported for {content_type}'
                }
            
            # Convert to PDF
            pdf_data = method(file_data, filename)
            
            return {
                'success': True,
                'format': 'pdf',
                'files': [{
                    'data': pdf_data,
                    'name': filename.rsplit('.', 1)[0] + '.pdf',
                    'size': len(pdf_data),
                    'content_type': 'application/pdf'
                }],
                'metadata': {
                    'original_filename': filename,
                    'original_type': content_type,
                    'conversion_method': method.__name__
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF conversion failed: {str(e)}'
            }
    
    
    def convert_to_images(self,
                         file_data: bytes,
                         content_type: str,
                         filename: str,
                         format: Literal['png', 'jpeg'] = 'png',
                         dpi: int = 150) -> Dict[str, Any]:
        """
        Convert document to images (one per page/sheet/slide)
        
        Args:
            file_data: Raw file bytes
            content_type: MIME type
            filename: Original filename
            format: Output format ('png' or 'jpeg')
            dpi: Resolution (default: 150)
        
        Returns:
            Conversion result with image bytes list
        """
        try:
            # Determine conversion method
            if content_type in self.DOCX_TYPES:
                method = self._convert_docx_to_images
            elif content_type in self.XLSX_TYPES:
                method = self._convert_xlsx_to_images
            elif content_type in self.PPTX_TYPES:
                method = self._convert_pptx_to_images
            else:
                return {
                    'success': False,
                    'error': f'Image conversion not supported for {content_type}'
                }
            
            # Convert to images
            images = method(file_data, filename, format, dpi)
            
            return {
                'success': True,
                'format': format,
                'files': images,
                'metadata': {
                    'original_filename': filename,
                    'original_type': content_type,
                    'image_count': len(images),
                    'dpi': dpi,
                    'conversion_method': method.__name__
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image conversion failed: {str(e)}'
            }
    
    
    # ==================== DOCX CONVERSION METHODS ====================
    
    def _convert_docx_to_pdf(self, file_data: bytes, filename: str) -> bytes:
        """Convert DOCX to PDF using python-docx + reportlab (pure Python, no system deps).

        Preserves: paragraph ordering relative to tables, heading levels H1-H3,
        bold / italic / underline runs, bullet list indentation, and table grid
        layouts with alternating row shading.
        """
        try:
            from docx import Document
            from docx.oxml.ns import qn
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer,
                Table, TableStyle,
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

            def _esc(text: str) -> str:
                return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            def _para_markup(para) -> str:
                """Convert paragraph runs to reportlab XML markup string."""
                parts = []
                for run in para.runs:
                    t = _esc(run.text)
                    if not t:
                        continue
                    if run.bold and run.italic:
                        t = f'<b><i>{t}</i></b>'
                    elif run.bold:
                        t = f'<b>{t}</b>'
                    elif run.italic:
                        t = f'<i>{t}</i>'
                    elif run.underline:
                        t = f'<u>{t}</u>'
                    parts.append(t)
                return ''.join(parts) or _esc(para.text)

            # Index top-level paragraphs and tables by their lxml element so we
            # can walk body children in document order and preserve interleaving.
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
                        elements.append(Spacer(1, 6))
                    elif 'Heading 2' in sname:
                        elements.append(Paragraph(markup, styles['Heading2']))
                        elements.append(Spacer(1, 4))
                    elif 'Heading 3' in sname:
                        elements.append(Paragraph(markup, styles['Heading3']))
                        elements.append(Spacer(1, 4))
                    elif 'List' in sname:
                        elements.append(Paragraph(f'\u2022 {markup}', bullet_style))
                    else:
                        elements.append(Paragraph(markup, styles['Normal']))
                        elements.append(Spacer(1, 4))

                elif tbl is not None:
                    table_data = [
                        [_esc(cell.text or '') for cell in row.cells]
                        for row in tbl.rows
                    ]
                    if table_data:
                        col_count = max(len(r) for r in table_data)
                        avail_w   = A4[0] - inch * 1.5
                        col_w     = avail_w / col_count if col_count else avail_w

                        rt = Table(table_data, colWidths=[col_w] * col_count)
                        rt.setStyle(TableStyle([
                            ('GRID',         (0, 0), (-1, -1), 0.5, colors.grey),
                            ('BACKGROUND',   (0, 0), (-1,  0), colors.HexColor('#e8e8e8')),
                            ('FONTNAME',     (0, 0), (-1,  0), 'Helvetica-Bold'),
                            ('FONTSIZE',     (0, 0), (-1, -1), 8),
                            ('TOPPADDING',   (0, 0), (-1, -1), 4),
                            ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
                            ('LEFTPADDING',  (0, 0), (-1, -1), 5),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                             [colors.white, colors.HexColor('#f8f8f8')]),
                            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
                        ]))
                        elements.append(rt)
                        elements.append(Spacer(1, 10))

            if not elements:
                elements.append(Paragraph(
                    f'[Empty document: {_esc(filename)}]', styles['Normal']
                ))

            pdf_doc.build(elements)
            pdf_buffer.seek(0)
            return pdf_buffer.read()

        except Exception as e:
            raise DocumentConverterError(f'DOCX to PDF conversion failed: {str(e)}')
    
    
    def _convert_docx_to_images(self,
                               file_data: bytes,
                               filename: str,
                               format: str = 'png',
                               dpi: int = 150) -> List[Dict[str, Any]]:
        """Convert DOCX to images (one per page).

        Pipeline: DOCX → PDF (via _convert_docx_to_pdf) → page images via
        pdf2image/poppler.  Falls back to a readable single-image text render
        when poppler is not available.
        """
        try:
            # Step 1: convert to PDF using our python-docx+reportlab converter
            pdf_data = self._convert_docx_to_pdf(file_data, filename)

            # Step 2: attempt high-quality page images via pdf2image (needs poppler)
            try:
                from pdf2image import convert_from_bytes
                pil_images = convert_from_bytes(pdf_data, dpi=dpi, fmt=format)
                images = []
                for i, pil_img in enumerate(pil_images, 1):
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format=format.upper())
                    data = img_bytes.getvalue()
                    images.append({
                        'data': data,
                        'name': f"{filename.rsplit('.', 1)[0]}_page{i}.{format}",
                        'size': len(data),
                        'content_type': f'image/{format}',
                    })
                return images or [self._create_placeholder_image(filename, format)]
            except Exception:
                # pdf2image / poppler not available – fall through to text render
                pass

            # Step 3: plain-text fallback – one image with all body text
            from docx import Document
            from PIL import Image, ImageDraw

            doc_obj = Document(io.BytesIO(file_data))
            lines: List[str] = []
            for para in doc_obj.paragraphs:
                if para.text.strip():
                    lines.append(para.text)

            return [self._render_text_as_image(lines, filename, format)]

        except Exception as e:
            raise DocumentConverterError(f'DOCX to images conversion failed: {str(e)}')
    
    
    # ==================== XLSX CONVERSION METHODS ====================
    
    def _convert_xlsx_to_pdf(self, file_data: bytes, filename: str) -> bytes:
        """Convert XLSX to PDF"""
        try:
            from openpyxl import load_workbook
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            wb = load_workbook(io.BytesIO(file_data), data_only=True)
            
            # Create PDF
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Process each sheet
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                
                # Add sheet title
                elements.append(Paragraph(f"<b>{sheet_name}</b>", styles['Heading1']))
                elements.append(Spacer(1, 12))
                
                # Extract data
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append([str(cell) if cell is not None else '' for cell in row])
                
                if data:
                    # Create table
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(table)
                    elements.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            
            return pdf_buffer.read()
            
        except Exception as e:
            raise DocumentConverterError(f'XLSX to PDF conversion failed: {str(e)}')
    
    
    def _convert_xlsx_to_images(self,
                               file_data: bytes,
                               filename: str,
                               format: str = 'png',
                               dpi: int = 150) -> List[Dict[str, Any]]:
        """Convert XLSX to images (one per sheet).

        Pipeline: XLSX → PDF (via _convert_xlsx_to_pdf) → page images via
        pdf2image/poppler.  Fallback: text-based image render per sheet.
        """
        try:
            pdf_data = self._convert_xlsx_to_pdf(file_data, filename)

            try:
                from pdf2image import convert_from_bytes
                pil_images = convert_from_bytes(pdf_data, dpi=dpi, fmt=format)
                images = []
                for i, pil_img in enumerate(pil_images, 1):
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format=format.upper())
                    data = img_bytes.getvalue()
                    images.append({
                        'data': data,
                        'name': f"{filename.rsplit('.', 1)[0]}_page{i}.{format}",
                        'size': len(data),
                        'content_type': f'image/{format}',
                    })
                return images or [self._create_placeholder_image(filename, format)]
            except Exception:
                pass

            # Fallback: per-sheet text image
            from openpyxl import load_workbook

            wb = load_workbook(io.BytesIO(file_data), data_only=True)
            images = []
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                lines = [sheet_name]
                for row in sheet.iter_rows(values_only=True):
                    row_text = '  |  '.join(str(c) if c is not None else '' for c in row)
                    if row_text.strip('  |  '):
                        lines.append(row_text)
                base = f"{filename.rsplit('.', 1)[0]}_{sheet_name}"
                images.append(self._render_text_as_image(lines, base, format))
            return images or [self._create_placeholder_image(filename, format)]

        except Exception as e:
            raise DocumentConverterError(f'XLSX to images conversion failed: {str(e)}')
    
    
    # ==================== PPTX CONVERSION METHODS ====================
    
    def _convert_pptx_to_pdf(self, file_data: bytes, filename: str) -> bytes:
        """Convert PPTX to PDF"""
        try:
            from pptx import Presentation
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            
            prs = Presentation(io.BytesIO(file_data))
            
            # Create PDF
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Process each slide
            for slide_num, slide in enumerate(prs.slides, 1):
                # Add slide number
                elements.append(Paragraph(f"<b>Slide {slide_num}</b>", styles['Heading1']))
                elements.append(Spacer(1, 12))
                
                # Extract text from shapes
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        elements.append(Paragraph(shape.text, styles['Normal']))
                        elements.append(Spacer(1, 6))
                
                # Page break between slides
                if slide_num < len(prs.slides):
                    elements.append(PageBreak())
            
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
            
            return pdf_buffer.read()
            
        except Exception as e:
            raise DocumentConverterError(f'PPTX to PDF conversion failed: {str(e)}')
    
    
    def _convert_pptx_to_images(self,
                               file_data: bytes,
                               filename: str,
                               format: str = 'png',
                               dpi: int = 150) -> List[Dict[str, Any]]:
        """Convert PPTX to images (one per slide).

        Pipeline: PPTX → PDF (via _convert_pptx_to_pdf) → page images via
        pdf2image/poppler.  Fallback: per-slide text image.
        """
        try:
            pdf_data = self._convert_pptx_to_pdf(file_data, filename)

            try:
                from pdf2image import convert_from_bytes
                pil_images = convert_from_bytes(pdf_data, dpi=dpi, fmt=format)
                images = []
                for i, pil_img in enumerate(pil_images, 1):
                    img_bytes = io.BytesIO()
                    pil_img.save(img_bytes, format=format.upper())
                    data = img_bytes.getvalue()
                    images.append({
                        'data': data,
                        'name': f"{filename.rsplit('.', 1)[0]}_slide{i}.{format}",
                        'size': len(data),
                        'content_type': f'image/{format}',
                    })
                return images or [self._create_placeholder_image(filename, format)]
            except Exception:
                pass

            # Fallback: per-slide text image
            from pptx import Presentation

            prs = Presentation(io.BytesIO(file_data))
            images = []
            for slide_num, slide in enumerate(prs.slides, 1):
                lines = [f'Slide {slide_num}']
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        lines.append(shape.text)
                base = f"{filename.rsplit('.', 1)[0]}_slide{slide_num}"
                images.append(self._render_text_as_image(lines, base, format))
            return images or [self._create_placeholder_image(filename, format)]

        except Exception as e:
            raise DocumentConverterError(f'PPTX to images conversion failed: {str(e)}')
    
    
    # ==================== HELPER METHODS ====================

    def _render_text_as_image(self,
                              lines: List[str],
                              base_name: str,
                              format: str = 'png') -> Dict[str, Any]:
        """Render a list of text lines as a clean A4-sized image (fallback renderer)."""
        from PIL import Image, ImageDraw

        WIDTH, HEIGHT = 1240, 1754   # A4 at 150 DPI
        MARGIN_X, MARGIN_Y = 60, 60
        LINE_H = 22
        MAX_CHARS = 110

        img = Image.new('RGB', (WIDTH, HEIGHT), 'white')
        draw = ImageDraw.Draw(img)

        y = MARGIN_Y
        for raw_line in lines:
            # Wrap long lines
            for i in range(0, max(1, len(raw_line)), MAX_CHARS):
                segment = raw_line[i:i + MAX_CHARS]
                draw.text((MARGIN_X, y), segment, fill='#111111')
                y += LINE_H
            if y > HEIGHT - MARGIN_Y:
                draw.text((MARGIN_X, y), '…', fill='#888888')
                break

        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format.upper())
        data = img_bytes.getvalue()
        return {
            'data': data,
            'name': f"{base_name}.{format}",
            'size': len(data),
            'content_type': f'image/{format}',
        }

    def _create_placeholder_image(self, filename: str, format: str = 'png') -> Dict[str, Any]:
        """Create placeholder image if conversion fails"""
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        draw.text((100, 250), f"Document: {filename}", fill='black')
        draw.text((100, 300), "(Conversion preview unavailable)", fill='gray')
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format.upper())
        img_bytes.seek(0)
        
        return {
            'data': img_bytes.read(),
            'name': f"{filename.rsplit('.', 1)[0]}_placeholder.{format}",
            'size': img_bytes.tell(),
            'content_type': f'image/{format}'
        }
    
    
    def _convert_via_images_to_pdf(self,
                                   file_data: bytes,
                                   filename: str,
                                   doc_type: str) -> bytes:
        """Fallback: Convert document to images, then combine into PDF"""
        from PIL import Image
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak
        
        # Get images first
        images = self._convert_docx_to_images(file_data, filename, 'png', 150)
        
        # Create PDF from images
        pdf_buffer = io.BytesIO()
        
        # Use A4 page size with margins
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        elements = []
        page_width, page_height = A4
        max_width = page_width - 72  # Account for margins
        max_height = page_height - 72
        
        for idx, img_data in enumerate(images):
            # Load image to get dimensions
            img_pil = Image.open(io.BytesIO(img_data['data']))
            img_width, img_height = img_pil.size
            
            # Calculate scaling to fit page while preserving aspect ratio
            width_scale = max_width / img_width
            height_scale = max_height / img_height
            scale = min(width_scale, height_scale, 1.0)  # Don't upscale
            
            # Calculate final dimensions
            final_width = img_width * scale
            final_height = img_height * scale
            
            # Add image
            img_bytes = io.BytesIO(img_data['data'])
            elements.append(RLImage(img_bytes, width=final_width, height=final_height))
            
            # Add page break between images
            if idx < len(images) - 1:
                elements.append(PageBreak())
        
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return pdf_buffer.read()


# Singleton instance
_converter_instance = None


def get_document_converter() -> DocumentConverter:
    """Get singleton document converter instance"""
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = DocumentConverter()
    return _converter_instance
