"""
Cloud Storage to Vector Database Integration

Provides direct upload capabilities from Google Drive, OneDrive, and Dropbox to Pinecone vector database.
Includes folder monitoring and scheduled sync for automatic vector database updates.

Features:
- Browse cloud storage folders
- Upload files directly to vector database  
- Create folder links with scheduled sync (hourly, daily, weekly)
- Monitor folders for new/updated files
- Automatic embedding generation and vector storage

Dependencies:
- google-api-python-client (Google Drive)
- msal (Microsoft OneDrive)
- dropbox (Dropbox)
- pinecone-client
- OpenAI/Voyager AI for embeddings

LAST MODIFIED: 2025-11-30
"""

import os
import io
import json
import hashlib
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Cloud storage SDKs
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import msal
    import requests as ms_requests
    ONEDRIVE_AVAILABLE = True
except ImportError:
    ONEDRIVE_AVAILABLE = False

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

# Document processing
try:
    import PyPDF2
    from docx import Document as DocxDocument
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False


class CloudStorageVectorIntegration:
    """Manages cloud storage to vector database integration"""
    
    def __init__(self):
        self.supported_providers = {
            'google_drive': GOOGLE_AVAILABLE,
            'onedrive': ONEDRIVE_AVAILABLE,
            'dropbox': DROPBOX_AVAILABLE
        }
        self.supported_file_types = ['.pdf', '.docx', '.txt', '.md']
    
    def _get_google_service(self, access_token: str):
        """Create Google Drive service with OAuth token"""
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API client not installed")
        
        creds = Credentials(token=access_token)
        return build('drive', 'v3', credentials=creds)
    
    def _get_onedrive_headers(self, access_token: str) -> Dict:
        """Get headers for OneDrive API"""
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _get_dropbox_client(self, access_token: str):
        """Create Dropbox client"""
        if not DROPBOX_AVAILABLE:
            raise ImportError("Dropbox SDK not installed")
        return dropbox.Dropbox(access_token)
    
    def _extract_text_from_file(self, file_content: bytes, file_extension: str) -> str:
        """Extract text from file based on type"""
        if not DOCUMENT_PROCESSING_AVAILABLE:
            raise ImportError("Document processing libraries not installed")
        
        if file_extension == '.pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            return '\n'.join(page.extract_text() for page in pdf_reader.pages)
        
        elif file_extension == '.docx':
            doc = DocxDocument(io.BytesIO(file_content))
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
        
        elif file_extension in ['.txt', '.md']:
            return file_content.decode('utf-8')
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - chunk_overlap
        
        return chunks
    
    def _generate_openai_embedding(self, text: str, api_key: str, model: str) -> List[float]:
        """Generate OpenAI embedding"""
        try:
            import openai
            
            openai.api_key = api_key
            response = openai.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            raise Exception(f"OpenAI embedding error: {str(e)}")
    
    def _generate_voyager_embedding(self, text: str, api_key: str, model: str) -> List[float]:
        """Generate Voyager AI embedding"""
        try:
            import requests
            
            url = "https://api.voyageai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": [text],
                "model": model
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data['data'][0]['embedding']
            
        except Exception as e:
            raise Exception(f"Voyager AI embedding error: {str(e)}")


# ==================== TOOL FUNCTIONS ====================

def cloud_storage_list_providers(**kwargs) -> Dict[str, Any]:
    """
    List available cloud storage providers and connection status
    
    Args:
        **kwargs: Credential injection
    
    Returns:
        Dict with provider list and connection status
    """
    integration = CloudStorageVectorIntegration()
    
    # Check for connected providers via credentials
    google_connected = kwargs.get('google_access_token') is not None
    onedrive_connected = kwargs.get('onedrive_access_token') is not None
    dropbox_connected = kwargs.get('dropbox_access_token') is not None
    
    providers = [
        {
            'name': 'Google Drive',
            'platform': 'google_drive',
            'connected': google_connected,
            'available': integration.supported_providers['google_drive'],
            'features': ['browse', 'upload', 'folder_sync']
        },
        {
            'name': 'Microsoft OneDrive',
            'platform': 'onedrive',
            'connected': onedrive_connected,
            'available': integration.supported_providers['onedrive'],
            'features': ['browse', 'upload', 'folder_sync']
        },
        {
            'name': 'Dropbox',
            'platform': 'dropbox',
            'connected': dropbox_connected,
            'available': integration.supported_providers['dropbox'],
            'features': ['browse', 'upload', 'folder_sync']
        }
    ]
    
    return {
        'success': True,
        'providers': providers,
        'supported_file_types': integration.supported_file_types
    }


def cloud_storage_browse_folders(
    provider: str,
    folder_id: Optional[str] = None,
    include_files: bool = False,
    file_types: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Browse folders in cloud storage
    
    Args:
        provider: Cloud storage provider (google_drive, onedrive, dropbox)
        folder_id: Folder ID to browse (optional)
        include_files: Include files in response
        file_types: Filter by file types
        **kwargs: Credential injection
    
    Returns:
        Dict with folder tree and files
    """
    integration = CloudStorageVectorIntegration()
    
    if provider == 'google_drive':
        access_token = kwargs.get('google_access_token')
        if not access_token:
            return {'success': False, 'error': 'Google Drive not connected'}
        
        try:
            service = integration._get_google_service(access_token)
            
            # Build query
            query_parts = []
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            else:
                query_parts.append("'root' in parents")
            
            query_parts.append("trashed = false")
            query = ' and '.join(query_parts)
            
            # Fetch folders
            folder_results = service.files().list(
                q=f"{query} and mimeType='application/vnd.google-apps.folder'",
                fields='files(id, name, modifiedTime)',
                pageSize=100
            ).execute()
            
            folders = []
            for folder in folder_results.get('files', []):
                folders.append({
                    'id': folder['id'],
                    'name': folder['name'],
                    'type': 'folder',
                    'modified': folder.get('modifiedTime')
                })
            
            result = {
                'success': True,
                'provider': provider,
                'folder_id': folder_id or 'root',
                'folders': folders
            }
            
            # Include files if requested
            if include_files:
                file_query = query
                if file_types:
                    # Add file type filters
                    type_conditions = [f"name contains '.{ft}'" for ft in file_types]
                    file_query += f" and ({' or '.join(type_conditions)})"
                
                file_results = service.files().list(
                    q=f"{file_query} and mimeType!='application/vnd.google-apps.folder'",
                    fields='files(id, name, size, mimeType, modifiedTime)',
                    pageSize=100
                ).execute()
                
                files = []
                for file in file_results.get('files', []):
                    files.append({
                        'id': file['id'],
                        'name': file['name'],
                        'size': int(file.get('size', 0)),
                        'mime_type': file.get('mimeType'),
                        'modified': file.get('modifiedTime')
                    })
                
                result['files'] = files
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    elif provider == 'onedrive':
        access_token = kwargs.get('onedrive_access_token')
        if not access_token:
            return {'success': False, 'error': 'OneDrive not connected'}
        
        try:
            headers = integration._get_onedrive_headers(access_token)
            
            # Determine folder path
            if folder_id:
                url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
            else:
                url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
            
            # Fetch folders and files
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            folders = []
            files = []
            
            for item in data.get('value', []):
                if 'folder' in item:
                    folders.append({
                        'id': item['id'],
                        'name': item['name'],
                        'type': 'folder',
                        'modified': item.get('lastModifiedDateTime')
                    })
                elif include_files:
                    file_name = item['name']
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    # Filter by file types if specified
                    if not file_types or file_extension[1:] in file_types:
                        files.append({
                            'id': item['id'],
                            'name': file_name,
                            'size': item.get('size', 0),
                            'mime_type': item.get('file', {}).get('mimeType', 'unknown'),
                            'modified': item.get('lastModifiedDateTime')
                        })
            
            result = {
                'success': True,
                'provider': provider,
                'folder_id': folder_id or 'root',
                'folders': folders
            }
            
            if include_files:
                result['files'] = files
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'OneDrive error: {str(e)}'}
    
    elif provider == 'dropbox':
        access_token = kwargs.get('dropbox_access_token')
        if not access_token:
            return {'success': False, 'error': 'Dropbox not connected'}
        
        try:
            import dropbox
            from dropbox.exceptions import ApiError
            
            dbx = integration._get_dropbox_client(access_token)
            
            # Determine folder path
            path = '' if not folder_id or folder_id == 'root' else folder_id
            
            # List folder contents
            result_obj = dbx.files_list_folder(path)
            
            folders = []
            files = []
            
            for entry in result_obj.entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    folders.append({
                        'id': entry.path_display,
                        'name': entry.name,
                        'type': 'folder',
                        'modified': None
                    })
                elif include_files and isinstance(entry, dropbox.files.FileMetadata):
                    file_name = entry.name
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    # Filter by file types if specified
                    if not file_types or file_extension[1:] in file_types:
                        files.append({
                            'id': entry.path_display,
                            'name': file_name,
                            'size': entry.size,
                            'mime_type': 'unknown',
                            'modified': entry.server_modified.isoformat() if entry.server_modified else None
                        })
            
            result = {
                'success': True,
                'provider': provider,
                'folder_id': folder_id or 'root',
                'folders': folders
            }
            
            if include_files:
                result['files'] = files
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Dropbox error: {str(e)}'}
    
    else:
        return {'success': False, 'error': f'Unknown provider: {provider}'}


def cloud_storage_upload_to_vector_db(
    provider: str,
    file_ids: List[str],
    namespace: Optional[str] = None,
    metadata: Optional[Dict] = None,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    **kwargs
) -> Dict[str, Any]:
    """
    Upload files from cloud storage directly to Pinecone
    
    Args:
        provider: Cloud storage provider
        file_ids: List of file IDs to upload
        namespace: Pinecone namespace
        metadata: Additional metadata
        chunk_size: Text chunk size
        chunk_overlap: Chunk overlap
        **kwargs: Credential injection (access tokens, Pinecone credentials, embedding credentials)
    
    Returns:
        Dict with upload results
    """
    integration = CloudStorageVectorIntegration()
    
    # Get Pinecone credentials
    pinecone_api_key = kwargs.get('pinecone_api_key')
    pinecone_index = kwargs.get('pinecone_index_name')
    pinecone_environment = kwargs.get('pinecone_environment')
    
    if not all([pinecone_api_key, pinecone_index, pinecone_environment]):
        return {'success': False, 'error': 'Pinecone credentials missing'}
    
    # Get embedding credentials
    embedding_provider = kwargs.get('embedding_provider', 'openai')
    embedding_api_key = kwargs.get('embedding_api_key')
    embedding_model = kwargs.get('embedding_model', 'text-embedding-3-small')
    
    if not embedding_api_key:
        return {'success': False, 'error': 'Embedding API key missing'}
    
    try:
        # Initialize Pinecone (v8.0+ API)
        from pinecone import Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index)
        
        # Process each file
        processed = 0
        total_chunks = 0
        vector_ids = []
        failed = []
        
        for file_id in file_ids:
            try:
                # Download file from cloud storage
                if provider == 'google_drive':
                    access_token = kwargs.get('google_access_token')
                    service = integration._get_google_service(access_token)
                    
                    # Get file metadata
                    file_meta = service.files().get(fileId=file_id, fields='name,mimeType').execute()
                    file_name = file_meta['name']
                    file_extension = os.path.splitext(file_name)[1]
                    
                    # Download file content
                    request = service.files().get_media(fileId=file_id)
                    file_content = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_content, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    
                    # Extract text
                    text = integration._extract_text_from_file(
                        file_content.getvalue(), 
                        file_extension
                    )
                    
                    # Chunk text
                    chunks = integration._chunk_text(text, chunk_size, chunk_overlap)
                    
                    # Generate embeddings and upload to Pinecone
                    for i, chunk in enumerate(chunks):
                        try:
                            # Generate embedding
                            if embedding_provider == 'voyager':
                                embedding = integration._generate_voyager_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            else:  # openai
                                embedding = integration._generate_openai_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            
                            # Create vector ID (hash of content for deduplication)
                            vector_id = hashlib.md5(chunk.encode()).hexdigest()
                            
                            # Prepare metadata
                            vector_metadata = {
                                'filename': file_name,
                                'source_provider': provider,
                                'source_file_id': file_id,
                                'chunk_index': i,
                                'total_chunks': len(chunks),
                                'text': chunk,
                                'created_at': datetime.now().isoformat()
                            }
                            
                            # Merge with custom metadata
                            if metadata:
                                vector_metadata.update(metadata)
                            
                            # Upload to Pinecone
                            index.upsert(
                                vectors=[(vector_id, embedding, vector_metadata)],
                                namespace=namespace or ''
                            )
                            
                            vector_ids.append(vector_id)
                            
                        except Exception as e:
                            print(f"[CLOUD_STORAGE] Chunk {i} embedding error: {e}")
                            failed.append({'file_id': file_id, 'chunk': i, 'error': str(e)})
                    
                    processed += 1
                    total_chunks += len(chunks)
                    
                elif provider == 'onedrive':
                    # OneDrive implementation
                    access_token = kwargs.get('onedrive_access_token')
                    headers = integration._get_onedrive_headers(access_token)
                    
                    # Get file metadata
                    file_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
                    file_response = requests.get(file_url, headers=headers)
                    file_response.raise_for_status()
                    file_meta = file_response.json()
                    
                    file_name = file_meta['name']
                    file_extension = os.path.splitext(file_name)[1]
                    
                    # Download file content
                    download_url = file_meta.get('@microsoft.graph.downloadUrl')
                    if not download_url:
                        raise Exception(f"No download URL for file: {file_name}")
                    
                    download_response = requests.get(download_url)
                    download_response.raise_for_status()
                    file_content = download_response.content
                    
                    # Extract text
                    text = integration._extract_text_from_file(file_content, file_extension)
                    
                    # Chunk text
                    chunks = integration._chunk_text(text, chunk_size, chunk_overlap)
                    
                    # Generate embeddings and upload (same as Google Drive)
                    for i, chunk in enumerate(chunks):
                        try:
                            # Generate embedding
                            if embedding_provider == 'voyager':
                                embedding = integration._generate_voyager_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            else:  # openai
                                embedding = integration._generate_openai_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            
                            # Create vector ID
                            vector_id = hashlib.md5(chunk.encode()).hexdigest()
                            
                            # Prepare metadata
                            vector_metadata = {
                                'filename': file_name,
                                'source_provider': provider,
                                'source_file_id': file_id,
                                'chunk_index': i,
                                'total_chunks': len(chunks),
                                'text': chunk,
                                'created_at': datetime.now().isoformat()
                            }
                            
                            if metadata:
                                vector_metadata.update(metadata)
                            
                            # Upload to Pinecone
                            index.upsert(
                                vectors=[(vector_id, embedding, vector_metadata)],
                                namespace=namespace or ''
                            )
                            
                            vector_ids.append(vector_id)
                            
                        except Exception as e:
                            print(f"[CLOUD_STORAGE] OneDrive chunk {i} error: {e}")
                            failed.append({'file_id': file_id, 'chunk': i, 'error': str(e)})
                    
                    processed += 1
                    total_chunks += len(chunks)
                
                elif provider == 'dropbox':
                    # Dropbox implementation
                    import dropbox
                    
                    access_token = kwargs.get('dropbox_access_token')
                    dbx = integration._get_dropbox_client(access_token)
                    
                    # Get file metadata and download
                    metadata_obj, response = dbx.files_download(file_id)
                    file_name = metadata_obj.name
                    file_extension = os.path.splitext(file_name)[1]
                    file_content = response.content
                    
                    # Extract text
                    text = integration._extract_text_from_file(file_content, file_extension)
                    
                    # Chunk text
                    chunks = integration._chunk_text(text, chunk_size, chunk_overlap)
                    
                    # Generate embeddings and upload (same as Google Drive)
                    for i, chunk in enumerate(chunks):
                        try:
                            # Generate embedding
                            if embedding_provider == 'voyager':
                                embedding = integration._generate_voyager_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            else:  # openai
                                embedding = integration._generate_openai_embedding(
                                    chunk, embedding_api_key, embedding_model
                                )
                            
                            # Create vector ID
                            vector_id = hashlib.md5(chunk.encode()).hexdigest()
                            
                            # Prepare metadata
                            vector_metadata = {
                                'filename': file_name,
                                'source_provider': provider,
                                'source_file_id': file_id,
                                'chunk_index': i,
                                'total_chunks': len(chunks),
                                'text': chunk,
                                'created_at': datetime.now().isoformat()
                            }
                            
                            if metadata:
                                vector_metadata.update(metadata)
                            
                            # Upload to Pinecone
                            index.upsert(
                                vectors=[(vector_id, embedding, vector_metadata)],
                                namespace=namespace or ''
                            )
                            
                            vector_ids.append(vector_id)
                            
                        except Exception as e:
                            print(f"[CLOUD_STORAGE] Dropbox chunk {i} error: {e}")
                            failed.append({'file_id': file_id, 'chunk': i, 'error': str(e)})
                    
                    processed += 1
                    total_chunks += len(chunks)
                
            except Exception as e:
                failed.append({'file_id': file_id, 'error': str(e)})
        
        return {
            'success': True,
            'processed': processed,
            'total_chunks': total_chunks,
            'vector_ids': vector_ids[:10],  # First 10 for reference
            'failed': failed
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def cloud_storage_create_folder_link(
    provider: str,
    folder_id: str,
    sync_schedule: str,
    namespace: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    auto_delete: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Create monitored folder link for automatic sync
    
    Args:
        provider: Cloud storage provider
        folder_id: Folder ID to link
        sync_schedule: Sync frequency (hourly, daily, weekly, manual)
        namespace: Pinecone namespace
        file_types: File types to sync
        auto_delete: Delete vectors when source deleted
        **kwargs: Credential injection
    
    Returns:
        Dict with folder link details
    """
    # TODO: Store folder link in database with sync configuration
    # TODO: Setup scheduled job based on sync_schedule
    
    link_id = f"link_{hashlib.md5(f'{provider}_{folder_id}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
    
    return {
        'success': True,
        'link_id': link_id,
        'provider': provider,
        'folder_id': folder_id,
        'sync_schedule': sync_schedule,
        'namespace': namespace,
        'file_types': file_types or ['pdf', 'docx', 'txt', 'md'],
        'auto_delete': auto_delete,
        'status': 'active',
        'next_sync': 'Not yet scheduled',
        'message': 'Folder link created successfully - sync scheduling will be implemented'
    }


def cloud_storage_list_folder_links(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    List all folder links
    
    Args:
        provider: Filter by provider
        status: Filter by status
        **kwargs: Credential injection
    
    Returns:
        Dict with folder links list
    """
    # TODO: Query database for folder links
    
    return {
        'success': True,
        'links': [],
        'message': 'Folder link management database not yet implemented'
    }


def cloud_storage_sync_folder_now(link_id: str, **kwargs) -> Dict[str, Any]:
    """Trigger immediate folder sync"""
    # TODO: Execute sync job
    return {
        'success': True,
        'link_id': link_id,
        'message': 'Manual sync trigger not yet implemented'
    }


def cloud_storage_update_folder_link(
    link_id: str,
    sync_schedule: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    status: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Update folder link settings"""
    # TODO: Update database
    return {
        'success': True,
        'link_id': link_id,
        'message': 'Folder link update not yet implemented'
    }


def cloud_storage_delete_folder_link(
    link_id: str,
    delete_vectors: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Delete folder link"""
    # TODO: Remove from database, optionally delete vectors
    return {
        'success': True,
        'link_id': link_id,
        'vectors_deleted': delete_vectors,
        'message': 'Folder link deletion not yet implemented'
    }
