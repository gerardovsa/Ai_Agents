"""
Vector Database Tools - Autonomous AI-controlled document search and retrieval

PURPOSE: Give AI agents control over when and how to search vector databases
         instead of automatic snippet injection every message.

FEATURES:
- AI-initiated searches (not automatic)
- Metadata-rich results with cloud storage links
- Full document retrieval from Google Drive/OneDrive
- Namespace/collection management
- Smart chunking with context preservation

DEPENDENCIES:
- Pinecone (cloud vector database)
- OpenAI embeddings
- Google Drive/OneDrive APIs (for full doc retrieval)

ARCHITECTURE:
┌─────────────────────────────────────────────────────┐
│ AI Agent                                            │
│ "I need info about return policy"                  │
└────────────────┬────────────────────────────────────┘
                 │ Decides to search (not automatic)
                 ▼
┌─────────────────────────────────────────────────────┐
│ vector_db_search(query="return policy")            │
│ Returns: 5 snippets + metadata + cloud URLs        │
└────────────────┬────────────────────────────────────┘
                 │ Snippets not enough?
                 ▼
┌─────────────────────────────────────────────────────┐
│ vector_db_get_full_document(doc_id)                │
│ Fetches from Google Drive → Full text              │
└─────────────────────────────────────────────────────┘

LAST MODIFIED: 2025-11-29
"""

from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime
import uuid

# Pinecone imports (handle package rename from pinecone-client to pinecone)
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except (ImportError, Exception) as e:
    PINECONE_AVAILABLE = False
    if "renamed from `pinecone-client` to `pinecone`" in str(e):
        print("⚠️  Pinecone package conflict detected. Run: pip uninstall pinecone-client && pip install pinecone")
    else:
        print("⚠️  Pinecone not installed. Install: pip install pinecone")

# OpenAI embeddings
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Install: pip install openai")

# Google Drive integration (optional)
try:
    from google_workspace.google_docs import get_user_drive_service
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Document extraction libraries
try:
    import PyPDF2
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    print("⚠️  PyPDF2 not installed. PDF extraction unavailable.")

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not installed. DOCX extraction unavailable.")

try:
    import openpyxl
    import csv
    import pandas as pd
    SPREADSHEET_AVAILABLE = True
except ImportError:
    SPREADSHEET_AVAILABLE = False
    print("⚠️  openpyxl/pandas not installed. Spreadsheet extraction unavailable.")


class VectorDatabaseError(Exception):
    """Custom exception for vector database errors"""
    pass


class VectorDatabaseManager:
    """
    Manages vector database operations with Pinecone
    
    Features:
    - Embedding generation (OpenAI)
    - Vector search with metadata
    - Document retrieval from cloud storage
    - Namespace management
    """
    
    def __init__(self, **kwargs):
        """
        Initialize with credentials from database or environment
        
        Credentials injected via:
        - pinecone_api_key (from database)
        - pinecone_index_name (from database)
        - openai_api_key (from database)
        - voyager_api_key (from database, alternative to OpenAI)
        """
        # Get credentials from kwargs (injected) or fallback to environment
        self.pinecone_api_key = kwargs.get('pinecone_api_key') or os.getenv('PINECONE_API_KEY')
        self.pinecone_index_name = kwargs.get('pinecone_index_name') or os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors')
        self.openai_api_key = kwargs.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        self.voyager_api_key = kwargs.get('voyager_api_key')
        
        # Initialize clients
        self.pinecone_client = None
        self.openai_client = None
        self.index = None
        
        # Initialize if credentials available
        if PINECONE_AVAILABLE and self.pinecone_api_key:
            self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        print(f"[VECTOR DB] Initialized - Pinecone: {'✅' if self.pinecone_client else '❌'}, Embeddings: {'✅' if self.openai_client or self.voyager_api_key else '❌'}")
    
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists, create if needed"""
        if not self.pinecone_client:
            raise VectorDatabaseError("Pinecone client not initialized. Set PINECONE_API_KEY environment variable.")
        
        # List existing indexes
        indexes = self.pinecone_client.list_indexes()
        index_names = [idx['name'] for idx in indexes]
        
        if self.pinecone_index_name not in index_names:
            print(f"Creating Pinecone index: {self.pinecone_index_name}")
            self.pinecone_client.create_index(
                name=self.pinecone_index_name,
                dimension=1536,  # OpenAI text-embedding-ada-002 dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"✅ Index created: {self.pinecone_index_name}")
        
        # Connect to index
        self.index = self.pinecone_client.Index(self.pinecone_index_name)
        return self.index
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI"""
        if not self.openai_client:
            raise VectorDatabaseError("OpenAI client not initialized. Set OPENAI_API_KEY environment variable.")
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise VectorDatabaseError(f"Failed to generate embedding: {str(e)}")
    
    @staticmethod
    def _extract_text_from_file(file_path: str) -> str:
        """
        Extract text from various file formats including spreadsheets
        
        Supported formats:
        - PDF (.pdf)
        - Word (.docx, .doc)
        - Excel (.xlsx, .xls)
        - CSV (.csv)
        - TSV (.tsv)
        - Text (.txt, .md, .json, .xml, .yml, .yaml, etc.)
        
        Returns:
            Extracted text content
        """
        import io
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # Text files
            if ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.yml', '.yaml', 
                       '.toml', '.ini', '.cfg', '.log', '.rst', '.adoc', '.tex', '.latex']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            # PDF files
            elif ext == '.pdf':
                if not PYPDF_AVAILABLE:
                    raise VectorDatabaseError("PyPDF2 not installed. Install: pip install PyPDF2")
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = []
                    for page in reader.pages:
                        text.append(page.extract_text())
                    return '\n\n'.join(text)
            
            # Word documents
            elif ext in ['.docx', '.doc']:
                if not DOCX_AVAILABLE:
                    raise VectorDatabaseError("python-docx not installed. Install: pip install python-docx")
                doc = DocxDocument(file_path)
                return '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # Excel files (.xlsx, .xls)
            elif ext in ['.xlsx', '.xls']:
                if not SPREADSHEET_AVAILABLE:
                    raise VectorDatabaseError("openpyxl/pandas not installed. Install: pip install openpyxl pandas")
                
                # Use pandas for comprehensive extraction
                excel_file = pd.ExcelFile(file_path)
                sheets_text = []
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    
                    # Convert dataframe to readable text format
                    sheet_text = [f"# Sheet: {sheet_name}\n"]
                    
                    # Add column headers
                    headers = ' | '.join(str(col) for col in df.columns)
                    sheet_text.append(headers)
                    sheet_text.append('-' * len(headers))
                    
                    # Add rows
                    for _, row in df.iterrows():
                        row_text = ' | '.join(str(val) if pd.notna(val) else '' for val in row)
                        sheet_text.append(row_text)
                    
                    sheets_text.append('\n'.join(sheet_text))
                
                return '\n\n'.join(sheets_text)
            
            # CSV files
            elif ext == '.csv':
                if not SPREADSHEET_AVAILABLE:
                    # Fallback to simple text reading
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                
                # Use pandas for better handling
                df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
                text_lines = []
                
                # Add headers
                headers = ' | '.join(str(col) for col in df.columns)
                text_lines.append(headers)
                text_lines.append('-' * len(headers))
                
                # Add rows
                for _, row in df.iterrows():
                    row_text = ' | '.join(str(val) if pd.notna(val) else '' for val in row)
                    text_lines.append(row_text)
                
                return '\n'.join(text_lines)
            
            # TSV files
            elif ext == '.tsv':
                if not SPREADSHEET_AVAILABLE:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8', errors='ignore')
                text_lines = []
                
                headers = ' | '.join(str(col) for col in df.columns)
                text_lines.append(headers)
                text_lines.append('-' * len(headers))
                
                for _, row in df.iterrows():
                    row_text = ' | '.join(str(val) if pd.notna(val) else '' for val in row)
                    text_lines.append(row_text)
                
                return '\n'.join(text_lines)
            
            else:
                raise VectorDatabaseError(f"Unsupported file format: {ext}")
        
        except Exception as e:
            raise VectorDatabaseError(f"Text extraction failed for {ext}: {str(e)}")
    
    def search(
        self,
        query: str,
        namespace: str = "default",
        top_k: int = 5,
        min_score: float = 0.7,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Search vector database for relevant documents
        
        Args:
            query: Search query text
            namespace: Pinecone namespace to search
            top_k: Number of results to return
            min_score: Minimum similarity score threshold (0-1)
            include_metadata: Include full document metadata
        
        Returns:
            Dict with search results and metadata
        """
        try:
            # Ensure index exists
            index = self._ensure_index_exists()
            
            # Generate query embedding
            print(f"🔍 Generating embedding for query: {query[:50]}...")
            query_vector = self._generate_embedding(query)
            
            # Search Pinecone
            print(f"🔍 Searching namespace '{namespace}' for top {top_k} results...")
            search_results = index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=include_metadata
            )
            
            # Filter by minimum score
            filtered_matches = [
                match for match in search_results['matches']
                if match['score'] >= min_score
            ]
            
            print(f"✅ Found {len(filtered_matches)} results (min_score: {min_score})")
            
            # Format results
            results = []
            for match in filtered_matches:
                result = {
                    'id': match['id'],
                    'score': round(match['score'], 4),
                    'text': match.get('metadata', {}).get('text', '')[:400] + '...',  # 400 char snippet
                    'metadata': match.get('metadata', {}) if include_metadata else {}
                }
                results.append(result)
            
            return {
                'success': True,
                'query': query,
                'results_count': len(results),
                'namespace': namespace,
                'results': results,
                'next_actions': {
                    'fetch_full_doc': 'Use vector_db_get_full_document(document_id) to retrieve complete file',
                    'refine_search': 'Adjust query or min_score to refine results',
                    'search_again': 'Try different query terms'
                }
            }
        
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'namespace': namespace
            }
    
    def get_full_document(
        self,
        document_id: str,
        namespace: str = "default",
        format: str = "text",
        fetch_from_cloud: bool = True,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve complete document from cloud storage or cache
        
        Args:
            document_id: Document ID from search results
            namespace: Pinecone namespace
            format: Return format ('text', 'markdown', 'json')
            fetch_from_cloud: Fetch latest from Google Drive/OneDrive
            user_id: User ID for credential injection (Google Drive access)
        
        Returns:
            Dict with full document text and metadata
        """
        try:
            # First, get document metadata from vector DB
            index = self._ensure_index_exists()
            
            # Query for all chunks of this document
            print(f"📄 Retrieving document chunks for: {document_id}")
            
            # Search for all chunks matching document_id
            # Use a broad query with metadata filter
            dummy_vector = [0.0] * 1536  # Placeholder vector
            results = index.query(
                vector=dummy_vector,
                top_k=100,  # Get all chunks
                namespace=namespace,
                filter={'document_id': document_id},
                include_metadata=True
            )
            
            if not results['matches']:
                return {
                    'success': False,
                    'error': f"Document not found: {document_id}",
                    'document_id': document_id
                }
            
            # Sort chunks by chunk_index
            chunks = sorted(results['matches'], key=lambda x: x.get('metadata', {}).get('chunk_index', 0))
            
            # Get metadata from first chunk
            metadata = chunks[0].get('metadata', {})
            
            # Reconstruct full text from chunks
            full_text = '\n\n'.join([
                chunk.get('metadata', {}).get('text', '') 
                for chunk in chunks
            ])
            
            # Try to fetch from cloud storage if requested
            cloud_fetched = False
            if fetch_from_cloud and GOOGLE_DRIVE_AVAILABLE:
                cloud_storage = metadata.get('cloud_storage', {})
                if cloud_storage.get('provider') == 'google_drive' and user_id:
                    try:
                        print(f"☁️  Fetching latest version from Google Drive...")
                        drive_service = get_user_drive_service(user_id=user_id)
                        file_id = cloud_storage.get('file_id')
                        
                        if file_id and drive_service:
                            # Fetch file content from Drive
                            request = drive_service.files().get_media(fileId=file_id)
                            content = request.execute()
                            full_text = content.decode('utf-8') if isinstance(content, bytes) else str(content)
                            cloud_fetched = True
                            print(f"✅ Fetched from Google Drive")
                    except Exception as e:
                        print(f"⚠️  Cloud fetch failed, using cached version: {str(e)}")
            
            # Format output
            if format == 'markdown':
                full_text = f"# {metadata.get('filename', 'Document')}\n\n{full_text}"
            
            return {
                'success': True,
                'document_id': document_id,
                'filename': metadata.get('filename', 'unknown'),
                'full_text': full_text,
                'metadata': {
                    'file_type': metadata.get('file_type', 'unknown'),
                    'file_size_bytes': metadata.get('file_size_bytes', 0),
                    'created_at': metadata.get('created_at'),
                    'modified_at': metadata.get('modified_at'),
                    'page_count': metadata.get('page_count'),
                    'word_count': len(full_text.split()),
                    'total_chunks': len(chunks),
                    'cloud_storage': metadata.get('cloud_storage', {})
                },
                'source': 'cloud' if cloud_fetched else 'cache',
                'next_actions': {
                    'summarize': 'Use AI to summarize this document',
                    'extract_data': 'Extract specific data points',
                    'compare': 'Compare with other documents'
                }
            }
        
        except Exception as e:
            print(f"❌ Document retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'document_id': document_id
            }
    
    def list_namespaces(self) -> Dict[str, Any]:
        """
        List all available namespaces with statistics
        
        Returns:
            Dict with namespace list and stats
        """
        try:
            index = self._ensure_index_exists()
            
            # Get index stats
            stats = index.describe_index_stats()
            
            # Extract namespaces
            namespaces = []
            for ns_name, ns_stats in stats.get('namespaces', {}).items():
                namespaces.append({
                    'name': ns_name,
                    'vector_count': ns_stats.get('vector_count', 0),
                    'document_count': 'unknown',  # Would need metadata query
                    'last_updated': 'unknown'
                })
            
            return {
                'success': True,
                'namespaces': namespaces,
                'total_namespaces': len(namespaces)
            }
        
        except Exception as e:
            print(f"❌ Failed to list namespaces: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document_metadata(
        self,
        document_id: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Get document metadata without fetching full text
        
        Args:
            document_id: Document ID
            namespace: Pinecone namespace
        
        Returns:
            Dict with metadata only
        """
        try:
            index = self._ensure_index_exists()
            
            # Query for first chunk to get metadata
            dummy_vector = [0.0] * 1536
            results = index.query(
                vector=dummy_vector,
                top_k=1,
                namespace=namespace,
                filter={'document_id': document_id},
                include_metadata=True
            )
            
            if not results['matches']:
                return {
                    'success': False,
                    'error': f"Document not found: {document_id}"
                }
            
            metadata = results['matches'][0].get('metadata', {})
            file_size = metadata.get('file_size_bytes', 0)
            
            return {
                'success': True,
                'document_id': document_id,
                'filename': metadata.get('filename', 'unknown'),
                'metadata': {
                    'file_type': metadata.get('file_type'),
                    'file_size_bytes': file_size,
                    'file_size_human': self._format_bytes(file_size),
                    'created_at': metadata.get('created_at'),
                    'page_count': metadata.get('page_count'),
                    'total_chunks': metadata.get('total_chunks'),
                    'cloud_storage': metadata.get('cloud_storage', {})
                }
            }
        
        except Exception as e:
            print(f"❌ Failed to get metadata: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _format_bytes(bytes: int) -> str:
        """Format bytes to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"


# ==================== TOOL FUNCTIONS ====================

def _get_manager(**kwargs):
    """
    Get or create vector database manager with credential injection
    
    Credentials automatically injected by credential_injector.py based on user_id
    """
    return VectorDatabaseManager(**kwargs)


def vector_db_search(
    query: str,
    namespace: str = "default",
    top_k: int = 5,
    min_score: float = 0.7,
    include_metadata: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Search vector database for relevant document snippets
    
    AI-initiated search (not automatic). Returns snippets with metadata
    for full document retrieval.
    
    Args:
        query: Search query text
        namespace: Vector database namespace
        top_k: Number of results (max 20)
        min_score: Minimum similarity score (0-1)
        include_metadata: Include full metadata
    
    Returns:
        Search results with snippets and cloud storage links
    """
    print(f"[VECTOR DB] AI-initiated search: {query[:50]}...")
    
    # Pass all kwargs including injected credentials
    manager = _get_manager(**kwargs)
    return manager.search(
        query=query,
        namespace=namespace,
        top_k=min(top_k, 20),  # Cap at 20
        min_score=min_score,
        include_metadata=include_metadata
    )


def vector_db_get_full_document(
    document_id: str,
    namespace: str = "default",
    format: str = "text",
    fetch_from_cloud: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve complete document from cloud storage
    
    Fetches full document from Google Drive/OneDrive or cached version.
    
    Args:
        document_id: Document ID from search results
        namespace: Vector database namespace
        format: Return format ('text', 'markdown', 'json')
        fetch_from_cloud: Fetch latest from cloud
    
    Returns:
        Full document text and metadata
    """
    print(f"[VECTOR DB] Fetching full document: {document_id}")
    
    # Extract user_id from kwargs (credential injection)
    user_id = kwargs.get('_user_id')
    
    # Pass all kwargs including injected credentials
    manager = _get_manager(**kwargs)
    return manager.get_full_document(
        document_id=document_id,
        namespace=namespace,
        format=format,
        fetch_from_cloud=fetch_from_cloud,
        user_id=user_id
    )


def vector_db_list_namespaces(**kwargs) -> Dict[str, Any]:
    """
    List all available vector database namespaces
    
    Returns:
        List of namespaces with statistics
    """
    print("[VECTOR DB] Listing namespaces...")
    
    # Pass all kwargs including injected credentials
    manager = _get_manager(**kwargs)
    return manager.list_namespaces()


def vector_db_get_document_metadata(
    document_id: str,
    namespace: str = "default",
    **kwargs
) -> Dict[str, Any]:
    """
    Get document metadata without fetching full text
    
    Args:
        document_id: Document ID
        namespace: Vector database namespace
    
    Returns:
        Document metadata only (no text)
    """
    print(f"[VECTOR DB] Getting metadata for: {document_id}")
    
    manager = _get_manager()
    return manager.get_document_metadata(
        document_id=document_id,
        namespace=namespace
    )
