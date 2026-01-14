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
        """Convert DOCX to PDF using docx2pdf or pypandoc"""
        try:
            # Try docx2pdf first (Windows-only, requires MS Word)
            try:
                from docx2pdf import convert
                
                # Write to temp file
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                    temp_docx.write(file_data)
                    temp_docx_path = temp_docx.name
                
                temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')
                
                # Convert
                convert(temp_docx_path, temp_pdf_path)
                
                # Read result
                with open(temp_pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                # Cleanup
                os.unlink(temp_docx_path)
                os.unlink(temp_pdf_path)
                
                return pdf_data
                
            except ImportError:
                # Fallback: Convert to images then to PDF
                print("[INFO] docx2pdf not available, using image-based conversion")
                return self._convert_via_images_to_pdf(file_data, filename, 'docx')
        
        except Exception as e:
            raise DocumentConverterError(f'DOCX to PDF conversion failed: {str(e)}')
    
    
    def _convert_docx_to_images(self,
                               file_data: bytes,
                               filename: str,
                               format: str = 'png',
                               dpi: int = 150) -> List[Dict[str, Any]]:
        """Convert DOCX to images (one per page)"""
        try:
            from docx import Document
            from PIL import Image, ImageDraw, ImageFont
            
            doc = Document(io.BytesIO(file_data))
            
            images = []
            
            # Convert each page to image
            # Note: This is a simplified implementation
            # For production, consider using pdf2image after PDF conversion
            for page_num, paragraph in enumerate(doc.paragraphs, 1):
                # Create blank image
                img = Image.new('RGB', (2480, 3508), 'white')  # A4 at 300 DPI
                draw = ImageDraw.Draw(img)
                
                # Draw text (simplified)
                draw.text((100, 100 * page_num), paragraph.text, fill='black')
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=format.upper())
                img_bytes.seek(0)
                
                images.append({
                    'data': img_bytes.read(),
                    'name': f"{filename.rsplit('.', 1)[0]}_page{page_num}.{format}",
                    'size': img_bytes.tell(),
                    'content_type': f'image/{format}'
                })
            
            return images if images else [self._create_placeholder_image(filename, format)]
            
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
        """Convert XLSX to images (one per sheet)"""
        try:
            from openpyxl import load_workbook
            from PIL import Image, ImageDraw, ImageFont
            
            wb = load_workbook(io.BytesIO(file_data), data_only=True)
            
            images = []
            
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                
                # Create image for sheet
                img = Image.new('RGB', (2480, 3508), 'white')  # A4 at 300 DPI
                draw = ImageDraw.Draw(img)
                
                # Draw sheet title
                draw.text((100, 50), sheet_name, fill='black')
                
                # Draw table data (simplified)
                y_offset = 150
                for row_num, row in enumerate(sheet.iter_rows(values_only=True)):
                    x_offset = 100
                    for cell in row:
                        cell_text = str(cell) if cell is not None else ''
                        draw.text((x_offset, y_offset), cell_text[:30], fill='black')
                        x_offset += 200
                    y_offset += 40
                    
                    if y_offset > 3400:  # Near bottom
                        break
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=format.upper())
                img_bytes.seek(0)
                
                images.append({
                    'data': img_bytes.read(),
                    'name': f"{filename.rsplit('.', 1)[0]}_{sheet_name}.{format}",
                    'size': img_bytes.tell(),
                    'content_type': f'image/{format}'
                })
            
            return images if images else [self._create_placeholder_image(filename, format)]
            
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
        """Convert PPTX to images (one per slide)"""
        try:
            from pptx import Presentation
            from PIL import Image, ImageDraw, ImageFont
            
            prs = Presentation(io.BytesIO(file_data))
            
            images = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                # Create image for slide
                img = Image.new('RGB', (1920, 1080), 'white')  # 16:9 HD
                draw = ImageDraw.Draw(img)
                
                # Draw slide content
                y_offset = 50
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        # Draw text (simplified)
                        lines = shape.text.split('\n')
                        for line in lines:
                            draw.text((50, y_offset), line[:100], fill='black')
                            y_offset += 40
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=format.upper())
                img_bytes.seek(0)
                
                images.append({
                    'data': img_bytes.read(),
                    'name': f"{filename.rsplit('.', 1)[0]}_slide{slide_num}.{format}",
                    'size': img_bytes.tell(),
                    'content_type': f'image/{format}'
                })
            
            return images if images else [self._create_placeholder_image(filename, format)]
            
        except Exception as e:
            raise DocumentConverterError(f'PPTX to images conversion failed: {str(e)}')
    
    
    # ==================== HELPER METHODS ====================
    
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
