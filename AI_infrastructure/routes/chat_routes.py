"""
Chat Routes - SSE Streaming & File Upload
File: AI_infrastructure/routes/chat_routes.py
Handles multi-agent chat with streaming responses and file uploads

FIXED: 2025-01-XX - Bug fixes (NO cursor leaks found - file was clean!)
CHANGES:
- Fixed undefined 'session_manager' variable (use get_session_manager() consistently)
- Added proper error handling
- Improved code clarity
- NO CURSOR MANAGEMENT CHANGES (file doesn't use database directly)

Endpoints:
- GET /api/chat/stream - Server-Sent Events streaming
- POST /api/chat/upload - File upload handling
- POST /api/chat/message - Single message (non-streaming fallback)
"""

from flask import Blueprint, request, Response, jsonify, stream_with_context, current_app
import json
import time
from datetime import datetime
from AI_infrastructure.core.universal_file_handler import UniversalFileHandler
from AI_infrastructure.core.unified_session_manager import UnifiedSessionManager

# Blueprint
chat_bp = Blueprint('chat', __name__)

def get_session_manager():
    """Get session manager from Flask app config"""
    return current_app.config.get('SESSION_MANAGER') or UnifiedSessionManager()

def get_ai_client():
    """Get AI client from Flask app config (lazy-loaded)"""
    # Try lazy-loading getter first (new pattern)
    getter = current_app.config.get('GET_AI_CLIENT')
    if getter:
        return getter()
    # Fallback to direct config access (legacy pattern)
    return current_app.config.get('AI_CLIENT')


@chat_bp.route('/stream', methods=['GET'])
def stream_chat():
    """
    SSE streaming endpoint for AI chat
    
    Query Parameters:
        session_id (str): Unique session identifier
        message (str): User message to send to AI
    
    Returns:
        text/event-stream: Server-Sent Events stream
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    session_id = request.args.get('session_id')
    message = request.args.get('message', '')
    
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    
    def generate():
        try:
            # ✅ FIX: Use get_session_manager() instead of undefined session_manager
            session_mgr = get_session_manager()
            
            # Get session context
            session = session_mgr.get_session(session_id)
            
            # Add user message to history
            if message:
                session_mgr.add_message(session_id, 'user', message)
            
            # Stream AI response
            yield f"event: message_start\ndata: {json.dumps({'session_id': session_id})}\n\n"
            
            # Get AI response using unified client
            response_text = ''
            content_block_index = 0
            
            # Simulate streaming (replace with actual AI client streaming)
            for chunk in stream_ai_response(session, message):
                chunk_type = chunk.get('type')
                
                if chunk_type == 'content_block_start':
                    yield f"event: content_block_start\ndata: {json.dumps(chunk)}\n\n"
                    content_block_index = chunk.get('index', 0)
                
                elif chunk_type == 'content_block_delta':
                    delta = chunk.get('delta', '')
                    response_text += delta
                    yield f"event: content_block_delta\ndata: {json.dumps({'delta': delta, 'index': content_block_index})}\n\n"
                
                elif chunk_type == 'content_block_stop':
                    yield f"event: content_block_stop\ndata: {json.dumps({'index': content_block_index})}\n\n"
                
                elif chunk_type == 'thinking':
                    yield f"event: thinking\ndata: {json.dumps(chunk)}\n\n"
                
                elif chunk_type == 'tool_use':
                    yield f"event: tool_use\ndata: {json.dumps(chunk)}\n\n"
            
            # Save AI response to session
            if response_text:
                session_mgr.add_message(session_id, 'assistant', response_text)
            
            yield f"event: message_stop\ndata: {json.dumps({'session_id': session_id})}\n\n"
            
        except Exception as error:
            print(f'❌ Stream error: {error}')
            yield f"event: error\ndata: {json.dumps({'error': str(error)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@chat_bp.route('/upload', methods=['POST'])
def upload_files():
    """
    Handle file uploads for chat context
    
    Form Data:
        session_id (str): Session identifier
        files (FileStorage[]): Multiple files
        message (str, optional): Associated message
        convert_pref (str, optional): 'pdf' | 'image' | 'hybrid' | 'auto' (default 'auto')
        image_format (str, optional): Image format for conversion (default 'png')
        image_dpi (int, optional): DPI for image conversion (default 150)
    
    Returns:
        JSON: {success: bool, files: [{name, type, size, content}]}
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    session_id = request.form.get('session_id')
    message = request.form.get('message', '')
    files = request.files.getlist('files')
    
    # Optional form parameters to control conversion behavior for office docs
    convert_pref = request.form.get('convert_pref', 'auto')
    image_format = request.form.get('image_format', 'png')
    try:
        image_dpi = int(request.form.get('image_dpi', 150))
    except Exception:
        image_dpi = 150
    
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    
    processed_files = []
    
    # ✅ FIX: Use get_session_manager() instead of undefined session_manager
    session_mgr = get_session_manager()
    
    # Initialize UniversalFileHandler for binary/attachment processing
    handler = UniversalFileHandler()
    
    for file in files:
        try:
            # Validate file
            if file.filename == '':
                continue
            
            # Read file content
            content = file.read()
            file_size = len(content)
            
            # Process based on type. For text-like files, extract raw text.
            if file.content_type.startswith('text/'):
                text_content = content.decode('utf-8')
                processed_files.append({
                    'name': file.filename,
                    'type': file.content_type,
                    'size': file_size,
                    'content': text_content[:5000]
                })
                session_mgr.add_file_context(session_id, file.filename, text_content)

            elif file.content_type == 'application/pdf':
                text_content = extract_pdf_text(content)
                processed_files.append({
                    'name': file.filename,
                    'type': file.content_type,
                    'size': file_size,
                    'content': text_content[:5000]
                })
                session_mgr.add_file_context(session_id, file.filename, text_content)

            elif file.content_type == 'text/csv':
                text_content = content.decode('utf-8')
                processed_files.append({
                    'name': file.filename,
                    'type': file.content_type,
                    'size': file_size,
                    'content': text_content[:5000]
                })
                session_mgr.add_file_context(session_id, file.filename, text_content)

            else:
                # Binary files (images, office docs, etc.) - use UniversalFileHandler
                try:
                    # SMART TWO-TIER STRATEGY:
                    # Tier 1: Try converting to PDF for visual analysis (preserves images/charts)
                    # Tier 2: If too large (>2000 tokens) or conversion fails, fall back to markdown extraction
                    
                    # Decide processing mode for this file
                    mode = 'auto'
                    
                    # ✅ FIX: Safe attribute access with hasattr()
                    try:
                        extractable = (
                            hasattr(handler, 'TEXT_EXTRACTABLE_TYPES') and 
                            file.content_type in handler.TEXT_EXTRACTABLE_TYPES
                        )
                        supported = handler._is_supported_by_anthropic(file.content_type)
                    except Exception as e:
                        print(f"⚠️ Error checking file type support: {e}")
                        extractable = False
                        supported = False

                    # Check if file is large (heuristic: spreadsheets >100KB or docs >500KB likely exceed 2000 tokens)
                    is_large_spreadsheet = (
                        file.content_type in [
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            'application/vnd.ms-excel',
                            'text/csv'
                        ] and file_size > 100 * 1024  # >100KB spreadsheet
                    )
                    is_large_document = (
                        extractable and 
                        file_size > 500 * 1024  # >500KB doc
                    )

                    if extractable and not supported:
                        # Office document or text file
                        if convert_pref == 'image':
                            mode = 'convert_image'
                        elif convert_pref == 'hybrid':
                            mode = 'hybrid'
                        elif convert_pref == 'extract':
                            # Explicitly requested markdown extraction
                            mode = 'extract'
                        elif is_large_spreadsheet or is_large_document:
                            # Tier 2: Large file - extract to markdown directly (avoid token overflow)
                            print(f"[INFO] Large file detected ({file_size} bytes) - extracting to markdown instead of PDF")
                            mode = 'extract'
                        elif convert_pref == 'auto' or convert_pref == 'pdf':
                            # Tier 1: Default for office docs - convert to PDF for visual analysis
                            mode = 'convert_pdf'

                    # Call the universal handler with explicit options when needed
                    conversion_result = handler.process_file(
                        source='bytes',
                        source_id={
                            'filename': file.filename,
                            'content_type': file.content_type,
                            'data': content
                        },
                        mode=mode,
                        image_format=image_format,
                        image_dpi=image_dpi
                    )
                    
                    # FALLBACK: If conversion resulted in huge token estimate (>2000), retry with extraction
                    if conversion_result.get('success') and conversion_result.get('method') in ['convert_pdf', 'convert_image']:
                        token_estimate = conversion_result.get('metadata', {}).get('token_estimate', 0)
                        if token_estimate > 2000:
                            print(f"[INFO] Conversion exceeded 2000 tokens ({token_estimate}) - retrying with markdown extraction")
                            # Retry with extract mode
                            conversion_result = handler.process_file(
                                source='bytes',
                                source_id={
                                    'filename': file.filename,
                                    'content_type': file.content_type,
                                    'data': content
                                },
                                mode='extract',
                                image_format=image_format,
                                image_dpi=image_dpi
                            )

                    if conversion_result.get('success'):
                        # Attach summary info and content_blocks if present
                        processed_entry = {
                            'name': file.filename,
                            'type': file.content_type,
                            'size': file_size,
                            'method': conversion_result.get('method'),
                            'metadata': conversion_result.get('metadata')
                        }

                        # Prefer content_block for single block, otherwise content_blocks
                        if conversion_result.get('content_block'):
                            processed_entry['content'] = conversion_result['content_block']
                            # Save a text summary to session if available
                            if conversion_result['content_block'].get('type') == 'text':
                                session_mgr.add_file_context(
                                    session_id, 
                                    file.filename, 
                                    conversion_result['content_block'].get('text', '')
                                )
                        elif conversion_result.get('content_blocks'):
                            processed_entry['content'] = conversion_result['content_blocks']
                            # Save first text block if exists
                            for cb in conversion_result['content_blocks']:
                                if cb.get('type') == 'text':
                                    session_mgr.add_file_context(
                                        session_id, 
                                        file.filename, 
                                        cb.get('text', '')
                                    )
                                    break

                        processed_files.append(processed_entry)
                    else:
                        # Fallback to storing a binary note
                        text_content = f'[Binary file: {file.filename}]'
                        processed_files.append({
                            'name': file.filename,
                            'type': file.content_type,
                            'size': file_size,
                            'content': text_content
                        })
                        session_mgr.add_file_context(session_id, file.filename, text_content)
                        
                except Exception as e:
                    print(f'❌ File processing error (handler): {e}')
                    import traceback
                    traceback.print_exc()
                    processed_files.append({
                        'name': file.filename,
                        'type': file.content_type,
                        'size': file_size,
                        'content': f'[Processing error: {str(e)}]'
                    })
                    session_mgr.add_file_context(
                        session_id, 
                        file.filename, 
                        f'[Processing error: {str(e)}]'
                    )
            
        except Exception as error:
            print(f'❌ File processing error: {error}')
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to process {file.filename}'}), 500
    
    return jsonify({
        'success': True,
        'files': processed_files,
        'message': f'Processed {len(processed_files)} files'
    })


@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    Single message endpoint (non-streaming fallback)
    
    JSON Body:
        session_id (str): Session identifier
        message (str): User message
    
    Returns:
        JSON: {response: str, session_id: str}
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message', '')
    
    if not session_id or not message:
        return jsonify({'error': 'session_id and message required'}), 400
    
    try:
        # ✅ FIX: Use get_session_manager() instead of undefined session_manager
        session_mgr = get_session_manager()
        
        # Get session
        session = session_mgr.get_session(session_id)
        
        # Add user message
        session_mgr.add_message(session_id, 'user', message)
        
        # Get AI response (non-streaming)
        response = get_ai_response(session, message)
        
        # Save AI response
        session_mgr.add_message(session_id, 'assistant', response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        print(f'❌ Message error: {error}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(error)}), 500


# ==================== HELPER FUNCTIONS ====================

def stream_ai_response(session, message):
    """
    Stream AI response chunks
    
    This is a placeholder - integrate with your actual AI client
    (UnifiedAIClient from core/unified_ai_client.py)
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    # Simulate streaming response
    response_text = f"I received your message: '{message}'. This is a streaming response. "
    response_text += "In production, this would connect to Claude/GPT via the UnifiedAIClient. "
    
    # Yield content block start
    yield {
        'type': 'content_block_start',
        'index': 0,
        'content_block': {'type': 'text'}
    }
    
    # Stream text in chunks
    words = response_text.split(' ')
    for i, word in enumerate(words):
        chunk = word + ' '
        yield {
            'type': 'content_block_delta',
            'delta': chunk,
            'index': 0
        }
        time.sleep(0.05)  # Simulate streaming delay
    
    # Yield content block stop
    yield {
        'type': 'content_block_stop',
        'index': 0
    }


def get_ai_response(session, message):
    """
    Get AI response (non-streaming)
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    # Placeholder - integrate with UnifiedAIClient
    return f"Non-streaming response to: {message}"


def extract_pdf_text(pdf_content):
    """
    Extract text from PDF bytes
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        # TODO: Implement PDF text extraction
        # import PyPDF2 or pdfplumber
        return "[PDF content extraction not yet implemented]"
    except Exception as e:
        print(f"⚠️ PDF extraction error: {e}")
        return "[Failed to extract PDF text]"


# ==================== HEALTH CHECK ====================

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    return jsonify({
        'status': 'ok',
        'service': 'chat',
        'timestamp': datetime.utcnow().isoformat()
    })