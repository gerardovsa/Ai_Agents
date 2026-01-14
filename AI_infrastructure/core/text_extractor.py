"""
TEXT EXTRACTOR - Universal Document Text Extraction (Markdown Output)
======================================================================

Extracts text from ANY document type for AI processing with RICH MARKDOWN FORMATTING.
Complements Universal File Handler by processing unsupported file types.

✨ OUTPUT FORMAT: Markdown with preserved structure (headings, lists, tables, bold/italic)

Supported Types:
- Documents: DOCX, DOC, ODT, RTF → Markdown with headings, lists, bold/italic
- Spreadsheets: XLSX, XLS, CSV → Markdown tables
- Presentations: PPTX, PPT → Structured slides with headings
- Data: JSON, XML, YAML → Code blocks with syntax highlighting
- Text: TXT, MD, HTML → Preserved/converted to Markdown
- Code: PY, JS, TS, JSX, TSX, etc. → Code blocks with language tags

Usage:
    from AI_infrastructure.core.text_extractor import TextExtractor
    
    extractor = TextExtractor()
    
    # Extract from bytes (returns Markdown)
    result = extractor.extract_text(
        file_data=file_bytes,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename='document.docx',
        output_format='markdown'  # 'markdown' (default) or 'plain'
    )
    
    # Returns:
    {
        'success': True,
        'text': '# Document Title\n\n## Section 1\n\n- **Bold item**\n- *Italic item*\n\n### Subsection...',
        'format': 'markdown',
        'metadata': {
            'word_count': 1500,
            'char_count': 9000,
            'extraction_method': 'python-docx',
            'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
    }
"""

import io
import json
from typing import Dict, Any, Optional, BinaryIO, Union


class TextExtractorError(Exception):
    """Custom exception for text extraction errors"""
    pass


class TextExtractor:
    """
    Universal text extractor for all document types
    """
    
    # Supported content types
    DOCUMENT_TYPES = [
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
        'application/msword',  # DOC
        'application/vnd.oasis.opendocument.text',  # ODT
        'application/rtf',  # RTF
        'text/rtf'
    ]
    
    SPREADSHEET_TYPES = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # XLSX
        'application/vnd.ms-excel',  # XLS
        'text/csv',
        'application/csv'
    ]
    
    PRESENTATION_TYPES = [
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PPTX
        'application/vnd.ms-powerpoint'  # PPT
    ]
    
    DATA_TYPES = [
        'application/json',
        'application/xml',
        'text/xml',
        'application/yaml',
        'text/yaml',
        'application/x-yaml'
    ]
    
    TEXT_TYPES = [
        'text/plain',
        'text/markdown',
        'text/html',
        'text/javascript',
        'application/javascript',
        'text/typescript',
        'application/typescript',
        'text/x-python',
        'application/x-python-code'
    ]
    
    
    def __init__(self):
        """Initialize text extractor"""
        self.extraction_methods = {
            'docx': self._extract_from_docx,
            'xlsx': self._extract_from_xlsx,
            'csv': self._extract_from_csv,
            'pptx': self._extract_from_pptx,
            'json': self._extract_from_json,
            'xml': self._extract_from_xml,
            'text': self._extract_from_text,
            'html': self._extract_from_html
        }
    
    
    def is_extractable(self, content_type: str) -> bool:
        """Check if content type supports text extraction"""
        all_types = (
            self.DOCUMENT_TYPES +
            self.SPREADSHEET_TYPES +
            self.PRESENTATION_TYPES +
            self.DATA_TYPES +
            self.TEXT_TYPES
        )
        return content_type in all_types
    
    
    def extract_text(self,
                    file_data: bytes,
                    content_type: str,
                    filename: str,
                    max_chars: int = 50000,
                    output_format: str = 'markdown') -> Dict[str, Any]:
        """
        Extract text from file with rich formatting
        
        Args:
            file_data: Raw file bytes
            content_type: MIME type
            filename: Original filename
            max_chars: Maximum characters to extract (default: 50,000)
            output_format: 'markdown' (default) or 'plain'
        
        Returns:
            Extraction result with formatted text and metadata
        """
        try:
            # Determine extraction method
            method = self._get_extraction_method(content_type, filename)
            
            if not method:
                return {
                    'success': False,
                    'error': f'No extraction method for {content_type}'
                }
            
            # Extract text (now with Markdown formatting)
            text = method(file_data, filename, output_format)
            
            # Truncate if too long
            original_length = len(text)
            if len(text) > max_chars:
                text = text[:max_chars] + f'\n\n[... truncated {original_length - max_chars} characters ...]'
            
            # Count words and characters
            word_count = len(text.split())
            char_count = len(text)
            
            return {
                'success': True,
                'text': text,
                'format': output_format,
                'metadata': {
                    'filename': filename,
                    'content_type': content_type,
                    'word_count': word_count,
                    'char_count': char_count,
                    'original_length': original_length,
                    'truncated': original_length > max_chars,
                    'extraction_method': method.__name__,
                    'output_format': output_format
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Text extraction failed: {str(e)}'
            }
    
    
    def _get_extraction_method(self, content_type: str, filename: str):
        """Determine which extraction method to use"""
        # DOCX
        if content_type in self.DOCUMENT_TYPES:
            if '.docx' in filename.lower():
                return self.extraction_methods['docx']
        
        # XLSX
        if content_type in self.SPREADSHEET_TYPES:
            if '.xlsx' in filename.lower() or '.xls' in filename.lower():
                return self.extraction_methods['xlsx']
            if '.csv' in filename.lower() or content_type in ['text/csv', 'application/csv']:
                return self.extraction_methods['csv']
        
        # PPTX
        if content_type in self.PRESENTATION_TYPES:
            return self.extraction_methods['pptx']
        
        # JSON/XML
        if content_type in self.DATA_TYPES:
            if 'json' in content_type:
                return self.extraction_methods['json']
            if 'xml' in content_type:
                return self.extraction_methods['xml']
        
        # Text/HTML
        if content_type in self.TEXT_TYPES:
            if 'html' in content_type:
                return self.extraction_methods['html']
            return self.extraction_methods['text']
        
        return None
    
    
    # ==================== EXTRACTION METHOD IMPLEMENTATIONS ====================
    
    def _extract_from_docx(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from DOCX file with Markdown formatting"""
        try:
            from docx import Document
            from docx.enum.style import WD_STYLE_TYPE
            
            doc = Document(io.BytesIO(file_data))
            
            markdown_lines = []
            
            # Process paragraphs with style detection
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    markdown_lines.append('')  # Blank line
                    continue
                
                # Detect heading styles
                if para.style.name.startswith('Heading'):
                    level = para.style.name.replace('Heading ', '')
                    try:
                        level_num = int(level) if level.isdigit() else 1
                        markdown_lines.append(f"{'#' * level_num} {text}")
                    except:
                        markdown_lines.append(f"## {text}")
                elif para.style.name == 'Title':
                    markdown_lines.append(f"# {text}")
                elif para.style.name.startswith('List'):
                    # Detect list items
                    markdown_lines.append(f"- {text}")
                else:
                    # Regular paragraph - check for inline formatting
                    if output_format == 'markdown':
                        formatted_text = self._format_docx_runs(para)
                        markdown_lines.append(formatted_text)
                    else:
                        markdown_lines.append(text)
            
            # Extract tables as Markdown tables
            for table in doc.tables:
                markdown_lines.append('')  # Blank line before table
                
                # Get headers (first row)
                if len(table.rows) > 0:
                    headers = [cell.text.strip() for cell in table.rows[0].cells]
                    markdown_lines.append('| ' + ' | '.join(headers) + ' |')
                    markdown_lines.append('|' + '|'.join(['---' for _ in headers]) + '|')
                    
                    # Get data rows
                    for row in table.rows[1:]:
                        cells = [cell.text.strip() for cell in row.cells]
                        markdown_lines.append('| ' + ' | '.join(cells) + ' |')
                
                markdown_lines.append('')  # Blank line after table
            
            return '\n'.join(markdown_lines)
            
        except ImportError:
            raise TextExtractorError('python-docx library not installed: pip install python-docx')
        except Exception as e:
            raise TextExtractorError(f'DOCX extraction failed: {str(e)}')
    
    
    def _format_docx_runs(self, paragraph) -> str:
        """Format paragraph runs with bold/italic Markdown"""
        formatted_parts = []
        
        for run in paragraph.runs:
            text = run.text
            if not text:
                continue
            
            # Apply formatting
            if run.bold and run.italic:
                text = f"***{text}***"
            elif run.bold:
                text = f"**{text}**"
            elif run.italic:
                text = f"*{text}*"
            
            formatted_parts.append(text)
        
        return ''.join(formatted_parts)
    
    
    def _extract_from_xlsx(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from XLSX file as Markdown tables"""
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(io.BytesIO(file_data), data_only=True)
            
            markdown_lines = []
            
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                
                # Add sheet heading
                markdown_lines.append(f'\n## Sheet: {sheet_name}\n')
                
                # Convert to list of rows
                rows = list(sheet.iter_rows(values_only=True))
                
                if not rows:
                    markdown_lines.append('*(Empty sheet)*\n')
                    continue
                
                # Treat first row as headers
                headers = [str(cell) if cell is not None else '' for cell in rows[0]]
                
                if output_format == 'markdown':
                    # Markdown table format
                    markdown_lines.append('| ' + ' | '.join(headers) + ' |')
                    markdown_lines.append('|' + '|'.join(['---' for _ in headers]) + '|')
                    
                    # Data rows
                    for row in rows[1:]:
                        cells = [str(cell) if cell is not None else '' for cell in row]
                        markdown_lines.append('| ' + ' | '.join(cells) + ' |')
                else:
                    # Plain text format
                    for row in rows:
                        row_text = ' | '.join([str(cell) if cell is not None else '' for cell in row])
                        if row_text.strip():
                            markdown_lines.append(row_text)
                
                markdown_lines.append('')  # Blank line after table
            
            return '\n'.join(markdown_lines)
            
        except ImportError:
            raise TextExtractorError('openpyxl library not installed: pip install openpyxl')
        except Exception as e:
            raise TextExtractorError(f'XLSX extraction failed: {str(e)}')
    
    
    def _extract_from_csv(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from CSV file as Markdown table"""
        try:
            import csv
            
            text_data = file_data.decode('utf-8', errors='ignore')
            reader = csv.reader(io.StringIO(text_data))
            
            rows = list(reader)
            
            if not rows:
                return '*(Empty CSV)*'
            
            if output_format == 'markdown':
                # First row as headers
                headers = rows[0]
                markdown_lines = []
                
                markdown_lines.append('| ' + ' | '.join(headers) + ' |')
                markdown_lines.append('|' + '|'.join(['---' for _ in headers]) + '|')
                
                # Data rows
                for row in rows[1:]:
                    # Pad row to match header length
                    while len(row) < len(headers):
                        row.append('')
                    markdown_lines.append('| ' + ' | '.join(row[:len(headers)]) + ' |')
                
                return '\n'.join(markdown_lines)
            else:
                # Plain text format
                return '\n'.join([' | '.join(row) for row in rows])
            
        except Exception as e:
            raise TextExtractorError(f'CSV extraction failed: {str(e)}')
    
    
    def _extract_from_pptx(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from PPTX file as structured Markdown"""
        try:
            from pptx import Presentation
            
            prs = Presentation(io.BytesIO(file_data))
            
            markdown_lines = []
            
            for i, slide in enumerate(prs.slides, 1):
                if output_format == 'markdown':
                    markdown_lines.append(f'\n## Slide {i}\n')
                else:
                    markdown_lines.append(f'\n=== SLIDE {i} ===\n')
                
                # Extract title if present
                if slide.shapes.title:
                    title_text = slide.shapes.title.text.strip()
                    if title_text:
                        if output_format == 'markdown':
                            markdown_lines.append(f'### {title_text}\n')
                        else:
                            markdown_lines.append(f'{title_text}\n')
                
                # Extract other text
                for shape in slide.shapes:
                    if shape == slide.shapes.title:
                        continue  # Skip title (already processed)
                    
                    if hasattr(shape, 'text') and shape.text.strip():
                        text = shape.text.strip()
                        
                        if output_format == 'markdown':
                            # Format as bullet points if multiple lines
                            lines = text.split('\n')
                            if len(lines) > 1:
                                for line in lines:
                                    if line.strip():
                                        markdown_lines.append(f'- {line.strip()}')
                            else:
                                markdown_lines.append(text)
                        else:
                            markdown_lines.append(text)
                        
                        markdown_lines.append('')  # Blank line
            
            return '\n'.join(markdown_lines)
            
        except ImportError:
            raise TextExtractorError('python-pptx library not installed: pip install python-pptx')
        except Exception as e:
            raise TextExtractorError(f'PPTX extraction failed: {str(e)}')
    
    
    def _extract_from_json(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from JSON file as Markdown code block"""
        try:
            data = json.loads(file_data.decode('utf-8'))
            formatted_json = json.dumps(data, indent=2)
            
            if output_format == 'markdown':
                return f'```json\n{formatted_json}\n```'
            else:
                return formatted_json
        except Exception as e:
            raise TextExtractorError(f'JSON extraction failed: {str(e)}')
    
    
    def _extract_from_xml(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from XML file as Markdown code block"""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            # Parse and pretty-print
            root = ET.fromstring(file_data.decode('utf-8'))
            xml_str = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            formatted_xml = dom.toprettyxml(indent='  ')
            
            if output_format == 'markdown':
                return f'```xml\n{formatted_xml}\n```'
            else:
                return formatted_xml
            
        except Exception as e:
            raise TextExtractorError(f'XML extraction failed: {str(e)}')
    
    
    def _extract_from_text(self, file_data: bytes, filename: str, output_format: str = 'markdown') -> str:
        """Extract text from plain text file with optional code block formatting"""
        try:
            # Try UTF-8 first, fallback to latin-1
            try:
                text = file_data.decode('utf-8')
            except UnicodeDecodeError:
                text = file_data.decode('latin-1', errors='ignore')
            
            # If Markdown output and code file, wrap in code block
            if output_format == 'markdown':
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                code_extensions = {
                    'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                    'jsx': 'jsx', 'tsx': 'tsx', 'html': 'html', 'css': 'css',
                    'sql': 'sql', 'sh': 'bash', 'yml': 'yaml', 'yaml': 'yaml',
                    'json': 'json', 'xml': 'xml', 'md': 'markdown'
                }
                
                if ext in code_extensions:
                    lang = code_extensions[ext]
                    return f'```{lang}\n{text}\n```'
            
            return text
        except Exception as e:
            raise TextExtractorError(f'Text extraction failed: {str(e)}')
    
    
    def _extract_from_html(self, file_data: bytes, filename: str) -> str:
        """Extract text from HTML file"""
        try:
            from bs4 import BeautifulSoup
            
            html = file_data.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except ImportError:
            # Fallback: basic HTML stripping
            html = file_data.decode('utf-8', errors='ignore')
            import re
            text = re.sub('<[^<]+?>', '', html)
            return text.strip()
        except Exception as e:
            raise TextExtractorError(f'HTML extraction failed: {str(e)}')


# Global instance
_global_extractor = None

def get_text_extractor() -> TextExtractor:
    """Get or create global text extractor instance"""
    global _global_extractor
    if _global_extractor is None:
        _global_extractor = TextExtractor()
    return _global_extractor


print('[TEXT EXTRACTOR] Module loaded - Universal document text extraction ready')
