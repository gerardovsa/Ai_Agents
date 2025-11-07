"""
UNIVERSAL EMAIL PARSER - AI Infrastructure Core
================================================

Parses emails from ANY source (Gmail, Outlook, raw MIME) into clean,
AI-optimized structured JSON. This is PLATFORM-AGNOSTIC.

Supports:
- Gmail API format (payload structure)
- Microsoft Graph API format (body/attachments structure)
- Raw MIME messages (RFC 822 format)

Key Features:
- HTML → Clean text conversion
- PDF → Text extraction
- Word/Excel → Text extraction
- Base64 attachment handling
- Thread conversation timeline
- Token-optimized output (1-2k tokens vs 50k)

Usage:
    from AI_infrastructure.core.email_parser import UniversalEmailParser
    
    parser = UniversalEmailParser()
    
    # Parse Gmail message
    gmail_result = parser.parse_gmail_message(gmail_api_response)
    
    # Parse Outlook message
    outlook_result = parser.parse_outlook_message(graph_api_response)
    
    # Parse raw MIME
    mime_result = parser.parse_mime_message(raw_mime_bytes)
"""

import base64
import re
import html
import mimetypes
import io
from email import message_from_bytes
from email.parser import BytesParser
from email.policy import default as email_policy
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Optional dependencies (gracefully degrade if not installed)
try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False
    print("[Email Parser] html2text not installed. HTML will be plain text stripped.")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class UniversalEmailParser:
    """
    Universal email parser for Gmail, Outlook, and raw MIME messages
    
    Platform-agnostic email parsing with intelligent content extraction,
    attachment processing, and AI-optimized output formatting.
    """
    
    def __init__(self, max_attachment_size_mb: int = 10):
        """
        Initialize parser
        
        Args:
            max_attachment_size_mb: Max attachment size to parse (default 10MB)
        """
        self.max_attachment_size_bytes = max_attachment_size_mb * 1024 * 1024
    
    
    # ==================== GMAIL API PARSING ====================
    
    def parse_gmail_message(self, 
                            raw_message: Dict[str, Any],
                            download_attachments: bool = True) -> Dict[str, Any]:
        """
        Parse Gmail API message (format='full') into AI-optimized structure
        
        Args:
            raw_message: Raw message from Gmail API (format='full')
            download_attachments: Whether to download and parse attachments
        
        Returns:
            Structured email data (see _create_structured_result)
        """
        result = {
            'id': raw_message['id'],
            'thread_id': raw_message['threadId'],
            'labels': raw_message.get('labelIds', []),
            'snippet': raw_message.get('snippet', ''),
            'source': 'gmail'
        }
        
        # Extract headers
        payload = raw_message.get('payload', {})
        headers = {h['name'].lower(): h['value'] for h in payload.get('headers', [])}
        
        result['subject'] = headers.get('subject', '(No Subject)')
        result['date'] = headers.get('date', '')
        
        # Parse email addresses
        result['from'] = self._parse_email_address(headers.get('from', ''))
        result['to'] = self._parse_email_address_list(headers.get('to', ''))
        result['cc'] = self._parse_email_address_list(headers.get('cc', ''))
        result['bcc'] = self._parse_email_address_list(headers.get('bcc', ''))
        
        # Parse date to timestamp
        result['timestamp'] = self._parse_email_date(result['date'])
        
        # Extract body content
        body_text, body_html = self._extract_gmail_body(payload)
        result['body_text'] = body_text
        result['body_html'] = body_html
        
        # Extract attachments
        if download_attachments:
            result['attachments'] = self._extract_gmail_attachments(payload)
        else:
            result['attachments'] = []
        
        # Estimate tokens
        result['token_estimate'] = self._estimate_tokens(result)
        
        return result
    
    
    def _extract_gmail_body(self, payload: Dict[str, Any]) -> tuple[str, str]:
        """
        Extract text and HTML body from Gmail message payload
        
        Returns:
            (body_text, body_html) tuple
        """
        body_text = ''
        body_html = ''
        
        # Single part message
        if 'body' in payload and payload['body'].get('data'):
            data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            mime_type = payload.get('mimeType', 'text/plain')
            
            if 'html' in mime_type:
                body_html = data
                body_text = self._html_to_text(data)
            else:
                body_text = data
        
        # Multipart message
        elif 'parts' in payload:
            body_text, body_html = self._extract_gmail_multipart_body(payload['parts'])
        
        return body_text, body_html
    
    
    def _extract_gmail_multipart_body(self, 
                                       parts: List[Dict[str, Any]],
                                       depth: int = 0) -> tuple[str, str]:
        """
        Recursively extract body from Gmail multipart message
        
        Returns:
            (body_text, body_html) tuple
        """
        if depth > 10:  # Safety limit
            return '', ''
        
        body_text = ''
        body_html = ''
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            # Nested multipart (recursion)
            if mime_type.startswith('multipart/'):
                nested_text, nested_html = self._extract_gmail_multipart_body(
                    part.get('parts', []), 
                    depth + 1
                )
                if nested_text:
                    body_text = body_text or nested_text
                if nested_html:
                    body_html = body_html or nested_html
            
            # Skip attachments
            elif part.get('filename'):
                continue
            
            # Extract body content
            elif 'body' in part and part['body'].get('data'):
                data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                
                if 'html' in mime_type:
                    body_html = body_html or data
                elif 'plain' in mime_type:
                    body_text = body_text or data
        
        # If we only have HTML, convert it to text
        if body_html and not body_text:
            body_text = self._html_to_text(body_html)
        
        return body_text, body_html
    
    
    def _extract_gmail_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and parse attachments from Gmail payload"""
        attachments = []
        
        def _process_parts(parts: List[Dict[str, Any]]):
            for part in parts:
                # Recursively process nested multipart
                if part.get('mimeType', '').startswith('multipart/'):
                    _process_parts(part.get('parts', []))
                    continue
                
                filename = part.get('filename')
                if not filename:
                    continue
                
                attachment_data = part.get('body', {})
                size = attachment_data.get('size', 0)
                attachment_id = attachment_data.get('attachmentId')
                
                if size > self.max_attachment_size_bytes:
                    attachments.append({
                        'filename': filename,
                        'content_type': part.get('mimeType', 'application/octet-stream'),
                        'size_bytes': size,
                        'parsed_content': f'[Attachment too large: {size / 1024 / 1024:.1f}MB]',
                        'parse_method': 'skipped',
                        'attachment_id': attachment_id
                    })
                    continue
                
                # Decode attachment data
                if attachment_data.get('data'):
                    raw_data = base64.urlsafe_b64decode(attachment_data['data'])
                    parsed_attachment = self._parse_attachment_content(
                        filename,
                        part.get('mimeType', 'application/octet-stream'),
                        raw_data,
                        size
                    )
                    parsed_attachment['attachment_id'] = attachment_id
                    attachments.append(parsed_attachment)
        
        if 'parts' in payload:
            _process_parts(payload['parts'])
        
        return attachments
    
    
    # ==================== OUTLOOK/MICROSOFT GRAPH API PARSING ====================
    
    def parse_outlook_message(self,
                               raw_message: Dict[str, Any],
                               download_attachments: bool = True) -> Dict[str, Any]:
        """
        Parse Microsoft Graph API message into AI-optimized structure
        
        Args:
            raw_message: Raw message from Microsoft Graph API
            download_attachments: Whether to parse attachments
        
        Returns:
            Structured email data (same format as Gmail parsing)
        """
        result = {
            'id': raw_message.get('id'),
            'thread_id': raw_message.get('conversationId'),
            'labels': [raw_message.get('parentFolderId', 'inbox')],
            'snippet': raw_message.get('bodyPreview', ''),
            'source': 'outlook'
        }
        
        # Extract basic fields
        result['subject'] = raw_message.get('subject', '(No Subject)')
        result['date'] = raw_message.get('receivedDateTime', '')
        
        # Parse email addresses (Microsoft Graph format)
        result['from'] = self._parse_outlook_email(raw_message.get('from', {}))
        result['to'] = [self._parse_outlook_email(addr) for addr in raw_message.get('toRecipients', [])]
        result['cc'] = [self._parse_outlook_email(addr) for addr in raw_message.get('ccRecipients', [])]
        result['bcc'] = [self._parse_outlook_email(addr) for addr in raw_message.get('bccRecipients', [])]
        
        # Parse timestamp
        result['timestamp'] = self._parse_email_date(result['date'])
        
        # Extract body (Microsoft Graph has body object)
        body_obj = raw_message.get('body', {})
        body_content = body_obj.get('content', '')
        body_type = body_obj.get('contentType', 'text')
        
        if body_type == 'html':
            result['body_html'] = body_content
            result['body_text'] = self._html_to_text(body_content)
        else:
            result['body_text'] = body_content
            result['body_html'] = ''
        
        # Extract attachments (if included in response)
        if download_attachments and raw_message.get('hasAttachments'):
            # Note: Attachments need separate API call in Microsoft Graph
            # Here we just parse what's provided
            attachments_data = raw_message.get('attachments', [])
            result['attachments'] = [
                self._parse_outlook_attachment(att) for att in attachments_data
            ]
        else:
            result['attachments'] = []
        
        # Estimate tokens
        result['token_estimate'] = self._estimate_tokens(result)
        
        return result
    
    
    def _parse_outlook_email(self, email_obj: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Parse Outlook email address object"""
        if not email_obj:
            return None
        
        email_address = email_obj.get('emailAddress', {})
        return {
            'name': email_address.get('name', ''),
            'email': email_address.get('address', '')
        }
    
    
    def _parse_outlook_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Outlook attachment object"""
        filename = attachment.get('name', 'unknown')
        content_type = attachment.get('contentType', 'application/octet-stream')
        size = attachment.get('size', 0)
        
        if size > self.max_attachment_size_bytes:
            return {
                'filename': filename,
                'content_type': content_type,
                'size_bytes': size,
                'parsed_content': f'[Attachment too large: {size / 1024 / 1024:.1f}MB]',
                'parse_method': 'skipped',
                'attachment_id': attachment.get('id')
            }
        
        # Decode content bytes
        content_bytes = attachment.get('contentBytes')
        if content_bytes:
            raw_data = base64.b64decode(content_bytes)
            return self._parse_attachment_content(filename, content_type, raw_data, size)
        
        return {
            'filename': filename,
            'content_type': content_type,
            'size_bytes': size,
            'parsed_content': '[Attachment content not available - requires separate download]',
            'parse_method': 'unavailable',
            'attachment_id': attachment.get('id')
        }
    
    
    # ==================== RAW MIME PARSING ====================
    
    def parse_mime_message(self,
                           raw_mime: Union[bytes, str],
                           download_attachments: bool = True) -> Dict[str, Any]:
        """
        Parse raw MIME message (RFC 822 format)
        
        Args:
            raw_mime: Raw MIME bytes or string
            download_attachments: Whether to parse attachments
        
        Returns:
            Structured email data
        """
        if isinstance(raw_mime, str):
            raw_mime = raw_mime.encode('utf-8')
        
        # Parse with Python stdlib
        msg = BytesParser(policy=email_policy).parsebytes(raw_mime)
        
        result = {
            'id': msg.get('Message-ID', '').strip('<>'),
            'thread_id': msg.get('In-Reply-To', '').strip('<>'),
            'labels': [],
            'snippet': '',
            'source': 'mime'
        }
        
        # Extract headers
        result['subject'] = msg.get('Subject', '(No Subject)')
        result['date'] = msg.get('Date', '')
        
        # Parse email addresses
        result['from'] = self._parse_email_address(msg.get('From', ''))
        result['to'] = self._parse_email_address_list(msg.get('To', ''))
        result['cc'] = self._parse_email_address_list(msg.get('Cc', ''))
        result['bcc'] = self._parse_email_address_list(msg.get('Bcc', ''))
        
        # Parse timestamp
        result['timestamp'] = self._parse_email_date(result['date'])
        
        # Extract body
        body = msg.get_body(preferencelist=['plain', 'html'])
        if body:
            body_content = body.get_content()
            body_type = body.get_content_type()
            
            if 'html' in body_type:
                result['body_html'] = body_content
                result['body_text'] = self._html_to_text(body_content)
            else:
                result['body_text'] = body_content
                result['body_html'] = ''
        else:
            result['body_text'] = ''
            result['body_html'] = ''
        
        # Extract attachments
        if download_attachments:
            result['attachments'] = []
            for attachment in msg.iter_attachments():
                filename = attachment.get_filename() or 'unknown'
                content_type = attachment.get_content_type()
                raw_data = attachment.get_payload(decode=True)
                size = len(raw_data) if raw_data else 0
                
                if size > self.max_attachment_size_bytes:
                    result['attachments'].append({
                        'filename': filename,
                        'content_type': content_type,
                        'size_bytes': size,
                        'parsed_content': f'[Attachment too large: {size / 1024 / 1024:.1f}MB]',
                        'parse_method': 'skipped'
                    })
                else:
                    result['attachments'].append(
                        self._parse_attachment_content(filename, content_type, raw_data, size)
                    )
        else:
            result['attachments'] = []
        
        # Estimate tokens
        result['token_estimate'] = self._estimate_tokens(result)
        
        return result
    
    
    # ==================== SHARED UTILITY METHODS ====================
    
    def _parse_email_address(self, address_str: str) -> Optional[Dict[str, str]]:
        """Parse 'Name <email@example.com>' into {'name': 'Name', 'email': 'email@example.com'}"""
        if not address_str:
            return None
        
        match = re.match(r'(.*?)\s*<(.+?)>', address_str)
        if match:
            return {'name': match.group(1).strip(' "\''), 'email': match.group(2).strip()}
        else:
            return {'name': '', 'email': address_str.strip()}
    
    
    def _parse_email_address_list(self, address_str: str) -> List[Dict[str, str]]:
        """Parse comma-separated email addresses"""
        if not address_str:
            return []
        
        addresses = []
        for addr in address_str.split(','):
            parsed = self._parse_email_address(addr.strip())
            if parsed:
                addresses.append(parsed)
        return addresses
    
    
    def _parse_email_date(self, date_str: str) -> int:
        """Parse email date to Unix timestamp"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return int(dt.timestamp())
        except Exception:
            return 0
    
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML to clean plain text
        
        Priority:
        1. html2text library (best - preserves links, formatting)
        2. BeautifulSoup (good - strips HTML tags)
        3. Regex fallback (basic - removes HTML tags)
        """
        if HTML2TEXT_AVAILABLE:
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap lines
            return h.handle(html_content)
        
        elif BS4_AVAILABLE:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)
        
        else:
            # Fallback: basic regex strip
            text = re.sub(r'<[^>]+>', '', html_content)
            text = html.unescape(text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            return text.strip()
    
    
    def _parse_attachment_content(self,
                                   filename: str,
                                   content_type: str,
                                   raw_data: bytes,
                                   size: int) -> Dict[str, Any]:
        """
        Parse attachment content based on file type
        
        Supported formats:
        - PDF → Text extraction
        - Word (.docx) → Text extraction
        - Excel (.xlsx) → CSV-like text
        - Text files → Direct decode
        - Others → Binary (skip parsing)
        """
        result = {
            'filename': filename,
            'content_type': content_type,
            'size_bytes': size,
            'parsed_content': '',
            'parse_method': 'unknown'
        }
        
        # PDF parsing
        if content_type == 'application/pdf' or filename.lower().endswith('.pdf'):
            if PYPDF_AVAILABLE:
                try:
                    pdf_reader = pypdf.PdfReader(io.BytesIO(raw_data))
                    text = []
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                    result['parsed_content'] = '\n\n'.join(text)
                    result['parse_method'] = 'pdf'
                except Exception as e:
                    result['parsed_content'] = f'[PDF parsing failed: {str(e)}]'
                    result['parse_method'] = 'pdf_error'
            else:
                result['parsed_content'] = '[PDF parsing requires pypdf library]'
                result['parse_method'] = 'pdf_unavailable'
        
        # Word document parsing
        elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                               'application/msword'] or filename.lower().endswith(('.docx', '.doc')):
            if PYTHON_DOCX_AVAILABLE:
                try:
                    doc = docx.Document(io.BytesIO(raw_data))
                    result['parsed_content'] = '\n\n'.join(para.text for para in doc.paragraphs)
                    result['parse_method'] = 'docx'
                except Exception as e:
                    result['parsed_content'] = f'[Word parsing failed: {str(e)}]'
                    result['parse_method'] = 'docx_error'
            else:
                result['parsed_content'] = '[Word parsing requires python-docx library]'
                result['parse_method'] = 'docx_unavailable'
        
        # Excel parsing
        elif content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'application/vnd.ms-excel'] or filename.lower().endswith(('.xlsx', '.xls')):
            if OPENPYXL_AVAILABLE:
                try:
                    wb = openpyxl.load_workbook(io.BytesIO(raw_data), read_only=True)
                    sheets = []
                    for sheet_name in wb.sheetnames:
                        sheet = wb[sheet_name]
                        rows = []
                        for row in sheet.iter_rows(values_only=True):
                            rows.append('\t'.join(str(cell) if cell is not None else '' for cell in row))
                        sheets.append(f"# Sheet: {sheet_name}\n" + '\n'.join(rows))
                    result['parsed_content'] = '\n\n'.join(sheets)
                    result['parse_method'] = 'xlsx'
                except Exception as e:
                    result['parsed_content'] = f'[Excel parsing failed: {str(e)}]'
                    result['parse_method'] = 'xlsx_error'
            else:
                result['parsed_content'] = '[Excel parsing requires openpyxl library]'
                result['parse_method'] = 'xlsx_unavailable'
        
        # Text files
        elif content_type.startswith('text/') or filename.lower().endswith(('.txt', '.csv', '.json', '.xml', '.html')):
            try:
                result['parsed_content'] = raw_data.decode('utf-8', errors='ignore')
                result['parse_method'] = 'text'
            except Exception as e:
                result['parsed_content'] = f'[Text decoding failed: {str(e)}]'
                result['parse_method'] = 'text_error'
        
        # Binary files (images, zips, etc.) - don't parse
        else:
            result['parsed_content'] = f'[Binary file: {content_type}]'
            result['parse_method'] = 'binary'
        
        return result
    
    
    def _estimate_tokens(self, result: Dict[str, Any]) -> int:
        """Estimate token count (rough: 1 token ~= 4 chars)"""
        total_chars = len(result.get('body_text', ''))
        total_chars += sum(len(att.get('parsed_content', '')) for att in result.get('attachments', []))
        return total_chars // 4
    
    
    # ==================== THREAD TIMELINE ====================
    
    def parse_email_thread_timeline(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse email thread into chronological conversation timeline
        
        Works with messages from ANY source (Gmail/Outlook/MIME) as long as
        they're already parsed with parse_gmail_message/parse_outlook_message
        
        Args:
            messages: List of parsed messages (sorted oldest to newest)
        
        Returns:
            Thread timeline with conversation flow
        """
        if not messages:
            return {}
        
        # Collect unique participants
        participants_set = set()
        for msg in messages:
            if msg.get('from'):
                participants_set.add((msg['from']['email'], msg['from']['name']))
            for person in msg.get('to', []) + msg.get('cc', []):
                participants_set.add((person['email'], person['name']))
        
        participants = [{'email': email, 'name': name} for email, name in participants_set]
        
        # Build timeline
        timeline = {
            'thread_id': messages[0].get('thread_id'),
            'subject': messages[0].get('subject'),
            'participants': participants,
            'start_date': messages[0].get('date'),
            'last_date': messages[-1].get('date'),
            'message_count': len(messages),
            'messages': [],
            'token_estimate': 0
        }
        
        for i, msg in enumerate(messages, 1):
            preview = msg.get('body_text', '')[:500]
            if len(msg.get('body_text', '')) > 500:
                preview += '...'
            
            timeline['messages'].append({
                'position': i,
                'from': msg.get('from'),
                'date': msg.get('date'),
                'body_text': preview,
                'full_message_id': msg.get('id')
            })
        
        timeline['token_estimate'] = sum(msg.get('token_estimate', 0) for msg in messages)
        
        return timeline
    
    
    # ==================== PDF CONVERSION ====================
    
    def prepare_for_claude(self,
                            parsed_data: Union[Dict, List[Dict]],
                            output_format: str = 'json') -> Union[Dict, bytes]:
        """
        Prepare parsed email(s) for Claude API consumption
        
        Args:
            parsed_data: Single email dict or list of emails (thread)
            output_format: 'json' (default) or 'pdf'
        
        Returns:
            - If json: Original parsed dict/list
            - If pdf: PDF bytes ready for Claude document API
        
        Examples:
            # Single email as JSON
            result = parser.prepare_for_claude(email, output_format='json')
            
            # Thread as PDF for Claude
            pdf_bytes = parser.prepare_for_claude(thread_messages, output_format='pdf')
            pdf_base64 = base64.b64encode(pdf_bytes).decode()
            
            # Send to Claude
            message = {
                "content": [
                    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
                    {"type": "text", "text": "Analyze this email thread"}
                ]
            }
        """
        if output_format == 'json':
            return parsed_data
        
        elif output_format == 'pdf':
            # Import converter (lazy load)
            from AI_infrastructure.core.email_to_pdf_converter import EmailToPDFConverter
            
            converter = EmailToPDFConverter(
                detect_header_footer=True,
                ocr_header_footer=True
            )
            
            # Single email or thread?
            if isinstance(parsed_data, list):
                # Thread → Multi-page PDF
                return converter.thread_to_pdf(parsed_data, include_attachments=True)
            else:
                # Single email → PDF
                return converter.email_to_pdf(parsed_data, include_attachments=True)
        
        else:
            raise ValueError(f"Invalid output_format: {output_format}. Must be 'json' or 'pdf'.")
