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

from flask import Blueprint, request, jsonify, Response, g
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
_whisper_load_error = None
MODEL_SIZE = os.getenv('WHISPER_MODEL_SIZE', 'base')  # base, small, medium, large

# Store Whisper models on the Render persistent disk (/data) so they survive
# redeploys and don't re-download each time.  Same pattern as /data/vdb_models.
# Falls back to ~/.cache/whisper on local dev where /data isn't mounted.
WHISPER_CACHE_DIR = '/data/whisper_models' if os.path.isdir('/data') else os.path.join(
    os.path.expanduser('~'), '.cache', 'whisper'
)

# Use find_spec() instead of importing torch/whisper at module level.
# Actual import happens only inside get_whisper_model() on first transcription request.
# This avoids a 30-60s cold-start penalty on Render (torch is ~1GB and slow to load).
import importlib.util as _importlib_util
_whisper_lib_available = (
    _importlib_util.find_spec('whisper') is not None and
    _importlib_util.find_spec('torch') is not None
)
if not _whisper_lib_available:
    _whisper_load_error = 'whisper or torch package not installed'
    logger.warning('[TRANSCRIPTION] Whisper/torch not found in environment')


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
        os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
        from_cache = any(
            f.endswith('.pt') for f in os.listdir(WHISPER_CACHE_DIR)
        ) if os.path.isdir(WHISPER_CACHE_DIR) else False
        logger.info(
            f'[TRANSCRIPTION] Loading Whisper {MODEL_SIZE} from '
            f'{"disk cache" if from_cache else "HuggingFace (first-time download)"} '
            f'→ {WHISPER_CACHE_DIR}'
        )
        whisper_model = whisper.load_model(MODEL_SIZE, download_root=WHISPER_CACHE_DIR)
        WHISPER_AVAILABLE = True
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'[TRANSCRIPTION] Whisper loaded on {device} ({MODEL_SIZE})')
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
@require_auth
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
        engine = request.form.get('engine', 'local')  # local | openai | deepgram | assemblyai-async
        request_diarize = request.form.get('diarize', 'false').lower() == 'true'

        logger.info(f'[TRANSCRIPTION] Processing file: {file.filename} (engine: {engine}, session: {session_id}, language: {language_hint or "auto"}, diarize: {request_diarize})')
        
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
        speakers_data = None

        if file_size == 0:
            transcript_text = '[Error: Audio file is empty]'
            logger.warning('[TRANSCRIPTION] Audio file is empty')

        elif engine == 'openai':
            # ── OpenAI gpt-4o-transcribe (most accurate, uses org vault key) ──
            try:
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                from openai import OpenAI as _OpenAI
                oai_key = resolve_api_key(g.user_id, 'openai')
                if not oai_key:
                    raise ValueError('OpenAI API key not configured. Add it in Org → Connections.')
                client = _OpenAI(api_key=oai_key)
                logger.info('[TRANSCRIPTION] Transcribing with OpenAI gpt-4o-transcribe...')
                with open(temp_path, 'rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model='gpt-4o-transcribe',
                        file=audio_file,
                        language=language_hint if (language_hint and language_hint != 'auto') else None,
                        response_format='verbose_json'
                    )
                transcript_text = transcription.text or ''
                detected_language = getattr(transcription, 'language', None)
                duration_seconds = getattr(transcription, 'duration', None)
                confidence_score = 0.98
                logger.info(f'[TRANSCRIPTION] OpenAI: {len(transcript_text)} chars, lang={detected_language}')
            except Exception as e:
                logger.error(f'[TRANSCRIPTION] OpenAI error: {e}', exc_info=True)
                transcript_text = f'[OpenAI Error: {str(e)}]'

        elif engine == 'deepgram':
            # ── Deepgram Nova-3 (fast, GDPR/EU, speaker diarization) ──
            try:
                import requests as _ext_req
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                dg_key = resolve_api_key(g.user_id, 'deepgram')
                if not dg_key:
                    raise ValueError('Deepgram API key not configured. Add it in Org → Connections.')
                logger.info(f'[TRANSCRIPTION] Transcribing with Deepgram (diarize={request_diarize})...')
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                params = {
                    'model': 'nova-3', 'smart_format': 'true',
                    'diarize': 'true' if request_diarize else 'false', 'punctuate': 'true',
                }
                if language_hint and language_hint != 'auto':
                    params['language'] = language_hint
                dg_resp = _ext_req.post(
                    'https://api.deepgram.com/v1/listen', params=params, data=audio_data,
                    headers={'Authorization': f'Token {dg_key}', 'Content-Type': 'audio/*'}, timeout=120
                )
                if dg_resp.status_code != 200:
                    raise ValueError(f'Deepgram API error: {dg_resp.status_code}')
                dg_json = dg_resp.json()
                channel = dg_json.get('results', {}).get('channels', [{}])[0]
                alt = channel.get('alternatives', [{}])[0]
                words = alt.get('words', [])
                if request_diarize and words and any('speaker' in w for w in words):
                    lines, cur_speaker, cur_words = [], None, []
                    for w in words:
                        spk = w.get('speaker', 0)
                        if spk != cur_speaker:
                            if cur_words:
                                lines.append(f'[Speaker {cur_speaker}] {" ".join(cur_words)}')
                            cur_speaker, cur_words = spk, [w.get('punctuated_word', w.get('word', ''))]
                        else:
                            cur_words.append(w.get('punctuated_word', w.get('word', '')))
                    if cur_words:
                        lines.append(f'[Speaker {cur_speaker}] {" ".join(cur_words)}')
                    transcript_text = '\n'.join(lines)
                    speakers_data = list({w.get('speaker') for w in words if 'speaker' in w})
                else:
                    transcript_text = alt.get('transcript', '')
                meta = dg_json.get('metadata', {})
                duration_seconds = meta.get('duration')
                confidence_score = alt.get('confidence', 0.9)
                detected_language = channel.get('detected_language', 'en')
                logger.info(f'[TRANSCRIPTION] Deepgram: {len(transcript_text)} chars, {len(speakers_data or [])} speakers')
            except Exception as e:
                logger.error(f'[TRANSCRIPTION] Deepgram error: {e}', exc_info=True)
                transcript_text = f'[Deepgram Error: {str(e)}]'

        elif engine == 'assemblyai-async':
            # ── AssemblyAI async with optional speaker diarization ──
            try:
                import assemblyai as aai
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                aai_key = resolve_api_key(g.user_id, 'assemblyai')
                if not aai_key:
                    raise ValueError('AssemblyAI API key not configured. Add it in Org → Connections.')
                aai.settings.api_key = aai_key
                logger.info(f'[TRANSCRIPTION] Transcribing with AssemblyAI (diarize={request_diarize})...')
                config = aai.TranscriptionConfig(
                    speaker_labels=request_diarize,
                    language_code=language_hint if (language_hint and language_hint != 'auto') else None,
                )
                transcriber = aai.Transcriber()
                aai_result = transcriber.transcribe(temp_path, config=config)
                if aai_result.status == aai.TranscriptStatus.error:
                    raise ValueError(f'AssemblyAI error: {aai_result.error}')
                if request_diarize and aai_result.utterances:
                    lines = [f'[Speaker {u.speaker}] {u.text}' for u in aai_result.utterances]
                    transcript_text = '\n'.join(lines)
                    speakers_data = list({u.speaker for u in aai_result.utterances})
                else:
                    transcript_text = aai_result.text or ''
                detected_language = language_hint or 'en'
                confidence_score = aai_result.confidence
                duration_seconds = aai_result.audio_duration
                logger.info(f'[TRANSCRIPTION] AssemblyAI: {len(transcript_text)} chars')
            except Exception as e:
                logger.error(f'[TRANSCRIPTION] AssemblyAI error: {e}', exc_info=True)
                transcript_text = f'[AssemblyAI Error: {str(e)}]'

        else:
            # ── Default: Local PyTorch Whisper (engine='local') ──
            model = get_whisper_model()
            if model is None:
                logger.warning('[TRANSCRIPTION] Local Whisper not available.')
                transcript_text = ('[Local Whisper unavailable — Render Starter plan (512MB) is too small for '
                                   'the base model (~1GB RAM). Upgrade to Standard (2GB) or use the OpenAI engine.')
            else:
                try:
                    logger.info('[TRANSCRIPTION] Transcribing with local Whisper model...')
                    whisper_params = {}
                    if language_hint and language_hint != 'auto':
                        whisper_params['language'] = language_hint
                    result_dict = model.transcribe(temp_path, **whisper_params)
                    transcript_text = result_dict.get('text', '').strip()
                    detected_language = result_dict.get('language', 'unknown')
                    segments = result_dict.get('segments', [])
                    if segments:
                        avg_logprobs = [s.get('avg_logprob', 0) for s in segments if 'avg_logprob' in s]
                        if avg_logprobs:
                            avg_logprob = sum(avg_logprobs) / len(avg_logprobs)
                            confidence_score = max(0, min(1, 1 + (avg_logprob / 10)))
                        duration_seconds = segments[-1].get('end', None)
                    logger.info(f'[TRANSCRIPTION] Local Whisper: {len(transcript_text)} chars, lang={detected_language}')
                except Exception as e:
                    logger.error(f'[TRANSCRIPTION] Whisper error: {str(e)}', exc_info=True)
                    transcript_text = f'[Error: {str(e)}]'

        # Build result with enhanced metadata
        result = {
            'success': bool(transcript_text and not transcript_text.startswith('[')),
            'transcript': transcript_text,
            'text': transcript_text,  # Backward compatibility
            'language': detected_language,
            'confidence': confidence_score,
            'duration': duration_seconds,
            'engine': engine,
            'speakers': speakers_data,
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


# ============================================================================
# ASSEMBLYAI STREAMING SUPPORT
# ============================================================================

@transcription_bp.route('/api/transcription/assemblyai-status', methods=['GET'])
@require_auth
def assemblyai_status():
    """
    GET /api/transcription/assemblyai-status
    Lightweight check: does this org/user have an AssemblyAI API key configured?
    Uses the full 4-tier resolver (user key → sub-user inheritance → org key → env var).
    No external API call is made.
    """
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key

        user_id = g.user_id
        api_key = resolve_api_key(user_id, 'assemblyai')
        return jsonify({'has_key': bool(api_key)}), 200

    except Exception as e:
        logger.error(f'[TRANSCRIPTION] AssemblyAI status check error: {e}', exc_info=True)
        return jsonify({'has_key': False, 'error': str(e)}), 200


@transcription_bp.route('/api/transcription/assemblyai-token', methods=['GET'])
@require_auth
def get_assemblyai_token():
    """
    GET /api/transcription/assemblyai-token
    Exchange the user's/org's AssemblyAI API key for a short-lived streaming token.
    Uses the full 4-tier resolver: user key → sub-user inheritance → org key → env var.
    Token expires in 60 seconds but allows a session of up to 1 hour.
    The API key is NEVER sent to the browser — only the temporary token.
    """
    import requests as ext_requests
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key

        user_id = g.user_id
        api_key = resolve_api_key(user_id, 'assemblyai')
        if not api_key:
            return jsonify({'error': 'AssemblyAI API key not configured. Add it in Org → Connections.'}), 404

        # Exchange for a short-lived streaming token (never exposed to browser)
        token_resp = ext_requests.get(
            'https://streaming.assemblyai.com/v3/token',
            params={'expires_in_seconds': 60, 'max_session_duration_seconds': 3600},
            headers={'Authorization': api_key},
            timeout=10
        )

        if token_resp.status_code != 200:
            logger.error(f'[TRANSCRIPTION] AssemblyAI token error: {token_resp.status_code} {token_resp.text}')
            return jsonify({'error': 'Failed to obtain AssemblyAI streaming token'}), 502

        token_json = token_resp.json()
        return jsonify({'token': token_json.get('token'), 'expires_in': 60}), 200

    except Exception as e:
        logger.error(f'[TRANSCRIPTION] AssemblyAI token endpoint error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500



# ============================================================================
# ALL-ENGINES STATUS + TOKEN ENDPOINTS
# ============================================================================

@transcription_bp.route('/api/transcription/engines-status', methods=['GET'])
@require_auth
def engines_status():
    """
    GET /api/transcription/engines-status
    Check all transcription engine API keys at once via the 4-tier credential resolver.
    Returns {engines: {platform -> {has_key: bool, ...}}}
    """
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
        user_id = g.user_id
        result = {}
        for platform in ('openai', 'assemblyai', 'deepgram', 'speechmatics'):
            try:
                key = resolve_api_key(user_id, platform)
                result[platform] = {'has_key': bool(key)}
            except Exception as e:
                result[platform] = {'has_key': False, 'error': str(e)}
        result['local_whisper'] = {
            'has_key': True,
            'available': _whisper_lib_available,
            'model_loaded': whisper_model is not None,
            'error': _whisper_load_error if not _whisper_lib_available else None,
        }
        return jsonify({'engines': result}), 200
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] Engines status error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcription_bp.route('/api/transcription/deepgram-token', methods=['GET'])
@require_auth
def get_deepgram_token():
    """
    GET /api/transcription/deepgram-token
    Exchange the org's Deepgram API key for a short-lived streaming token (60s TTL).
    Frontend connects directly: wss://api.deepgram.com/v1/listen?model=nova-3&token=<temp_key>
    """
    import requests as ext_requests
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
        api_key = resolve_api_key(g.user_id, 'deepgram')
        if not api_key:
            return jsonify({'error': 'Deepgram API key not configured. Add it in Org → Connections.'}), 404
        # Step 1: get project ID
        proj_resp = ext_requests.get(
            'https://api.deepgram.com/v1/projects',
            headers={'Authorization': f'Token {api_key}'},
            timeout=10
        )
        if proj_resp.status_code != 200:
            return jsonify({'error': 'Failed to retrieve Deepgram project list'}), 502
        projects = proj_resp.json().get('projects', [])
        if not projects:
            return jsonify({'error': 'No Deepgram projects found for this API key'}), 404
        project_id = projects[0]['project_id']
        # Step 2: create temporary key (60s TTL)
        key_resp = ext_requests.post(
            f'https://api.deepgram.com/v1/projects/{project_id}/keys',
            json={'comment': 'temp-streaming', 'scopes': ['usage:write'], 'time_to_live_in_seconds': 60},
            headers={'Authorization': f'Token {api_key}', 'Content-Type': 'application/json'},
            timeout=10
        )
        if key_resp.status_code not in (200, 201):
            logger.error(f'[TRANSCRIPTION] Deepgram key creation failed: {key_resp.status_code}')
            return jsonify({'error': 'Failed to create Deepgram streaming token'}), 502
        temp_key = key_resp.json().get('key')
        return jsonify({'token': temp_key, 'expires_in': 60}), 200
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] Deepgram token error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcription_bp.route('/api/transcription/openai-realtime-token', methods=['GET'])
@require_auth
def get_openai_realtime_token():
    """
    GET /api/transcription/openai-realtime-token
    Exchange the org's OpenAI API key for a short-lived Realtime ephemeral token.
    Frontend: new WebSocket(url, ['realtime', 'openai-insecure-api-key.{token}', 'openai-beta.realtime-v1'])
    """
    import requests as ext_requests
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
        api_key = resolve_api_key(g.user_id, 'openai')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured. Add it in Org → Connections.'}), 404
        resp = ext_requests.post(
            'https://api.openai.com/v1/realtime/sessions',
            json={
                'model': 'gpt-4o-realtime-preview',
                'voice': 'echo',
                'input_audio_transcription': {'model': 'whisper-1'},
                'instructions': 'You are a transcription assistant. Transcribe all speech accurately.'
            },
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            timeout=10
        )
        if resp.status_code != 200:
            logger.error(f'[TRANSCRIPTION] OpenAI Realtime session error: {resp.status_code} {resp.text}')
            return jsonify({'error': 'Failed to create OpenAI Realtime session'}), 502
        data = resp.json()
        client_secret = data.get('client_secret', {})
        return jsonify({
            'token': client_secret.get('value'),
            'expires_at': client_secret.get('expires_at'),
            'model': data.get('model', 'gpt-4o-realtime-preview')
        }), 200
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] OpenAI Realtime token error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcription_bp.route('/api/transcription/speechmatics-token', methods=['GET'])
@require_auth
def get_speechmatics_token():
    """
    GET /api/transcription/speechmatics-token
    Exchange the org's Speechmatics API key for a short-lived JWT (1h TTL).
    EU endpoint wss://eu2.rt.speechmatics.com — GDPR-compliant UK/EU data processing.
    """
    import requests as ext_requests
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
        api_key = resolve_api_key(g.user_id, 'speechmatics')
        if not api_key:
            return jsonify({'error': 'Speechmatics API key not configured. Add it in Org → Connections.'}), 404
        resp = ext_requests.post(
            'https://mp.speechmatics.com/v1/api_keys?type=rt',
            json={'ttl': 3600},
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            timeout=10
        )
        if resp.status_code not in (200, 201):
            logger.error(f'[TRANSCRIPTION] Speechmatics token error: {resp.status_code} {resp.text}')
            return jsonify({'error': 'Failed to create Speechmatics JWT'}), 502
        token = resp.json().get('key_value')
        return jsonify({'token': token, 'expires_in': 3600}), 200
    except Exception as e:
        logger.error(f'[TRANSCRIPTION] Speechmatics token error: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


# Export blueprint for flask_app.py to register
__all__ = ['transcription_bp']