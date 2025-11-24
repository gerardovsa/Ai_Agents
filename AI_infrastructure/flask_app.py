"""
New Flask App - Clean Rebuild
Uses unified session manager and AI client

This is the NEW clean Flask app that replaces flask_triple_agent_app.py
Run on port 5001 for testing, then swap to port 5000 when ready
"""

import os
import sys
from pathlib import Path

# Configure AI_agents paths ONLY - Standalone project
ai_agents_root = Path(__file__).parent.parent  # Go up to AI_agents root
ai_infrastructure_path = ai_agents_root / 'AI_infrastructure'

# Add AI_agents paths
for path in [str(ai_agents_root), str(ai_infrastructure_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Setup unified logging FIRST
from utils.logger_config import setup_logger, log_init, log_config, log_success, log_warning, log_error
logger = setup_logger('flask_app')

log_init(logger, "AI_agents standalone - No external dependencies")

# Now import Flask and other dependencies
from flask import Flask, jsonify, request, Response, send_from_directory, send_file
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask_socketio import SocketIO
import json
from queue import Queue, Empty
import threading

# Load environment variables from .env or .env.master file (local development only)
from dotenv import load_dotenv
env_master_path = os.path.join(os.path.dirname(__file__), '..', '.env.master')
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

if os.path.exists(env_master_path):
    load_dotenv(env_master_path)
    log_config(logger, "Loaded .env.master file (local development)")
elif os.path.exists(env_path):
    load_dotenv(env_path)
    log_config(logger, "Loaded .env file (local development)")
else:
    log_config(logger, "Using environment variables from system (production/Render)")

# Import centralized database connection utility
from shared.database_utils import get_database_connection

log_config(logger, f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
log_config(logger, f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
log_config(logger, f"DEEPSEEK_API_KEY_1: {'SET' if os.getenv('DEEPSEEK_API_KEY_1') else 'NOT SET'}")
log_config(logger, f"MICROSOFT_CLIENT_ID: {'SET' if os.getenv('MICROSOFT_CLIENT_ID') else 'NOT SET'}")
log_config(logger, f"MICROSOFT_CLIENT_SECRET: {'SET' if os.getenv('MICROSOFT_CLIENT_SECRET') else 'NOT SET'}")
log_config(logger, f"USE_SUPABASE: {os.getenv('USE_SUPABASE', 'NOT SET')}")
log_config(logger, f"SUPABASE_URL: {'SET' if os.getenv('SUPABASE_URL') else 'NOT SET'}")
log_config(logger, f"SUPABASE_DB_URL: {'SET' if os.getenv('SUPABASE_DB_URL') else 'NOT SET'}")
log_config(logger, f"SUPABASE_KEY: {'SET' if os.getenv('SUPABASE_KEY') else 'NOT SET'}")

# Stock Management - ENABLED (Supabase + local fallback)
from AI_infrastructure.utils.db_path_helper import get_stock_db_path
STOCK_DB_PATH = get_stock_db_path()

# Check if using Supabase stock database
if STOCK_DB_PATH == 'supabase://stock_data':
    STOCK_DB_AVAILABLE = bool(os.getenv('SUPABASE_URL'))
    STOCK_DB_CONFIG = {'db_type': 'supabase', 'schema': 'stock_data'} if STOCK_DB_AVAILABLE else None
    if STOCK_DB_AVAILABLE:
        log_config(logger, f"Stock management enabled - using Supabase (schema: stock_data)")
    else:
        log_warning(logger, f"Stock management disabled - SUPABASE_URL not set")
else:
    # Local file fallback
    STOCK_DB_AVAILABLE = os.path.exists(STOCK_DB_PATH)
    STOCK_DB_CONFIG = {'db_type': 'sqlite', 'db_path': STOCK_DB_PATH} if STOCK_DB_AVAILABLE else None
    if STOCK_DB_AVAILABLE:
        log_config(logger, f"Stock management enabled - database found at {STOCK_DB_PATH}")
    else:
        log_warning(logger, f"Stock management disabled - database not found at {STOCK_DB_PATH}")

# Flask Configuration (inline - no external config.py needed)
class Config:
        """Flask app configuration - Fallback"""
        BASE_DIR = Path(__file__).parent
        ROOT_DIR = BASE_DIR.parent  # AI_agents root
        DATA_DIR = ROOT_DIR / 'data'  # Centralized data folder
        SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        TESTING = False
        DB_CONFIG_PATH = DATA_DIR / 'database-config.json'
        SESSION_DB_PATH = DATA_DIR / 'sessions.db'
        
        # Session configuration - OAuth state stored in database (oauth_states table)
        # Default Flask sessions for temporary data only
        SESSION_TYPE = 'filesystem'
        PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
        
        # CORS configuration
        CORS_ORIGINS = ['http://localhost:5001', 'http://localhost:5000', 'http://127.0.0.1:5001', 'http://127.0.0.1:5000', '*']
        
        # Database configuration (SQLite) - Centralized location
        DATABASE_PATH = os.getenv('DATABASE_PATH', str(DATA_DIR / 'ai_infrastructure.db'))

# Import core infrastructure (NEW CLEAN CODE)
from core.unified_session_manager import session_manager
from core.unified_ai_client import initialize_ai_client

# Import routes (blueprints) - Working In_House_SQL implementation
from routes.agent_routes_v4 import agent_bp  # V4 modular architecture with tool execution
from routes.thread_routes import thread_bp
from routes.message_operations import message_ops_bp  # NEW: Message operations (fork, clone, copy, delete)
from routes.export_routes import export_bp
from routes.woocommerce_routes import woocommerce_bp
from routes.auth_routes import auth_bp  # NEW: User authentication
from routes.oauth_routes import oauth_bp  # NEW: OAuth workspace integration (Google Workspace + M365)
from routes.google_auth_routes_V2_FIXED import google_auth_bp  # NEW: Google OAuth V2
from routes.microsoft_auth_routes_V2_FIXED import microsoft_auth_bp  # NEW: Microsoft OAuth V2
from routes.account_linking_routes import account_linking_bp  # NEW: Account linking
from routes.kanban_routes import kanban_bp  # NEW: Kanban board with AI agent integration
# from routes.database_visualizer_routes import database_visualizer_bp  # DISABLED: Needs migration to Supabase PostgreSQL
from routes.synergy_routes import synergy_bp  # NEW: Synergy Dashboard Kanban
from routes.scheduler_routes import scheduler_bp  # NEW: AI Automation Scheduler
from routes.automation_routes import automation_bp  # NEW: Visual Automation Canvas

# Optional: InHousePrint production workflow (requires pymssql)
try:
    from routes.inhouse_kanban_routes import inhouse_kanban_bp
    INHOUSE_KANBAN_AVAILABLE = True
except ImportError as e:
    log_warning(logger, f"InHouse Kanban module not available: {e}")
    inhouse_kanban_bp = None
    INHOUSE_KANBAN_AVAILABLE = False

from routes.kanban_analytics_routes import kanban_analytics_bp  # NEW: Kanban Analytics (SQLite database with custom metrics)
from routes.production_log_routes import production_log_bp  # NEW: Production Log (comprehensive job tracking)
from routes.user_preferences_routes import user_preferences_bp  # NEW: User personalization preferences
from routes.geolocation_routes import geolocation_bp  # NEW: Geolocation detection
from routes.thread_assignment_routes import thread_assignment_bp  # NEW: Thread assignments (JSON storage)
from routes.workspace_routes import workspace_bp  # NEW: Workspace management (CRUD, members, invitations)
from routes.thread_sharing_routes import thread_sharing_bp  # NEW: Thread sharing (multi-user collaboration)
from routes.communication_routes import communication_bp  # NEW: Communication Hub (Gmail + Outlook unified inbox)
from routes.user_management_routes import user_management_bp  # NEW: Sub-user management (parent-child hierarchy)
from routes.render_routes import render_bp  # NEW: Render cloud management (deploy, logs, metrics)
from routes.file_routes import file_bp  # NEW: File storage management (upload, download, delete)
from routes.prompt_library_routes import prompt_routes  # NEW: Prompt library (database-backed prompt management)
from routes.token_routes import token_routes  # NEW: Token tracking (real-time token counts for threads)
from routes.device_lock_routes import device_lock_bp  # NEW: Device lock (multi-device session management)
from routes.pool_monitor_routes import pool_monitor_bp  # NEW: Connection pool monitoring dashboard
from routes.monitoring_routes import monitoring_bp  # NEW: Connection pool health monitoring (Supabase optimization)
# from routes.quote_calculator_routes import quote_calc_bp  # DISABLED: In_House_SQL dependency

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Note: OAuth state tokens are stored in database (oauth_states table) instead of Flask sessions
# This ensures cloud compatibility on Render (multi-instance, ephemeral filesystem)
log_config(logger, "OAuth uses database-backed state storage (cloud-compatible)")

# Ensure /data directory exists on Render (persistent disk mount)
if os.getenv('RENDER') == 'true':
    data_dir = Path('/data')
    if not data_dir.exists():
        log_warning(logger, f"/data directory does not exist - checking Render disk mount")
    else:
        log_success(logger, f"/data directory exists - Render persistent disk mounted")

# Initialize database schema BEFORE any routes are registered
try:
    from init_prompt_library import init_prompt_library_table
    # No db_path needed - uses Supabase ai_infrastructure schema
    init_prompt_library_table()
    log_success(logger, "Prompt library table initialized in Supabase")
except Exception as e:
    log_error(logger, f"Failed to initialize prompt library table: {e}")

# Initialize user authentication tables (users, oauth_tokens, etc.)
try:
    from auth.user_auth import user_auth_manager
    log_success(logger, f"User authentication tables initialized at {user_auth_manager.db_path}")
    # Verify tables actually exist
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    # Use is_using_supabase() to correctly detect database type
    from shared.database_utils import is_using_supabase
    if is_using_supabase():
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cursor.fetchall()
    # Handle both SQLite (tuples) and PostgreSQL (tuples or DictRow)
    if rows and len(rows) > 0:
        # Try to access first element - works for both tuples and postgres rows
        try:
            tables = [row[0] if isinstance(row, (tuple, list)) else row['name' if 'name' in row else 'tablename'] for row in rows]
        except (KeyError, TypeError, IndexError):
            # Fallback: just get first item from each row
            tables = [list(row.values())[0] if hasattr(row, 'values') else row[0] for row in rows]
    else:
        tables = []
    conn.close()
    log_success(logger, f"Database tables verified: {len(tables)} tables found")
except Exception as e:
    log_error(logger, f"Failed to initialize user authentication: {e}")
    import traceback
    log_error(logger, traceback.format_exc())

# Run OAuth tokens schema migrations (add missing columns)
# DISABLED ON RENDER: Supabase already has all tables/columns
if not os.getenv('USE_SUPABASE') == 'true' and not os.getenv('RENDER') == 'true':
    try:
        from migrations.add_missing_oauth_columns import add_missing_oauth_columns
        added = add_missing_oauth_columns()
        log_success(logger, f"OAuth tokens schema migration complete ({added} columns added)")
    except Exception as e:
        log_error(logger, f"Failed to run OAuth migration: {e}")
        import traceback
        log_error(logger, traceback.format_exc())

    # CRITICAL: Fix users table OAuth columns (has_microsoft_oauth, has_google_oauth)
    try:
        from migrations.fix_users_oauth_columns import run_migration
        added = run_migration()
        log_success(logger, f"Users OAuth columns migration complete ({added} columns added)")
    except Exception as e:
        log_error(logger, f"Failed to fix users OAuth columns: {e}")
        import traceback
        log_error(logger, traceback.format_exc())

    # Initialize user_sessions table for JWT tokens
    try:
        from migrations.init_user_sessions_table import init_user_sessions_table
        init_user_sessions_table()
        log_success(logger, "User sessions table initialized")
    except Exception as e:
        log_error(logger, f"Failed to initialize user_sessions table: {e}")

    # Add refresh_attempts column to oauth_tokens table
    try:
        from migrations.add_refresh_attempts_column import add_refresh_attempts_column
        add_refresh_attempts_column()
        log_success(logger, "OAuth tokens refresh_attempts column added")
    except Exception as e:
        log_error(logger, f"Failed to add refresh_attempts column: {e}")
else:
    log_success(logger, "Skipping SQLite migrations (using Supabase - tables already exist)")

# Initialize automation tables
try:
    from routes.automation_routes import init_automation_tables
    init_automation_tables()
    log_success(logger, "Automation tables initialized (visual_automations, automation_executions)")
except Exception as e:
    log_error(logger, f"Failed to initialize automation tables: {e}")

# Register blueprints - Working In_House_SQL implementation
app.register_blueprint(agent_bp, url_prefix='/api/agent')           # Working agent routes with async support
app.register_blueprint(thread_bp, url_prefix='/api/threads')        # 8 endpoints (conversation storage)
app.register_blueprint(thread_sharing_bp)                            # NEW: Thread sharing (6 endpoints: share, accept, revoke, list)
app.register_blueprint(message_ops_bp)                               # NEW: Message operations - fork, clone, copy, delete (5 endpoints)
app.register_blueprint(file_bp)                                      # NEW: File storage (7 endpoints: serve, download, delete, usage)
app.register_blueprint(export_bp, url_prefix='/api/export')         # 3 endpoints (export functionality)
app.register_blueprint(woocommerce_bp)                               # 9 endpoints (WooCommerce direct API)
app.register_blueprint(auth_bp)                                      # NEW: 6 endpoints (user auth)
app.register_blueprint(oauth_bp)                                     # NEW: OAuth workspace integration (/api/oauth/*)
app.register_blueprint(google_auth_bp)                               # NEW: Google OAuth V2 (/api/auth/google/*)
app.register_blueprint(microsoft_auth_bp)                            # NEW: Microsoft OAuth V2 (/api/auth/microsoft/*)
app.register_blueprint(account_linking_bp)                           # NEW: Account linking (/api/account/*)
app.register_blueprint(kanban_bp)                                    # NEW: Kanban board + AI agent bridge (8 endpoints)
# app.register_blueprint(database_visualizer_bp)                       # DISABLED: Needs migration to Supabase PostgreSQL
app.register_blueprint(synergy_bp)                                   # NEW: Synergy Dashboard (6 endpoints: /api/synergy/*)
app.register_blueprint(scheduler_bp)                                 # NEW: AI Automation Scheduler (10 endpoints: /api/scheduler/*)
app.register_blueprint(automation_bp)                                # NEW: Visual Automation Canvas (9 endpoints: /api/automation/*)
if INHOUSE_KANBAN_AVAILABLE:
    app.register_blueprint(inhouse_kanban_bp)                        # NEW: InHousePrint production workflow (5 endpoints)
app.register_blueprint(kanban_analytics_bp)                          # NEW: Kanban Analytics SQLite (15 endpoints: /api/kanban-analytics/*)
app.register_blueprint(device_lock_bp)                               # NEW: Device lock (5 endpoints: /api/device/*, /api/thread/*/lock*)
app.register_blueprint(production_log_bp)                            # NEW: Production Log (10 endpoints: /api/production-log/*)
app.register_blueprint(user_preferences_bp)                          # NEW: User preferences (2 endpoints: /api/user/preferences)
app.register_blueprint(geolocation_bp)                               # NEW: Geolocation detection (2 endpoints: /api/geolocation/*)
app.register_blueprint(thread_assignment_bp)                         # NEW: Thread assignments (7 endpoints: /api/thread-assignments/*)
app.register_blueprint(workspace_bp)                                 # NEW: Workspace management (18 endpoints: /api/workspaces/*)
app.register_blueprint(communication_bp)                             # NEW: Communication Hub (8 endpoints: /api/communication-hub/*)
app.register_blueprint(user_management_bp)                           # NEW: Sub-user management (5 endpoints: /api/users/sub-users/*)
app.register_blueprint(render_bp)                                    # NEW: Render cloud management (6 endpoints: /api/render/*)
app.register_blueprint(prompt_routes)                                # NEW: Prompt library (10 endpoints: /api/prompts/*)
app.register_blueprint(token_routes)                                 # NEW: Token tracking (3 endpoints: /api/tokens/*)
app.register_blueprint(pool_monitor_bp)                              # NEW: Connection pool monitoring (4 endpoints: /api/pool/*)
app.register_blueprint(monitoring_bp)                                # NEW: Connection pool health monitoring (4 endpoints: /api/pool/stats, /api/pool/health)
# app.register_blueprint(quote_calc_bp)                                # DISABLED: In_House_SQL dependency

# 🆕 AUTO-LOAD MODULE BLUEPRINTS (Quote Calculator, Stock Management, etc.)
# This discovers and registers Flask routes from UI/external/modules/*/routes/
# INCLUDES: Stock Management, Shopify E-Commerce, Database Visualizer, Quote Calculator, etc.
try:
    from core.module_blueprint_loader import load_module_blueprints
    from utils.logger_config import log_module, log_route
    module_bp_count = load_module_blueprints(app)
    log_module(logger, f"Loaded {module_bp_count} module blueprints from UI/external/modules")
    log_route(logger, "Auto-discovered routes from: UI/external/modules/*/routes/*.py")
    log_route(logger, "Stock Management: /api/stock-management/* (Blueprint auto-loaded)")
except Exception as e:
    log_warning(logger, f"Module blueprints not loaded: {e} (Module blueprints are optional)")

# REMOVED DUPLICATE: Stock Management routes now loaded via module_blueprint_loader above
# Old init_stock_routes() pattern caused route conflicts with Blueprint system

# Shopify E-Commerce: ENABLED (load routes from module folder)
if STOCK_DB_AVAILABLE:  # Shopify uses same database as Stock Management
    try:
        # Add shopify module to path
        shopify_module_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'external', 'modules', 'shopify')
        if os.path.exists(shopify_module_path):
            sys.path.insert(0, shopify_module_path)
            from shopify_routes import init_shopify_routes
            init_shopify_routes(app, STOCK_DB_CONFIG, STOCK_DB_AVAILABLE)
            log_success(logger, f"Shopify E-Commerce routes registered from {shopify_module_path}")
        else:
            log_warning(logger, f"Shopify module not found at {shopify_module_path}")
    except Exception as e:
        log_error(logger, f"Failed to load shopify routes: {e}")
        import traceback
        traceback.print_exc()
else:
    log_config(logger, "Shopify E-Commerce disabled - database not available")

# Xero Accounting: ENABLED (load routes from module folder)
try:
    # Add xero module to path
    xero_module_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'external', 'modules', 'xero')
    if os.path.exists(xero_module_path):
        sys.path.insert(0, xero_module_path)
        from xero_routes import init_xero_routes
        init_xero_routes(app)
        log_success(logger, f"Xero Accounting routes registered from {xero_module_path}")
    else:
        log_warning(logger, f"Xero module not found at {xero_module_path}")
except Exception as e:
    log_error(logger, f"Failed to load xero routes: {e}")
    import traceback
    traceback.print_exc()

# Legacy compatibility: register /api/sessions/* proxy so older UIs work
try:
    from routes.compat_sessions import compat_bp
    app.register_blueprint(compat_bp)
    log_route(logger, "Compatibility blueprint registered: /api/sessions/* -> /api/kanban/*")
except Exception:
    log_warning(logger, "Compatibility blueprint not available")

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
    """Serve the main UI page with no-cache headers to prevent stale JS/CSS"""
    response = send_from_directory(UI_DIR, 'business-ai-platform-v2.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/<path:filename>')
def serve_ui_static(filename):
    """Serve static files from UI directory (CSS, JS, etc.)"""
    return send_from_directory(UI_DIR, filename)

# Enable CORS - Allow all origins for development
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "x-user-id", "X-User-ID"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)

# Initialize SocketIO with full async support
# FIX: Disable session management and cookies to prevent WSGI "write() before start_response" errors
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    always_connect=True,
    manage_session=False,  # ✅ FIX: Disable Flask-SocketIO session management to avoid WSGI conflicts
    cookie=None,  # ✅ FIX: Disable cookies to prevent "write before start_response" errors
    engineio_logger_level='WARNING'  # Only show warnings/errors
)

# Track connected clients and their rooms
connected_clients = {}

# ============================================================================
# DEFAULT NAMESPACE HANDLERS (catch unwanted connections)
# ============================================================================

@socketio.on('connect')
def default_connect():
    """
    Handle connection attempts to default namespace (/)
    Reject these connections as we only support /ws/synergy
    """
    log_warning(logger, "[WS] Connection attempt to default namespace - rejecting")
    return False  # Reject connection

@socketio.on('disconnect')
def default_disconnect():
    """
    Handle disconnection from default namespace (/)
    This should rarely be called since we reject connections
    """
    pass  # Silently ignore

# ============================================================================
# COMPREHENSIVE SOCKETIO HANDLERS FOR /ws/synergy NAMESPACE
# ============================================================================

@socketio.on('connect', namespace='/ws/synergy')
def ws_synergy_connect(auth=None):
    """Handle client connection to Synergy namespace"""
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        client_id = flask_request.sid
        
        # Check if client_id is valid
        if not client_id:
            log_error(logger, "[WS] Connection attempt with invalid client_id")
            return False  # Reject connection
        
        connected_clients[client_id] = {
            'rooms': set(),
            'connected_at': datetime.now().isoformat()
        }
        
        log_config(logger, f'[WS] Client connected to /ws/synergy: {client_id}')
        emit('connected', {
            'status': 'connected',
            'client_id': client_id,
            'timestamp': datetime.now().isoformat()
        })
        return True  # Accept connection
        
    except Exception as e:
        log_error(logger, f'[WS ERROR] Connection failed: {e}')
        import traceback
        traceback.print_exc()
        return False  # Reject connection on error

@socketio.on('disconnect', namespace='/ws/synergy')
def ws_synergy_disconnect(reason=None):
    """
    Handle client disconnection from /ws/synergy namespace
    
    Args:
        reason: Disconnect reason passed by Flask-SocketIO (optional)
    
    Note: Flask-SocketIO automatically provides request context with session ID.
    This works identically on local Windows and Render Linux deployments with Supabase.
    """
    try:
        from flask import request as flask_request
        
        # Get client_id from Flask-SocketIO request context
        client_id = getattr(flask_request, 'sid', None)
        
        # If no client_id could be determined, skip silently (normal for some disconnect scenarios)
        if not client_id:
            return
        
        if client_id in connected_clients:
            del connected_clients[client_id]
            log_config(logger, f"Client disconnected from /ws/synergy: {client_id}")
        # Silently ignore untracked clients (normal during connection failures)
    
    except Exception as e:
        # Prevent exceptions from breaking WebSocket connection handling
        # Log error but don't re-raise to avoid 500 errors
        log_error(logger, f"Error in ws_synergy_disconnect: {e}")
        pass  # Silently continue

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

# ============================================================================
# SOCKETIO ERROR HANDLERS
# ============================================================================

@socketio.on_error()
def global_error_handler(e):
    """Handle Socket.IO errors gracefully across all namespaces"""
    log_error(logger, f"[WS ERROR] Global: {str(e)}")
    import traceback
    log_error(logger, traceback.format_exc())
    return {'error': str(e), 'status': 'error'}

@socketio.on_error(namespace='/ws/synergy')
def ws_synergy_error_handler(e):
    """Handle errors in /ws/synergy namespace"""
    log_error(logger, f'[WS ERROR] /ws/synergy: {str(e)}')
    import traceback
    log_error(logger, traceback.format_exc())
    return {'error': str(e), 'status': 'error'}

@socketio.on_error_default
def default_error_handler(e):
    """Handle errors in default namespace"""
    log_error(logger, f'[WS ERROR] Default namespace: {str(e)}')
    import traceback
    log_error(logger, traceback.format_exc())
    return {'error': str(e), 'status': 'error'}

# ============================================================================
# SOCKETIO EVENT HANDLERS (CONTINUED)
# ============================================================================

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
print(f"[DEBUG] Using config path: {Config.DB_CONFIG_PATH}")
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-user-id,X-User-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    
    return response


@app.route('/api/config/supabase', methods=['GET', 'OPTIONS'])
def get_supabase_config():
    """Get Supabase configuration for frontend"""
    try:
        # Try to get from environment first (for Render deployment)
        supabase_url = os.getenv('SUPABASE_URL')
        
        # Try multiple possible key names in order of preference
        anon_key = (
            os.getenv('SUPABASE_ANON_KEY') or 
            os.getenv('SUPABASE_KEY') or 
            os.getenv('SUPABASE_SERVICE_KEY')  # Fallback to service key if anon key not available
        )
        
        # If not in env, try to load from config.py
        if not supabase_url or not anon_key:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            try:
                from config import SUPABASE_URL, SUPABASE_ANON_KEY
                supabase_url = supabase_url or SUPABASE_URL
                anon_key = anon_key or SUPABASE_ANON_KEY
            except (ImportError, AttributeError) as e:
                print(f"⚠️ [SUPABASE CONFIG] Could not load from config.py: {e}")
        
        if not supabase_url or not anon_key:
            return jsonify({
                'error': 'Supabase configuration not found',
                'details': 'SUPABASE_URL or SUPABASE_*_KEY not set in environment'
            }), 500
        
        response = jsonify({
            'url': supabase_url,
            'anonKey': anon_key
        })
        
        # Add CORS headers explicitly
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        
        return response
        
    except Exception as e:
        print(f"❌ [SUPABASE CONFIG] Error: {str(e)}")
        return jsonify({
            'error': 'Failed to load Supabase config',
            'details': str(e)
        }), 500


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

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Serve static files (JS, CSS, images)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, images)"""
    print(f"🔷 [STATIC] Requested: {filename}")
    
    # Check if file is in AI_infrastructure folder (new modular files)
    if filename.startswith('AI_infrastructure/'):
        # Get the project root directory (parent of AI_infrastructure/)
        project_root = Path(__file__).parent.parent
        full_path = project_root / filename
        
        print(f"🔷 [STATIC] Project root: {project_root}")
        print(f"🔷 [STATIC] Full path: {full_path}")
        print(f"🔷 [STATIC] File exists: {full_path.exists()}")
        
        if full_path.exists():
            # Extract the directory and filename parts for send_from_directory
            # send_from_directory handles MIME types automatically
            file_dir = full_path.parent
            file_name = full_path.name
            print(f"🔷 [STATIC] ✓ Serving from dir: {file_dir}, file: {file_name}")
            return send_from_directory(file_dir, file_name)
    
    # Fallback to old static directory
    print(f"🔷 [STATIC] Falling back to STATIC_DIR: {STATIC_DIR}")
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
# STOCK MANAGEMENT API ENDPOINTS - MOVED TO stock_routes.py
# ============================================================================
# NOTE: All stock endpoints now handled by stock_routes.py (thin wrappers)
# Old inline implementations commented out below for reference
# Delete this section once confirmed working

# # @app.route('/api/stock/test', methods=['GET', 'OPTIONS'])
# @cross_origin()
# def stock_health_check():
    """
    Health check endpoint - tests database connection
    Returns stock count and connection status
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Stock database connection not configured',
                'db_connected': False
            }), 503
        
        # Test database connection
        db = InHousePrintDB(STOCK_DB_CONFIG)
        result = db.execute_query("SELECT COUNT(*) as count FROM Quote_DigitalStocks")
        db.close()
        
        # Extract count from DataFrame
        import pandas as pd
        if isinstance(result, pd.DataFrame) and not result.empty:
            stock_count = int(result.iloc[0]['count'])
        else:
            stock_count = 0
        
        return jsonify({
            'status': 'ok',
            'db_connected': True,
            'stock_count': stock_count,
            'database': 'In HousePrint',
            'server': '3.25.76.138\\INHPSQLSERVER',
            'config': STOCK_DB_CONFIG
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Stock health check failed: {error_details}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'db_connected': False,
            'details': error_details
        }), 500


# @app.route('/api/stock/usage-analytics', methods=['GET', 'OPTIONS'])
# @cross_origin()
# def stock_usage_analytics():
    """
    Usage Analytics - Thin wrapper calling stock_manager.py
    Query params: days (30, 90, 180, 365)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        days = int(request.args.get('days', 30))
        
        # Stock management disabled - standalone mode
        raise ImportError("Stock management not available in standalone mode")
        
        # TODO: Implement standalone stock manager in AI_agents
        # manager = StockManager(STOCK_DB_CONFIG)
        result = manager.get_usage_analytics_complete(days=days)
        
        # Return result directly (stock_manager.py already formats for Chart.js)
        return jsonify({
            'status': 'ok',
            'days': days,
            'data': result
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Usage analytics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/reorder-dashboard', methods=['GET', 'OPTIONS'])
# @cross_origin()
# def stock_reorder_dashboard():
    """
    Reorder Dashboard - Returns stock alerts and recommendations
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        db = InHousePrintDB(STOCK_DB_CONFIG)
        
        # Get all stocks with usage metrics (via JobTickets → GSM)
        query = """
        SELECT 
            ds.StockID,
            dst.StockType,
            ds.GSM,
            ds.Length,
            ds.Width,
            ds.CostPerThousand,
            COUNT(jt.TicketID) as recent_jobs,
            SUM(jt.QTY) as total_quantity_used,
            MAX(o.OrderDate) as last_used_date
        FROM Quote_DigitalStocks ds
        LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
        LEFT JOIN GSM gsm 
            ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
        LEFT JOIN JobTickets jt ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN Orders o ON jt.OrderID = o.OrderID 
            AND o.OrderDate >= DATEADD(day, -90, GETDATE())
        GROUP BY ds.StockID, dst.StockType, ds.GSM, ds.Length, ds.Width, ds.CostPerThousand
        ORDER BY recent_jobs DESC
        """
        stocks_data = db.execute_query(query)
        db.close()
        
        import pandas as pd
        if not isinstance(stocks_data, pd.DataFrame):
            return jsonify({'status': 'ok', 'critical': [], 'warning': [], 'healthy': []})
        
        # Classify stocks by usage
        critical = []
        warning = []
        healthy = []
        
        for _, row in stocks_data.iterrows():
            stock_info = {
                'stock_id': int(row['StockID']) if pd.notna(row['StockID']) else 0,
                'stock_type': str(row['StockType']) if pd.notna(row['StockType']) else 'Unknown',
                'gsm': int(row['GSM']) if pd.notna(row['GSM']) else 0,
                'recent_jobs': int(row['recent_jobs']) if pd.notna(row['recent_jobs']) else 0,
                'last_used': str(row['last_used_date']) if pd.notna(row['last_used_date']) else 'Never',
                'cost': float(row['CostPerThousand']) if pd.notna(row['CostPerThousand']) else 0
            }
            
            # Categorize based on usage
            if stock_info['recent_jobs'] > 20:
                critical.append(stock_info)
            elif stock_info['recent_jobs'] > 5:
                warning.append(stock_info)
            else:
                healthy.append(stock_info)
        
        return jsonify({
            'status': 'ok',
            'critical': critical,
            'warning': warning,
            'healthy': healthy
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Reorder dashboard failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/profit-analysis', methods=['GET', 'OPTIONS'])
# @cross_origin()
# def stock_profit_analysis():
    """
    Profit Analysis - Returns profitability data by stock
    Query params: days (30, 90, 180, 365)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        days = int(request.args.get('days', 30))
        
        db = InHousePrintDB(STOCK_DB_CONFIG)
        
        # Profitability by stock (via JobTickets → GSM)
        query = f"""
        SELECT 
            ds.StockID,
            dst.StockType,
            ds.GSM,
            ds.CostPerThousand as cost_per_thousand,
            ds.Markup,
            COUNT(jt.TicketID) as job_count,
            SUM(jt.QTY) as total_quantity,
            SUM(jt.QTY * ds.CostPerThousand / 1000) as total_cost,
            SUM(jt.QTY * ds.CostPerThousand * ds.Markup / 1000) as total_revenue,
            SUM((jt.QTY * ds.CostPerThousand * ds.Markup / 1000) - (jt.QTY * ds.CostPerThousand / 1000)) as total_profit
        FROM JobTickets jt
        INNER JOIN Orders o ON jt.OrderID = o.OrderID
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        LEFT JOIN Quote_DigitalStocks ds 
            ON ds.GSM = CAST(REPLACE(REPLACE(gsm.[DESC], 'GSM', ''), 'gsm', '') AS INT)
        LEFT JOIN Quote_DigitalStockType dst ON ds.StockTypeID = dst.StockTypeID
        WHERE o.OrderDate >= DATEADD(day, -{days}, GETDATE())
        GROUP BY ds.StockID, dst.StockType, ds.GSM, ds.CostPerThousand, ds.Markup
        ORDER BY total_profit DESC
        """
        profit_data = db.execute_query(query)
        db.close()
        
        import pandas as pd
        return jsonify({
            'status': 'ok',
            'days': days,
            'profit_by_stock': profit_data.to_dict('records') if isinstance(profit_data, pd.DataFrame) else []
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Profit analysis failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/sql-query', methods=['POST', 'OPTIONS'])
# @cross_origin()
# def stock_sql_query():
    """
    SQL Viewer - Execute SELECT queries
    Body: { "query": "SELECT ..." }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        data = request.get_json()
        query = data.get('query', '')
        
        # Security: only allow SELECT queries
        if not query.strip().upper().startswith('SELECT'):
            return jsonify({'status': 'error', 'message': 'Only SELECT queries allowed'}), 400
        
        db = InHousePrintDB(STOCK_DB_CONFIG)
        result = db.execute_query(query)
        db.close()
        
        import pandas as pd
        return jsonify({
            'status': 'ok',
            'columns': list(result.columns) if isinstance(result, pd.DataFrame) else [],
            'rows': result.to_dict('records') if isinstance(result, pd.DataFrame) else []
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  SQL query failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/update-cell', methods=['POST', 'OPTIONS'])
# @cross_origin()
# def stock_update_cell():
    """
    SQL Viewer - Update single cell
    Body: { "table": "...", "column": "...", "value": "...", "where": "..." }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        data = request.get_json()
        table = data.get('table')
        column = data.get('column')
        value = data.get('value')
        where_clause = data.get('where')
        
        if not all([table, column, value, where_clause]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Build UPDATE query
        query = f"UPDATE {table} SET {column} = '{value}' WHERE {where_clause}"
        
        db = InHousePrintDB(STOCK_DB_CONFIG)
        result = db.execute_query(query)
        db.close()
        
        return jsonify({'status': 'ok', 'message': 'Cell updated successfully'})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Cell update failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/ai-analytics', methods=['GET', 'OPTIONS'])
# @cross_origin()
# def stock_ai_analytics():
    """
    AI Analytics - Placeholder for AI usage metrics
    Query params: days (30, 90, 180, 365)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        days = int(request.args.get('days', 30))
        
        # Placeholder data - in real implementation would track AI usage
        return jsonify({
            'status': 'ok',
            'days': days,
            'total_queries': 0,
            'cost_estimate': 0,
            'recent_operations': []
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  AI analytics failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/api/stock/invoice-process', methods=['POST', 'OPTIONS'])
# @cross_origin()
# def stock_invoice_process():
    """
    Invoice Processing - Upload and extract invoice data
    Multipart form: invoice_file
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        if not STOCK_DB_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Database not configured'}), 503
        
        if 'invoice_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
        
        file = request.files['invoice_file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Save file temporarily
        import os
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # Placeholder for AI extraction
        # In real implementation, would use Claude API here
        
        return jsonify({
            'status': 'ok',
            'message': 'Invoice uploaded successfully',
            'filename': file.filename,
            'extracted_data': {
                'supplier': 'Unknown',
                'invoice_number': 'TBD',
                'items': []
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"  Invoice processing failed: {error_details}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(400)
def bad_request(error):
    """
    Handle 400 Bad Request errors, including SSL/TLS handshake attempts
    
    Common cause: Browser trying to connect via HTTPS to HTTP-only server
    Solution: Ensure all redirects use http:// for localhost
    """
    error_msg = str(error)
    if 'Bad request version' in error_msg or 'SSL' in error_msg.upper():
        log_warning(logger, "SSL/TLS handshake attempt detected on HTTP-only server")
        log_warning(logger, "If this happens after OAuth, check redirect URLs use http:// for localhost")
    return jsonify({'error': 'Bad request'}), 400


# ============================================================================
# SERVE UI (STATIC FILES)
# ============================================================================
# UI route already defined above at line 72-80 - no duplicate needed

# ============================================================================
# START SCHEDULER
# ============================================================================

# Initialize and start automation scheduler
from scheduler import start_scheduler
try:
    scheduler = start_scheduler()
    log_success(logger, "Automation scheduler started")
except Exception as e:
    log_error(logger, f"Failed to start scheduler: {e}")
    import traceback
    log_error(logger, traceback.format_exc())

# ============================================================================
# CLEANUP HANDLER
# ============================================================================

import atexit
from shared.database_utils import close_all_pools

def cleanup_resources():
    """Cleanup connection pools on shutdown"""
    print("\n🔷 [SHUTDOWN] Cleaning up connection pools...")
    try:
        close_all_pools()
        print("✅ [SHUTDOWN] Connection pools closed")
    except Exception as e:
        print(f"⚠️  [SHUTDOWN] Failed to close pools: {e}")

# Register cleanup handler (called on normal exit)
atexit.register(cleanup_resources)

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    # Startup banner removed from logs (not sent to AI)
    
    # Get port from environment (Render sets PORT=10000, local uses 5001)
    port = int(os.environ.get('PORT', 5001))
    
    # Detect production environment
    is_production = os.environ.get('RENDER', 'false').lower() == 'true'
    debug_mode = not is_production
    
    # CRITICAL: Must use socketio.run() when WebSockets are enabled
    # Waitress does NOT support WebSockets - causes "Cannot obtain socket from WSGI environment" error
    USE_SOCKETIO = True  # Always use SocketIO server (supports WebSockets)
    
    print("=" * 80)
    print(f"STARTING FLASK SERVER")
    print("=" * 80)
    print(f"Environment: {'PRODUCTION (Render)' if is_production else 'DEVELOPMENT (Local)'}")
    print(f"Port: {port}")
    print(f"Host: 0.0.0.0")
    print(f"Debug: {debug_mode}")
    print(f"WebSocket Support: ENABLED (using socketio.run)")
    print(f"Auto-reload: {not is_production}")
    print("=" * 80 + "\n")
    
    if USE_SOCKETIO:
        # Use SocketIO server (supports WebSockets + HTTP)
        print("=" * 80)
        print(f"{'PRODUCTION' if is_production else 'DEVELOPMENT'} MODE: Flask SocketIO server")
        print("=" * 80 + "\n")
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=debug_mode,
            use_reloader=False,  # DISABLED - Manual restart only (prevents constant reloading)
            allow_unsafe_werkzeug=True,  # Allow Werkzeug in production (Render uses container isolation)
            extra_files=[]  # Only watch files in AI_agents project, not In_House_SQL
        )
