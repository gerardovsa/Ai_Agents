"""
Transcription Routes - Voice/Audio Transcription with Whisper API

Endpoints:
- POST /api/transcribe - Audio transcription with streaming support
- GET /api/system/check - System health check

Features:
- OpenAI Whisper API integration for audio-to-text
- Streaming transcription results
- Audio format validation
- Error handling and logging

LAST MODIFIED: 2025-11-26
"""

from flask import Blueprint, request, jsonify, Response
import os
import logging
from werkzeug.utils import secure_filename
import tempfile
import json

# Setup logging
logger = logging.getLogger(__name__)

# Whisper model configuration (local)
WHISPER_AVAILABLE = False
whisper_model = None

try:
    import whisper
    import torch
    
    # Determine best model based on environment
    # For Render.com: Use 'base' or 'small' to fit in memory constraints
    # For local: Can use 'medium' or 'large' if you have GPU
    MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')  # base, small, medium, large
    
    logger.info(f'[TRANSCRIPTION] Loading Whisper model: {MODEL_SIZE}')
    whisper_model = whisper.load_model(MODEL_SIZE)
    WHISPER_AVAILABLE = True
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f'[TRANSCRIPTION] Whisper loaded successfully on {device}')
    logger.info(f'[TRANSCRIPTION] Model size: {MODEL_SIZE}')
    
except ImportError as e:
    logger.warning(f'[TRANSCRIPTION] Whisper library not installed: {e}')
    logger.warning('[TRANSCRIPTION] Install with: pip install openai-whisper')
except Exception as e:
    logger.warning(f'[TRANSCRIPTION] Failed to load Whisper model: {e}')

# Create blueprint
transcription_bp = Blueprint('transcription', __name__)

# Allowed audio formats
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm', 'ogg', 'm4a', 'flac'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@transcription_bp.route('/api/transcribe', methods=['POST', 'OPTIONS'])
def transcribe_audio():
    """
    Transcribe audio file using Whisper API
    
    Request:
    - file: Audio file (multipart/form-data)
    - session_id: Session identifier (optional)
    
    Response:
    - JSON with transcript text
    - Streaming chunks if streaming enabled
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.error('[TRANSCRIPTION] No file in request')
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error('[TRANSCRIPTION] Empty filename')
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f'[TRANSCRIPTION] Invalid file type: {file.filename}')
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get session ID
        session_id = request.form.get('session_id', 'unknown')
        
        logger.info(f'[TRANSCRIPTION] Processing file: {file.filename} (session: {session_id})')
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        file.save(temp_path)
        file_size = os.path.getsize(temp_path)
        
        logger.info(f'[TRANSCRIPTION] File saved: {temp_path} ({file_size} bytes)')
        
        # Transcribe with local Whisper model
        transcript_text = ''
        
        if WHISPER_AVAILABLE and file_size > 0:
            try:
                logger.info('[TRANSCRIPTION] Transcribing with local Whisper model...')
                
                # Transcribe audio file
                result = whisper_model.transcribe(temp_path)
                transcript_text = result['text'].strip()
                
                logger.info(f'[TRANSCRIPTION] Success: {len(transcript_text)} chars')
                logger.info(f'[TRANSCRIPTION] Language detected: {result.get("language", "unknown")}')
                
            except Exception as e:
                logger.error(f'[TRANSCRIPTION] Whisper error: {str(e)}', exc_info=True)
                transcript_text = f'[Error: {str(e)}]'
        else:
            if not WHISPER_AVAILABLE:
                transcript_text = '[Whisper not available - install with: pip install openai-whisper]'
                logger.warning('[TRANSCRIPTION] Whisper library not loaded')
            elif file_size == 0:
                transcript_text = '[Error: Audio file is empty]'
                logger.warning('[TRANSCRIPTION] Audio file is empty')
        
        # Build result
        result = {
            'success': bool(transcript_text and not transcript_text.startswith('[Error')),
            'transcript': transcript_text,
            'text': transcript_text,
            'session_id': session_id,
            'file_info': {
                'filename': filename,
                'size': file_size,
                'format': filename.rsplit('.', 1)[1].lower()
            }
        }
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except Exception as e:
            logger.warning(f'[TRANSCRIPTION] Failed to remove temp file: {e}')
        
        logger.info(f'[TRANSCRIPTION] Success: {len(result["transcript"])} chars')
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] Error: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@transcription_bp.route('/api/system/check', methods=['GET', 'OPTIONS'])
def system_check():
    """
    System health check endpoint
    
    Returns:
    - status: System status
    - available: Whether transcription service is available
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get model info if available
        model_info = 'Not loaded'
        if WHISPER_AVAILABLE and whisper_model:
            model_size = os.getenv('WHISPER_MODEL_SIZE', 'base')
            model_info = f'{model_size} (local)'
        
        return jsonify({
            'status': 'ok',
            'service': 'transcription',
            'available': WHISPER_AVAILABLE,
            'provider': 'Local Whisper Model' if WHISPER_AVAILABLE else 'Not configured',
            'model': model_info,
            'supported_formats': list(ALLOWED_EXTENSIONS),
            'installation': 'pip install openai-whisper' if not WHISPER_AVAILABLE else None
        }), 200
        
    except Exception as e:
        logger.error(f'[SYSTEM CHECK] Error: {str(e)}')
        return jsonify({
            'status': 'error',
            'service': 'transcription',
            'available': False,
            'error': str(e)
        }), 500


# Export blueprint for flask_app.py to register
__all__ = ['transcription_bp']
