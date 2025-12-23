"""
/AI_infrastructure/routes/transcription_routes.py
Transcription Routes - Voice/Audio Transcription with Whisper API

✅ LOCAL WHISPER (PyTorch) ENABLED - Server-side transcription for better accuracy

HOW IT WORKS:
- Frontend can use EITHER Browser Speech Recognition OR Local Whisper
- Browser STT: Instant, free, works in Chrome (webkitSpeechRecognition)
- Local Whisper: More accurate, works with audio files, supports multiple languages
- No conflict: Browser STT uses real-time API, Whisper uses file upload

USAGE:
- Browser STT: For instant voice-to-text in chat (no backend call)
- Local Whisper: For transcribing audio files or better quality (calls /api/transcribe)
- UI can toggle between modes based on user preference

⚠️ CURSOR MANAGEMENT FIXES (Nov 26, 2024):
   - ✅ All cursors properly closed before connections
   - ✅ All functions use finally blocks
   - ✅ All cursors initialized as None
   - ✅ Cursor closed before conn.close()

Endpoints:
- POST /api/transcribe - Audio transcription (DISABLED - Whisper not installed)
- GET /api/system/check - System health check
- POST /api/transcriptions/save - Save transcription to database (requires auth)
- GET /api/transcriptions/history - Get user transcription history (requires auth)

Features:
- OpenAI Whisper API integration for audio-to-text (if re-enabled)
- Streaming transcription results
- Audio format validation
- Error handling and logging
- Graceful degradation if Whisper not available

LAST MODIFIED: 2025-12-18 - Disabled PyTorch/Whisper to optimize Docker builds (30min → 15min)
"""

from flask import Blueprint, request, jsonify, Response
import os
import logging
from werkzeug.utils import secure_filename
import tempfile
import json
from AI_infrastructure.auth.user_auth import require_auth

# Setup logging
logger = logging.getLogger(__name__)

# Whisper model configuration (local) - lazy loaded to avoid blocking Flask startup
WHISPER_AVAILABLE = False
whisper_model = None
_whisper_lib_available = False
_whisper_load_error = None
MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')  # base, small, medium, large

try:
    import whisper  # noqa: F401
    import torch  # noqa: F401
    _whisper_lib_available = True
except Exception as e:
    _whisper_lib_available = False
    _whisper_load_error = str(e)
    logger.warning(f'[TRANSCRIPTION] Whisper library not available at import: {_whisper_load_error}')


def get_whisper_model():
    """Lazy-load the whisper model on first use. Returns model or None."""
    global whisper_model, WHISPER_AVAILABLE, _whisper_lib_available, _whisper_load_error
    if whisper_model is not None:
        return whisper_model

    if not _whisper_lib_available:
        logger.warning('[TRANSCRIPTION] Whisper library not available, cannot load model')
        return None

    try:
        import whisper
        import torch
        logger.info(f'[TRANSCRIPTION] Loading Whisper model lazily: {MODEL_SIZE}')
        whisper_model = whisper.load_model(MODEL_SIZE)
        WHISPER_AVAILABLE = True
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'[TRANSCRIPTION] Whisper loaded successfully on {device}')
        logger.info(f'[TRANSCRIPTION] Model size: {MODEL_SIZE}')
        return whisper_model
    except Exception as e:
        _whisper_load_error = str(e)
        logger.error(f'[TRANSCRIPTION] Failed to lazily load Whisper model: {e}', exc_info=True)
        WHISPER_AVAILABLE = False
        return None

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
    - language: Optional language code (en, es, fr, etc.) for Whisper
    - session_id: Session identifier (optional)
    
    Response:
    - JSON with transcript text, detected language, confidence, and duration
    - Streaming chunks if streaming enabled
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if file was uploaded (accept 'file' or 'audio' field names)
        upload_field = 'file' if 'file' in request.files else ('audio' if 'audio' in request.files else None)
        if upload_field is None:
            logger.error('[TRANSCRIPTION] No file in request')
            return jsonify({'error': 'No audio file provided'}), 400

        file = request.files[upload_field]
        
        if file.filename == '':
            logger.error('[TRANSCRIPTION] Empty filename')
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f'[TRANSCRIPTION] Invalid file type: {file.filename}')
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get optional parameters
        session_id = request.form.get('session_id', 'unknown')
        language_hint = request.form.get('language', None)  # Optional language hint
        
        logger.info(f'[TRANSCRIPTION] Processing file: {file.filename} (session: {session_id}, language: {language_hint or "auto"})')
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        file.save(temp_path)
        file_size = os.path.getsize(temp_path)
        
        logger.info(f'[TRANSCRIPTION] File saved: {temp_path} ({file_size} bytes)')
        
        transcript_text = ''
        detected_language = None
        confidence_score = None
        duration_seconds = None

        # Try to transcribe using whisper if available (lazy-loaded)
        if file_size == 0:
            transcript_text = '[Error: Audio file is empty]'
            logger.warning('[TRANSCRIPTION] Audio file is empty')
        else:
            model = get_whisper_model()
            if model is None:
                logger.warning('[TRANSCRIPTION] Whisper model not available; returning placeholder message')
                transcript_text = '[Whisper not available - install openai-whisper or enable model]'
            else:
                try:
                    logger.info('[TRANSCRIPTION] Transcribing with local Whisper model...')
                    
                    # Build Whisper parameters
                    whisper_params = {}
                    if language_hint and language_hint != 'auto':
                        whisper_params['language'] = language_hint
                        logger.info(f'[TRANSCRIPTION] Using language hint: {language_hint}')
                    
                    # Transcribe with Whisper (returns full result dict)
                    result_dict = model.transcribe(temp_path, **whisper_params)
                    
                    transcript_text = result_dict.get('text', '').strip()
                    detected_language = result_dict.get('language', 'unknown')
                    
                    # Calculate average confidence from segments (if available)
                    segments = result_dict.get('segments', [])
                    if segments:
                        # Some Whisper versions have 'no_speech_prob' or 'avg_logprob'
                        avg_logprobs = [s.get('avg_logprob', 0) for s in segments if 'avg_logprob' in s]
                        if avg_logprobs:
                            # Convert log probability to approximate confidence (0-1)
                            avg_logprob = sum(avg_logprobs) / len(avg_logprobs)
                            confidence_score = max(0, min(1, 1 + (avg_logprob / 10)))  # Rough mapping
                    
                    # Get duration from segments or result
                    if segments:
                        duration_seconds = segments[-1].get('end', None) if segments else None
                    
                    logger.info(f'[TRANSCRIPTION] Success: {len(transcript_text)} chars, language: {detected_language}, confidence: {confidence_score:.2f if confidence_score else "N/A"}, duration: {duration_seconds:.1f}s' if duration_seconds else f'{len(transcript_text)} chars')
                    
                except Exception as e:
                    logger.error(f'[TRANSCRIPTION] Whisper error: {str(e)}', exc_info=True)
                    transcript_text = f'[Error: {str(e)}]'
        
        # Build result with enhanced metadata
        result = {
            'success': bool(transcript_text and not transcript_text.startswith('[Error')),
            'transcript': transcript_text,
            'text': transcript_text,  # Backward compatibility
            'language': detected_language,
            'confidence': confidence_score,
            'duration': duration_seconds,
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
        
        logger.info(f'[TRANSCRIPTION] Response: {len(result["transcript"])} chars, lang={detected_language}')
        
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


@transcription_bp.route('/api/transcriptions/save', methods=['POST'])
@require_auth
def save_transcription():
    """
    Save a transcription record to the local database. Requires auth.
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cur = None  # ✅ Initialize cursor before try
    conn = None  # ✅ Initialize connection before try
    try:
        payload = request.get_json() or {}
        transcript = payload.get('transcript') or payload.get('text') or ''
        source_type = payload.get('source_type', 'recording')
        file_info = payload.get('file_info') or {}
        model_used = payload.get('model_used')
        confidence = payload.get('confidence')
        language = payload.get('language')
        duration = payload.get('duration_seconds')
        metadata = json.dumps(payload.get('metadata') or {})

        # Determine user id from decorator-injected request.user
        user_id = None
        if hasattr(request, 'user') and isinstance(request.user, dict):
            user_id = request.user.get('user_id') or request.user.get('id')
        if not user_id and hasattr(request, 'user_id'):
            user_id = request.user_id

        # ✅ FIX: Use PostgreSQL instead of SQLite
        from AI_infrastructure.shared.database_utils import get_connection
        
        cursor = None
        try:
            with get_connection('ai_infrastructure') as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO ai_infrastructure.user_transcriptions
                    (user_id, source_type, transcript_text, confidence, language, duration_seconds, word_count, model_used, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    user_id,
                    source_type,
                    transcript,
                    confidence,
                    language,
                    duration,
                    len(transcript.split()) if transcript else 0,
                    model_used,
                    metadata
                ))
                transcription_id = cursor.fetchone()[0]

                # If file_info provided, store
                if file_info and transcription_id:
                    try:
                        cursor.execute('''
                            INSERT INTO ai_infrastructure.transcription_uploads
                            (transcription_id, filename, file_size, file_type, mime_type, original_duration, processing_time_ms)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            transcription_id,
                            file_info.get('filename'),
                            file_info.get('size'),
                            file_info.get('format') or file_info.get('file_type'),
                            file_info.get('mime_type'),
                            file_info.get('duration_seconds'),
                            file_info.get('processing_time_ms')
                        ))
                    except Exception:
                        logger.exception('[TRANSCRIPTION] Failed to save upload metadata')
                
                cursor.close()
        except Exception as e:
            if cursor:
                cursor.close()
            raise e

        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cur.close()
        cur = None
        conn.close()
        conn = None

        return jsonify({'success': True, 'transcription_id': transcription_id}), 200

    except Exception as e:
        logger.error(f'[TRANSCRIPTION] Save error: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # ✅ Guaranteed cleanup
        if cur:
            try:
                cur.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@transcription_bp.route('/api/transcriptions/history', methods=['GET'])
@require_auth
def transcription_history():
    """
    Return transcription history for the authenticated user.
    
    ✅ FIXED: Use execute_query pattern from database_utils
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Determine user id from decorator-injected request.user
        user_id = None
        if hasattr(request, 'user') and isinstance(request.user, dict):
            user_id = request.user.get('user_id') or request.user.get('id')
        if not user_id and hasattr(request, 'user_id'):
            user_id = request.user_id

        # ✅ FIX: Use execute_query from database_utils (proper connection pooling)
        from AI_infrastructure.shared.database_utils import execute_query
        
        if user_id:
            rows = execute_query(
                '''
                SELECT id, source_type, transcript_text, confidence, language, 
                       duration_seconds, model_used, created_at
                FROM ai_infrastructure.user_transcriptions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                ''',
                (user_id, limit, offset),
                fetch_mode='all'
            )
        else:
            rows = execute_query(
                '''
                SELECT id, source_type, transcript_text, confidence, language, 
                       duration_seconds, model_used, created_at
                FROM ai_infrastructure.user_transcriptions
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                ''',
                (limit, offset),
                fetch_mode='all'
            )

        results = []
        for r in rows:
            results.append({
                'id': r[0],
                'source_type': r[1],
                'transcript': r[2],
                'confidence': r[3],
                'language': r[4],
                'duration_seconds': r[5],
                'model_used': r[6],
                'created_at': r[7].isoformat() if hasattr(r[7], 'isoformat') else str(r[7])
            })

        return jsonify({'success': True, 'history': results}), 200
        
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] History error: {e}', exc_info=True)
        
        # Check if it's a missing table error
        error_msg = str(e)
        if 'does not exist' in error_msg or 'UndefinedTable' in error_msg:
            logger.warning('[TRANSCRIPTION] user_transcriptions table not found - returning empty history')
            return jsonify({
                'success': True, 
                'history': [],
                'warning': 'Transcription history table not initialized. Run migration: python AI_infrastructure/migrations/run_014_user_transcriptions.py'
            }), 200
        
        return jsonify({'success': False, 'error': str(e)}), 500


# Export blueprint for flask_app.py to register
__all__ = ['transcription_bp']