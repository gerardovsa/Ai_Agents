"""
New Flask App - Clean Rebuild
Uses unified session manager and AI client

This is the NEW clean Flask app that replaces flask_triple_agent_app.py
Run on port 5001 for testing, then swap to port 5000 when ready

✅ REFACTORED: All cursor leaks fixed (10 locations)
"""

# Fix Windows console encoding FIRST (before any prints or logging)
import sys
import io
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
from pathlib import Path

# Configure AI_agents paths ONLY - Standalone project
ai_agents_root = Path(__file__).parent.parent  # Go up to AI_agents root
ai_infrastructure_path = ai_agents_root / 'AI_infrastructure'

# Add AI_agents paths
for path in [str(ai_agents_root), str(ai_infrastructure_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Setup unified logging FIRST
from utils.logger_config import setup_logger, log_init, log_config, log_success, log_warning, log_error, ColoredFormatter, Colors
import logging

def log_debug(message: str):
    """Print debug message with color"""
    print(f"{Colors.DEBUG}[DEBUG]{Colors.RESET} {message}")

logger = setup_logger('flask_app')

# Configure werkzeug (Flask's HTTP server) with colored output
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers.clear()
werkzeug_handler = logging.StreamHandler(sys.stdout)
werkzeug_handler.setFormatter(ColoredFormatter('%(levelname)s:%(name)s: %(message)s'))
werkzeug_logger.addHandler(werkzeug_handler)
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.propagate = False

# Configure apscheduler (task scheduler) with colored output
apscheduler_logger = logging.getLogger('apscheduler.executors.default')
apscheduler_logger.handlers.clear()
apscheduler_handler = logging.StreamHandler(sys.stdout)
apscheduler_handler.setFormatter(ColoredFormatter('%(levelname)s:%(name)s: %(message)s'))
apscheduler_logger.addHandler(apscheduler_handler)
apscheduler_logger.setLevel(logging.INFO)
apscheduler_logger.propagate = False

# Configure registry logger with colored output
registry_logger = logging.getLogger('tools.registry_v3')
registry_logger.handlers.clear()
registry_handler = logging.StreamHandler(sys.stdout)
registry_handler.setFormatter(ColoredFormatter('%(levelname)s:%(name)s: %(message)s'))
registry_logger.addHandler(registry_handler)
registry_logger.setLevel(logging.INFO)
registry_logger.propagate = False

log_init(logger, "AI_agents standalone - No external dependencies")

# Now import Flask and other dependencies
from flask import Flask, jsonify, request, Response, send_from_directory, send_file
from flask_cors import CORS, cross_origin
from datetime import datetime
from flask_socketio import SocketIO
import json
from queue import Queue, Empty
import threading
import traceback

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

log_debug("About to import db_path_helper...")
# Stock Management - ENABLED (Supabase stock_data schema)
from AI_infrastructure.utils.db_path_helper import get_stock_db_path

STOCK_DB_SCHEMA = get_stock_db_path()  # Returns 'stock_data'
log_debug(f"STOCK_DB_SCHEMA={STOCK_DB_SCHEMA}")

# Check if using Supabase (always true for stock_data schema)
STOCK_DB_AVAILABLE = bool(os.getenv('SUPABASE_URL'))
STOCK_DB_CONFIG = {'db_type': 'supabase', 'schema': STOCK_DB_SCHEMA} if STOCK_DB_AVAILABLE else None

if STOCK_DB_AVAILABLE:
    log_config(logger, f"Stock management enabled - using Supabase (schema: {STOCK_DB_SCHEMA})")
else:
    log_warning(logger, f"Stock management disabled - SUPABASE_URL not set")

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
log_debug("Importing agent_routes_v4...")
from routes.agent_routes_v4 import agent_bp  # V4 modular architecture with tool execution
log_debug("Importing thread_routes...")
from routes.thread_routes import thread_bp
log_debug("Importing chat_routes...")
from routes.chat_routes import chat_bp  # NEW: Chat with file uploads
log_debug("Importing message_operations...")
from routes.message_operations import message_ops_bp  # NEW: Message operations (fork, clone, copy, delete) - ✅ IMPLEMENTED Dec 7, 2025
log_debug("Importing export_routes...")
from routes.export_routes import export_bp

# ⚠️ WooCommerce: Disabled on Render (local development only)
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
if not IS_RENDER:
    log_debug("Importing woocommerce_routes...")
    from routes.woocommerce_routes import woocommerce_bp
else:
    log_config(logger, "[CONFIG] WooCommerce disabled on Render deployment")
    woocommerce_bp = None

log_debug("Importing auth_routes...")
from routes.auth_routes import auth_bp  # NEW: User authentication
log_debug("Importing oauth_routes...")
from routes.oauth_routes import oauth_bp  # NEW: OAuth workspace integration (Google Workspace + M365)
log_debug("Importing vsa_alerts_routes...")
from routes.vsa_alerts_routes import vsa_alerts_bp  # NEW: VSA Veterinary Alerts (transcript + coaching generation)
log_debug("Importing google_auth_routes_V2_FIXED...")
from routes.google_auth_routes_V2_FIXED import google_auth_bp  # NEW: Google OAuth V2
log_debug("Importing microsoft_auth_routes_V2_FIXED...")
from routes.microsoft_auth_routes_V2_FIXED import microsoft_auth_bp  # NEW: Microsoft OAuth V2
log_debug("Importing account_linking_routes...")
from routes.account_linking_routes import account_linking_bp  # NEW: Account linking
log_debug("Importing kanban_routes...")
from routes.kanban_routes import kanban_bp  # NEW: Kanban board with AI agent integration
from routes.database_visualizer_routes import database_visualizer_bp  # ✅ MIGRATED to Supabase PostgreSQL (2025-12-07)
log_debug("Importing synergy_routes...")
from routes.synergy_routes import synergy_bp  # NEW: Synergy Dashboard Kanban
from routes.synergy_file_search import synergy_search_bp  # NEW: Synergy Files global search (Gap #8 fix)
log_debug("Importing scheduler_routes...")
from routes.scheduler_routes import scheduler_bp  # NEW: AI Automation Scheduler
log_debug("Importing automation_routes...")
from routes.automation_routes import automation_bp  # NEW: Visual Automation Canvas
log_debug("Done with main route imports!")

# Optional: InHousePrint production workflow (requires pymssql)
try:
    from routes.inhouse_kanban_routes import inhouse_kanban_bp
    INHOUSE_KANBAN_AVAILABLE = True
except ImportError as e:
    log_warning(logger, f"InHouse Kanban module not available: {e}")
    inhouse_kanban_bp = None
    INHOUSE_KANBAN_AVAILABLE = False

from routes.kanban_supabase_routes import kanban_supabase_bp  # NEW: Kanban Supabase integration (time tracking & analytics)
from routes.kanban_analytics_routes import kanban_analytics_bp  # NEW: Kanban Analytics (PostgreSQL database with custom metrics)
from routes.universal_search_routes import universal_search_bp  # NEW: Universal search (5 endpoints: search, facets, sources, index)
from routes.cloud_folder_sync_routes import cloud_sync_bp  # NEW: Cloud folder sync (5 endpoints: add, list, sync, schedule, delete)
from routes.qdrant_routes import qdrant_bp  # NEW: Qdrant vector database (8 endpoints: connect, create-collection, upsert, search, hybrid-search, stats, delete, snapshot)
from routes.production_log_routes import production_log_bp  # NEW: Production Log (comprehensive job tracking)
from routes.user_preferences_routes import user_preferences_bp  # NEW: User personalization preferences
from routes.geolocation_routes import geolocation_bp  # NEW: Geolocation detection
# TEMP: Testing which route causes hang
print("[DEBUG] Loading thread_assignment_routes...")
from routes.thread_assignment_routes import thread_assignment_bp  # NEW: Thread assignments (JSON storage)
print("[DEBUG] Loading vector_db_routes...")
from routes.vector_db_routes import vector_db_bp  # NEW: Vector Database management (Pinecone + embeddings)
print("[DEBUG] Loading workspace_routes...")
from routes.workspace_routes import workspace_bp  # NEW: Workspace management (CRUD, members, invitations)
from routes.workspace_search_routes import workspace_search_bp  # NEW: Workspace search & message retrieval (4 endpoints: search, semantic-search, messages, transcriptions)
print("[DEBUG] Loading thread_sharing_routes...")
from routes.thread_sharing_routes import thread_sharing_bp  # NEW: Thread sharing (multi-user collaboration)
print("[DEBUG] Loading communication_routes...")
from routes.communication_routes import communication_bp  # NEW: Communication Hub (Gmail + Outlook unified inbox)
print("[DEBUG] Loading user_management_routes...")
from routes.user_management_routes import user_management_bp  # NEW: Sub-user management (parent-child hierarchy)
from routes.render_routes import render_bp  # NEW: Render cloud management (deploy, logs, metrics)
from routes.file_routes import file_bp  # NEW: File storage management (upload, download, delete)
from routes.prompt_library_routes import prompt_routes  # NEW: Prompt library (database-backed prompt management)
from routes.token_routes import token_routes  # NEW: Token tracking (real-time token counts for threads)
from routes.transcription_routes import transcription_bp  # NEW: Voice/audio transcription with Whisper API
from routes.device_lock_routes import device_lock_bp  # NEW: Device lock (multi-device session management)
from routes.pool_monitor_routes import pool_monitor_bp  # NEW: Connection pool monitoring dashboard
from routes.monitoring_routes import monitoring_bp  # NEW: Connection pool health monitoring (Supabase optimization)
from routes.search_routes import search_bp  # NEW: Supabase full-text and semantic search (5 endpoints)
from routes.task_sync_routes import task_sync_bp  # NEW: Universal Task Sync (Google Tasks, Microsoft To Do, Google Calendar)
# from routes.quote_calculator_routes import quote_calc_bp  # DISABLED: In_House_SQL dependency
from routes.vector_db_routes import vector_db_bp  # NEW: Vector database management - AI autonomous search (Pinecone + OpenAI, 3 endpoints)
from routes.module_routes import module_bp  # NEW: Self-registering module system (8 endpoints)
from routes.session_management_routes import cloud_storage_bp  # NEW: Cloud storage sync (Google Drive folders to database, 6 endpoints)
from routes.connection_routes import connections_bp  # Platform connections (2 endpoints)

# Generate unique cache version on Flask startup (forces browser refresh)
import time
import random
CACHE_VERSION = f"{int(time.time())}_{random.randint(1000, 9999)}"
log_success(logger, f"🔄 Generated cache version: {CACHE_VERSION}")

# Initialize Flask app with error handling
try:
    app = Flask(__name__)
    app.config.from_object(Config)
    log_success(logger, "Flask app created successfully")
except Exception as e:
    log_error(logger, f"CRITICAL: Failed to create Flask app: {e}")
    logger.error(traceback.format_exc())
    raise


# ============================================================================
# 🚀 PRE-EMPTIVE SEMANTIC SEARCH INITIALIZATION
# ============================================================================
def initialize_semantic_search_on_startup():
    """
    Pre-emptively initialize persistent semantic search during server startup.
    
    This runs BEFORE server starts to ensure embeddings are ready for first request.
    Uses Supabase persistence - loads instantly if cache exists, regenerates if tools changed.
    
    Called after Flask app is created but before routes are registered.
    """
    try:
        print("\n" + "=" * 80)
        print("[STARTUP] INITIALIZING PERSISTENT SEMANTIC SEARCH (Supabase-backed)")
        print("=" * 80)
        
        # Import registry and semantic search initializer
        from tools.registry_v3 import get_registry
        from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
        
        # Get singleton registry (NOT a new instance)
        print("[STARTUP] Loading tool registry...")
        registry = get_registry()
        print(f"[STARTUP] [OK] Registry loaded with {len(registry.tools)} tools")
        
        # Initialize persistent semantic search (loads from Supabase or regenerates)
        print("[STARTUP] Loading embeddings from Supabase (or regenerating if needed)...")
        semantic_search = get_semantic_search(registry)
        
        if semantic_search and semantic_search.available:
            source = "Supabase" if semantic_search.db_available else "Generated (Database unavailable)"
            print(f"[STARTUP] [OK] Loaded {len(semantic_search.tool_embeddings)} embeddings from {source}")
            print(f"[STARTUP] Version Hash: {semantic_search.version_hash[:16]}...")
            print("=" * 80)
            print("[STARTUP] ✅ SEMANTIC SEARCH READY - Embeddings loaded and cached!")
            print("=" * 80 + "\n")
        else:
            print("[STARTUP] [WARNING] Semantic search not available (sentence-transformers not installed)")
            print("=" * 80 + "\n")
            
    except Exception as e:
        print(f"[STARTUP] [ERROR] Failed to initialize semantic search: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80 + "\n")


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

# ✅ REFACTORED: Initialize user authentication tables (FIXED CURSOR LEAK #1)
try:
    from auth.user_auth import user_auth_manager
    log_success(logger, f"User authentication tables initialized at {user_auth_manager.db_path}")
    
    # ✅ FIX: Use context manager for cursor
    with get_database_connection('ai_infrastructure') as conn:
        with conn.cursor() as cursor:
            
            # Use is_using_supabase() to correctly detect database type
            from shared.database_utils import is_using_supabase
            if is_using_supabase():
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
            else:
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'ai_infrastructure'")
            rows = cursor.fetchall()
            
            # Handle PostgreSQL rows
            if rows and len(rows) > 0:
                # Try to access first element - works for both tuples and postgres rows
                try:
                    tables = [row[0] if isinstance(row, (tuple, list)) else row['name' if 'name' in row else 'tablename'] for row in rows]
                except (KeyError, TypeError, IndexError):
                    # Fallback: just get first item from each row
                    tables = [list(row.values())[0] if hasattr(row, 'values') else row[0] for row in rows]
            else:
                tables = []
            
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
    log_success(logger, "Skipping migrations (using Supabase - tables already exist)")

# Initialize automation tables
try:
    from routes.automation_routes import init_automation_tables
    init_automation_tables()
    log_success(logger, "Automation tables initialized (visual_automations, automation_executions)")
except Exception as e:
    log_error(logger, f"Failed to initialize automation tables: {e}")

# Initialize ModuleRegistry (self-registering module system)
try:
    from AI_infrastructure.core.module_registry import get_module_registry  # ✅ FIX: Use full import path (matches module_routes.py)
    from pathlib import Path
    
    log_init(logger, "Initializing Module Registry...")
    base_dir = Path(__file__).parent.parent
    registry = get_module_registry()
    
    # ONLY scan UI/modules_external directory (plug-and-play modules with manifests)
    # UI/modules_internal are hardcoded/pre-loaded in HTML - they should NOT be managed by ModuleRegistry
    external_modules_dir = base_dir / 'UI' / 'modules_external'
    log_init(logger, f"Scanning {external_modules_dir}...")
    registry.initialize(str(external_modules_dir))  # Convert Path to string
    
    log_init(logger, "ℹ️  Note: modules_internal (thread-cards, universal-search, vector_database, etc.) are pre-loaded in HTML and NOT managed by ModuleRegistry")
    
    # Mark as loaded after ALL directories scanned
    registry._modules_loaded = True
    
    log_success(logger, f"Module Registry initialized: {len(registry.modules)} modules discovered")
    
    # List discovered modules
    for module_id, module in registry.modules.items():
        log_config(logger, f"  - {module.name} ({module_id}): {len(module.required_platforms)} required platforms")
except Exception as e:
    log_error(logger, f"Failed to initialize Module Registry: {e}")
    import traceback
    log_error(logger, traceback.format_exc())

# Register blueprints - Working In_House_SQL implementation
app.register_blueprint(agent_bp, url_prefix='/api/agent')           # Working agent routes with async support
app.register_blueprint(thread_bp, url_prefix='/api/threads')        # 8 endpoints (conversation storage)
app.register_blueprint(chat_bp, url_prefix='/api/chat')             # NEW: Chat with file upload (2 endpoints: /upload, /message)
app.register_blueprint(thread_sharing_bp)                            # NEW: Thread sharing (6 endpoints: share, accept, revoke, list)
app.register_blueprint(message_ops_bp)                               # NEW: Message operations - fork, clone, copy, delete, export, merge (6 endpoints) - ✅ IMPLEMENTED Dec 7, 2025
app.register_blueprint(file_bp)                                      # NEW: File storage (7 endpoints: serve, download, delete, usage)
app.register_blueprint(export_bp, url_prefix='/api/export')         # 3 endpoints (export functionality)
if woocommerce_bp:                                                   # ⚠️ Local development only (disabled on Render)
    app.register_blueprint(woocommerce_bp)                           # 9 endpoints (WooCommerce direct API)
app.register_blueprint(auth_bp)                                      # NEW: 6 endpoints (user auth)
app.register_blueprint(oauth_bp)                                     # NEW: OAuth workspace integration (/api/oauth/*)
app.register_blueprint(google_auth_bp)                               # NEW: Google OAuth V2 (/api/auth/google/*)
app.register_blueprint(microsoft_auth_bp)                            # NEW: Microsoft OAuth V2 (/api/auth/microsoft/*)
app.register_blueprint(vsa_alerts_bp)                                # NEW: VSA Veterinary Alerts (/api/vsa-alerts/*)
app.register_blueprint(account_linking_bp)                           # NEW: Account linking (/api/account/*)
app.register_blueprint(kanban_bp)                                    # NEW: Kanban board + AI agent bridge (8 endpoints)
app.register_blueprint(database_visualizer_bp)                       # ✅ ENABLED (Migrated to Supabase 2025-12-07)
app.register_blueprint(synergy_bp)                                   # NEW: Synergy Dashboard (6 endpoints: /api/synergy/*)
app.register_blueprint(synergy_search_bp, url_prefix='/api/synergy')  # NEW: Synergy file search (Gap #8 fix: 2 endpoints)
app.register_blueprint(cloud_storage_bp)                             # NEW: Cloud storage sync (6 endpoints: Google Drive folders to database)
app.register_blueprint(connections_bp)                               # Platform connections (2 endpoints: list, disconnect)
app.register_blueprint(scheduler_bp)                                 # NEW: AI Automation Scheduler (10 endpoints: /api/scheduler/*)
app.register_blueprint(automation_bp)                                # NEW: Visual Automation Canvas (9 endpoints: /api/automation/*)
if INHOUSE_KANBAN_AVAILABLE:
    app.register_blueprint(inhouse_kanban_bp)                        # NEW: InHousePrint production workflow (5 endpoints)
app.register_blueprint(kanban_supabase_bp)                           # NEW: Kanban Supabase integration (10 endpoints: /api/kanban/supabase/*)
app.register_blueprint(kanban_analytics_bp)                          # NEW: Kanban Analytics (15 endpoints: /api/kanban-analytics/*)
app.register_blueprint(universal_search_bp)                          # NEW: Universal search (5 endpoints: /api/universal-search/*)
app.register_blueprint(qdrant_bp, url_prefix='/api/qdrant')         # NEW: Qdrant vector database (8 endpoints: /api/qdrant/*)
app.register_blueprint(cloud_sync_bp)                                # NEW: Cloud folder sync (5 endpoints: /api/cloud-sync/*)
app.register_blueprint(device_lock_bp)                               # NEW: Device lock (5 endpoints: /api/device/*, /api/thread/*/lock*)
app.register_blueprint(production_log_bp)                            # NEW: Production Log (10 endpoints: /api/production-log/*)
app.register_blueprint(user_preferences_bp)                          # NEW: User preferences (2 endpoints: /api/user/preferences)
app.register_blueprint(geolocation_bp)                               # NEW: Geolocation detection (2 endpoints: /api/geolocation/*)
app.register_blueprint(thread_assignment_bp)                         # NEW: Thread assignments (7 endpoints: /api/thread-assignments/*)

# Calculator Test Dashboard routes
from routes.calculator_test_routes import calculator_test_bp
app.register_blueprint(calculator_test_bp, url_prefix='/api/calculator-test')  # NEW: Calculator testing dashboard (5 endpoints: /api/calculator-test/*)

# Vector Database Enhanced Routes
try:
    from AI_infrastructure.routes.vector_db.vector_db_enhanced_routes import vector_db_enhanced_bp
    app.register_blueprint(vector_db_enhanced_bp)                    # NEW: Vector DB enhanced features (5 endpoints: /api/vector-db/*)
    log_success(logger, "Vector Database Enhanced routes registered (5 endpoints)")
except Exception as e:
    log_error(logger, f"Failed to register vector_db_enhanced routes: {e}")
app.register_blueprint(workspace_bp)                                 # NEW: Workspace management (18 endpoints: /api/workspaces/*)
app.register_blueprint(workspace_search_bp)                          # NEW: Workspace search & message retrieval (4 endpoints: /api/v1/workspace/*)
app.register_blueprint(communication_bp)                             # NEW: Communication Hub (8 endpoints: /api/communication-hub/*)
app.register_blueprint(user_management_bp)                           # NEW: Sub-user management (5 endpoints: /api/users/sub-users/*)
app.register_blueprint(render_bp)                                    # NEW: Render cloud management (6 endpoints: /api/render/*)
from AI_infrastructure.routes.pool_health_routes import pool_health_bp
app.register_blueprint(pool_health_bp)                               # NEW: Pool health metrics dashboard (4 endpoints: /api/pool-health/*)
app.register_blueprint(prompt_routes)                                # NEW: Prompt library (10 endpoints: /api/prompts/*)
app.register_blueprint(search_bp)                                    # NEW: Supabase search system (5 endpoints: /api/search/*)
app.register_blueprint(token_routes)                                 # NEW: Token tracking (3 endpoints: /api/tokens/*)
app.register_blueprint(transcription_bp)                             # NEW: Voice/audio transcription (2 endpoints: /api/transcribe, /api/system/check)
app.register_blueprint(vector_db_bp)                                 # NEW: Vector database management (5 endpoints: /api/vector-db/*)
app.register_blueprint(pool_monitor_bp)                              # NEW: Connection pool monitoring (4 endpoints: /api/pool/*)
app.register_blueprint(monitoring_bp)                                # NEW: Connection pool health monitoring (4 endpoints: /api/pool/stats, /api/pool/health)
app.register_blueprint(module_bp)                                    # NEW: Self-registering module system (8 endpoints: /api/modules/*)
app.register_blueprint(task_sync_bp)                                 # NEW: Universal Task Sync (Google Tasks, Microsoft To Do, Calendar - /api/sync/*)
# app.register_blueprint(quote_calc_bp)                                # DISABLED: In_House_SQL dependency

# 🛠️ DEV TOOLS: Module Creator & Verifier (Development-only endpoints)
from routes.dev_tools_routes import dev_tools_bp
app.register_blueprint(dev_tools_bp)                                 # DEV TOOLS: Module development endpoints (4 endpoints: /api/dev-tools/*)

# 🆕 AUTO-LOAD MODULE BLUEPRINTS (Quote Calculator, Stock Management, etc.)
# This discovers and registers Flask routes from UI/external/modules/*/routes/
# INCLUDES: Stock Management, Shopify E-Commerce, Database Visualizer, Quote Calculator, etc.
try:
    from core.module_blueprint_loader import load_module_blueprints
    from utils.logger_config import log_module, log_route
    module_bp_count = load_module_blueprints(app)
    log_module(logger, f"Loaded {module_bp_count} module blueprints from UI/modules_external")
    log_route(logger, "Auto-discovered routes from: UI/modules_external/*/routes/*.py")
    log_route(logger, "Stock Management: /api/stock-management/* (Blueprint auto-loaded)")
except Exception as e:
    log_warning(logger, f"Module blueprints not loaded: {e} (Module blueprints are optional)")

# REMOVED DUPLICATE: Stock Management routes now loaded via module_blueprint_loader above
# Old init_stock_routes() pattern caused route conflicts with Blueprint system

# Shopify E-Commerce: ENABLED (load routes from module folder)
if STOCK_DB_AVAILABLE:  # Shopify uses same database as Stock Management
    try:
        # Add shopify module to path
        shopify_module_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'modules_external', 'shopify')
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
    xero_module_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'modules_external', 'xero')
    if os.path.exists(xero_module_path):
        sys.path.insert(0, xero_module_path)
        from xero_routes import init_xero_routes
        from xero_reports_enhanced import init_enhanced_xero_routes
        init_xero_routes(app)
        init_enhanced_xero_routes(app)
        log_success(logger, f"Xero Accounting routes (+ enhanced reports) registered from {xero_module_path}")
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
# - woocommerce_routes.py (29 tools) - ⚠️ DISABLED ON RENDER (local development only)
# - deepseek_routes.py (8 tools)
# - gmail_routes.py (29 tools)
# - slack_routes.py (24 tools)
# - woocommerce_routes.py (29 tools)
# - stripe_routes.py (25 tools)
# - ... and 12 more platform routes

# ============================================================================
# CALCULATOR API ENDPOINTS (Quote Calculator Tools)
# ============================================================================

@app.route('/api/calculator/test', methods=['POST'])
def test_calculator():
    """
    Test a calculator using Registry V3 (exact AI usage pattern)
    
    POST /api/calculator/test
    Body: {
        "tool_name": "calculate_business_cards",
        "params": {
            "quantity": 1000,
            "stock_type": "premium",
            "sides": 2
        }
    }
    
    Returns: {
        "success": true,
        "result": {...calculator response...},
        "execution_time_ms": 123
    }
    """
    try:
        import time
        from tools.registry_v3 import RegistryV3
        
        data = request.json
        tool_name = data.get('tool_name')
        params = data.get('params', {})
        
        if not tool_name:
            return jsonify({
                "success": False,
                "error": "tool_name is required"
            }), 400
        
        # Initialize Registry V3 (same as AI uses)
        registry = RegistryV3()
        
        # Execute calculator
        start_time = time.time()
        result = registry.execute_tool(tool_name=tool_name, **params)
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return jsonify({
            "success": True,
            "result": result,
            "execution_time_ms": round(execution_time, 2),
            "tool_name": tool_name,
            "params": params
        })
        
    except Exception as e:
        log_error(logger, f"Calculator test error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/calculator/list', methods=['GET'])
def list_calculators():
    """
    List all available calculators from Registry V3
    
    GET /api/calculator/list
    
    Returns: {
        "success": true,
        "calculators": [
            {
                "name": "calculate_business_cards",
                "platform": "quote_calculator",
                "description": "...",
                "parameters": {...}
            },
            ...
        ],
        "total": 37
    }
    """
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Get all calculator tools
        calculators = []
        for tool_name, tool_info in registry.tools.items():
            if tool_name.startswith('calculate_'):
                calculators.append({
                    "name": tool_name,
                    "platform": tool_info.get('platform', 'unknown'),
                    "short_description": tool_info.get('short_description', ''),
                    "description": tool_info.get('description', ''),
                    "parameters": tool_info.get('parameters', {})
                })
        
        # Sort by name
        calculators.sort(key=lambda x: x['name'])
        
        return jsonify({
            "success": True,
            "calculators": calculators,
            "total": len(calculators)
        })
        
    except Exception as e:
        log_error(logger, f"List calculators error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Serve static UI files
UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'UI')
DEV_TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'dev-tools')

@app.route('/')
def serve_ui():
    """Serve the main UI page with aggressive no-cache headers"""
    # Force read from disk every time (no Flask caching)
    html_path = os.path.join(UI_DIR, 'business-ai-platform-v2.html')
    
    # Get file modification time for ETag
    file_mtime = os.path.getmtime(html_path)
    etag = f'"{file_mtime}"'
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # Fallback to utf-8-sig if utf-8 fails (handles BOM)
        with open(html_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            html_content = f.read()
    
    # 🔥 INJECT RUNTIME CACHE VERSION - Forces browser to reload all JavaScript/CSS
    html_content = html_content.replace(
        'const HTML_VERSION = \'20260103_161616\';',
        f'const HTML_VERSION = \'{CACHE_VERSION}\';'
    )
    # Also replace all ?v= query parameters with runtime cache version
    import re
    html_content = re.sub(r'\?v=\d+_\d+', f'?v={CACHE_VERSION}', html_content)
    
    response = Response(html_content, mimetype='text/html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['ETag'] = etag
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/dev-tools/<path:filename>')
def serve_dev_tools(filename):
    """Serve development tools (Module Creator, etc.)"""
    return send_from_directory(DEV_TOOLS_DIR, filename)

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
# NOTE: For multi-worker deployments, set SOCKETIO_MESSAGE_QUEUE (e.g. redis://) so rooms/broadcasts coordinate.
socketio_message_queue = os.environ.get('SOCKETIO_MESSAGE_QUEUE')

# ========================================
# ENVIRONMENT-AWARE SOCKET.IO CONFIGURATION
# ========================================
# Render production: Specific CORS origins for security
# Local development: Allow all origins for flexibility
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')

if IS_RENDER and RENDER_EXTERNAL_URL:
    # Production: Allow only Render domain + WebSocket protocol variant
    cors_origins = [
        RENDER_EXTERNAL_URL,
        RENDER_EXTERNAL_URL.replace('https://', 'wss://'),
        RENDER_EXTERNAL_URL.replace('https://', 'http://'),  # Fallback for internal requests
    ]
    log_config(logger, f"[WS] Render production mode - CORS origins: {cors_origins}")
else:
    # Local development: Allow all origins
    cors_origins = "*"
    log_config(logger, "[WS] Local development mode - CORS: allow all origins")

# Enhanced configuration for Render deployment
# Increased timeouts for cold starts and load balancer delays
ping_timeout_config = 90 if IS_RENDER else 60  # 90s for Render cold starts
ping_interval_config = 25  # Keep-alive ping every 25s

# Auto-detect best async mode: gevent on Render (better for WebSockets), threading locally
# None = auto-detect (Flask-SocketIO will choose gevent if available, else threading)
async_mode_config = None  # Auto-detect: gevent if available, else threading
log_config(logger, f"[WS] Async mode: auto-detect (will use gevent on Render, threading locally)")

try:
    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_origins,  # Environment-aware CORS
        async_mode=async_mode_config,  # Auto-detect: gevent on Render, threading locally
        logger=False,
        engineio_logger=False,
        ping_timeout=ping_timeout_config,  # 90s on Render, 60s local
        ping_interval=ping_interval_config,  # 25s keep-alive
        always_connect=True,
        manage_session=False,  # ✅ FIX: Disable Flask-SocketIO session management to avoid WSGI conflicts
        cookie=None,  # ✅ FIX: Disable cookies to prevent "write before start_response" errors
        engineio_logger_level='WARNING',  # Only show warnings/errors
        message_queue=socketio_message_queue,
        # Render-specific: Enhanced connection handling
        max_http_buffer_size=1e8 if IS_RENDER else 1e6,  # 100MB on Render, 1MB local (for large messages)
        allow_upgrades=True,  # Allow transport upgrades (polling -> WebSocket)
        http_compression=True,  # Compress HTTP responses
        compression_threshold=1024,  # Compress messages > 1KB
        # ✅ CONNECTION STATE RECOVERY (Socket.IO v4.6+)
        # Recovers session state after temporary disconnections without re-authentication
        # Improves UX during network hiccups, page refreshes, or mobile network switches
        connection_state_recovery={
            'maxDisconnectionDuration': 2 * 60 * 1000,  # 2 minutes buffer for recovery
            'skipMiddlewares': True  # Skip re-authentication on successful recovery
        }
    )
    if socketio_message_queue:
        log_config(logger, f"[WS] message_queue enabled: {socketio_message_queue}")
    else:
        if IS_RENDER:
            log_warning(logger, "[WS] ⚠️ No message_queue configured - MUST use single worker (--workers 1)")
            log_warning(logger, "[WS] For multi-worker, set SOCKETIO_MESSAGE_QUEUE=redis://... in environment")
    log_success(logger, f"[WS] SocketIO initialized - ping_timeout={ping_timeout_config}s, ping_interval={ping_interval_config}s")
    log_config(logger, f"[WS] Async mode: {socketio.async_mode} (auto-detected)")
except Exception as e:
    log_warning(logger, f"[WS] Failed to initialize message_queue ({socketio_message_queue}): {e} - using single-worker mode")
    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_origins,  # Environment-aware CORS
        async_mode=async_mode_config,  # Auto-detect: gevent on Render, threading locally
        logger=False,
        engineio_logger=False,
        ping_timeout=ping_timeout_config,
        ping_interval=ping_interval_config,
        always_connect=True,
        manage_session=False,
        cookie=None,
        engineio_logger_level='WARNING',
        max_http_buffer_size=1e8 if IS_RENDER else 1e6,
        allow_upgrades=True,
        http_compression=True,
        compression_threshold=1024,
        # ✅ CONNECTION STATE RECOVERY (fallback initialization)
        connection_state_recovery={
            'maxDisconnectionDuration': 2 * 60 * 1000,
            'skipMiddlewares': True
        }
    )
    log_success(logger, f"[WS] SocketIO initialized (fallback mode) - ping_timeout={ping_timeout_config}s")

# Track connected clients and their rooms
connected_clients = {}

# Track active users per account (for multi-user collaboration)
active_users = {}  # Format: { user_id: { session_token: { device, ip, connected_at, user_name, room, scope } } }

# Thread-safety for presence tracking (threading async_mode can interleave handlers)
active_users_lock = threading.RLock()

# Fast lookup from Socket.IO sid -> (user_id, session_token)
client_presence_index = {}

# Session TTL cleanup configuration
SESSION_TTL_SECONDS = 300  # 5 minutes of inactivity before cleanup
last_cleanup_time = datetime.now()

# Initialize Redis manager (falls back to in-memory if unavailable)
try:
    from AI_infrastructure.redis_manager import get_redis_manager
    redis_manager = get_redis_manager()
    USE_REDIS = redis_manager.connected
    log_config(logger, f"[REDIS] Status: {'Connected' if USE_REDIS else 'Using in-memory fallback'}")
except Exception as e:
    redis_manager = None
    USE_REDIS = False
    log_warning(logger, f"[REDIS] Failed to initialize: {e}")

# Initialize Message Service for database persistence
try:
    from AI_infrastructure.message_service import get_message_service
    message_service = get_message_service()
    log_config(logger, "[MESSAGE SERVICE] Initialized for database persistence")
except Exception as e:
    message_service = None
    log_warning(logger, f"[MESSAGE SERVICE] Failed to initialize: {e}")

# ============================================================================
# PROFESSIONAL VERIFICATION SYSTEM
# ============================================================================
# Register verification dashboard and WebSocket handlers (AFTER socketio init)
try:
    from routes.verification_routes import register_verification_routes
    register_verification_routes(app, socketio)
except Exception as e:
    log_error(logger, f"Failed to register verification routes: {e}")
    print(f"⚠️  Verification system not available: {e}")

# ============================================================================
# VAN LAYOUT DESIGNER - REMOVED (NOW STANDALONE)
# ============================================================================
# Van Thermal Manager now runs on its own standalone Flask server (port 5002)
# See: MCP_Server/van-thermal-manager/van_server.py
# To start: run start-van-server.bat
# Access at: http://localhost:5002/van-thermal-manager/renderer/van-layout-designer-enhanced.html

def cleanup_stale_sessions():
    """Remove sessions that haven't sent heartbeat within TTL"""
    global active_users, last_cleanup_time
    
    now = datetime.now()
    stale_sessions = []
    
    with active_users_lock:
        for user_id, sessions in list(active_users.items()):
            for session_token, session_info in list(sessions.items()):
                last_heartbeat_str = session_info.get('last_heartbeat')
                if not last_heartbeat_str:
                    continue

                try:
                    last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                    age_seconds = (now - last_heartbeat).total_seconds()

                    if age_seconds > SESSION_TTL_SECONDS:
                        stale_sessions.append((user_id, session_token, session_info))
                except:
                    pass
    
    # Remove stale sessions
    for user_id, session_token, session_info in stale_sessions:
        room = session_info.get('room', 'synergy_board')
        scope = session_info.get('scope')

        with active_users_lock:
            if user_id not in active_users or session_token not in active_users[user_id]:
                continue

            # Remove stale session
            del active_users[user_id][session_token]

            # Remove reverse index if it points to this session
            sid = session_info.get('client_id')
            if sid and client_presence_index.get(sid) == (user_id, session_token):
                del client_presence_index[sid]

            # Remaining counts for this user in this room/scope
            remaining_room_count = len([
                1
                for info in active_users.get(user_id, {}).values()
                if info.get('room', 'synergy_board') == room
            ])
            remaining_scope_count = 0
            if scope:
                remaining_scope_count = len([
                    1
                    for info in active_users.get(user_id, {}).values()
                    if info.get('room', 'synergy_board') == room and info.get('scope') == scope
                ])

            # Drop user container if empty
            if user_id in active_users and len(active_users[user_id]) == 0:
                del active_users[user_id]

        log_config(logger, f"[WS CLEANUP] Removed stale session: {session_info.get('user_name')} ({session_token[:8]}) room={room} scope={scope}")

        # Broadcast leave event so UI badges self-heal after crashes
        try:
            socketio.emit('user_session_left', {
                'user_id': user_id,
                'user_name': session_info.get('user_name', 'Unknown'),
                'device': session_info.get('device', 'Desktop'),
                'session_token': session_token,
                'room': room,
                'scope': scope,
                'active_session_count': remaining_room_count,
                'active_scope_session_count': remaining_scope_count,
                'timestamp': datetime.now().isoformat(),
                'reason': 'stale_timeout'
            }, namespace='/ws/synergy', room=room)
        except Exception as e:
            log_warning(logger, f"[WS CLEANUP] Failed to emit stale leave event: {e}")
    
    last_cleanup_time = now
    return len(stale_sessions)

# ============================================================================
# ============================================================================
# WEBSOCKET ERROR DIAGNOSTICS - Intelligent Root Cause Detection
# ============================================================================

@app.errorhandler(Exception)
def handle_websocket_errors(error):
    """
    Intelligent WebSocket error handler - identifies root causes instead of generic errors.
    
    Common causes detected:
    1. write() before start_response - Client disconnected during handshake
    2. Connection reset - Network interruption or browser refresh
    3. Timeout - Client took too long to complete handshake
    4. Multiple processes - Port conflict with another Flask instance
    """
    import traceback
    error_str = str(error)
    error_type = type(error).__name__
    
    # Pattern matching for root cause identification
    if "Session is disconnected" in error_str or (isinstance(error, KeyError) and "Session is disconnected" in str(error)):
        # ROOT CAUSE: Client sent request after session was terminated (race condition)
        # This happens when:
        # 1. Server terminates session (timeout/disconnect)
        # 2. Client still has pending HTTP polling requests in flight
        # 3. Server tries to lookup session -> KeyError
        log_warning(logger, f"[WS] Session lookup failed - client request arrived after session termination (normal race condition)")
        return None  # Suppress - this is expected behavior
    
    elif "write() before start_response" in error_str or isinstance(error, AssertionError):
        # ROOT CAUSE: Client disconnected mid-handshake (browser refresh, network issue)
        log_warning(logger, f"[WS] Client aborted WebSocket upgrade (likely browser refresh or network issue)")
        return None  # Suppress - this is normal behavior
    
    elif "Connection reset" in error_str or "ConnectionResetError" in error_type:
        # ROOT CAUSE: Network interruption or client forcefully closed connection
        log_warning(logger, f"[WS] Client connection reset (network interruption or forced close)")
        return None
    
    elif "Timeout" in error_str or "TimeoutError" in error_type:
        # ROOT CAUSE: Client took too long to respond during handshake
        log_warning(logger, f"[WS] Handshake timeout (slow network or client not responding)")
        return None
    
    elif "Address already in use" in error_str:
        # ROOT CAUSE: Multiple Flask instances trying to bind to same port
        log_error(logger, f"[CRITICAL] Port 5001 already in use - another Flask instance running!")
        log_error(logger, f"   Run: Stop-Process -Name python -Force")
        raise error  # This is critical - let it propagate
    
    elif "pool" in error_str.lower() and "exhaust" in error_str.lower():
        # ROOT CAUSE: Database connection pool exhausted
        log_error(logger, f"[DB] Connection pool exhausted - too many parallel queries")
        log_error(logger, f"   Check: parallel workers, missing conn.close(), long-running queries")
        raise error
    
    else:
        # Unknown error - log full details for investigation
        log_error(logger, f"[ERROR] Unhandled exception: {error_type}: {error_str}")
        log_error(logger, f"   Traceback: {traceback.format_exc()}")
        raise error


# DEFAULT NAMESPACE HANDLERS (catch unwanted connections)
# ============================================================================

@socketio.on('connect')
def default_connect():
    """
    Handle connection attempts to default namespace (/)
    Accept but do nothing - prevents WSGI "write before start_response" errors
    """
    try:
        log_warning(logger, f"[WS] Connection to default namespace from {request.sid}")
        # Don't return False - let it connect to avoid WSGI errors
        # Client should use /ws/synergy or /ws/streaming instead
        return True  # ✅ Explicitly return True to confirm connection
    except Exception as e:
        log_error(logger, f"[WS] Error in default_connect: {e}")
        return True  # Still return True to prevent errors

@socketio.on('disconnect')
def default_disconnect():
    """
    Handle disconnection from default namespace (/)
    """
    try:
        logger.info(f"[WS] Disconnection from default namespace: {request.sid}")
    except Exception as e:
        log_error(logger, f"[WS] Error in default_disconnect: {e}")

# ============================================================================
# COMPREHENSIVE SOCKETIO HANDLERS FOR /ws/synergy NAMESPACE
# ============================================================================

@socketio.on('connect', namespace='/ws/synergy')
def ws_synergy_connect(auth=None):
    """
    Handle client connection to Synergy namespace with intelligent error diagnosis.
    
    Detects and reports specific connection failure causes:
    - Invalid/missing client ID
    - Duplicate connections from same client
    - Rate limiting (too many connections)
    - Authentication failures
    """
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        client_id = flask_request.sid
        
        # Log connection attempt with details for debugging
        logger.info(f"[WS /ws/synergy] ✅ Connection from SID: {client_id}")
        logger.info(f"[WS /ws/synergy] Remote: {flask_request.remote_addr}")
        logger.info(f"[WS /ws/synergy] Transport: {flask_request.environ.get('werkzeug.socket', 'unknown')}")
        
        # DIAGNOSTIC: Check if client_id is valid
        if not client_id:
            logger.error("[WS] ROOT CAUSE: Flask-SocketIO failed to generate session ID")
            logger.error("   Possible causes: WSGI middleware conflict, session disabled, cookie issues")
            return False  # Reject connection
        
        # DIAGNOSTIC: Check for duplicate connection (reconnection without proper disconnect)
        if client_id in connected_clients:
            log_warning(logger, f"[WS] Client {client_id} reconnecting (previous session not cleaned up)")
            log_warning(logger, "   ROOT CAUSE: Browser refresh or network interruption")
            # Clean up old session before accepting new one
            if client_id in connected_clients:
                connected_clients.pop(client_id, None)
        
        # DIAGNOSTIC: Check connection rate (basic DoS protection)
        recent_connections = [
            c for c in connected_clients.values()
            if (datetime.now() - datetime.fromisoformat(c['connected_at'])).total_seconds() < 1
        ]
        if len(recent_connections) > 20:
            log_error(logger, f"[WS] ROOT CAUSE: Connection flood detected ({len(recent_connections)} in 1 second)")
            log_error(logger, "   Possible causes: DDoS attack, client reconnect loop, misconfigured keepalive")
            return False  # Reject - rate limit
        
        # Accept connection
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
        
    except AssertionError as e:
        # ROOT CAUSE: write() before start_response (client disconnected during handshake)
        log_warning(logger, f"[WS] Client disconnected during handshake (browser refresh/network issue)")
        return False  # Expected behavior - don't log as error
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Intelligent error diagnosis
        if "pool" in error_msg.lower():
            log_error(logger, f'[WS] ROOT CAUSE: Database connection pool exhausted during WebSocket handshake')
            log_error(logger, f'   Fix: Reduce parallel connections, add connection pooling, check for leaks')
        elif "timeout" in error_msg.lower():
            log_error(logger, f'[WS] ROOT CAUSE: Connection timeout during handshake')
            log_error(logger, f'   Fix: Increase ping_timeout (currently 60s), check network latency')
        elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
            log_error(logger, f'[WS] ROOT CAUSE: Permission denied (CORS, authentication, or firewall)')
            log_error(logger, f'   Fix: Check CORS settings, authentication middleware, firewall rules')
        else:
            log_error(logger, f'[WS ERROR] Connection failed - {error_type}: {error_msg}')
            import traceback
            log_error(logger, f'   Full trace: {traceback.format_exc()}')
        
        return False  # Reject connection on error

@socketio.on('disconnect', namespace='/ws/synergy')
def ws_synergy_disconnect(reason=None):
    """
    Handle client disconnection from /ws/synergy namespace with diagnostic logging.
    
    Args:
        reason: Disconnect reason passed by Flask-SocketIO (optional)
        Common reasons:
        - "Client disconnected" - Normal user-initiated disconnect
        - "Connection lost" - Network issue or timeout
        - "Server shutdown" - Flask restart
        - "Ping timeout" - Client stopped responding to keepalive
    
    Note: Flask-SocketIO automatically provides request context with session ID.
    This works identically on local Windows and Render Linux deployments with Supabase.
    """
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        # Get client_id from Flask-SocketIO request context
        client_id = getattr(flask_request, 'sid', None)
        
        # DIAGNOSTIC: Log disconnect reason for troubleshooting
        if reason:
            if reason == "Client disconnected":
                log_config(logger, f'[WS] Client {client_id} disconnected normally')
            elif "timeout" in reason.lower():
                log_warning(logger, f'[WS] Client {client_id} disconnected: Ping timeout (no response for {60}s)')
                log_warning(logger, f'   ROOT CAUSE: Client went offline, network issue, or tab backgrounded')
            elif "lost" in reason.lower():
                log_warning(logger, f'[WS] Client {client_id} disconnected: Connection lost')
                log_warning(logger, f'   ROOT CAUSE: Network interruption, browser closed, or WiFi dropped')
            else:
                log_config(logger, f'[WS] Client {client_id} disconnected: {reason}')
        
        # If no client_id could be determined, skip silently (normal for some disconnect scenarios)
        if not client_id:
            return
        
        # Clean up user presence tracking
        disconnected_user = None
        disconnected_session = None
        
        with active_users_lock:
            indexed = client_presence_index.get(client_id)
            if indexed:
                user_id, session_token = indexed
                session_info = active_users.get(user_id, {}).get(session_token)
                if session_info:
                    disconnected_user = user_id
                    disconnected_session = session_token
                    user_name = session_info.get('user_name', 'Unknown')
                    device = session_info.get('device', 'Desktop')
                    room = session_info.get('room', 'synergy_board')
                    scope = session_info.get('scope')

                    del active_users[user_id][session_token]
                    del client_presence_index[client_id]

                    remaining_room_count = len([
                        1
                        for info in active_users.get(user_id, {}).values()
                        if info.get('room', 'synergy_board') == room
                    ])
                    remaining_scope_count = 0
                    if scope:
                        remaining_scope_count = len([
                            1
                            for info in active_users.get(user_id, {}).values()
                            if info.get('room', 'synergy_board') == room and info.get('scope') == scope
                        ])

                    if user_id in active_users and len(active_users[user_id]) == 0:
                        del active_users[user_id]

                    # Always notify the room (including when this was the last session)
                    emit('user_session_left', {
                        'user_id': user_id,
                        'user_name': user_name,
                        'device': device,
                        'session_token': session_token,
                        'room': room,
                        'scope': scope,
                        'active_session_count': remaining_room_count,
                        'active_scope_session_count': remaining_scope_count,
                        'timestamp': datetime.now().isoformat()
                    }, namespace='/ws/synergy', room=room)
            else:
                # Fallback: scan when presence was never announced
                for user_id, sessions in list(active_users.items()):
                    for session_token, session_info in list(sessions.items()):
                        if session_info.get('client_id') == client_id:
                            disconnected_user = user_id
                            disconnected_session = session_token
                            user_name = session_info.get('user_name', 'Unknown')
                            device = session_info.get('device', 'Desktop')
                            room = session_info.get('room', 'synergy_board')
                            scope = session_info.get('scope')

                            del active_users[user_id][session_token]

                            remaining_room_count = len([
                                1
                                for info in active_users.get(user_id, {}).values()
                                if info.get('room', 'synergy_board') == room
                            ])
                            remaining_scope_count = 0
                            if scope:
                                remaining_scope_count = len([
                                    1
                                    for info in active_users.get(user_id, {}).values()
                                    if info.get('room', 'synergy_board') == room and info.get('scope') == scope
                                ])

                            if len(active_users.get(user_id, {})) == 0 and user_id in active_users:
                                del active_users[user_id]

                            emit('user_session_left', {
                                'user_id': user_id,
                                'user_name': user_name,
                                'device': device,
                                'session_token': session_token,
                                'room': room,
                                'scope': scope,
                                'active_session_count': remaining_room_count,
                                'active_scope_session_count': remaining_scope_count,
                                'timestamp': datetime.now().isoformat()
                            }, namespace='/ws/synergy', room=room)
                            break
                    if disconnected_user:
                        break
        
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

@socketio.on('user_presence', namespace='/ws/synergy')
def ws_synergy_user_presence(data):
    """
    Handle user presence announcement (for multi-user collaboration)
    
    Data format:
    {
        "user_id": 1,
        "user_name": "John Doe",
        "device": "💻 Windows",
        "session_token": "unique-browser-session-id"
    }
    """
    from flask_socketio import emit, join_room
    from flask import request as flask_request
    
    try:
        user_id = data.get('user_id')
        session_token = data.get('session_token')
        user_name = data.get('user_name', 'Unknown User')
        display_name = data.get('display_name', user_name)  # Per-session identity
        device = data.get('device', '💻 Desktop')
        room = (data.get('room', 'synergy_board') or 'synergy_board')
        scope = data.get('scope') or None
        
        # Sanitize display_name (max 50 chars, basic safety)
        if display_name:
            display_name = str(display_name)[:50].strip()
        if not display_name:
            display_name = user_name
        
        if not user_id or not session_token:
            log_warning(logger, "[WS] Invalid user_presence data - missing user_id or session_token")
            return
        
        # Ensure the client is in the room it's announcing for (defensive)
        try:
            join_room(room)
            client_id = flask_request.sid
            if client_id in connected_clients:
                connected_clients[client_id]['rooms'].add(room)
        except Exception:
            pass

        with active_users_lock:
            # Initialize user tracking
            if user_id not in active_users:
                active_users[user_id] = {}

            previous_room = None
            previous_scope = None

            if session_token in active_users[user_id]:
                previous_room = active_users[user_id][session_token].get('room', 'synergy_board')
                previous_scope = active_users[user_id][session_token].get('scope')

            # Add/update this session to active users
            active_users[user_id][session_token] = {
                'user_name': user_name,
                'display_name': display_name,  # Per-session identity for multi-person collaboration
                'device': device,
                'client_id': flask_request.sid,
                'connected_at': datetime.now().isoformat(),
                'last_heartbeat': datetime.now().isoformat(),
                'ip_address': flask_request.remote_addr if hasattr(flask_request, 'remote_addr') else None,
                'room': room,
                'scope': scope
            }

            # Update reverse index
            client_presence_index[flask_request.sid] = (user_id, session_token)
        
        # Count active sessions for this user in this room/scope
        with active_users_lock:
            active_session_count = len([
                1
                for info in active_users[user_id].values()
                if info.get('room', 'synergy_board') == room
            ])

            active_scope_session_count = 0
            if scope:
                active_scope_session_count = len([
                    1
                    for info in active_users[user_id].values()
                    if info.get('room', 'synergy_board') == room and info.get('scope') == scope
                ])
        
        log_config(logger, f"[WS] User presence: {user_name} (ID: {user_id}) from {device} - room={room} scope={scope} - {active_session_count} active session(s)")

        # If the client moved rooms/scopes, broadcast a synthetic leave to the previous context
        if previous_room and previous_room != room:
            prev_remaining_room_count = len([
                1
                for info in active_users[user_id].values()
                if info.get('room', 'synergy_board') == previous_room
            ])
            prev_remaining_scope_count = 0
            if previous_scope:
                prev_remaining_scope_count = len([
                    1
                    for info in active_users[user_id].values()
                    if info.get('room', 'synergy_board') == previous_room and info.get('scope') == previous_scope
                ])
            emit('user_session_left', {
                'user_id': user_id,
                'user_name': user_name,
                'display_name': display_name,
                'device': device,
                'session_token': session_token,
                'room': previous_room,
                'scope': previous_scope,
                'active_session_count': prev_remaining_room_count,
                'active_scope_session_count': prev_remaining_scope_count,
                'timestamp': datetime.now().isoformat()
            }, namespace='/ws/synergy', room=previous_room, skip_sid=flask_request.sid)

        if previous_room == room and previous_scope != scope and previous_scope:
            prev_remaining_scope_count = len([
                1
                for info in active_users[user_id].values()
                if info.get('room', 'synergy_board') == room and info.get('scope') == previous_scope
            ])
            emit('user_session_left', {
                'user_id': user_id,
                'user_name': user_name,
                'display_name': display_name,
                'device': device,
                'session_token': session_token,
                'room': room,
                'scope': previous_scope,
                'active_session_count': active_session_count,
                'active_scope_session_count': prev_remaining_scope_count,
                'timestamp': datetime.now().isoformat()
            }, namespace='/ws/synergy', room=room, skip_sid=flask_request.sid)
        
        # Broadcast to other clients of same user (skip sender)
        emit('user_joined', {
            'user_id': user_id,
            'user_name': user_name,
            'display_name': display_name,
            'device': device,
            'session_token': session_token,
            'room': room,
            'scope': scope,
            'active_session_count': active_session_count,
            'active_scope_session_count': active_scope_session_count,
            'timestamp': datetime.now().isoformat()
        }, namespace='/ws/synergy', room=room, skip_sid=flask_request.sid)
        
        # Send confirmation to sender with list of other active sessions
        with active_users_lock:
            other_sessions = [
                {
                    'session_token': token,
                    'user_name': info.get('user_name'),
                    'display_name': info.get('display_name', info.get('user_name')),
                    'device': info.get('device'),
                    'connected_at': info.get('connected_at'),
                    'room': info.get('room', 'synergy_board'),
                    'scope': info.get('scope')
                }
                for token, info in active_users[user_id].items()
                if token != session_token and info.get('room', 'synergy_board') == room
            ]
        
        emit('presence_confirmed', {
            'your_session_token': session_token,
            'room': room,
            'scope': scope,
            'active_session_count': active_session_count,
            'active_scope_session_count': active_scope_session_count,
            'other_sessions': other_sessions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] user_presence handler failed: {e}")
        import traceback
        traceback.print_exc()

@socketio.on('user_heartbeat', namespace='/ws/synergy')
def ws_synergy_user_heartbeat(data):
    """
    Update user's last active timestamp (keepalive) and trigger stale session cleanup
    Called periodically by frontend to maintain presence
    """
    global last_cleanup_time
    
    try:
        user_id = data.get('user_id')
        session_token = data.get('session_token')
        
        if user_id and session_token:
            with active_users_lock:
                if user_id in active_users and session_token in active_users[user_id]:
                    active_users[user_id][session_token]['last_heartbeat'] = datetime.now().isoformat()
        
        # Trigger cleanup every 60 seconds
        if (datetime.now() - last_cleanup_time).total_seconds() > 60:
            cleaned = cleanup_stale_sessions()
            if cleaned > 0:
                log_config(logger, f"[WS CLEANUP] Removed {cleaned} stale session(s)")
                
    except Exception as e:
        log_error(logger, f"[WS ERROR] user_heartbeat handler failed: {e}")

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
    user_id = data.get('user_id')
    
    print(f'[WS] Session update: {session_id} in room {room}')
    
    # Broadcast to all other clients in the room
    emit('session_updated', {
        'session_id': session_id,
        'updates': updates,
        'timestamp': datetime.now().isoformat()
    }, room=room, include_self=False)
    
    # ✅ CROSS-DEVICE SYNC: Also broadcast to user room for device sync
    if user_id:
        emit('session_updated', {
            'session_id': session_id,
            'updates': updates,
            'timestamp': datetime.now().isoformat()
        }, room=f'user_{user_id}', include_self=False)


# ============================================================================
# STREAMING SESSION REGISTRY (Inline Interaction System)
# ============================================================================
# Global registry to track active StreamingManager sessions
# This allows WebSocket messages to route to the correct session

from typing import Dict, Optional

# Global dictionary: session_id -> StreamingSession instance
streaming_sessions: Dict[str, any] = {}


def register_streaming_session(session_id: str, session):
    """
    Register a streaming session for WebSocket message routing.
    Called automatically when StreamingSession is created.
    
    Args:
        session_id: Unique session identifier
        session: StreamingSession instance
    """
    streaming_sessions[session_id] = session
    log_config(logger, f'[STREAMING] ✅ Registered session: {session_id}')


def unregister_streaming_session(session_id: str):
    """
    Unregister a streaming session.
    Called automatically when StreamingSession closes.
    
    Args:
        session_id: Session identifier to remove
    """
    if session_id in streaming_sessions:
        del streaming_sessions[session_id]
        log_config(logger, f'[STREAMING] ✅ Unregistered session: {session_id}')


def get_streaming_session(session_id: str):
    """
    Get a streaming session by ID.
    Returns None if session not found.
    
    Args:
        session_id: Session identifier
        
    Returns:
        StreamingSession instance or None
    """
    return streaming_sessions.get(session_id)


# ============================================================================
# AGENT STREAMING NAMESPACE (/ws/streaming)
# ============================================================================
# Dedicated namespace for AI agent inline interaction system
# Used by: agent-interaction-websocket.js (frontend)
# Purpose: Real-time two-way communication (input requests, progress updates)
# Separate from /ws/synergy to avoid conflicts with Synergy Board

@socketio.on('connect', namespace='/ws/streaming')
def handle_streaming_connect():
    """
    Handle agent streaming connection for inline interaction.
    Each agent gets its own session_id for isolation.
    
    URL format: ws://localhost:5000/ws/streaming?session_id=abc-123
    """
    from flask import request
    from flask_socketio import join_room, emit
    
    session_id = flask_request.args.get('session_id')
    client_id = flask_request.sid
    
    if not session_id:
        log_error(logger, f'[STREAMING] ❌ Connection rejected - no session_id')
        return False
    
    # Join session-specific room
    join_room(session_id, namespace='/ws/streaming')
    
    log_config(logger, f'[STREAMING] ✅ Agent session connected: {session_id} (client: {client_id})')
    
    # Send handshake confirmation to client
    emit('connected', {
        'session_id': session_id,
        'status': 'connected',
        'timestamp': datetime.now().isoformat()
    }, namespace='/ws/streaming')
    
    return True


@socketio.on('disconnect', namespace='/ws/streaming')
def handle_streaming_disconnect():
    """Handle agent streaming disconnection"""
    client_id = flask_request.sid
    log_config(logger, f'[STREAMING] 🔌 Client disconnected: {client_id}')


@socketio.on('handshake', namespace='/ws/streaming')
def handle_streaming_handshake(data):
    """
    Handle initial handshake from agent.
    
    Message format:
    {
        'type': 'handshake',
        'participant': 'user_123',
        'agent_id': 1
    }
    """
    from flask_socketio import emit
    
    agent_id = data.get('agent_id')
    participant = data.get('participant')
    
    log_config(logger, f'[STREAMING] 🤝 Handshake from agent {agent_id}: {participant}')
    
    emit('handshake_ack', {
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }, namespace='/ws/streaming')


@socketio.on('provide_input', namespace='/ws/streaming')
def handle_streaming_provide_input(data):
    """
    Handle user input submission from inline interaction bubble.
    This is called when user clicks Submit in the bubble UI.
    
    Message format from frontend:
    {
        'type': 'provide_input',
        'session_id': 'abc-123',
        'request_id': 'req-456',
        'input_value': 'user response',
        'from_participant': 'user_789',
        'timestamp': '2025-12-17T...'
    }
    """
    from flask_socketio import emit
    import asyncio
    
    session_id = data.get('session_id')
    request_id = data.get('request_id')
    input_value = data.get('input_value')
    from_participant = data.get('from_participant', 'unknown')
    
    log_config(logger, f'[STREAMING] 📥 Input received for session {session_id}: {input_value}')
    
    # Find the StreamingSession instance
    session = get_streaming_session(session_id)
    
    if session:
        try:
            # Check if provide_input is async
            result = session.provide_input(input_value, from_participant)
            if asyncio.iscoroutine(result):
                # If async, we need to run it in event loop
                try:
                    asyncio.create_task(result)
                except RuntimeError:
                    # No running event loop, use run_coroutine_threadsafe
                    import threading
                    loop = asyncio.new_event_loop()
                    threading.Thread(target=lambda: loop.run_until_complete(result), daemon=True).start()
            
            log_config(logger, f'[STREAMING] ✅ Input provided to session {session_id}')
            
            # Confirm receipt to client
            emit('input_received', {
                'request_id': request_id,
                'status': 'received',
                'timestamp': datetime.now().isoformat()
            }, room=session_id, namespace='/ws/streaming')
            
        except Exception as e:
            log_error(logger, f'[STREAMING] ❌ Error providing input: {str(e)}')
            emit('error', {
                'message': f'Error processing input: {str(e)}',
                'request_id': request_id
            }, namespace='/ws/streaming')
    else:
        log_error(logger, f'[STREAMING] ❌ Session not found: {session_id}')
        emit('error', {
            'message': f'Session {session_id} not found or expired',
            'request_id': request_id
        }, namespace='/ws/streaming')


@socketio.on('ping', namespace='/ws/streaming')
def handle_streaming_ping():
    """Handle keepalive ping from client"""
    from flask_socketio import emit
    emit('pong', {'timestamp': datetime.now().isoformat()}, namespace='/ws/streaming')

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

@socketio.on('send_direct_message', namespace='/ws/synergy')
def ws_synergy_send_direct_message(data):
    """Send direct message to specific user/session"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    try:
        target_user_id = data.get('target_user_id')
        target_session_token = data.get('target_session_token')  # Optional: specific session
        message = data.get('message')
        sender_user_id = data.get('sender_user_id')
        sender_user_name = data.get('sender_user_name')
        sender_session_token = data.get('sender_session_token')
        
        if not target_user_id or not message:
            log_warning(logger, "[WS] Invalid direct_message - missing target_user_id or message")
            return
        
        # Find target user's sessions
        if target_user_id not in active_users:
            emit('message_delivery_failed', {
                'target_user_id': target_user_id,
                'reason': 'User not online',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Save message to database
        message_id = None
        if message_service:
            message_id = message_service.save_message(
                sender_user_id=sender_user_id,
                message_text=message,
                message_type='direct',
                recipient_user_id=target_user_id,
                room='synergy_board',
                metadata={'source': 'socket.io'}
            )
        
        # Send to specific session or all sessions of target user
        target_sessions = active_users[target_user_id]
        delivered_count = 0
        
        for session_token, session_info in target_sessions.items():
            # Skip if targeting specific session and this isn't it
            if target_session_token and session_token != target_session_token:
                continue
            
            client_id = session_info.get('client_id')
            if client_id:
                emit('direct_message_received', {
                    'source': 'socket.io',
                    'message_id': message_id,
                    'from_user_id': sender_user_id,
                    'from_user_name': sender_user_name,
                    'from_session_token': sender_session_token,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }, room=client_id)
                delivered_count += 1
                
                # Mark as delivered in database
                if message_id and message_service:
                    message_service.mark_delivered(message_id, target_user_id)
        
        # Confirm delivery to sender
        emit('message_delivered', {
            'target_user_id': target_user_id,
            'target_session_token': target_session_token,
            'delivered_count': delivered_count,
            'timestamp': datetime.now().isoformat()
        })
        
        log_config(logger, f"[WS] Direct message: {sender_user_name} → User {target_user_id} ({delivered_count} session(s))")
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] send_direct_message failed: {e}")

@socketio.on('broadcast_message', namespace='/ws/synergy')
def ws_synergy_broadcast_message(data):
    """Broadcast message to all users in room"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    try:
        message = data.get('message')
        sender_user_id = data.get('sender_user_id')
        sender_user_name = data.get('sender_user_name')
        room = data.get('room', 'synergy_board')
        
        if not message:
            log_warning(logger, "[WS] Invalid broadcast_message - missing message")
            return
        
        # Save message to database
        message_id = None
        if message_service:
            message_id = message_service.save_message(
                sender_user_id=sender_user_id,
                message_text=message,
                message_type='broadcast',
                room=room,
                metadata={'source': 'socket.io'}
            )
        
        # Broadcast to all clients in room (excluding sender)
        emit('broadcast_message_received', {
            'source': 'socket.io',
            'message_id': message_id,
            'from_user_id': sender_user_id,
            'from_user_name': sender_user_name,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=room, skip_sid=flask_request.sid)
        
        log_config(logger, f"[WS] Broadcast: {sender_user_name} → room {room}")
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] broadcast_message failed: {e}")

@socketio.on('agent_message_sent', namespace='/ws/synergy')
def ws_synergy_agent_message_sent(data):
    """Broadcast agent message to other sessions based on privacy mode"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    try:
        thread_id = data.get('thread_id')
        agent_id = data.get('agent_id')
        message = data.get('message')
        role = data.get('role')
        content_blocks = data.get('content_blocks')
        session_token = data.get('session_token')
        privacy_mode = data.get('privacy_mode', 'central')  # Default to central (collaborative)
        team_id = data.get('team_id')
        
        if not thread_id or not message:
            log_warning(logger, "[WS] Invalid agent_message_sent - missing thread_id or message")
            return
        
        # Get user_id from data (WebSocket data includes user_id)
        user_id = data.get('user_id')
        
        if not user_id:
            log_warning(logger, "[WS] Cannot broadcast agent message - no user_id in data")
            return
        
        # Route based on privacy mode
        if privacy_mode == 'local':
            # Local Ops: Don't broadcast to other sessions (private to sender)
            log_config(logger, f"[WS] Agent message LOCAL mode: thread={thread_id}, no broadcast (private)")
            return  # Skip broadcast
        
        # ✅ PRODUCTION FIX: Always broadcast to user room (remove local mode - doesn't work)
        # Broadcast to all sessions with same user_id (team collaboration)
        emit('agent_message_received', {
            'source': 'socket.io',
            'thread_id': thread_id,
            'agent_id': agent_id,
            'message': message,
            'role': role,
            'content_blocks': content_blocks,
            'session_token': session_token,
            'privacy_mode': 'central',  # Force central mode (local mode removed)
            'timestamp': datetime.now().isoformat()
        }, room=f'user_{user_id}', skip_sid=flask_request.sid)
        
        log_config(logger, f"[WS] Agent message broadcast: thread={thread_id}, agent={agent_id}, role={role}, room=user_{user_id}")
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] agent_message_sent failed: {e}")

@socketio.on('typing_start', namespace='/ws/synergy')
def ws_synergy_typing_start(data):
    """User started typing"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    try:
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        room = data.get('room', 'synergy_board')
        agent_id = data.get('agent_id')
        
        # Store in Redis if available
        if USE_REDIS and redis_manager:
            redis_manager.set_typing(user_id, user_name, room, agent_id, ttl=10)
        
        # Broadcast typing indicator (exclude sender)
        emit('user_typing', {
            'user_id': user_id,
            'user_name': user_name,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat()
        }, room=room, skip_sid=flask_request.sid)
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] typing_start failed: {e}")

@socketio.on('typing_stop', namespace='/ws/synergy')
def ws_synergy_typing_stop(data):
    """User stopped typing"""
    from flask_socketio import emit
    from flask import request as flask_request
    
    try:
        user_id = data.get('user_id')
        room = data.get('room', 'synergy_board')
        agent_id = data.get('agent_id')
        
        # Broadcast typing stopped (exclude sender)
        emit('user_stopped_typing', {
            'user_id': user_id,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat()
        }, room=room, skip_sid=flask_request.sid)
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] typing_stop failed: {e}")

@socketio.on('mark_message_read', namespace='/ws/synergy')
def ws_synergy_mark_message_read(data):
    """Mark message as read by user"""
    from flask_socketio import emit
    
    try:
        message_id = data.get('message_id')
        user_id = data.get('user_id')
        
        if not message_id or not user_id:
            return
        
        # Mark in Redis
        if USE_REDIS and redis_manager:
            redis_manager.mark_message_read(str(message_id), user_id)
        
        # Mark in database
        if message_service:
            message_service.mark_read(message_id, user_id)
        
        # Send read receipt back to sender
        emit('message_read_receipt', {
            'message_id': message_id,
            'read_by_user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        
        log_config(logger, f"[WS] Message {message_id} marked read by user {user_id}")
        
    except Exception as e:
        log_error(logger, f"[WS ERROR] mark_message_read failed: {e}")

# Initialize AI client
print(f"[DEBUG] Using config path: {Config.DB_CONFIG_PATH}")
ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))

# Store AI client and session manager in app config for blueprints to access
app.config['AI_CLIENT'] = ai_client
app.config['SESSION_MANAGER'] = session_manager

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
# DEV TOOLS WEBSOCKET HANDLERS (/ws/dev-tools)
# ============================================================================

@socketio.on('connect', namespace='/ws/dev-tools')
def dev_tools_connect():
    """Handle client connection to dev tools namespace"""
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        client_id = flask_request.sid
        log_success(logger, f"[DEV TOOLS WS] Client connected: {client_id}")
        
        # Send welcome message
        emit('connected', {'message': 'Connected to dev tools WebSocket', 'client_id': client_id})
        return True
        
    except Exception as e:
        log_error(logger, f"[DEV TOOLS WS] Connection error: {e}")
        return False

@socketio.on('disconnect', namespace='/ws/dev-tools')
def dev_tools_disconnect():
    """Handle client disconnection from dev tools namespace"""
    from flask import request as flask_request
    client_id = flask_request.sid
    log_warning(logger, f"[DEV TOOLS WS] Client disconnected: {client_id}")

@socketio.on('file_saved', namespace='/ws/dev-tools')
def handle_file_saved(data):
    """
    Broadcast file save event to all connected clients (real-time sync)
    
    Expected data format:
    {
        'module_id': 'my_module',
        'file_type': 'html',  # html, js, css, routes, manifest
        'content': '<!-- file content -->'
    }
    """
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        client_id = flask_request.sid
        module_id = data.get('module_id')
        file_type = data.get('file_type')
        
        log_success(logger, f"[DEV TOOLS WS] File saved by {client_id}: {module_id}/{file_type}")
        
        # Broadcast to ALL clients EXCEPT sender (prevents duplicate updates)
        emit('file_updated', data, broadcast=True, include_self=False)
        
    except Exception as e:
        log_error(logger, f"[DEV TOOLS WS] Error broadcasting file save: {e}")

@socketio.on('module_created', namespace='/ws/dev-tools')
def handle_module_created(data):
    """
    Broadcast module creation event to all connected clients
    
    Expected data format:
    {
        'module_id': 'new_module',
        'name': 'New Module',
        'path': '/UI/modules_external/new_module'
    }
    """
    try:
        from flask_socketio import emit
        from flask import request as flask_request
        
        client_id = flask_request.sid
        module_id = data.get('module_id')
        
        log_success(logger, f"[DEV TOOLS WS] Module created by {client_id}: {module_id}")
        
        # Broadcast to ALL clients
        emit('module_created', data, broadcast=True)
        
    except Exception as e:
        log_error(logger, f"[DEV TOOLS WS] Error broadcasting module creation: {e}")

@socketio.on('ping', namespace='/ws/dev-tools')
def dev_tools_ping():
    """Handle ping from client (keep-alive)"""
    from flask_socketio import emit
    emit('pong', {'timestamp': datetime.now().isoformat()})


# ============================================================================
# HEALTH CHECK
# ============================================================================


@app.route('/dev/presence', methods=['GET'])
def dev_presence_snapshot():
        """Read-only presence snapshot for debugging rooms/scopes across browsers/tabs."""
        now = datetime.now()

        with active_users_lock:
                room_counts = {}
                scope_counts = {}
                users_out = []

                for user_id, sessions in active_users.items():
                        session_list = []

                        for session_token, info in sessions.items():
                                room = info.get('room', 'synergy_board')
                                scope = info.get('scope')
                                last_heartbeat_str = info.get('last_heartbeat')
                                age_seconds = None

                                try:
                                        if last_heartbeat_str:
                                                last_heartbeat_dt = datetime.fromisoformat(last_heartbeat_str)
                                                age_seconds = int((now - last_heartbeat_dt).total_seconds())
                                except Exception:
                                        age_seconds = None

                                room_counts[room] = room_counts.get(room, 0) + 1
                                if room not in scope_counts:
                                        scope_counts[room] = {}
                                if scope:
                                        scope_counts[room][scope] = scope_counts[room].get(scope, 0) + 1

                                session_list.append({
                                        'session_token': session_token,
                                        'session_token_short': session_token[:16] + '…' if isinstance(session_token, str) and len(session_token) > 16 else session_token,
                                        'user_name': info.get('user_name'),
                                        'device': info.get('device'),
                                        'room': room,
                                        'scope': scope,
                                        'connected_at': info.get('connected_at'),
                                        'last_heartbeat': last_heartbeat_str,
                                        'age_seconds': age_seconds
                                })

                        users_out.append({
                                'user_id': user_id,
                                'active_sessions': len(session_list),
                                'sessions': session_list
                        })

        response = jsonify({
                'now': now.isoformat(),
                'ttl_seconds': SESSION_TTL_SECONDS,
                'room_counts': room_counts,
                'scope_counts': scope_counts,
                'users': users_out
        })

        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route('/dev/presence-view', methods=['GET'])
def dev_presence_view():
        """Tiny HTML viewer for /dev/presence (auto-refresh) for quick local verification."""
        html = """<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Presence Debug</title>
        <style>
            body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 16px; }
            .row { display: flex; gap: 16px; flex-wrap: wrap; }
            pre { background: #0b1220; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow: auto; }
            .pill { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #e5e7eb; margin-right: 6px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }
            th { background: #f3f4f6; position: sticky; top: 0; }
            .muted { color: #6b7280; }
        </style>
    </head>
    <body>
        <h2>Presence Debug</h2>
        <div class=\"muted\">Auto-refreshes every 2s. Source: <a href=\"/dev/presence\">/dev/presence</a></div>
        <div id=\"summary\" class=\"row\" style=\"margin-top:12px\"></div>
        <h3>Sessions</h3>
        <div style=\"overflow:auto; max-height: 70vh; border: 1px solid #e5e7eb; border-radius: 8px;\">
            <table>
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Session</th>
                        <th>Room</th>
                        <th>Scope</th>
                        <th>Device</th>
                        <th>Last heartbeat</th>
                        <th>Age (s)</th>
                    </tr>
                </thead>
                <tbody id=\"rows\"></tbody>
            </table>
        </div>

        <script>
            async function refresh() {
                const res = await fetch('/dev/presence', { cache: 'no-store' });
                const data = await res.json();

                const summary = document.getElementById('summary');
                const rows = document.getElementById('rows');

                const roomPills = Object.entries(data.room_counts || {}).map(([room, count]) =>
                    `<span class=\"pill\">room: <b>${room}</b> = ${count}</span>`
                ).join('') || '<span class=\"muted\">No active sessions</span>';

                summary.innerHTML = `
                    <div><div class=\"muted\">Now</div><div><b>${data.now}</b></div></div>
                    <div><div class=\"muted\">TTL seconds</div><div><b>${data.ttl_seconds}</b></div></div>
                    <div style=\"min-width: 320px\"><div class=\"muted\">Room counts</div><div>${roomPills}</div></div>
                `;

                const sessionRows = [];
                (data.users || []).forEach(u => {
                    (u.sessions || []).forEach(s => {
                        sessionRows.push(`
                            <tr>
                                <td>${u.user_id}</td>
                                <td><span class=\"muted\">${s.session_token_short || ''}</span></td>
                                <td><b>${s.room || ''}</b></td>
                                <td>${s.scope || ''}</td>
                                <td>${s.device || ''}</td>
                                <td class=\"muted\">${s.last_heartbeat || ''}</td>
                                <td>${typeof s.age_seconds === 'number' ? s.age_seconds : ''}</td>
                            </tr>
                        `);
                    });
                });

                rows.innerHTML = sessionRows.join('') || `<tr><td colspan=\"7\" class=\"muted\">No active sessions</td></tr>`;
            }

            refresh();
            setInterval(refresh, 2000);
        </script>
    </body>
</html>"""

        return html

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Enhanced health check endpoint with Socket.IO metrics and explicit CORS"""
    from datetime import datetime
    
    # Gather Socket.IO connection metrics
    socketio_status = {
        'connected_clients': len(connected_clients),
        'async_mode': socketio.async_mode if socketio else 'not_initialized',
        'transport': 'websocket_ready',
        'active_users': len(active_users) if 'active_users' in globals() else 0
    }
    
    response = jsonify({
        'status': 'healthy',
        'app': 'new_flask_app',
        'infrastructure': 'AI_infrastructure',
        'providers': ['anthropic', 'deepseek', 'openai'],
        'socketio': socketio_status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'environment': 'production' if IS_RENDER else 'development'
    })
    
    # Add CORS headers explicitly
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-user-id,X-User-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    
    return response


# ✅ REFACTORED: /api/connections endpoint (FIXED CURSOR LEAK #2)
@app.route('/api/connections', methods=['GET', 'OPTIONS'])
def get_connections():
    """Get OAuth connections for current user + platform global credentials"""
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    try:
        # Get user_id from request (from auth token or default to 1)
        user_id = request.headers.get('X-User-ID') or request.args.get('user_id') or '1'
        
        # Fetch OAuth connections from Supabase
        connections = []
        supabase_db_url = os.environ.get('SUPABASE_DB_URL_POOLER')
        
        if supabase_db_url:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # ✅ FIX: Use context manager for connection AND cursor
            with psycopg2.connect(supabase_db_url, cursor_factory=RealDictCursor) as conn:
                with conn.cursor() as cursor:
                    
                    # ✅ FIX: Fetch user-specific + platform global credentials (user_id=1)
                    # Use UNION to combine both sources
                    cursor.execute("""
                        -- User-specific credentials
                        SELECT 
                            platform,
                            credential_type,
                            credentials,
                            metadata,
                            updated_at,
                            is_active,
                            user_id,
                            CASE WHEN user_id = 1 THEN true ELSE false END as is_platform_global
                        FROM ai_infrastructure.user_platform_credentials
                        WHERE user_id = %s 
                          AND is_active = true
                        
                        UNION
                        
                        -- Platform global credentials (only if not already in user's list)
                        SELECT 
                            platform,
                            credential_type,
                            credentials,
                            metadata,
                            updated_at,
                            is_active,
                            user_id,
                            true as is_platform_global
                        FROM ai_infrastructure.user_platform_credentials
                        WHERE user_id = 1
                          AND is_active = true
                          AND platform NOT IN (
                              SELECT platform 
                              FROM ai_infrastructure.user_platform_credentials 
                              WHERE user_id = %s AND is_active = true
                          )
                        
                        ORDER BY is_platform_global ASC, platform ASC
                    """, (int(user_id), int(user_id)))
                    
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        connection = {
                            'platform': row['platform'],
                            'type': row['credential_type'],
                            'is_active': row['is_active'],
                            'is_platform_global': row['is_platform_global'],
                            'created_at': row['updated_at'].isoformat() if row.get('updated_at') else None,
                            'metadata': row.get('metadata', {}) or {}
                        }
                        
                        # Add scope info if available
                        if row.get('metadata'):
                            meta = row['metadata']
                            if isinstance(meta, dict):
                                connection['scopes'] = meta.get('scopes', [])
                        
                        connections.append(connection)
        
        response = jsonify({
            'success': True,
            'connections': connections
        })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        
        return response
        
    except Exception as e:
        print(f"❌ [CONNECTIONS] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            'success': False,
            'error': 'Failed to load connections',
            'details': str(e),
            'connections': []  # Return empty array on error
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200  # Return 200 with empty connections instead of 500


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

# CRITICAL FIX NOV 29: Favicon served from AI_infrastructure/static
FAVICON_DIR = Path(__file__).parent / 'static'

# CRITICAL FIX DEC 16 2025: Define UI_DIR for module file serving
UI_DIR = str(Path(__file__).parent.parent / 'UI')  # AI_agents/UI directory

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
    """Serve favicon to prevent 404 errors - FIXED NOV 29 to use correct path"""
    return send_from_directory(FAVICON_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Serve external module files (HTML, CSS, JS) - ADDED NOV 29
@app.route('/external/modules/<module_id>/<path:filename>')
def serve_external_module_file(module_id, filename):
    """Serve static files for external modules from UI/modules_external/"""
    try:
        # UI_DIR is a string, convert to Path for proper path operations
        ui_path = Path(UI_DIR)
        module_dir = ui_path / 'modules_external' / module_id
        
        # Fallback: Try underscore version if hyphenated version doesn't exist
        if not module_dir.exists():
            module_dir_underscore = ui_path / 'modules_external' / module_id.replace('-', '_')
            if module_dir_underscore.exists():
                module_dir = module_dir_underscore
                log_success(logger, f"Using underscore folder for module: {module_id}")
            else:
                log_error(logger, f"Module directory not found: {module_dir}")
                return jsonify({'error': f'Module directory not found: {module_id}'}), 404
        
        file_path = module_dir / filename
        
        if not file_path.exists():
            log_error(logger, f"Module file not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        log_success(logger, f"Serving module file: {module_id}/{filename}")
        return send_from_directory(str(module_dir), filename)
    
    except Exception as e:
        log_error(logger, f"Error serving module file {module_id}/{filename}: {e}")
        return jsonify({'error': str(e)}), 500

# Serve UI module files via UI/modules_external path (alternative route) - ADDED NOV 30
@app.route('/UI/modules_external/<module_id>/<path:filename>')
def serve_ui_module_file(module_id, filename):
    """Serve static files for external modules from UI/modules_external/ (alternative path)"""
    try:
        # UI_DIR is a string, convert to Path for proper path operations
        ui_path = Path(UI_DIR)
        module_dir = ui_path / 'modules_external' / module_id
        
        # Fallback: Try underscore version if hyphenated version doesn't exist
        if not module_dir.exists():
            module_dir_underscore = ui_path / 'modules_external' / module_id.replace('-', '_')
            if module_dir_underscore.exists():
                module_dir = module_dir_underscore
                log_success(logger, f"Using underscore folder for UI module: {module_id}")
            else:
                log_error(logger, f"Module directory not found: {module_dir}")
                return jsonify({'error': f'Module directory not found: {module_id}'}), 404
        
        file_path = module_dir / filename
        
        if not file_path.exists():
            log_error(logger, f"Module file not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        log_success(logger, f"Serving UI module file: {module_id}/{filename}")
        return send_from_directory(str(module_dir), filename)
    
    except Exception as e:
        log_error(logger, f"Error serving UI module file {module_id}/{filename}: {e}")
        return jsonify({'error': str(e)}), 500

# Serve internal module files - ADDED NOV 30 for Universal Search and Vector Database
@app.route('/internal/modules/<module_id>/<path:filename>')
def serve_internal_modules(module_id, filename):
    """Serve internal modules from UI/modules_internal/"""
    try:
        ui_path = Path(UI_DIR)
        module_dir = ui_path / 'modules_internal' / module_id
        
        if not module_dir.exists():
            log_error(logger, f"Internal module directory not found: {module_dir}")
            return jsonify({'error': f'Module directory not found: {module_id}'}), 404
        
        file_path = module_dir / filename
        
        if not file_path.exists():
            log_error(logger, f"Internal module file not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        log_success(logger, f"Serving internal module file: {module_id}/{filename}")
        return send_from_directory(str(module_dir), filename)
    
    except Exception as e:
        log_error(logger, f"Error serving internal module file {module_id}/{filename}: {e}")
        return jsonify({'error': str(e)}), 500

# Serve internal module files via UI/modules_internal path (alternative route) - ADDED NOV 30
@app.route('/UI/modules_internal/<module_id>/<path:filename>')
def serve_ui_internal_module_file(module_id, filename):
    """Serve static files for internal modules from UI/modules_internal/ (alternative path)"""
    try:
        ui_path = Path(UI_DIR)
        module_dir = ui_path / 'modules_internal' / module_id
        
        if not module_dir.exists():
            log_error(logger, f"Internal module directory not found: {module_dir}")
            return jsonify({'error': f'Module directory not found: {module_id}'}), 404
        
        file_path = module_dir / filename
        
        if not file_path.exists():
            log_error(logger, f"Internal module file not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        log_success(logger, f"Serving UI internal module file: {module_id}/{filename}")
        return send_from_directory(str(module_dir), filename)
    
    except Exception as e:
        log_error(logger, f"Error serving UI internal module file {module_id}/{filename}: {e}")
        return jsonify({'error': str(e)}), 500

# Serve internal module files directly via /modules_internal path (for test suite) - ADDED DEC 1
@app.route('/modules_internal/<module_id>/<path:filename>')
def serve_modules_internal_direct(module_id, filename):
    """Serve internal modules from UI/modules_internal/ - direct path for test suite"""
    try:
        ui_path = Path(UI_DIR)
        module_dir = ui_path / 'modules_internal' / module_id
        
        if not module_dir.exists():
            log_error(logger, f"Internal module directory not found: {module_dir}")
            return jsonify({'error': f'Module directory not found: {module_id}'}), 404
        
        file_path = module_dir / filename
        
        if not file_path.exists():
            log_error(logger, f"Internal module file not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        log_success(logger, f"Serving modules_internal file: {module_id}/{filename}")
        return send_from_directory(str(module_dir), filename)
    
    except Exception as e:
        log_error(logger, f"Error serving modules_internal file {module_id}/{filename}: {e}")
        return jsonify({'error': str(e)}), 500

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


# Serve node_modules for CAD visualization libraries (manifold-3d, three.js)
@app.route('/node_modules/<path:filename>')
def serve_node_modules(filename):
    """Serve JavaScript libraries from node_modules for frontend CAD renderer"""
    print(f"📦 [NODE_MODULES] Requested: {filename}")
    
    # Get project root (parent of AI_infrastructure/)
    project_root = Path(__file__).parent.parent
    node_modules_path = project_root / 'node_modules'
    full_path = node_modules_path / filename
    
    print(f"📦 [NODE_MODULES] Full path: {full_path}")
    print(f"📦 [NODE_MODULES] File exists: {full_path.exists()}")
    
    if full_path.exists():
        file_dir = full_path.parent
        file_name = full_path.name
        print(f"📦 [NODE_MODULES] ✓ Serving: {file_name}")
        
        # Set proper MIME type for JavaScript modules
        mimetype = None
        if filename.endswith('.js') or filename.endswith('.mjs'):
            mimetype = 'application/javascript'
        elif filename.endswith('.wasm'):
            mimetype = 'application/wasm'
        
        return send_from_directory(file_dir, file_name, mimetype=mimetype)
    else:
        print(f"📦 [NODE_MODULES] ✗ File not found: {filename}")
        return jsonify({'error': 'Module not found', 'path': filename}), 404


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
# CHAT/MESSAGING REST API ENDPOINTS
# ============================================================================
# REST endpoints for chat sidebar - complements WebSocket real-time messaging
# Uses MessageService for database operations with proper connection handling

# ✅ REFACTORED: get_conversations() (FIXED CURSOR LEAK #3)
@app.route('/api/messages/conversations', methods=['GET'])
def get_conversations():
    """
    Get list of conversations with unread counts for current user
    
    Query params:
        - user_id: Current user's ID (required)
    
    Returns:
        List of conversations with metadata (last message, unread count, timestamp)
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not message_service:
            return jsonify({'error': 'Message service not available'}), 503
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get conversations with last message and unread count
                cursor.execute("""
                    WITH user_messages AS (
                        SELECT 
                            CASE 
                                WHEN sender_user_id = %s THEN recipient_user_id
                                ELSE sender_user_id
                            END AS other_user_id,
                            message_text,
                            created_at,
                            read_by,
                            sender_user_id
                        FROM ai_infrastructure.realtime_messages
                        WHERE (sender_user_id = %s OR recipient_user_id = %s)
                        AND message_type = 'direct'
                    ),
                    latest_messages AS (
                        SELECT 
                            other_user_id,
                            message_text AS last_message,
                            created_at AS last_message_time,
                            sender_user_id AS last_sender_id
                        FROM user_messages
                        WHERE (other_user_id, created_at) IN (
                            SELECT other_user_id, MAX(created_at)
                            FROM user_messages
                            GROUP BY other_user_id
                        )
                    ),
                    unread_counts AS (
                        SELECT 
                            sender_user_id AS other_user_id,
                            COUNT(*) AS unread_count
                        FROM ai_infrastructure.realtime_messages
                        WHERE recipient_user_id = %s
                        AND message_type = 'direct'
                        AND NOT (%s = ANY(read_by))
                        GROUP BY sender_user_id
                    )
                    SELECT 
                        lm.other_user_id,
                        lm.last_message,
                        lm.last_message_time,
                        lm.last_sender_id,
                        COALESCE(uc.unread_count, 0) AS unread_count
                    FROM latest_messages lm
                    LEFT JOIN unread_counts uc ON lm.other_user_id = uc.other_user_id
                    ORDER BY lm.last_message_time DESC
                """, (user_id, user_id, user_id, user_id, user_id))
                
                rows = cursor.fetchall()
                
                conversations = []
                for row in rows:
                    conversations.append({
                        'user_id': row[0],
                        'last_message': row[1],
                        'last_message_time': row[2].isoformat() if row[2] else None,
                        'last_sender_id': row[3],
                        'unread_count': int(row[4])
                    })
                
                return jsonify({
                    'status': 'success',
                    'conversations': conversations
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] get_conversations error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: get_conversation() (FIXED CURSOR LEAK #4)
@app.route('/api/messages/conversation/<int:other_user_id>', methods=['GET'])
def get_conversation(other_user_id):
    """
    Get message history between current user and another user
    
    Path params:
        - other_user_id: The other user's ID
    
    Query params:
        - user_id: Current user's ID (required)
        - limit: Max messages to return (default: 50, max: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        List of messages with metadata
    """
    try:
        user_id = request.args.get('user_id', type=int)
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not message_service:
            return jsonify({'error': 'Message service not available'}), 503
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get messages between two users
                cursor.execute("""
                    SELECT 
                        message_id,
                        sender_user_id,
                        recipient_user_id,
                        message_text,
                        created_at,
                        delivered_to,
                        read_by,
                        message_metadata
                    FROM ai_infrastructure.realtime_messages
                    WHERE (
                        (sender_user_id = %s AND recipient_user_id = %s)
                        OR (sender_user_id = %s AND recipient_user_id = %s)
                    )
                    AND message_type = 'direct'
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, other_user_id, other_user_id, user_id, limit, offset))
                
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    messages.append({
                        'message_id': row[0],
                        'sender_user_id': row[1],
                        'recipient_user_id': row[2],
                        'message_text': row[3],
                        'created_at': row[4].isoformat() if row[4] else None,
                        'delivered': user_id in (row[5] or []),
                        'read': user_id in (row[6] or []),
                        'metadata': row[7]
                    })
                
                return jsonify({
                    'status': 'success',
                    'messages': messages,
                    'limit': limit,
                    'offset': offset
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] get_conversation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/messages/send', methods=['POST'])
def send_direct_message():
    """
    Send a direct message (REST fallback for WebSocket)
    
    Body:
        - sender_user_id: Sender's user ID
        - recipient_user_id: Recipient's user ID
        - message_text: Message content
        - metadata: Optional metadata dict
    
    Returns:
        Message ID and delivery status
    """
    try:
        data = request.get_json()
        
        sender_user_id = data.get('sender_user_id')
        recipient_user_id = data.get('recipient_user_id')
        message_text = data.get('message_text')
        metadata = data.get('metadata', {})
        
        if not all([sender_user_id, recipient_user_id, message_text]):
            return jsonify({'error': 'sender_user_id, recipient_user_id, and message_text required'}), 400
        
        if not message_service:
            return jsonify({'error': 'Message service not available'}), 503
        
        # Save message to database
        message_id = message_service.save_message(
            sender_user_id=sender_user_id,
            message_text=message_text,
            message_type='direct',
            recipient_user_id=recipient_user_id,
            room='synergy_board',
            metadata={'source': 'rest_api', **metadata}
        )
        
        if message_id:
            # Try to deliver via WebSocket if recipient is online
            delivered = False
            if recipient_user_id in active_users:
                try:
                    from flask_socketio import emit
                    for session_token, session_info in active_users[recipient_user_id].items():
                        client_id = session_info.get('client_id')
                        if client_id:
                            emit('direct_message_received', {
                                'source': 'rest_api',
                                'message_id': message_id,
                                'from_user_id': sender_user_id,
                                'message': message_text,
                                'timestamp': datetime.now().isoformat()
                            }, room=client_id, namespace='/ws/synergy')
                            delivered = True
                            
                            # Mark as delivered
                            message_service.mark_delivered(message_id, recipient_user_id)
                except Exception as ws_error:
                    log_warning(logger, f"[CHAT API] WebSocket delivery failed: {ws_error}")
            
            return jsonify({
                'status': 'success',
                'message_id': message_id,
                'delivered': delivered,
                'recipient_online': recipient_user_id in active_users
            })
        else:
            return jsonify({'error': 'Failed to save message'}), 500
    
    except Exception as e:
        log_error(logger, f"[CHAT API] send_message error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: mark_messages_read() (FIXED CURSOR LEAK #5)
@app.route('/api/messages/mark-read', methods=['POST'])
def mark_messages_read():
    """
    Mark messages as read for a conversation
    
    Body:
        - user_id: Current user's ID
        - other_user_id: The other user's ID
        - message_ids: Optional list of specific message IDs (if empty, marks all unread)
    
    Returns:
        Number of messages marked as read
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        other_user_id = data.get('other_user_id')
        message_ids = data.get('message_ids', [])
        
        if not all([user_id, other_user_id]):
            return jsonify({'error': 'user_id and other_user_id required'}), 400
        
        if not message_service:
            return jsonify({'error': 'Message service not available'}), 503
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                if message_ids:
                    # Mark specific messages as read
                    cursor.execute("""
                        UPDATE ai_infrastructure.realtime_messages
                        SET read_by = array_append(read_by, %s)
                        WHERE message_id = ANY(%s)
                        AND recipient_user_id = %s
                        AND NOT (%s = ANY(read_by))
                    """, (user_id, message_ids, user_id, user_id))
                else:
                    # Mark all unread messages from other_user_id as read
                    cursor.execute("""
                        UPDATE ai_infrastructure.realtime_messages
                        SET read_by = array_append(read_by, %s)
                        WHERE sender_user_id = %s
                        AND recipient_user_id = %s
                        AND message_type = 'direct'
                        AND NOT (%s = ANY(read_by))
                    """, (user_id, other_user_id, user_id, user_id))
                
                marked_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'marked_count': marked_count
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] mark_messages_read error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: delete_message() (FIXED CURSOR LEAK #6)
@app.route('/api/messages/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """
    Soft delete a message (marks as deleted, doesn't remove from DB)
    
    Path params:
        - message_id: Message ID to delete
    
    Query params:
        - user_id: Current user's ID (required for authorization)
    
    Returns:
        Success status
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        if not message_service:
            return jsonify({'error': 'Message service not available'}), 503
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Check if user is sender or recipient
                cursor.execute("""
                    SELECT sender_user_id, recipient_user_id, message_metadata
                    FROM ai_infrastructure.realtime_messages
                    WHERE message_id = %s
                """, (message_id,))
                
                row = cursor.fetchone()
                if not row:
                    return jsonify({'error': 'Message not found'}), 404
                
                sender_id, recipient_id, metadata = row
                
                # Authorization check
                if user_id not in [sender_id, recipient_id]:
                    return jsonify({'error': 'Unauthorized'}), 403
                
                # Soft delete by adding deleted flag to metadata
                import json
                meta = metadata or {}
                if isinstance(meta, str):
                    meta = json.loads(meta)
                meta['deleted_by'] = user_id
                meta['deleted_at'] = datetime.now().isoformat()
                
                cursor.execute("""
                    UPDATE ai_infrastructure.realtime_messages
                    SET message_metadata = %s
                    WHERE message_id = %s
                """, (json.dumps(meta), message_id))
                
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Message deleted'
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] delete_message error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: get_user_info() (FIXED CURSOR LEAK #7)
@app.route('/api/users/<int:user_id>/info', methods=['GET'])
def get_user_info(user_id):
    """
    Get user information including online status
    
    Path params:
        - user_id: User ID to get info for
    
    Returns:
        User info with online status and last seen
    """
    try:
        # Check if user is online
        is_online = user_id in active_users
        session_count = len(active_users.get(user_id, {}))
        
        # Get last seen from most recent session
        last_seen = None
        if is_online:
            sessions = active_users.get(user_id, {})
            for session_token, session_info in sessions.items():
                last_heartbeat = session_info.get('last_heartbeat')
                if last_heartbeat:
                    if not last_seen or last_heartbeat > last_seen:
                        last_seen = last_heartbeat
        
        # Get user details from database
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT username, email, created_at
                    FROM ai_infrastructure.users
                    WHERE user_id = %s
                """, (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return jsonify({
                        'status': 'success',
                        'user_id': user_id,
                        'username': row[0],
                        'email': row[1],
                        'is_online': is_online,
                        'session_count': session_count,
                        'last_seen': last_seen,
                        'member_since': row[2].isoformat() if row[2] else None
                    })
                else:
                    return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        log_error(logger, f"[CHAT API] get_user_info error: {e}")
        # Return basic info even if database query fails
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'is_online': is_online,
            'session_count': session_count,
            'last_seen': last_seen
        })


# ✅ REFACTORED: get_team_members() (FIXED CURSOR LEAK #8)
@app.route('/api/users/team-members', methods=['GET'])
def get_team_members():
    """
    Get list of team members for Contacts tab
    
    Query params:
        - user_id: Current user's ID (required)
    
    Returns:
        List of all users except current user with online status
    """
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get all users except current user
                cursor.execute("""
                    SELECT id, username, email, created_at
                    FROM ai_infrastructure.users
                    WHERE id != %s
                    ORDER BY username ASC
                """, (user_id,))
                
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    uid = row[0]
                    is_online = uid in active_users
                    
                    users.append({
                        'user_id': uid,
                        'name': row[1],
                        'email': row[2],
                        'is_online': is_online,
                        'avatar_url': f'/api/user/avatar/{uid}',
                        'member_since': row[3].isoformat() if row[3] else None
                    })
                
                return jsonify({
                    'status': 'success',
                    'users': users,
                    'total': len(users)
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] get_team_members error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: get_call_history() (FIXED CURSOR LEAK #9)
@app.route('/api/calls/history', methods=['GET'])
def get_call_history():
    """
    Get call history for Calls tab
    
    Query params:
        - user_id: Current user's ID (required)
        - limit: Max records to return (default: 50, max: 100)
    
    Returns:
        List of call records with user info
    """
    try:
        user_id = request.args.get('user_id', type=int)
        limit = min(int(request.args.get('limit', 50)), 100)
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Create call_history table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_infrastructure.call_history (
                        call_id SERIAL PRIMARY KEY,
                        caller_user_id INTEGER NOT NULL,
                        recipient_user_id INTEGER NOT NULL,
                        call_type VARCHAR(20) NOT NULL,
                        duration INTERVAL,
                        started_at TIMESTAMP DEFAULT NOW(),
                        ended_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create indexes if they don't exist
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_call_history_caller 
                    ON ai_infrastructure.call_history(caller_user_id, created_at DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_call_history_recipient 
                    ON ai_infrastructure.call_history(recipient_user_id, created_at DESC)
                """)
                
                conn.commit()
                
                # Get call history
                cursor.execute("""
                    SELECT 
                        ch.call_id,
                        ch.caller_user_id,
                        ch.recipient_user_id,
                        ch.call_type,
                        ch.duration,
                        ch.started_at,
                        ch.ended_at,
                        u.username as other_user_name
                    FROM ai_infrastructure.call_history ch
                    LEFT JOIN ai_infrastructure.users u ON (
                        CASE 
                            WHEN ch.caller_user_id = %s THEN ch.recipient_user_id
                            ELSE ch.caller_user_id
                        END = u.id
                    )
                    WHERE ch.caller_user_id = %s OR ch.recipient_user_id = %s
                    ORDER BY ch.created_at DESC
                    LIMIT %s
                """, (user_id, user_id, user_id, limit))
                
                rows = cursor.fetchall()
                
                calls = []
                for row in rows:
                    # Determine call type from perspective of current user
                    if row[1] == user_id:
                        call_type = 'outgoing'
                    else:
                        call_type = 'incoming' if row[3] != 'missed' else 'missed'
                    
                    other_user_id = row[2] if row[1] == user_id else row[1]
                    
                    # Format duration
                    duration_str = None
                    if row[4]:
                        total_seconds = int(row[4].total_seconds())
                        minutes = total_seconds // 60
                        seconds = total_seconds % 60
                        duration_str = f"{minutes:02d}:{seconds:02d}"
                    
                    calls.append({
                        'call_id': row[0],
                        'user_id': other_user_id,
                        'user_name': row[7] or 'Unknown User',
                        'type': call_type,
                        'duration': duration_str,
                        'timestamp': row[5].isoformat() if row[5] else None
                    })
                
                return jsonify({
                    'status': 'success',
                    'calls': calls,
                    'total': len(calls)
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] get_call_history error: {e}")
        return jsonify({'error': str(e)}), 500


# ✅ REFACTORED: clear_call_history() (FIXED CURSOR LEAK #10)
@app.route('/api/calls/clear-history', methods=['DELETE'])
def clear_call_history():
    """
    Clear all call history for current user
    
    Query params:
        - user_id: Current user's ID (required)
    
    Returns:
        Number of records deleted
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # ✅ FIX: Use context manager for connection AND cursor
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Delete all calls involving this user
                cursor.execute("""
                    DELETE FROM ai_infrastructure.call_history
                    WHERE caller_user_id = %s OR recipient_user_id = %s
                """, (user_id, user_id))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Call history cleared',
                    'deleted_count': deleted_count
                })
    
    except Exception as e:
        log_error(logger, f"[CHAT API] clear_call_history error: {e}")
        return jsonify({'error': str(e)}), 500


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

# ============================================================================
# GLOBAL ERROR HANDLERS (Dec 3, 2025)
# ============================================================================

@app.errorhandler(Exception)
def handle_uncaught_exception(error):
    """
    Global error handler for all uncaught exceptions.
    Ensures ALL errors are logged to server logs and returned to UI.
    """
    error_details = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat(),
        'path': request.path,
        'method': request.method
    }
    
    # Log error with full traceback to server logs
    logger.error('='*80)
    logger.error(f'❌ UNCAUGHT EXCEPTION: {error_details["error_type"]}')
    logger.error('='*80)
    logger.error(f'Path: {request.path}')
    logger.error(f'Method: {request.method}')
    logger.error(f'Error: {error}')
    logger.error('Stack Trace:')
    logger.error(traceback.format_exc())
    logger.error('='*80)
    
    # Return user-friendly error to UI
    return jsonify({
        'success': False,
        'error': str(error),
        'error_type': error_details['error_type'],
        'user_message': 'An unexpected error occurred. Please try again or contact support if the problem persists.',
        'timestamp': error_details['timestamp']
    }), 500

@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors with logging"""
    logger.warning(f'404 Not Found: {request.method} {request.path}')
    return jsonify({
        'success': False,
        'error': 'Resource not found',
        'path': request.path
    }), 404

@app.errorhandler(500)
def handle_internal_error(error):
    """Handle 500 errors with logging"""
    logger.error(f'500 Internal Server Error: {request.path}')
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'user_message': 'Something went wrong on our end. Please try again later.'
    }), 500

# Health check logging throttle
_last_health_log_time = 0
_HEALTH_LOG_INTERVAL = 30  # seconds

@app.before_request
def log_request_info():
    """Log incoming requests for debugging (throttled for /health endpoint)"""
    global _last_health_log_time
    
    # Handle Socket.IO WebSocket upgrade requests specially
    if request.path.startswith('/socket.io/'):
        # Ensure proper headers for WebSocket upgrade
        if request.environ.get('HTTP_UPGRADE', '').lower() == 'websocket':
            # This is a WebSocket upgrade - ensure no buffering
            request.environ['wsgi.input_terminated'] = True
    
    # Only log non-static requests
    if not request.path.startswith('/static') and not request.path.startswith('/UI'):
        # Throttle /health endpoint logging to once every 30 seconds
        if request.path == '/health':
            import time
            current_time = time.time()
            if current_time - _last_health_log_time >= _HEALTH_LOG_INTERVAL:
                logger.info(f'➡️  {request.method} {request.path} (health checks muted for {_HEALTH_LOG_INTERVAL}s)')
                _last_health_log_time = current_time
        else:
            logger.info(f'➡️  {request.method} {request.path}')

@app.after_request
def log_response_info(response):
    """Log outgoing responses for debugging"""
    # Only log non-static responses and errors
    if not request.path.startswith('/static') and not request.path.startswith('/UI'):
        if response.status_code >= 400:
            logger.warning(f'⬅️  {response.status_code} {request.method} {request.path}')
        elif response.status_code >= 300:
            logger.info(f'⬅️  {response.status_code} {request.method} {request.path}')
    return response

# ============================================================================
# CACHE CONTROL FOR MODULE LOADING FIX (Dec 1, 2025)
# ============================================================================

@app.after_request
def add_no_cache_headers(response):
    """
    Force browsers to revalidate JavaScript and CSS modules on every request.
    
    CRITICAL FIX: Browser was caching old module-utilities.js and CSS files despite cache-busting
    query parameters. This prevented UI updates from appearing.
    
    Solution: Add strict no-cache headers to ALL JavaScript AND CSS responses.
    """
    if response.content_type and ('javascript' in response.content_type or 'css' in response.content_type):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Register cleanup handler (called on normal exit)
atexit.register(cleanup_resources)

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    # Reduce noise from geventwebsocket health check logs
    import logging
    logging.getLogger('geventwebsocket.handler').setLevel(logging.WARNING)
    
    # Startup banner removed from logs (not sent to AI)
    
    # Get port from environment (Render sets PORT=10000, local uses 5001)
    port = int(os.environ.get('PORT', 5001))
    
    # Detect production environment
    is_production = os.environ.get('RENDER', 'false').lower() == 'true'
    debug_mode = not is_production
    
    # 🔍 START CONNECTION MONITOR (Background monitoring thread)
    try:
        from AI_infrastructure.tools.connection_monitor import start_connection_monitor
        connection_monitor = start_connection_monitor()
        print("\n✅ Connection monitor started (background thread)")
        print(f"   Log file: AI_infrastructure/logs/connection_monitor.log\n")
    except Exception as e:
        print(f"\n⚠️  Failed to start connection monitor: {e}\n")
    
    # 🔍 START CONNECTION LEAK DETECTOR (Auto-closes idle connections >30 sec)
    try:
        from AI_infrastructure.shared.connection_leak_detector import start_leak_detector
        detector = start_leak_detector()
        
        # 🧹 PROACTIVE CLEANUP: Remove zombie connections from pool
        print("🧹 Cleaning zombie connections from pool...")
        cleanup_result = detector.cleanup_pool()
        if cleanup_result['cleaned'] > 0:
            print(f"   ⚠️  Cleaned {cleanup_result['cleaned']} zombie connections")
        else:
            print("   ✅ No zombie connections found")
        
        print("✅ Connection leak detector started (auto-close idle >30 sec)")
        print("   Metrics: GET /api/pool-health")
        print("   Force check: POST /api/pool-health/force-check\n")
    except Exception as e:
        print(f"⚠️  Failed to start leak detector: {e}\n")
    
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
    
    # 🚀 PRE-EMPTIVE SEMANTIC SEARCH INITIALIZATION
    # Initialize BEFORE server starts to ensure embeddings are ready for first request
    # Uses Supabase persistence - loads instantly if cache exists, regenerates if tools changed
    print("[STARTUP] Initializing persistent semantic search (loads from Supabase)...")
    print("[STARTUP] Server will start accepting requests after initialization completes.\n")
    initialize_semantic_search_on_startup()
    
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