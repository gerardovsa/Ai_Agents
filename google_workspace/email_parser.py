"""
EMAIL PARSER MIDDLEWARE
Converts raw Gmail API responses into clean, AI-optimized JSON

This module parses email MIME structures, extracts text content,
downloads and parses attachments, and returns structured data
optimized for Claude/GPT consumption (NO raw base64 blobs!).

Key Features:
- HTML → Clean text conversion
- PDF → Text extraction
- Word/Excel → Text extraction
- Base64 attachment handling
- Thread conversation timeline
- Token-optimized output (1-2k tokens vs 50k)

Usage:
    from google_workspace.email_parser import parse_gmail_message
    
    # Get message with full MIME data
    raw_message = service.users().messages().get(
        userId='me', id=message_id, format='full'
    ).execute()
    
    # Parse into AI-friendly format
    parsed = parse_gmail_message(raw_message)
"""

import base64
import re
import html
import mimetypes
from email import message_from_bytes
from email.parser import BytesParser
from email.policy import default as email_policy
from typing import Dict, List, Optional, Any
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


def parse_gmail_message(raw_message: Dict[str, Any], 
                         download_attachments: bool = True,
                         max_attachment_size_mb: int = 10) -> Dict[str, Any]:
    """
    Parse Gmail API message into AI-optimized structured data
    
    Args:
        raw_message: Raw message from Gmail API (format='full')
        download_attachments: Whether to download and parse attachments
        max_attachment_size_mb: Max attachment size to parse (default 10MB)
    
    Returns:
        {
            'id': str,
            'thread_id': str,
            'from': {'name': str, 'email': str},
            'to': [{'name': str, 'email': str}],
            'subject': str,
            'date': str (ISO format),
            'timestamp': int (Unix timestamp),
            'body_text': str (clean text version),
            'body_html': str (original HTML if available),
            'attachments': [
                {
                    'filename': str,
                    'content_type': str,
                    'size_bytes': int,
                    'parsed_content': str (text extracted from PDF/Word/Excel),
                    'parse_method': str ('pdf', 'docx', 'xlsx', 'text', 'binary')
                }
            ],
            'labels': [str],
            'snippet': str (Gmail's preview),
            'token_estimate': int (rough token count for AI context)
        }
    """
    result = {
        'id': raw_message['id'],
        'thread_id': raw_message['threadId'],
        'labels': raw_message.get('labelIds', []),
        'snippet': raw_message.get('snippet', ''),
        'from': None,
        'to': [],
        'cc': [],
        'bcc': [],
        'subject': '',
        'date': '',
        'timestamp': 0,
        'body_text': '',
        'body_html': '',
        'attachments': [],
        'token_estimate': 0
    }
    
    # Extract headers
    payload = raw_message.get('payload', {})
    headers = {h['name'].lower(): h['value'] for h in payload.get('headers', [])}
    
    result['subject'] = headers.get('subject', '(No Subject)')
    result['date'] = headers.get('date', '')
    
    # Parse email addresses
    result['from'] = _parse_email_address(headers.get('from', ''))
    result['to'] = _parse_email_address_list(headers.get('to', ''))
    result['cc'] = _parse_email_address_list(headers.get('cc', ''))
    result['bcc'] = _parse_email_address_list(headers.get('bcc', ''))
    
    # Parse date to timestamp
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(result['date'])
        result['timestamp'] = int(dt.timestamp())
        result['date'] = dt.isoformat()
    except Exception:
        result['timestamp'] = 0
    
    # Extract body content
    body_text, body_html = _extract_body(payload)
    result['body_text'] = body_text
    result['body_html'] = body_html
    
    # Extract attachments
    if download_attachments:
        result['attachments'] = _extract_attachments(
            payload, 
            max_size_bytes=max_attachment_size_mb * 1024 * 1024
        )
    
    # Estimate tokens (rough: 1 token ~= 4 chars)
    total_chars = len(result['body_text']) + sum(
        len(att.get('parsed_content', '')) for att in result['attachments']
    )
    result['token_estimate'] = total_chars // 4
    
    return result


def _parse_email_address(address_str: str) -> Optional[Dict[str, str]]:
    """Parse 'Name <email@example.com>' into {'name': 'Name', 'email': 'email@example.com'}"""
    if not address_str:
        return None
    
    match = re.match(r'(.*?)\s*<(.+?)>', address_str)
    if match:
        return {'name': match.group(1).strip(' "\''), 'email': match.group(2).strip()}
    else:
        return {'name': '', 'email': address_str.strip()}


def _parse_email_address_list(address_str: str) -> List[Dict[str, str]]:
    """Parse comma-separated email addresses"""
    if not address_str:
        return []
    
    addresses = []
    for addr in address_str.split(','):
        parsed = _parse_email_address(addr.strip())
        if parsed:
            addresses.append(parsed)
    return addresses


def _extract_body(payload: Dict[str, Any]) -> tuple[str, str]:
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
            body_text = _html_to_text(data)
        else:
            body_text = data
    
    # Multipart message
    elif 'parts' in payload:
        body_text, body_html = _extract_multipart_body(payload['parts'])
    
    return body_text, body_html


def _extract_multipart_body(parts: List[Dict[str, Any]], 
                              depth: int = 0) -> tuple[str, str]:
    """
    Recursively extract body from multipart message
    
    Args:
        parts: List of message parts
        depth: Recursion depth (safety limit at 10)
    
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
            nested_text, nested_html = _extract_multipart_body(
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
        body_text = _html_to_text(body_html)
    
    return body_text, body_html


def _html_to_text(html_content: str) -> str:
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
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()


def _extract_attachments(payload: Dict[str, Any], 
                          max_size_bytes: int = 10 * 1024 * 1024) -> List[Dict[str, Any]]:
    """
    Extract and parse attachments from message payload
    
    Args:
        payload: Gmail message payload
        max_size_bytes: Max size to parse (default 10MB)
    
    Returns:
        List of parsed attachment dictionaries
    """
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
            
            if size > max_size_bytes:
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
                parsed_attachment = _parse_attachment_content(
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


def _parse_attachment_content(filename: str, 
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
                import io
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
                import io
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
                import io
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


def parse_email_thread_timeline(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse email thread into chronological conversation timeline
    
    Args:
        messages: List of raw Gmail messages (sorted oldest to newest)
    
    Returns:
        {
            'thread_id': str,
            'subject': str,
            'participants': [{'name': str, 'email': str}],
            'start_date': str (ISO),
            'last_date': str (ISO),
            'message_count': int,
            'messages': [
                {
                    'position': int (1-indexed),
                    'from': {'name': str, 'email': str},
                    'date': str,
                    'body_text': str (first 500 chars),
                    'full_message_id': str
                }
            ],
            'token_estimate': int
        }
    """
    if not messages:
        return {}
    
    parsed_messages = [parse_gmail_message(msg, download_attachments=False) for msg in messages]
    
    # Collect unique participants
    participants_set = set()
    for msg in parsed_messages:
        if msg['from']:
            participants_set.add((msg['from']['email'], msg['from']['name']))
        for person in msg['to'] + msg['cc']:
            participants_set.add((person['email'], person['name']))
    
    participants = [{'email': email, 'name': name} for email, name in participants_set]
    
    # Build timeline
    timeline = {
        'thread_id': parsed_messages[0]['thread_id'],
        'subject': parsed_messages[0]['subject'],
        'participants': participants,
        'start_date': parsed_messages[0]['date'],
        'last_date': parsed_messages[-1]['date'],
        'message_count': len(parsed_messages),
        'messages': [],
        'token_estimate': 0
    }
    
    for i, msg in enumerate(parsed_messages, 1):
        preview = msg['body_text'][:500] + ('...' if len(msg['body_text']) > 500 else '')
        timeline['messages'].append({
            'position': i,
            'from': msg['from'],
            'date': msg['date'],
            'body_text': preview,
            'full_message_id': msg['id']
        })
    
    timeline['token_estimate'] = sum(msg['token_estimate'] for msg in parsed_messages)
    
    return timeline
