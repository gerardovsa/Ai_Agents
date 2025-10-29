"""
Flask Integration Module
Clean Flask routes using unified session manager and Anthropic client

Usage:
    from AI_infrastructure.flask_integration import create_unified_routes
    
    app = Flask(__name__)
    create_unified_routes(app, config_path='config/database-config.json')
"""

from flask import request, jsonify, Response
from queue import Queue, Empty
import threading
import json
from typing import Callable

from .core.unified_session_manager import session_manager
from .core.unified_anthropic_client import init_anthropic_client


def create_unified_routes(app, config_path: str):
    """
    Create unified Flask routes
    
    Args:
        app: Flask app instance
        config_path: Path to database-config.json
    """
    # Initialize Anthropic client
    anthropic_client = init_anthropic_client(config_path)
    
    print("[FlaskIntegration] Unified routes initialized")
    
    # ============================================
    # UNIVERSAL SSE STREAM ENDPOINT
    # ============================================
    
    @app.route('/api/stream/<session_id>')
    def stream(session_id):
        """
        Universal SSE endpoint for all UIs
        
        Replaces:
        - /stream/<agent_id> (old Triple Agent)
        - /stock/stream (old Stock Chat)
        - /data-agent/stream (old Data Agent)
        """
        # Get queue for session
        queue = session_manager.get_queue(session_id)
        
        def generate():
            try:
                while True:
                    try:
                        event = queue.get(timeout=30)
                        
                        # Check for completion
                        if event.get('type') in ['done', 'complete']:
                            yield f"data: {json.dumps(event)}\n\n"
                            break
                        
                        # Stream event
                        yield f"data: {json.dumps(event)}\n\n"
                    
                    except Empty:
                        # Keepalive ping (prevents timeout)
                        yield f"data: {json.dumps({'type': 'ping'})}\n\n"
            
            except GeneratorExit:
                print(f"[Stream] Client disconnected: {session_id}")
        
        return Response(generate(), mimetype='text/event-stream')
    
    
    # ============================================
    # SESSION MANAGEMENT
    # ============================================
    
    @app.route('/api/session/create', methods=['POST'])
    def create_session():
        """
        Create new session
        
        Request JSON:
            {
                "ui_context": "stock_chat" | "data_agent_chat" | "single_viewer" | "triple_agent",
                "agent_id": "1" | "2" | "3" (optional, for triple_agent)
            }
        
        Response JSON:
            {
                "session_id": "uuid-string"
            }
        """
        ui_context = request.json.get('ui_context')
        agent_id = request.json.get('agent_id')
        
        if not ui_context:
            return jsonify({'error': 'ui_context required'}), 400
        
        session_id = session_manager.create_session(ui_context, agent_id)
        
        return jsonify({'session_id': session_id})
    
    
    # ============================================
    # UNIVERSAL CHAT ENDPOINT
    # ============================================
    
    @app.route('/api/chat/send', methods=['POST'])
    def send_message():
        """
        Universal chat endpoint for all UIs
        
        Replaces:
        - /agent/<agent_id>/start (old Triple Agent)
        - /stock/chat (old Stock Chat)
        - /data-agent/chat (old Data Agent)
        
        Request (JSON or FormData):
            {
                "session_id": "uuid-string",
                "prompt": "user message",
                "files": [file uploads] (optional)
            }
        
        Response JSON:
            {
                "status": "processing",
                "session_id": "uuid-string"
            }
        """
        # Parse request (supports JSON and FormData)
        if request.is_json:
            session_id = request.json.get('session_id')
            prompt = request.json.get('prompt')
            files = None
        else:
            session_id = request.form.get('session_id')
            prompt = request.form.get('prompt')
            files = request.files.getlist('files') if request.files else None
        
        # Validate
        if not session_id:
            return jsonify({'error': 'session_id required'}), 400
        
        if not prompt and not files:
            return jsonify({'error': 'prompt or files required'}), 400
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Invalid session'}), 404
        
        # Get execution lock (prevent concurrent requests)
        lock = session_manager.get_lock(session_id)
        if lock.locked():
            return jsonify({'error': 'Already processing a request'}), 409
        
        # Get queue
        queue = session_manager.get_queue(session_id)
        
        # Start background processing
        def process():
            with lock:
                try:
                    # Process with Anthropic client
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    updated_conversation = loop.run_until_complete(
                        anthropic_client.process_streaming(
                            session_id=session_id,
                            session_data=session,
                            prompt=prompt or "",
                            files=files,
                            sse_callback=lambda event: queue.put(event)
                        )
                    )
                    
                    # Update conversation in session manager
                    session_manager.update_conversation(session_id, updated_conversation)
                    
                except Exception as e:
                    print(f"[Chat] Error processing request: {e}")
                    queue.put({
                        'type': 'error',
                        'message': str(e)
                    })
        
        threading.Thread(target=process, daemon=True).start()
        
        return jsonify({'status': 'processing', 'session_id': session_id})
    
    
    # ============================================
    # LEGACY ENDPOINT REDIRECTS (for compatibility)
    # ============================================
    
    @app.route('/stock/chat', methods=['POST'])
    def legacy_stock_chat():
        """Legacy Stock Chat endpoint - redirects to new API"""
        
        # Create session if not exists
        session_id = request.form.get('session_id')
        if not session_id:
            session_id = session_manager.create_session('stock_chat')
        
        # Forward to new endpoint
        from flask import request as req
        req.form = req.form.copy()
        req.form['session_id'] = session_id
        
        return send_message()
    
    
    @app.route('/data-agent/chat', methods=['POST'])
    def legacy_data_agent_chat():
        """Legacy Data Agent endpoint - redirects to new API"""
        
        # Create session if not exists
        session_id = request.json.get('session_id')
        if not session_id:
            session_id = session_manager.create_session('data_agent_chat')
        
        # Forward to new endpoint
        request.json['session_id'] = session_id
        
        return send_message()
    
    
    @app.route('/agent/<agent_id>/start', methods=['POST'])
    def legacy_triple_agent_start(agent_id):
        """Legacy Triple Agent endpoint - redirects to new API"""
        
        # Create session
        session_id = session_manager.create_session('triple_agent', agent_id=agent_id)
        
        # Forward to new endpoint
        request.json['session_id'] = session_id
        
        return send_message()
    
    
    print("[FlaskIntegration] Routes created successfully")
    print("  - Universal: /api/stream/<session_id>")
    print("  - Universal: /api/session/create")
    print("  - Universal: /api/chat/send")
    print("  - Legacy: /stock/chat (redirects)")
    print("  - Legacy: /data-agent/chat (redirects)")
    print("  - Legacy: /agent/<agent_id>/start (redirects)")
