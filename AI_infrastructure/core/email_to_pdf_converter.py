"""
EMAIL TO PDF CONVERTER - Universal Email Thread to PDF
=======================================================

Converts emails and email threads into comprehensive PDF documents
with intelligent handling of attachments, images, and header/footer detection.

Key Features:
- Single emails → Professional PDF
- Email threads → Multi-page PDF with context
- Smart header/footer image detection (signatures, logos)
- OCR text extraction from header/footer images
- Inline attachment rendering
- Maintains conversation flow

Usage:
    from AI_infrastructure.core.email_to_pdf_converter import EmailToPDFConverter
    
    converter = EmailToPDFConverter()
    pdf_bytes = converter.thread_to_pdf(thread_messages)
    pdf_base64 = base64.b64encode(pdf_bytes).decode()
"""

import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
from io import BytesIO

# Optional dependencies
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, 
                                     PageBreak, Table, TableStyle, Image as RLImage)
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[Email PDF Converter] reportlab not installed. PDF conversion unavailable.")

try:
    from PyPDF2 import PdfMerger, PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        import pypdf
        PdfMerger = pypdf.PdfMerger
        PdfReader = pypdf.PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False
        print("[Email PDF Converter] PyPDF2/pypdf not installed. PDF merging unavailable.")

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[Email PDF Converter] pytesseract not installed. OCR text extraction unavailable.")


class EmailToPDFConverter:
    """
    Convert emails and threads to comprehensive PDF documents
    """
    
    def __init__(self,
                 detect_header_footer=True,
                 max_header_height_ratio=0.15,
                 max_footer_height_ratio=0.10,
                 ocr_header_footer=True):
        """
        Initialize converter
        
        Args:
            detect_header_footer: Auto-detect header/footer images
            max_header_height_ratio: Max height ratio to consider header (15% of image)
            max_footer_height_ratio: Max height ratio to consider footer (10% of image)
            ocr_header_footer: Extract text from header/footer images via OCR
        """
        self.detect_header_footer = detect_header_footer
        self.max_header_height = max_header_height_ratio
        self.max_footer_height = max_footer_height_ratio
        self.ocr_header_footer = ocr_header_footer
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Email header style
        self.styles.add(ParagraphStyle(
            name='EmailHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10
        ))
        
        # Signature/footer text style
        self.styles.add(ParagraphStyle(
            name='SignatureText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leftIndent=20,
            spaceAfter=5
        ))
        
        # Attachment separator style
        self.styles.add(ParagraphStyle(
            name='AttachmentSeparator',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#0066CC'),
            spaceBefore=10,
            spaceAfter=5
        ))
    
    
    # ==================== HEADER/FOOTER DETECTION ====================
    
    def _is_header_or_footer_image(self, 
                                     image_bytes: bytes,
                                     image_context: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Detect if image is likely a header/footer (logo, signature)
        
        Args:
            image_bytes: Raw image bytes
            image_context: Context about where image appears
        
        Returns:
            (is_header_footer, type, extracted_text)
            - is_header_footer: True if detected as header/footer
            - type: 'header', 'footer', or 'content'
            - extracted_text: OCR text if found, None otherwise
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            width, height = img.size
            
            # Detection heuristics
            is_small = width < 800 or height < 200
            is_wide_banner = width / height > 4 if height > 0 else False
            is_thin_strip = height < 100
            
            # Check filename patterns (common signature/logo patterns)
            filename = image_context.get('filename', '').lower()
            signature_patterns = ['signature', 'logo', 'banner', 'header', 'footer', 
                                   'letterhead', 'company', 'brand']
            has_signature_name = any(pattern in filename for pattern in signature_patterns)
            
            # Position in email (if available)
            position = image_context.get('position', 'unknown')
            is_first = position == 'first'
            is_last = position == 'last'
            
            # Combined detection logic
            is_header = (is_first and (is_small or is_wide_banner or has_signature_name))
            is_footer = (is_last and (is_small or is_thin_strip or has_signature_name))
            
            detected_type = 'header' if is_header else ('footer' if is_footer else 'content')
            is_header_footer = is_header or is_footer
            
            # Extract text via OCR if it's header/footer
            extracted_text = None
            if is_header_footer and self.ocr_header_footer and OCR_AVAILABLE:
                try:
                    extracted_text = pytesseract.image_to_string(img).strip()
                    # Only keep if meaningful text found
                    if len(extracted_text) < 5 or not any(c.isalnum() for c in extracted_text):
                        extracted_text = None
                except Exception as e:
                    print(f"[OCR] Failed to extract text: {e}")
                    extracted_text = None
            
            return is_header_footer, detected_type, extracted_text
        
        except Exception as e:
            print(f"[Header Detection] Error: {e}")
            return False, 'content', None
    
    
    # ==================== EMAIL TO PDF CONVERSION ====================
    
    def email_to_pdf(self, 
                      parsed_email: Dict[str, Any],
                      include_attachments: bool = True) -> bytes:
        """
        Convert single email to PDF
        
        Args:
            parsed_email: Parsed email from UniversalEmailParser
            include_attachments: Whether to include attachments
        
        Returns:
            PDF bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                 topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Email header section
        story.extend(self._create_email_header(parsed_email))
        
        # Email body
        story.extend(self._create_email_body(parsed_email))
        
        # Attachments (if any)
        if include_attachments and parsed_email.get('attachments'):
            story.extend(self._create_attachments_section(parsed_email))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    
    def thread_to_pdf(self,
                       thread_messages: List[Dict[str, Any]],
                       include_attachments: bool = True) -> bytes:
        """
        Convert email thread to comprehensive PDF
        
        Args:
            thread_messages: List of parsed emails (chronological order)
            include_attachments: Whether to include attachments
        
        Returns:
            PDF bytes with entire thread + attachments
        """
        if not PYPDF_AVAILABLE:
            raise ImportError("PyPDF2/pypdf required for thread merging: pip install pypdf")
        
        merger = PdfMerger()
        
        for i, message in enumerate(thread_messages):
            # Create PDF for this message
            msg_pdf = self._create_thread_message_pdf(message, i+1, len(thread_messages))
            merger.append(BytesIO(msg_pdf))
            
            # Append attachments if enabled
            if include_attachments:
                for attachment in message.get('attachments', []):
                    att_pdf = self._process_attachment_for_pdf(attachment, message)
                    if att_pdf:
                        merger.append(BytesIO(att_pdf))
        
        # Output merged PDF
        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        return output.read()
    
    
    def _create_thread_message_pdf(self,
                                     message: Dict[str, Any],
                                     msg_num: int,
                                     total_msgs: int) -> bytes:
        """Create PDF page for single message in thread"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                 topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Thread position indicator
        story.append(Paragraph(
            f"<b>Message {msg_num} of {total_msgs}</b>",
            self.styles['Title']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Email metadata
        story.extend(self._create_email_header(message))
        
        # Email body
        story.extend(self._create_email_body(message))
        
        # Attachment list (actual files follow)
        if message.get('attachments'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(
                f"<b>Attachments ({len(message['attachments'])}):</b>",
                self.styles['Heading3']
            ))
            for att in message['attachments']:
                story.append(Paragraph(
                    f"• {att.get('filename', 'Unknown')} ({att.get('content_type', 'unknown')})",
                    self.styles['Normal']
                ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    
    def _create_email_header(self, message: Dict[str, Any]) -> List:
        """Create email header section"""
        story = []
        
        # From
        from_addr = message.get('from', {})
        from_text = f"{from_addr.get('name', '')} &lt;{from_addr.get('email', '')}&gt;"
        story.append(Paragraph(f"<b>From:</b> {from_text}", self.styles['EmailHeader']))
        
        # To
        to_addrs = message.get('to', [])
        to_text = ', '.join(f"{t.get('name', '')} &lt;{t.get('email', '')}&gt;" for t in to_addrs)
        story.append(Paragraph(f"<b>To:</b> {to_text}", self.styles['EmailHeader']))
        
        # CC (if present)
        if message.get('cc'):
            cc_text = ', '.join(f"{c.get('name', '')} &lt;{c.get('email', '')}&gt;" for c in message['cc'])
            story.append(Paragraph(f"<b>CC:</b> {cc_text}", self.styles['EmailHeader']))
        
        # Subject
        story.append(Paragraph(
            f"<b>Subject:</b> {message.get('subject', '(No Subject)')}",
            self.styles['EmailHeader']
        ))
        
        # Date
        story.append(Paragraph(f"<b>Date:</b> {message.get('date', '')}", self.styles['EmailHeader']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Divider line
        story.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.grey)
        ])))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    
    def _create_email_body(self, message: Dict[str, Any]) -> List:
        """Create email body section"""
        story = []
        
        body_text = message.get('body_text', '')
        
        # Split into paragraphs
        paragraphs = body_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Escape HTML entities
                safe_para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Preserve line breaks within paragraph
                safe_para = safe_para.replace('\n', '<br/>')
                story.append(Paragraph(safe_para, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    
    def _create_attachments_section(self, message: Dict[str, Any]) -> List:
        """Create attachments section (metadata only, files processed separately)"""
        story = []
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("<b>Attachments:</b>", self.styles['Heading3']))
        
        for att in message.get('attachments', []):
            filename = att.get('filename', 'Unknown')
            content_type = att.get('content_type', 'unknown')
            size = att.get('size_bytes', 0)
            size_mb = size / (1024 * 1024)
            
            story.append(Paragraph(
                f"• <b>{filename}</b> ({content_type}, {size_mb:.2f} MB)",
                self.styles['Normal']
            ))
        
        return story
    
    
    # ==================== ATTACHMENT PROCESSING ====================
    
    def _process_attachment_for_pdf(self,
                                      attachment: Dict[str, Any],
                                      message_context: Dict[str, Any]) -> Optional[bytes]:
        """
        Process attachment for PDF inclusion
        
        Handles:
        - PDFs → Direct append
        - Images → Check header/footer, convert to PDF or extract text
        - Word docs → Convert to PDF
        - Others → Skip or create info page
        """
        content_type = attachment.get('content_type', '')
        filename = attachment.get('filename', 'unknown')
        
        # PDF attachments → Direct append
        if content_type == 'application/pdf':
            raw_data = attachment.get('raw_data')
            if raw_data:
                return raw_data
        
        # Image attachments → Smart handling
        elif content_type.startswith('image/'):
            return self._process_image_attachment(attachment, message_context)
        
        # Word documents → Would need conversion (TODO)
        elif 'word' in content_type:
            # For now, create info page
            return self._create_attachment_info_page(attachment, "Word document conversion not yet implemented")
        
        # Other types → Info page
        else:
            return self._create_attachment_info_page(attachment, "Preview not available")
        
        return None
    
    
    def _process_image_attachment(self,
                                    attachment: Dict[str, Any],
                                    message_context: Dict[str, Any]) -> Optional[bytes]:
        """
        Process image attachment with header/footer detection
        
        Returns:
            - PDF with image (if content image)
            - PDF with extracted text (if header/footer with text)
            - None (if header/footer with no useful text)
        """
        raw_data = attachment.get('raw_data')
        if not raw_data:
            return None
        
        # Detect header/footer
        image_context = {
            'filename': attachment.get('filename', ''),
            'position': attachment.get('position', 'unknown')
        }
        
        is_header_footer, detected_type, extracted_text = self._is_header_or_footer_image(
            raw_data, image_context
        )
        
        # If header/footer with useful text, create text page
        if is_header_footer and extracted_text:
            return self._create_signature_text_page(
                extracted_text, 
                attachment.get('filename', ''),
                detected_type
            )
        
        # If header/footer with no text, skip
        elif is_header_footer and not extracted_text:
            print(f"[PDF Converter] Skipping {detected_type} image: {attachment.get('filename')}")
            return None
        
        # Otherwise, it's content image → Convert to PDF page
        else:
            return self._image_to_pdf_page(raw_data, attachment.get('filename', ''))
    
    
    def _image_to_pdf_page(self, image_bytes: bytes, filename: str) -> bytes:
        """Convert image to PDF page"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Add filename as header
        story.append(Paragraph(f"<b>Image Attachment:</b> {filename}", self.styles['Heading3']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add image (scaled to fit page)
        try:
            img = Image.open(BytesIO(image_bytes))
            img_width, img_height = img.size
            
            # Scale to fit page (max 6 inches wide)
            max_width = 6 * inch
            max_height = 8 * inch
            
            scale = min(max_width / img_width, max_height / img_height, 1.0)
            
            rl_img = RLImage(BytesIO(image_bytes), 
                              width=img_width * scale, 
                              height=img_height * scale)
            story.append(rl_img)
        except Exception as e:
            story.append(Paragraph(f"[Error rendering image: {e}]", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    
    def _create_signature_text_page(self, 
                                      extracted_text: str,
                                      filename: str,
                                      signature_type: str) -> bytes:
        """Create PDF page with extracted signature/header text"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph(
            f"<b>Extracted {signature_type.capitalize()} Information:</b>",
            self.styles['Heading3']
        ))
        story.append(Paragraph(f"<i>From: {filename}</i>", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Divider
        story.append(Table([['']], colWidths=[6.5*inch], style=TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.lightgrey)
        ])))
        story.append(Spacer(1, 0.1*inch))
        
        # Extracted text
        for line in extracted_text.split('\n'):
            if line.strip():
                story.append(Paragraph(line, self.styles['SignatureText']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    
    def _create_attachment_info_page(self, 
                                       attachment: Dict[str, Any],
                                       message: str) -> bytes:
        """Create info page for unsupported attachment types"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        story.append(Paragraph("<b>Attachment Information</b>", self.styles['Heading3']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(f"<b>Filename:</b> {attachment.get('filename', 'Unknown')}", 
                                self.styles['Normal']))
        story.append(Paragraph(f"<b>Type:</b> {attachment.get('content_type', 'unknown')}", 
                                self.styles['Normal']))
        story.append(Paragraph(f"<b>Size:</b> {attachment.get('size_bytes', 0) / 1024:.1f} KB", 
                                self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"<i>{message}</i>", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
