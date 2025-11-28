"""
UNIVERSAL FILE HANDLER - Core AI Infrastructure
================================================

Universal file processor for ANY file source (email attachments, cloud storage, local files).
Automatically chooses optimal method to deliver files to Anthropic Claude.

Supported Sources:
- Outlook/Exchange attachments
- Gmail attachments  
- OneDrive files
- Google Drive files
- Local filesystem files
- Direct file uploads

Delivery Methods (auto-selected):
1. Direct Base64 (< 5MB images/PDFs) → ~800 tokens/MB
2. Anthropic Files API (5-100MB) → ~50 tokens/file
3. Cloud Storage URL (>100MB or unsupported) → 0 tokens

This is the SINGLE SOURCE OF TRUTH for file processing across the entire platform.

Usage:
    from AI_infrastructure.core.universal_file_handler import UniversalFileHandler
    
    handler = UniversalFileHandler()
    
    # From Outlook attachment
    result = handler.process_file(
        source='outlook',
        source_id={'message_id': 'msg123', 'attachment_id': 'att456'},
        mode='auto'
    )
    
    # From Gmail attachment
    result = handler.process_file(
        source='gmail',
        source_id={'message_id': 'msg123', 'attachment_id': 'att456'},
        mode='auto'
    )
    
    # From local file
    result = handler.process_file(
        source='local',
        source_id={'file_path': '/path/to/file.pdf'},
        mode='auto'
    )
    
    # Returns:
    {
        'success': True,
        'method': 'direct' | 'files_api' | 'url',
        'content_block': {...},  # For Anthropic API
        'url': 'https://...',    # For URL method
        'metadata': {
            'name': 'document.pdf',
            'size': 123456,
            'type': 'application/pdf',
            'token_estimate': 800,
            'source': 'outlook'
        }
    }
"""

import base64
import io
import os
import mimetypes
from typing import Dict, Any, Optional, List, Union, BinaryIO
from pathlib import Path


class UniversalFileHandler:
    """
    Universal file processor for ANY source, optimized for Anthropic Claude
    """
    
    # Anthropic-supported content types
    SUPPORTED_IMAGES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    SUPPORTED_DOCUMENTS = ['application/pdf']
    
    # Size thresholds (bytes)
    DIRECT_THRESHOLD = 5 * 1024 * 1024      # 5MB - send directly as base64
    FILES_API_THRESHOLD = 100 * 1024 * 1024  # 100MB - use Anthropic Files API
    # > 100MB → Use cloud storage URL
    
    # Max file size (Anthropic limit)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    
    def __init__(self, user_id: Optional[int] = None, **kwargs):
        """
        Initialize handler
        
        Args:
            user_id: User ID for credential injection
            **kwargs: Additional config (api_keys, etc.)
        """
        self.user_id = user_id
        self.config = kwargs
    
    
    def process_file(self,
                    source: str,
                    source_id: Dict[str, Any],
                    mode: str = 'auto',
                    **kwargs) -> Dict[str, Any]:
        """
        Universal file processor - handles ANY file from ANY source
        
        Args:
            source: File source type
                - 'outlook': Microsoft Outlook/Exchange attachment
                - 'gmail': Gmail attachment
                - 'onedrive': OneDrive file
                - 'google_drive': Google Drive file
                - 'local': Local filesystem
                - 'bytes': Raw file bytes
            
            source_id: Source-specific identifier
                Outlook: {'message_id': str, 'attachment_id': str}
                Gmail: {'message_id': str, 'attachment_id': str}
                OneDrive: {'file_id': str}
                Google Drive: {'file_id': str}
                Local: {'file_path': str}
                Bytes: {'filename': str, 'content_type': str, 'data': bytes}
            
            mode: Delivery mode
                - 'auto' (default): Smart detection based on size/type
                - 'direct': Force base64 content block
                - 'files_api': Force Anthropic Files API
                - 'url': Force cloud storage URL
        
        Returns:
            {
                'success': bool,
                'method': 'direct' | 'files_api' | 'url',
                'content_block': dict | None,  # For direct/files_api
                'url': str | None,              # For url method
                'metadata': {
                    'name': str,
                    'size': int,
                    'type': str,
                    'token_estimate': int,
                    'source': str
                }
            }
        """
        # Step 1: Get file metadata and content
        file_data = self._get_file_data(source, source_id, **kwargs)
        
        if not file_data['success']:
            return file_data
        
        # Step 2: Auto-detect best delivery method
        if mode == 'auto':
            mode = self._determine_optimal_method(
                file_data['content_type'],
                file_data['size']
            )
        
        # Step 3: Process using chosen method
        if mode == 'direct':
            return self._process_direct_base64(file_data)
        elif mode == 'files_api':
            return self._process_files_api(file_data)
        elif mode == 'url':
            return self._process_cloud_url(file_data, source)
        else:
            return {
                'success': False,
                'error': f"Invalid mode: {mode}. Use 'auto', 'direct', 'files_api', or 'url'"
            }
    
    
    def process_batch(self,
                     files: List[Dict[str, Any]],
                     mode: str = 'auto',
                     **kwargs) -> Dict[str, Any]:
        """
        Process multiple files at once (optimized for threads/batches)
        
        Args:
            files: List of file specs
                [
                    {'source': 'outlook', 'source_id': {...}},
                    {'source': 'gmail', 'source_id': {...}}
                ]
            mode: Delivery mode (applied to all)
        
        Returns:
            {
                'success': bool,
                'results': [
                    {'file': 'img1.png', 'method': 'direct', ...},
                    {'file': 'doc.pdf', 'method': 'files_api', ...}
                ],
                'total_token_estimate': int,
                'content_blocks': [...]  # Ready for Anthropic API
            }
        """
        results = []
        content_blocks = []
        total_tokens = 0
        
        for file_spec in files:
            result = self.process_file(
                source=file_spec['source'],
                source_id=file_spec['source_id'],
                mode=mode,
                **kwargs
            )
            
            results.append(result)
            
            if result['success']:
                if result.get('content_block'):
                    content_blocks.append(result['content_block'])
                total_tokens += result['metadata'].get('token_estimate', 0)
        
        return {
            'success': all(r['success'] for r in results),
            'results': results,
            'total_token_estimate': total_tokens,
            'content_blocks': content_blocks
        }
    
    
    # ==================== FILE DATA RETRIEVAL ====================
    
    def _get_file_data(self,
                      source: str,
                      source_id: Dict[str, Any],
                      **kwargs) -> Dict[str, Any]:
        """
        Get file content and metadata from ANY source
        """
        if source == 'outlook':
            return self._get_outlook_attachment(source_id, **kwargs)
        elif source == 'gmail':
            return self._get_gmail_attachment(source_id, **kwargs)
        elif source == 'onedrive':
            return self._get_onedrive_file(source_id, **kwargs)
        elif source == 'google_drive':
            return self._get_google_drive_file(source_id, **kwargs)
        elif source == 'local':
            return self._get_local_file(source_id)
        elif source == 'bytes':
            return self._get_from_bytes(source_id)
        else:
            return {
                'success': False,
                'error': f"Unsupported source: {source}"
            }
    
    
    def _get_outlook_attachment(self,
                               source_id: Dict[str, Any],
                               **kwargs) -> Dict[str, Any]:
        """Get file from Outlook attachment"""
        from tools.implementations.microsoft_outlook_tools import microsoft_outlook_download_attachment
        
        result = microsoft_outlook_download_attachment(
            message_id=source_id['message_id'],
            attachment_id=source_id['attachment_id'],
            _user_id=self.user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not result['success']:
            return result
        
        # Decode base64 from Outlook API
        file_bytes = base64.b64decode(result['content'])
        
        return {
            'success': True,
            'name': result['name'],
            'content_type': result['content_type'],
            'size': result['size'],
            'data': file_bytes,
            'source': 'outlook'
        }
    
    
    def _get_gmail_attachment(self,
                             source_id: Dict[str, Any],
                             **kwargs) -> Dict[str, Any]:
        """Get file from Gmail attachment"""
        # Import Gmail tools
        try:
            from google_workspace.gmail import GmailManager
            
            gmail = GmailManager()
            
            # Get attachment data
            result = gmail.get_attachment(
                message_id=source_id['message_id'],
                attachment_id=source_id['attachment_id'],
                user_id=self.user_id
            )
            
            if not result.get('success'):
                return {'success': False, 'error': result.get('error', 'Gmail attachment download failed')}
            
            # Decode base64 from Gmail API
            file_bytes = base64.b64decode(result['data'])
            
            return {
                'success': True,
                'name': result.get('filename', 'unknown'),
                'content_type': result.get('mime_type', 'application/octet-stream'),
                'size': len(file_bytes),
                'data': file_bytes,
                'source': 'gmail'
            }
        except Exception as e:
            return {'success': False, 'error': f'Gmail attachment error: {str(e)}'}
    
    
    def _get_onedrive_file(self,
                          source_id: Dict[str, Any],
                          **kwargs) -> Dict[str, Any]:
        """Get file from OneDrive"""
        from tools.implementations.microsoft_onedrive_tools import microsoft_onedrive_download_file
        
        result = microsoft_onedrive_download_file(
            item_id=source_id['file_id'],
            _user_id=self.user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not result['success']:
            return result
        
        # Decode base64 if needed
        if isinstance(result['content'], str):
            file_bytes = base64.b64decode(result['content'])
        else:
            file_bytes = result['content']
        
        return {
            'success': True,
            'name': result.get('name', 'unknown'),
            'content_type': result.get('content_type', 'application/octet-stream'),
            'size': len(file_bytes),
            'data': file_bytes,
            'source': 'onedrive'
        }
    
    
    def _get_google_drive_file(self,
                               source_id: Dict[str, Any],
                               **kwargs) -> Dict[str, Any]:
        """Get file from Google Drive"""
        try:
            from google_workspace.google_docs import GoogleDocsManager
            
            gdrive = GoogleDocsManager()
            
            # Download file
            result = gdrive.download_file(
                file_id=source_id['file_id'],
                user_id=self.user_id
            )
            
            if not result.get('success'):
                return {'success': False, 'error': result.get('error', 'Google Drive download failed')}
            
            file_bytes = result['content']
            
            return {
                'success': True,
                'name': result.get('name', 'unknown'),
                'content_type': result.get('mime_type', 'application/octet-stream'),
                'size': len(file_bytes),
                'data': file_bytes,
                'source': 'google_drive'
            }
        except Exception as e:
            return {'success': False, 'error': f'Google Drive error: {str(e)}'}
    
    
    def _get_local_file(self, source_id: Dict[str, Any]) -> Dict[str, Any]:
        """Get file from local filesystem"""
        file_path = source_id['file_path']
        
        if not os.path.exists(file_path):
            return {'success': False, 'error': f'File not found: {file_path}'}
        
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            # Detect content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            return {
                'success': True,
                'name': os.path.basename(file_path),
                'content_type': content_type,
                'size': len(file_bytes),
                'data': file_bytes,
                'source': 'local'
            }
        except Exception as e:
            return {'success': False, 'error': f'Local file read error: {str(e)}'}
    
    
    def _get_from_bytes(self, source_id: Dict[str, Any]) -> Dict[str, Any]:
        """Get file from raw bytes"""
        return {
            'success': True,
            'name': source_id.get('filename', 'unknown'),
            'content_type': source_id.get('content_type', 'application/octet-stream'),
            'size': len(source_id['data']),
            'data': source_id['data'],
            'source': 'bytes'
        }
    
    
    # ==================== DELIVERY METHOD SELECTION ====================
    
    def _determine_optimal_method(self,
                                  content_type: str,
                                  size: int) -> str:
        """
        Auto-detect best delivery method based on file type and size
        """
        # Check if file is supported by Anthropic directly
        is_supported = (
            content_type in self.SUPPORTED_IMAGES or
            content_type in self.SUPPORTED_DOCUMENTS
        )
        
        # Size-based decision tree
        if is_supported:
            if size < self.DIRECT_THRESHOLD:
                return 'direct'  # Small, supported → Direct base64
            elif size < self.FILES_API_THRESHOLD:
                return 'files_api'  # Large, supported → Files API
            else:
                return 'url'  # Too large → Cloud URL
        else:
            # Unsupported type → Always use URL
            return 'url'
    
    
    def _is_supported_by_anthropic(self, content_type: str) -> bool:
        """Check if content type is natively supported by Anthropic"""
        return (content_type in self.SUPPORTED_IMAGES or
                content_type in self.SUPPORTED_DOCUMENTS)
    
    
    # ==================== DELIVERY METHOD IMPLEMENTATIONS ====================
    
    def _process_direct_base64(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Method 1: Direct base64 in content block
        ✅ Best for small images/PDFs (< 5MB)
        """
        # Encode to base64
        base64_data = base64.b64encode(file_data['data']).decode('utf-8')
        
        # Determine block type
        if file_data['content_type'] in self.SUPPORTED_DOCUMENTS:
            block_type = 'document'
        elif file_data['content_type'] in self.SUPPORTED_IMAGES:
            block_type = 'image'
        else:
            return {
                'success': False,
                'error': f"Content type {file_data['content_type']} not supported for direct base64. Use 'url' mode instead."
            }
        
        # Build Anthropic content block
        content_block = {
            'type': block_type,
            'source': {
                'type': 'base64',
                'media_type': file_data['content_type'],
                'data': base64_data
            }
        }
        
        return {
            'success': True,
            'method': 'direct',
            'content_block': content_block,
            'url': None,
            'metadata': {
                'name': file_data['name'],
                'size': file_data['size'],
                'type': file_data['content_type'],
                'token_estimate': self._estimate_tokens(file_data['size'], block_type),
                'source': file_data['source']
            }
        }
    
    
    def _process_files_api(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Method 2: Upload to Anthropic Files API, reference by ID
        ✅ Best for large files (5-100MB) or repeated use
        """
        try:
            import anthropic
            from config import get_api_key_enhanced
            
            # Get API key
            api_key = get_api_key_enhanced('ANTHROPIC')
            if not api_key:
                return {'success': False, 'error': 'Anthropic API key not found'}
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Create file-like object
            file_obj = io.BytesIO(file_data['data'])
            file_obj.name = file_data['name']
            
            # Upload to Anthropic Files API
            response = client.files.create(
                file=file_obj,
                purpose='messages'
            )
            
            # Determine block type
            if file_data['content_type'] in self.SUPPORTED_DOCUMENTS:
                block_type = 'document'
            else:
                block_type = 'image'
            
            # Build content block with file reference
            content_block = {
                'type': block_type,
                'source': {
                    'type': 'file',
                    'file_id': response.id
                }
            }
            
            return {
                'success': True,
                'method': 'files_api',
                'content_block': content_block,
                'url': None,
                'metadata': {
                    'file_id': response.id,
                    'name': file_data['name'],
                    'size': file_data['size'],
                    'type': file_data['content_type'],
                    'token_estimate': 50,  # File references are tiny
                    'source': file_data['source']
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'Anthropic Files API error: {str(e)}'}
    
    
    def _process_cloud_url(self,
                          file_data: Dict[str, Any],
                          original_source: str) -> Dict[str, Any]:
        """
        Method 3: Upload to cloud storage, return shareable URL
        ✅ Best for unsupported types (DOCX, XLSX) or huge files (>100MB)
        """
        # Determine upload destination (prefer source's native cloud)
        if original_source in ['outlook', 'onedrive']:
            return self._upload_to_onedrive(file_data)
        elif original_source in ['gmail', 'google_drive']:
            return self._upload_to_google_drive(file_data)
        else:
            # Default to OneDrive
            return self._upload_to_onedrive(file_data)
    
    
    def _upload_to_onedrive(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload file to OneDrive and return shareable URL"""
        try:
            from tools.implementations.microsoft_onedrive_tools import (
                microsoft_onedrive_upload_file,
                microsoft_onedrive_create_share_link
            )
            
            # Upload to OneDrive
            upload_result = microsoft_onedrive_upload_file(
                file_path=f'AI_Attachments/{file_data["name"]}',
                file_content=file_data['data'],
                content_type=file_data['content_type'],
                _user_id=self.user_id,
                _injected_credentials=True
            )
            
            if not upload_result['success']:
                return upload_result
            
            # Create shareable link
            share_result = microsoft_onedrive_create_share_link(
                item_id=upload_result['file_id'],
                share_type='view',
                _user_id=self.user_id,
                _injected_credentials=True
            )
            
            if not share_result['success']:
                return share_result
            
            return {
                'success': True,
                'method': 'url',
                'content_block': None,
                'url': share_result['web_url'],
                'metadata': {
                    'file_id': upload_result['file_id'],
                    'name': file_data['name'],
                    'size': file_data['size'],
                    'type': file_data['content_type'],
                    'token_estimate': 0,  # URLs are token-free
                    'source': 'onedrive'
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'OneDrive upload error: {str(e)}'}
    
    
    def _upload_to_google_drive(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload file to Google Drive and return shareable URL"""
        try:
            from google_workspace.google_docs import GoogleDocsManager
            
            gdrive = GoogleDocsManager()
            
            # Upload to Google Drive
            upload_result = gdrive.upload_file(
                filename=file_data['name'],
                content=file_data['data'],
                mime_type=file_data['content_type'],
                folder_name='AI_Attachments',
                user_id=self.user_id
            )
            
            if not upload_result.get('success'):
                return {'success': False, 'error': upload_result.get('error', 'Google Drive upload failed')}
            
            # Create shareable link
            share_result = gdrive.create_share_link(
                file_id=upload_result['file_id'],
                user_id=self.user_id
            )
            
            return {
                'success': True,
                'method': 'url',
                'content_block': None,
                'url': share_result.get('web_url', upload_result.get('web_url')),
                'metadata': {
                    'file_id': upload_result['file_id'],
                    'name': file_data['name'],
                    'size': file_data['size'],
                    'type': file_data['content_type'],
                    'token_estimate': 0,
                    'source': 'google_drive'
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'Google Drive upload error: {str(e)}'}
    
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def _estimate_tokens(self, file_size: int, block_type: str) -> int:
        """Estimate token count for content block"""
        if block_type == 'image':
            # Images: ~800 tokens per MB
            return int((file_size / 1_000_000) * 800)
        elif block_type == 'document':
            # PDFs: ~3000 tokens per page (estimate 500KB per page)
            pages = max(1, file_size / 500_000)
            return int(pages * 3000)
        return 0


# Global instance (singleton pattern)
_global_handler = None

def get_universal_file_handler(user_id: Optional[int] = None, **kwargs) -> UniversalFileHandler:
    """Get or create global file handler instance"""
    global _global_handler
    if _global_handler is None or user_id is not None:
        _global_handler = UniversalFileHandler(user_id=user_id, **kwargs)
    return _global_handler
