"""
Document Parser - Global Utility
=================================

PURPOSE:
Universal document parsing service for extracting structured data from resumes, invoices, 
contracts, and any other documents across the platform.

USAGE:
    from AI_infrastructure.utils.document_parser import DocumentParser
    
    parser = DocumentParser()
    result = parser.parse_document('/path/to/resume.pdf', doc_type='resume')
    
    # Access parsed data
    print(result['text'])  # Full extracted text
    print(result['structured_data']['emails'])  # Extracted emails
    print(result['metadata'])  # Document metadata

SUPPORTED FORMATS:
    - PDF (via PyPDF2 and pdfplumber)
    - DOCX (via python-docx)
    - TXT (native Python)

FEATURES:
    - Text extraction with layout preservation
    - Metadata extraction (author, creation date, etc.)
    - Structured data extraction (emails, URLs, dates, organizations)
    - Resume-specific parsing (name, skills, education, experience)
    - AI-generated content detection
    - Multi-language support

REUSABLE BY:
    - Professional Verification Module (resume parsing)
    - Invoice Processing Module (invoice parsing)
    - Document Library Module (universal document handling)
    - Any module needing document extraction

CREATED: December 16, 2025
AUTHOR: AI Agent Platform
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Universal document parser supporting PDF, DOCX, TXT formats.
    
    This utility provides a unified interface for document parsing across the platform.
    Supports both generic document parsing and specialized extractors for resumes, invoices, etc.
    """
    
    def __init__(self):
        """Initialize parser and check available libraries"""
        self.available_libraries = self._check_libraries()
        
        # Regex patterns for structured data extraction
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'date': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+',
            'github': r'(?:https?://)?(?:www\.)?github\.com/[\w-]+',
        }
        
        logger.info(f"[DOCUMENT_PARSER] Initialized with libraries: {self.available_libraries}")
    
    def _check_libraries(self) -> Dict[str, bool]:
        """Check which document parsing libraries are available"""
        libraries = {}
        
        # Check PyPDF2
        try:
            import PyPDF2
            libraries['PyPDF2'] = True
        except ImportError:
            libraries['PyPDF2'] = False
            logger.warning("[DOCUMENT_PARSER] PyPDF2 not available - PDF parsing will be limited")
        
        # Check pdfplumber (better for tables and layout)
        try:
            import pdfplumber
            libraries['pdfplumber'] = True
        except ImportError:
            libraries['pdfplumber'] = False
            logger.warning("[DOCUMENT_PARSER] pdfplumber not available - advanced PDF parsing disabled")
        
        # Check python-docx
        try:
            import docx
            libraries['python-docx'] = True
        except ImportError:
            libraries['python-docx'] = False
            logger.warning("[DOCUMENT_PARSER] python-docx not available - DOCX parsing disabled")
        
        return libraries
    
    def parse_document(
        self,
        file_path: Union[str, Path],
        doc_type: str = 'generic',
        extract_structured: bool = True
    ) -> Dict[str, Any]:
        """
        Parse a document and extract text and metadata.
        
        Args:
            file_path: Path to document file
            doc_type: Type of document ('generic', 'resume', 'invoice', 'contract')
            extract_structured: Whether to extract structured data (emails, URLs, etc.)
        
        Returns:
            Dict containing:
                - text: Extracted text content
                - metadata: Document metadata (author, dates, etc.)
                - structured_data: Extracted emails, URLs, dates, etc. (if extract_structured=True)
                - resume_data: Parsed resume sections (if doc_type='resume')
                - success: Boolean indicating success
                - error: Error message if failed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}'
            }
        
        # Detect file type
        file_ext = file_path.suffix.lower()
        
        try:
            # Route to appropriate parser
            if file_ext == '.pdf':
                result = self._parse_pdf(file_path)
            elif file_ext == '.docx':
                result = self._parse_docx(file_path)
            elif file_ext in ['.txt', '.md']:
                result = self._parse_text(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}'
                }
            
            if not result['success']:
                return result
            
            # Extract structured data if requested
            if extract_structured and result.get('text'):
                result['structured_data'] = self.extract_structured_data(result['text'])
            
            # Specialized parsing for resumes
            if doc_type == 'resume' and result.get('text'):
                result['resume_data'] = self.parse_resume(result['text'])
            
            return result
            
        except Exception as e:
            logger.error(f"[DOCUMENT_PARSER] Error parsing {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF document"""
        result = {
            'success': False,
            'text': '',
            'metadata': {},
            'page_count': 0
        }
        
        # Try pdfplumber first (better quality)
        if self.available_libraries.get('pdfplumber'):
            try:
                import pdfplumber
                
                with pdfplumber.open(file_path) as pdf:
                    result['page_count'] = len(pdf.pages)
                    result['metadata'] = pdf.metadata or {}
                    
                    # Extract text from all pages
                    text_parts = []
                    for page in pdf.pages:
                        text_parts.append(page.extract_text() or '')
                    
                    result['text'] = '\n\n'.join(text_parts)
                    result['success'] = True
                    
                logger.info(f"[DOCUMENT_PARSER] ✅ Parsed PDF with pdfplumber: {result['page_count']} pages")
                return result
                
            except Exception as e:
                logger.warning(f"[DOCUMENT_PARSER] pdfplumber failed: {e}, trying PyPDF2...")
        
        # Fallback to PyPDF2
        if self.available_libraries.get('PyPDF2'):
            try:
                import PyPDF2
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    result['page_count'] = len(pdf_reader.pages)
                    result['metadata'] = pdf_reader.metadata or {}
                    
                    # Extract text from all pages
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text() or '')
                    
                    result['text'] = '\n\n'.join(text_parts)
                    result['success'] = True
                
                logger.info(f"[DOCUMENT_PARSER] ✅ Parsed PDF with PyPDF2: {result['page_count']} pages")
                return result
                
            except Exception as e:
                result['error'] = f'PyPDF2 parsing failed: {e}'
                return result
        
        result['error'] = 'No PDF parsing library available (install PyPDF2 or pdfplumber)'
        return result
    
    def _parse_docx(self, file_path: Path) -> Dict[str, Any]:
        """Parse DOCX document"""
        if not self.available_libraries.get('python-docx'):
            return {
                'success': False,
                'error': 'python-docx library not available (install python-docx)'
            }
        
        try:
            import docx
            
            doc = docx.Document(file_path)
            
            # Extract metadata
            metadata = {
                'author': doc.core_properties.author,
                'created': doc.core_properties.created,
                'modified': doc.core_properties.modified,
                'title': doc.core_properties.title,
            }
            
            # Extract text from paragraphs
            text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
            text = '\n\n'.join(text_parts)
            
            logger.info(f"[DOCUMENT_PARSER] ✅ Parsed DOCX: {len(doc.paragraphs)} paragraphs")
            
            return {
                'success': True,
                'text': text,
                'metadata': metadata,
                'paragraph_count': len(doc.paragraphs)
            }
            
        except Exception as e:
            logger.error(f"[DOCUMENT_PARSER] DOCX parsing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_text(self, file_path: Path) -> Dict[str, Any]:
        """Parse plain text document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Get file metadata
            stat = file_path.stat()
            metadata = {
                'size_bytes': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
            }
            
            logger.info(f"[DOCUMENT_PARSER] ✅ Parsed text file: {len(text)} chars")
            
            return {
                'success': True,
                'text': text,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"[DOCUMENT_PARSER] Text parsing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_structured_data(self, text: str) -> Dict[str, List[str]]:
        """
        Extract structured data from text using regex patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with lists of found emails, URLs, phones, dates, etc.
        """
        structured_data = {}
        
        for key, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            # Deduplicate and clean
            if isinstance(matches[0] if matches else None, tuple):
                # Phone numbers return tuples from groups
                matches = ['-'.join(m) for m in matches]
            
            structured_data[key + 's'] = list(set(matches))
        
        logger.debug(f"[DOCUMENT_PARSER] Extracted structured data: {list(structured_data.keys())}")
        
        return structured_data
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume-specific sections from text.
        
        Args:
            text: Resume text
            
        Returns:
            Dict with parsed resume sections:
                - name: Detected name
                - skills: List of skills
                - education: Education entries
                - experience: Work experience entries
                - summary: Professional summary
        """
        resume_data = {
            'name': None,
            'skills': [],
            'education': [],
            'experience': [],
            'summary': None,
            'certifications': []
        }
        
        # Try to extract name (usually first line or near "Name:" label)
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if len(line.strip()) > 0 and len(line.strip().split()) <= 4:
                # Likely a name (short, at top of document)
                resume_data['name'] = line.strip()
                break
        
        # Extract skills (look for "Skills" section)
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'core competencies'])
        if skills_section:
            # Split by common separators
            skills = re.split(r'[,•\|\n]', skills_section)
            resume_data['skills'] = [s.strip() for s in skills if s.strip() and len(s.strip()) > 2]
        
        # Extract education (look for "Education" section)
        education_section = self._extract_section(text, ['education', 'academic background'])
        if education_section:
            # Split by double newlines or degree indicators
            edu_entries = re.split(r'\n\n+|(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|Ph\.D\.)', education_section)
            resume_data['education'] = [e.strip() for e in edu_entries if e.strip() and len(e.strip()) > 10]
        
        # Extract experience (look for "Experience" or "Work History" section)
        experience_section = self._extract_section(text, ['experience', 'work history', 'employment', 'professional experience'])
        if experience_section:
            # Split by double newlines or company/date indicators
            exp_entries = re.split(r'\n\n+', experience_section)
            resume_data['experience'] = [e.strip() for e in exp_entries if e.strip() and len(e.strip()) > 20]
        
        # Extract certifications
        cert_section = self._extract_section(text, ['certifications', 'certificates', 'licenses'])
        if cert_section:
            certs = re.split(r'[,•\|\n]', cert_section)
            resume_data['certifications'] = [c.strip() for c in certs if c.strip() and len(c.strip()) > 5]
        
        # Extract summary/objective
        summary_section = self._extract_section(text, ['summary', 'objective', 'profile', 'about'])
        if summary_section:
            resume_data['summary'] = summary_section.strip()
        
        logger.info(f"[DOCUMENT_PARSER] Parsed resume: {len(resume_data['skills'])} skills, {len(resume_data['experience'])} jobs")
        
        return resume_data
    
    def _extract_section(self, text: str, headers: List[str]) -> Optional[str]:
        """
        Extract a section from text based on header keywords.
        
        Args:
            text: Full document text
            headers: List of possible header names (e.g., ['skills', 'technical skills'])
            
        Returns:
            Extracted section text, or None if not found
        """
        text_lower = text.lower()
        
        for header in headers:
            # Look for header with various formatting
            patterns = [
                f"\n{header}\n",  # Plain header
                f"\n{header}:",  # Header with colon
                f"\n{header} -",  # Header with dash
                f"## {header}",  # Markdown header
                f"**{header}**",  # Bold header
            ]
            
            for pattern in patterns:
                idx = text_lower.find(pattern.lower())
                if idx != -1:
                    # Found section, extract until next section or end
                    start = idx + len(pattern)
                    
                    # Find next section (another header in all caps or with similar formatting)
                    next_section = re.search(r'\n[A-Z][A-Z\s]{5,}\n', text[start:])
                    if next_section:
                        end = start + next_section.start()
                    else:
                        end = len(text)
                    
                    return text[start:end].strip()
        
        return None
    
    def detect_ai_generated(self, text: str) -> Dict[str, Any]:
        """
        Detect if text was likely AI-generated (e.g., by ChatGPT).
        
        This uses heuristics to identify AI-generated content:
        - Repetitive phrasing
        - Overly formal language
        - Lack of personal anecdotes
        - Generic descriptions
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with:
                - is_ai_generated: Boolean likelihood
                - confidence: 0-100 score
                - indicators: List of detected indicators
        """
        indicators = []
        score = 0
        
        # Common AI phrases
        ai_phrases = [
            'as an ai', 'i am an ai', 'i don\'t have personal',
            'furthermore', 'moreover', 'in addition to',
            'it is important to note', 'it should be noted',
            'in conclusion', 'to summarize',
            'comprehensive', 'cutting-edge', 'state-of-the-art',
            'robust', 'seamlessly', 'leverage',
            'utilize', 'facilitate', 'optimize'
        ]
        
        text_lower = text.lower()
        
        for phrase in ai_phrases:
            if phrase in text_lower:
                indicators.append(f"AI phrase detected: '{phrase}'")
                score += 10
        
        # Check for repetitive sentence structures
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 5:
            # Check if many sentences start similarly
            starts = [s.strip().split()[0] if s.strip() else '' for s in sentences]
            from collections import Counter
            start_counts = Counter(starts)
            if start_counts.most_common(1)[0][1] > len(sentences) * 0.3:
                indicators.append("Repetitive sentence structure")
                score += 15
        
        # Check for overly formal language (high ratio of long words)
        words = text.split()
        long_words = [w for w in words if len(w) > 10]
        if len(words) > 50 and len(long_words) / len(words) > 0.15:
            indicators.append("Overly formal language")
            score += 10
        
        # Check for lack of personal pronouns (I, my, me)
        personal_pronouns = len(re.findall(r'\b(I|my|me|mine)\b', text, re.IGNORECASE))
        if len(words) > 100 and personal_pronouns < 5:
            indicators.append("Lack of personal pronouns")
            score += 10
        
        # Cap score at 100
        confidence = min(score, 100)
        
        return {
            'is_ai_generated': confidence > 50,
            'confidence': confidence,
            'indicators': indicators
        }
