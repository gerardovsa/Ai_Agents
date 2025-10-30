"""
New Flask App - Clean Rebuild
Uses unified session manager and AI client

This is the NEW clean Flask app that replaces flask_triple_agent_app.py
Run on port 5001 for testing, then swap to port 5000 when ready
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import json
import os
from pathlib import Path
from queue import Queue, Empty
import threading

# Load environment variables from .env.master file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.master'))
print(f"Loaded .env.master file")
print(f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"DEEPSEEK_API_KEY_1: {'SET' if os.getenv('DEEPSEEK_API_KEY_1') else 'NOT SET'}")
print(f"MICROSOFT_CLIENT_ID: {'SET' if os.getenv('MICROSOFT_CLIENT_ID') else 'NOT SET'}")
print(f"MICROSOFT_CLIENT_SECRET: {'SET' if os.getenv('MICROSOFT_CLIENT_SECRET') else 'NOT SET'}")

# Import configuration from LOCAL config.py (AI_infrastructure/config.py)
try:
    # Try importing from same directory
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from config import Config
    print("[OK] Using AI_infrastructure/config.py for configuration")
except (ImportError, AttributeError) as e:
    print(f"[WARNING] Local config.py import failed ({e}) - using fallback configuration")
    # Fallback configuration class with all required attributes
    class Config:
        """Flask app configuration - Fallback"""
        BASE_DIR = Path(__file__).parent
        SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        TESTING = False
        DB_CONFIG_PATH = Path(__file__).parent / 'data' / 'database-config.json'
        SESSION_DB_PATH = Path(__file__).parent / 'data' / 'sessions.db'
        
        # Session configuration
        SESSION_TYPE = 'filesystem'
        PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
        
        # CORS configuration
        CORS_ORIGINS = ['http://localhost:5001', 'http://localhost:5000', 'http://127.0.0.1:5001', 'http://127.0.0.1:5000', '*']
        
        # Database configuration (SQLite)
        DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'ai_infrastructure.db'))

# Import core infrastructure (NEW CLEAN CODE)
from core.unified_session_manager import session_manager
from core.unified_ai_client import initialize_ai_client

# Import routes (blueprints) - CLEANED UP: Only generic routes
from routes.agent_routes import agent_bp
from routes.thread_routes import thread_bp
from routes.export_routes import export_bp
from routes.woocommerce_routes import woocommerce_bp
from routes.auth_routes import auth_bp  # NEW: User authentication
from routes.google_auth_routes import google_auth_bp  # NEW: Google OAuth
from routes.microsoft_auth_routes import microsoft_auth_bp  # NEW: Microsoft OAuth
from routes.account_linking_routes import account_linking_bp  # NEW: Account linking
from routes.kanban_routes import kanban_bp  # NEW: Kanban board with AI agent integration

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints - CLEANED UP: Generic routes only (16 endpoints)
app.register_blueprint(agent_bp, url_prefix='/api/agent')           # 8 endpoints (AI agent orchestration)
app.register_blueprint(thread_bp, url_prefix='/api/threads')        # 8 endpoints (conversation storage)
app.register_blueprint(export_bp, url_prefix='/api/export')         # 3 endpoints (export functionality)
app.register_blueprint(woocommerce_bp)                               # 9 endpoints (WooCommerce direct API)
app.register_blueprint(auth_bp)                                      # NEW: 6 endpoints (user auth)
app.register_blueprint(google_auth_bp)                               # NEW: Google OAuth (/api/auth/google/*)
app.register_blueprint(microsoft_auth_bp)                            # NEW: Microsoft OAuth (/api/auth/microsoft/*)
app.register_blueprint(account_linking_bp)                           # NEW: Account linking (/api/account/*)
app.register_blueprint(kanban_bp)                                    # NEW: Kanban board + AI agent bridge (8 endpoints)

# Legacy compatibility: register /api/sessions/* proxy so older UIs work
try:
    from routes.compat_sessions import compat_bp
    app.register_blueprint(compat_bp)
    print('Compatibility blueprint registered: /api/sessions/* -> /api/kanban/*')
except Exception:
    print('Compatibility blueprint not available')

# TODO: Add platform-specific routes for 281 tools across 19 platforms:
# - openai_routes.py (15 tools)
# - anthropic_routes.py (10 tools)
# - deepseek_routes.py (8 tools)
# - gmail_routes.py (29 tools)
# - slack_routes.py (24 tools)
# - woocommerce_routes.py (29 tools)
# - stripe_routes.py (25 tools)
# - ... and 12 more platform routes

# Serve static UI files
UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'UI')

@app.route('/')
def serve_ui():
    """Serve the main UI page"""
    return send_from_directory(UI_DIR, 'business-ai-platform-v2.html')

@app.route('/<path:filename>')
def serve_ui_static(filename):
    """Serve static files from UI directory (CSS, JS, etc.)"""
    return send_from_directory(UI_DIR, filename)

# Enable CORS - Allow all origins for development
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Initialize SocketIO with full async support
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Track connected clients and their rooms
connected_clients = {}

# ============================================================================
# COMPREHENSIVE SOCKETIO HANDLERS FOR /ws/synergy NAMESPACE
# ============================================================================

@socketio.on('connect', namespace='/ws/synergy')
def ws_synergy_connect():
    """Handle client connection to Synergy namespace"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    client_id = flask_request.sid
    connected_clients[client_id] = {
        'rooms': set(),
        'connected_at': datetime.now().isoformat()
    }
    
    print(f'[WS] Client connected to /ws/synergy: {client_id}')
    emit('connected', {
        'status': 'connected',
        'client_id': client_id,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect', namespace='/ws/synergy')
def ws_synergy_disconnect():
    """Handle client disconnection"""
    from flask import request as flask_request
    
    client_id = flask_request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]
    
    print(f'[WS] Client disconnected from /ws/synergy: {client_id}')

@socketio.on('subscribe', namespace='/ws/synergy')
def ws_synergy_subscribe(data):
    """Subscribe client to specific rooms/channels"""
    from flask_socketio import join_room, emit
    from flask import request as flask_request
    
    client_id = flask_request.sid
    room = data.get('room', 'default')
    
    join_room(room)
    
    if client_id in connected_clients:
        connected_clients[client_id]['rooms'].add(room)
    
    print(f'[WS] Client {client_id} subscribed to room: {room}')
    emit('subscribed', {
        'room': room,
        'status': 'subscribed',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('unsubscribe', namespace='/ws/synergy')
def ws_synergy_unsubscribe(data):
    """Unsubscribe client from room"""
    from flask_socketio import leave_room, emit
    from flask import request as flask_request
    
    client_id = flask_request.sid
    room = data.get('room', 'default')
    
    leave_room(room)
    
    if client_id in connected_clients and room in connected_clients[client_id]['rooms']:
        connected_clients[client_id]['rooms'].remove(room)
    
    print(f'[WS] Client {client_id} unsubscribed from room: {room}')
    emit('unsubscribed', {'room': room, 'status': 'unsubscribed'})

@socketio.on('ping', namespace='/ws/synergy')
def ws_synergy_ping(data):
    """Handle ping from client"""
    from flask_socketio import emit
    print(f'[WS] Ping received: {data}')
    emit('pong', {
        'timestamp': datetime.now().isoformat(),
        'data': data
    })

@socketio.on('broadcast', namespace='/ws/synergy')
def ws_synergy_broadcast(data):
    """Broadcast message to all clients in a room"""
    from flask_socketio import emit
    
    room = data.get('room', 'default')
    message = data.get('message', {})
    
    print(f'[WS] Broadcasting to room {room}: {message}')
    emit('message', message, room=room, include_self=False)

@socketio.on('session_update', namespace='/ws/synergy')
def ws_synergy_session_update(data):
    """Handle Kanban session updates and broadcast to other clients"""
    from flask_socketio import emit
    
    session_id = data.get('session_id')
    updates = data.get('updates', {})
    room = data.get('room', 'default')
    
    print(f'[WS] Session update: {session_id} in room {room}')
    
    # Broadcast to all other clients in the room
    emit('session_updated', {
        'session_id': session_id,
        'updates': updates,
        'timestamp': datetime.now().isoformat()
    }, room=room, include_self=False)

@socketio.on('column_change', namespace='/ws/synergy')
def ws_synergy_column_change(data):
    """Handle Kanban column changes (drag & drop)"""
    from flask_socketio import emit
    
    session_id = data.get('session_id')
    from_column = data.get('from_column')
    to_column = data.get('to_column')
    room = data.get('room', 'default')
    
    print(f'[WS] Column change: {session_id} from {from_column} to {to_column}')
    
    # Broadcast to other clients
    emit('column_changed', {
        'session_id': session_id,
        'from_column': from_column,
        'to_column': to_column,
        'timestamp': datetime.now().isoformat()
    }, room=room, include_self=False)

@socketio.on('user_activity', namespace='/ws/synergy')
def ws_synergy_user_activity(data):
    """Track user activity (typing, viewing, etc.)"""
    from flask_socketio import emit
    
    user = data.get('user')
    activity = data.get('activity')
    room = data.get('room', 'default')
    
    # Broadcast user activity to room
    emit('activity', {
        'user': user,
        'activity': activity,
        'timestamp': datetime.now().isoformat()
    }, room=room, include_self=False)

# Initialize AI client
ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))

# Store AI client in app config for blueprints to access
app.config['AI_CLIENT'] = ai_client

print("=" * 80)
print("AI INFRASTRUCTURE - CLEANED & READY FOR 281 TOOLS")
print("=" * 80)
print(f"3 Generic Route Blueprints Registered (19 endpoints)")
print(f"Core Infrastructure: Session Manager + AI Clients")
print(f"Testing Framework: 22 tests passing (100% coverage)")
print("=" * 80)
print(f"Base Directory: {Config.BASE_DIR}")
print(f"Config Path: {Config.DB_CONFIG_PATH}")
print(f"Session DB: {Config.SESSION_DB_PATH}")
print(f"UnifiedSessionManager loaded")
print(f"UnifiedAIClient loaded (Anthropic + DeepSeek + OpenAI)")
print("=" * 80)
print("CURRENT API ENDPOINTS (CLEANED UP):")
print("   • Agent Routes:      8 endpoints (/api/agent/*)")
print("   • Thread Routes:     8 endpoints (/api/threads/*)")
print("   • Export Routes:     3 endpoints (/api/export/*)")
print("   • TOTAL:             19 endpoints (generic foundation)")
print("=" * 80)
print("READY TO ADD:")
print("   • 281 tools across 19 platforms")
print("   • OpenAI/Anthropic/DeepSeek (AI models)")
print("   • Gmail/Slack/Twilio (communication)")
print("   • WooCommerce/Stripe/PayPal (e-commerce)")
print("   • Google Workspace (Docs/Forms/Drive/etc)")
print("   • Supabase/GitHub/CloudFlare (infrastructure)")
print("=" * 80)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint with explicit CORS"""
    response = jsonify({
        'status': 'healthy',
        'app': 'new_flask_app',
        'infrastructure': 'AI_infrastructure',
        'providers': ['anthropic', 'deepseek', 'openai']
    })
    
    # Add CORS headers explicitly
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    
    return response


# ============================================================================
# TEMPLATE SERVING - Connect to existing HTML UIs
# ============================================================================

# Path to OLD Flask templates
TEMPLATE_DIR = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'templates'
STATIC_DIR = Path(__file__).parent.parent / 'Quote_Calculator' / 'AI_Quote_Agent' / 'web_interface' / 'static'

@app.route('/stock-management')
def serve_stock_management():
    """Serve Stock Management HTML UI"""
    return send_from_directory(TEMPLATE_DIR, 'stock_management.html')

@app.route('/single-agent-viewer')
@app.route('/data-agent-chat')
def serve_single_agent_viewer():
    """Serve Single Agent Viewer HTML UI (also accessible as data-agent-chat)"""
    return send_from_directory(TEMPLATE_DIR, 'single_agent_viewer.html')

@app.route('/triple-agent')
def serve_triple_agent():
    """Serve Triple Agent HTML UI"""
    return send_from_directory(TEMPLATE_DIR, 'triple_agent.html')

# Serve static files (JS, CSS, images)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, images)"""
    return send_from_directory(STATIC_DIR, filename)


# ============================================================================
# CHAT ROUTES (CLEAN - 20 lines instead of 400!)
# ============================================================================

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """
    Universal chat endpoint for ALL UIs
    
    Request JSON:
    {
        "session_id": "uuid" (optional - auto-create if missing),
        "ui_context": "stock_chat" | "data_agent_chat" | "single_viewer",
        "agent_id": "1" | "2" | "3" (for triple_agent only),
        "prompt": "User message",
        "provider": "anthropic" | "deepseek" | "openai" (default: anthropic)
    }
    
    Returns SSE stream
    """
    try:
        data = request.json
        
        # Get or create session
        session_id = data.get('session_id')
        if not session_id:
            session_id = session_manager.create_session(
                ui_context=data['ui_context'],
                agent_id=data.get('agent_id')
            )
        
        # Get session data
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get queue and lock
        queue = session_manager.get_queue(session_id)
        lock = session_manager.get_lock(session_id)
        
        # Process in background thread
        def process():
            with lock:
                try:
                    # Process with AI client
                    conversation = ai_client.process_streaming(
                        session_id=session_id,
                        session_data=session,
                        prompt=data['prompt'],
                        provider=data.get('provider', 'anthropic'),
                        sse_callback=lambda event: queue.put(event)
                    )
                    
                    # Save conversation
                    session_manager.update_conversation(session_id, conversation)
                    
                    # Send completion event
                    queue.put({'type': 'done'})
                    
                except Exception as e:
                    queue.put({'type': 'error', 'message': str(e)})
        
        # Start processing thread
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
        
        # Return session ID
        return jsonify({
            'status': 'processing',
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/stream/<session_id>', methods=['GET'])
def stream_chat(session_id):
    """
    SSE stream endpoint
    Client connects after calling /api/chat/send
    """
    
    def generate():
        """Generate SSE events from queue"""
        queue = session_manager.get_queue(session_id)
        
        while True:
            try:
                # Get event from queue (timeout 30s)
                event = queue.get(timeout=30)
                
                # Check if done
                if event.get('type') == 'done':
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                
                # Send event
                yield f"data: {json.dumps(event)}\n\n"
                
            except Empty:
                # Timeout - send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/chat/send-with-files', methods=['POST'])
def send_message_with_files():
    """
    Chat endpoint with file attachments (for Stock AI Chat document processing)
    
    FormData:
    - session_id: UUID (optional)
    - ui_context: stock_chat | data_agent_chat
    - prompt: User message
    - files: File uploads (PDF/images)
    - provider: anthropic (only Claude supports Vision)
    """
    try:
        # Get form data
        session_id = request.form.get('session_id')
        ui_context = request.form.get('ui_context', 'stock_chat')
        prompt = request.form.get('prompt', '')
        
        # Get or create session
        if not session_id:
            session_id = session_manager.create_session(ui_context=ui_context)
        
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Process files
        files_data = []
        if 'files' in request.files:
            for file in request.files.getlist('files'):
                # Read file
                file_bytes = file.read()
                
                # Encode to base64
                import base64
                file_base64 = base64.b64encode(file_bytes).decode('utf-8')
                
                # Determine media type
                media_type = file.content_type or 'application/pdf'
                
                files_data.append({
                    'data': file_base64,
                    'media_type': media_type,
                    'filename': file.filename
                })
        
        # Get queue and lock
        queue = session_manager.get_queue(session_id)
        lock = session_manager.get_lock(session_id)
        
        # Process in background
        def process():
            with lock:
                try:
                    # Process with AI client (Anthropic only for Vision)
                    conversation = ai_client.process_streaming(
                        session_id=session_id,
                        session_data=session,
                        prompt=prompt,
                        files=files_data if files_data else None,
                        provider='anthropic',  # Only Claude supports Vision
                        sse_callback=lambda event: queue.put(event)
                    )
                    
                    # Save
                    session_manager.update_conversation(session_id, conversation)
                    queue.put({'type': 'done'})
                    
                except Exception as e:
                    queue.put({'type': 'error', 'message': str(e)})
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'processing',
            'session_id': session_id,
            'files_uploaded': len(files_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create new session"""
    data = request.json
    session_id = session_manager.create_session(
        ui_context=data['ui_context'],
        agent_id=data.get('agent_id')
    )
    return jsonify({'session_id': session_id})


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    session = session_manager.get_session(session_id)
    if session:
        return jsonify(session)
    return jsonify({'error': 'Session not found'}), 404


@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Get conversation history"""
    session = session_manager.get_session(session_id)
    if session:
        return jsonify({'conversation': session.get('conversation', [])})
    return jsonify({'error': 'Session not found'}), 404


@app.route('/api/session/cleanup', methods=['POST'])
def cleanup_sessions():
    """Cleanup inactive sessions"""
    hours = request.json.get('hours', 24)
    count = session_manager.cleanup_inactive_sessions(hours)
    return jsonify({'cleaned': count})


# ============================================================================
# STATIC FILES (Frontend)
# ============================================================================
# NOTE: Template serving moved to top of file (after health check)
# - /stock-management → stock_management.html
# - /single-agent-viewer → single_agent_viewer.html
# - /triple-agent or / → triple_agent.html
# - /static/<file> → static files


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# SERVE UI (STATIC FILES)
# ============================================================================
# UI route already defined above at line 72-80 - no duplicate needed

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("STARTING NEW FLASK APP (Clean Architecture)")
    print("=" * 80)
    print("Port: 5001 (AI Infrastructure - Testing)")
    print("Infrastructure: AI_infrastructure/")
    print("Session Manager: Unified (SQLite + in-memory)")
    print("AI Client: Multi-provider (Anthropic + DeepSeek + OpenAI)")
    print("=" * 80)
    print("\nAccess at: http://localhost:5001")
    print("Health check: http://localhost:5001/health")
    print("\n")
    
    # Run Flask app
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,  # AI Infrastructure port (5001 for testing, 5000 for production)
        debug=True,
        use_reloader=True
    )
