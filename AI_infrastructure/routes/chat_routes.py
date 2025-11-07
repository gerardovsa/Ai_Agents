"""
Chat Routes - SSE Streaming & File Upload
Handles multi-agent chat with streaming responses and file uploads

Endpoints:
- GET /api/chat/stream - Server-Sent Events streaming
- POST /api/chat/upload - File upload handling
- POST /api/chat/message - Single message (non-streaming fallback)
"""

from flask import Blueprint, request, Response, jsonify, stream_with_context
import json
import time
from datetime import datetime

# Will be initialized by flask_app.py
chat_bp = Blueprint('chat', __name__)

# Global references (set by flask_app)
session_manager = None
ai_client = None

def init_chat_routes(sm, aic):
    """Initialize with session manager and AI client"""
    global session_manager, ai_client
    session_manager = sm
    ai_client = aic


@chat_bp.route('/stream', methods=['GET'])
def stream_chat():
    """
    SSE streaming endpoint for AI chat
    
    Query Parameters:
        session_id (str): Unique session identifier
        message (str): User message to send to AI
    
    Returns:
        text/event-stream: Server-Sent Events stream
    """
    session_id = request.args.get('session_id')
    message = request.args.get('message', '')
    
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    
    def generate():
        try:
            # Get session context
            session = session_manager.get_session(session_id)
            
            # Add user message to history
            if message:
                session_manager.add_message(session_id, 'user', message)
            
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
                session_manager.add_message(session_id, 'assistant', response_text)
            
            yield f"event: message_stop\ndata: {json.dumps({'session_id': session_id})}\n\n"
            
        except Exception as error:
            print(f' Stream error: {error}')
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
    
    Returns:
        JSON: {success: bool, files: [{name, type, size, content}]}
    """
    session_id = request.form.get('session_id')
    message = request.form.get('message', '')
    files = request.files.getlist('files')
    
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    
    processed_files = []
    
    for file in files:
        try:
            # Validate file
            if file.filename == '':
                continue
            
            # Read file content
            content = file.read()
            file_size = len(content)
            
            # Process based on type
            if file.content_type.startswith('text/'):
                text_content = content.decode('utf-8')
            elif file.content_type == 'application/pdf':
                text_content = extract_pdf_text(content)
            elif file.content_type == 'text/csv':
                text_content = content.decode('utf-8')
            else:
                text_content = f'[Binary file: {file.filename}]'
            
            processed_files.append({
                'name': file.filename,
                'type': file.content_type,
                'size': file_size,
                'content': text_content[:5000]  # Limit to 5KB per file
            })
            
            # Save file context to session
            session_manager.add_file_context(session_id, file.filename, text_content)
            
        except Exception as error:
            print(f' File processing error: {error}')
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
    """
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message', '')
    
    if not session_id or not message:
        return jsonify({'error': 'session_id and message required'}), 400
    
    try:
        # Get session
        session = session_manager.get_session(session_id)
        
        # Add user message
        session_manager.add_message(session_id, 'user', message)
        
        # Get AI response (non-streaming)
        response = get_ai_response(session, message)
        
        # Save AI response
        session_manager.add_message(session_id, 'assistant', response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as error:
        print(f' Message error: {error}')
        return jsonify({'error': str(error)}), 500


# ==================== HELPER FUNCTIONS ====================

def stream_ai_response(session, message):
    """
    Stream AI response chunks
    
    This is a placeholder - integrate with your actual AI client
    (UnifiedAIClient from core/unified_ai_client.py)
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
    """Get AI response (non-streaming)"""
    # Placeholder - integrate with UnifiedAIClient
    return f"Non-streaming response to: {message}"


def extract_pdf_text(pdf_content):
    """Extract text from PDF bytes"""
    try:
        # TODO: Implement PDF text extraction
        # import PyPDF2 or pdfplumber
        return "[PDF content extraction not yet implemented]"
    except:
        return "[Failed to extract PDF text]"


# ==================== HEALTH CHECK ====================

@chat_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'chat',
        'timestamp': datetime.utcnow().isoformat()
    })
