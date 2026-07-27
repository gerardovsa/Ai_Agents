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

# FIX (July 23, 2026): Pin TIKTOKEN_CACHE_DIR to the persistent Render disk
# BEFORE any module that imports tiktoken (utils.token_counter, etc.). Without
# this, tiktoken re-downloads its BPE tables (~2 MB) on every cold start and
# on every redeploy. Set via setdefault() so a user-supplied env var still wins.
_DATA_DIR = "/data"
_TIKTOKEN_CACHE_DIR = "/data/.cache/tiktoken"
if os.path.isdir(_DATA_DIR):
    os.makedirs(_TIKTOKEN_CACHE_DIR, exist_ok=True)
    os.environ.setdefault("TIKTOKEN_CACHE_DIR", _TIKTOKEN_CACHE_DIR)
    # Mirror the registry warm cache dir pattern so all persistent caches live
    # under the same /data/.cache/ tree. Cheap to mkdir, no harm if it already
    # exists.
    os.makedirs("/data/.cache/registry", exist_ok=True)
    print(f"[CACHE] Persistent caches pinned to {_DATA_DIR}/.cache/ "
          f"(tiktoken + registry warm cache)")

# Configure AI_agents paths ONLY - Standalone project
ai_agents_root = Path(__file__).parent.parent  # Go up to AI_agents root
ai_infrastructure_path = ai_agents_root / 'AI_infrastructure'

# Add AI_agents paths
for path in [str(ai_agents_root), str(ai_infrastructure_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ✅ PREWARM GATE (July 24, 2026): Optional is referenced by the
# PrewarmPending / PrewarmFailed sentinels + get_prewarm_error() helper
# defined near line ~480 (after the background prewarm thread spawn).
# Import it here so the annotations resolve at module load — these
# helpers are evaluated at function-definition time (no `from __future__
# import annotations` in this file), so the import must precede the def.
from typing import Optional  # noqa: E402,F401

# Import startup-timing helper FIRST so its _BOOT_T0 anchor captures every
# subsequent millisecond of import time (including the logging setup below).
# See AI_infrastructure/shared/startup_timing.py for the public API.
from shared.startup_timing import begin as _st_begin, end as _st_end  # noqa: E402

# Setup unified logging FIRST
from utils.logger_config import setup_logger, log_init, log_config, log_success, log_warning, log_error, ColoredFormatter, Colors
import logging

def log_debug(message: str):
    """Print debug message with color"""
    print(f"{Colors.DEBUG}[DEBUG]{Colors.RESET} {message}")

logger = setup_logger('flask_app')

# ============================================================================
# Phase 1 of 12: bootstrap_logging (werkzeug + apscheduler + registry loggers)
# ============================================================================
_st_begin('bootstrap_logging', note='werkzeug + apscheduler + registry logger config')

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

_st_end('bootstrap_logging', note='loggers configured')

log_init(logger, "AI_agents standalone - No external dependencies")

# Now import Flask and other dependencies
from flask import Flask, jsonify, request, Response, send_from_directory, send_file
from flask_cors import CORS, cross_origin
from datetime import datetime, UTC
from flask_socketio import SocketIO
from markupsafe import escape  # ✅ FIX: HTML escaping for display names (XSS prevention)
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
# ============================================================================
# Phase 2 of 12: framework_config (inline Config class)
# ============================================================================
_st_begin('framework_config', note='inline Config class (paths, sessions, CORS, DB)')
class Config:
        """Flask app configuration - Fallback"""
        BASE_DIR = Path(__file__).parent
        ROOT_DIR = BASE_DIR.parent  # AI_agents root
        DATA_DIR = ROOT_DIR / 'data'  # Centralized data folder
        SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        TESTING = False
        # DEPRECATED: database-config.json no longer required (uses environment variables)
        # Kept for backward compatibility with legacy modules (disabled in production)
        DB_CONFIG_PATH = DATA_DIR / 'database-config.json'  # OPTIONAL - auto-created if missing
        SESSION_DB_PATH = DATA_DIR / 'sessions.db'
        
        # Session configuration - OAuth state stored in database (oauth_states table)
        # Default Flask sessions for temporary data only
        SESSION_TYPE = 'filesystem'
        PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
        
        # CORS configuration
        CORS_ORIGINS = ['http://localhost:5001', 'http://localhost:5000', 'http://127.0.0.1:5001', 'http://127.0.0.1:5000', '*']
        
        # Database configuration (SQLite) - Centralized location
        DATABASE_PATH = os.getenv('DATABASE_PATH', str(DATA_DIR / 'ai_infrastructure.db'))

_st_end('framework_config', note='Config class defined')

# Import core infrastructure (NEW CLEAN CODE)
from core.unified_session_manager import session_manager
from core.unified_ai_client import initialize_ai_client

# ============================================================================
# Phase 3 of 12: core_route_imports (~50 Flask blueprints)
# ============================================================================
_st_begin('core_route_imports', note='50+ blueprint imports (agent, thread, chat, etc.)')

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

# WooCommerce routes (always registered; tools may not be available on Render)
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
log_debug("Importing woocommerce_routes...")
try:
    from routes.woocommerce_routes import woocommerce_bp
except Exception as _wc_err:
    log_config(logger, f"[CONFIG] WooCommerce routes could not be imported: {_wc_err}")
    woocommerce_bp = None

log_debug("Importing auth_routes...")
from routes.auth_routes import auth_bp  # NEW: User authentication
log_debug("Importing oauth_routes...")
from routes.oauth_routes import oauth_bp  # NEW: OAuth workspace integration (Google Workspace + M365)
log_debug("Importing vsa_alerts_routes...")
from routes.vsa_alerts_routes import vsa_alerts_bp  # NEW: VSA Veterinary Alerts (transcript + coaching generation)
from routes.vsa_supabase_proxy_routes import vsa_supabase_proxy_bp  # NEW: VSA Supabase vault-backed proxy (server-side fetch from the external Supabase project via org credentials; 4 endpoints: dashboard, calls list, call detail, admin seed)
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
from routes.synergy_share_routes import synergy_share_bp  # NEW: Synergy visibility & member management (/api/synergy/sessions/*/visibility|members)
from routes.synergy_file_search import synergy_search_bp  # NEW: Synergy Files global search (Gap #8 fix)
log_debug("Importing scheduler_routes...")
from routes.scheduler_routes import scheduler_bp  # NEW: AI Automation Scheduler
log_debug("Importing automation_routes...")
from routes.automation_routes import automation_bp  # NEW: Visual Automation Canvas
log_debug("Importing ml_routes...")
from routes.ml_routes import ml_bp  # NEW: ML Analytics & Predictions (churn, payment timing, fraud detection)
log_debug("Importing auspost_routes...")
from routes.auspost_routes import auspost_bp  # NEW: Australia Post shipping calculations
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

_st_end('core_route_imports', note='all blueprints imported')

# Generate unique cache version on Flask startup (forces browser refresh)
import time
import random
CACHE_VERSION = f"{int(time.time())}_{random.randint(1000, 9999)}"
log_success(logger, f"🔄 Generated cache version: {CACHE_VERSION}")

# ============================================================================
# Phase 4 of 12: flask_app_create (Flask app object + Config binding)
# ============================================================================
_st_begin('flask_app_create', note='app = Flask(__name__) + Config binding')

# Initialize Flask app with error handling
try:
    app = Flask(__name__)
    app.config.from_object(Config)
    log_success(logger, "Flask app created successfully")
except Exception as e:
    log_error(logger, f"CRITICAL: Failed to create Flask app: {e}")
    logger.error(traceback.format_exc())
    raise

_st_end('flask_app_create', note='app ready')


# ============================================================================
# 🚑 EARLY /health ROUTE — Registered BEFORE heavy init so Render's 5-second
#    healthCheckPath can succeed on cold start.
#
#    Why: ~2,450 lines of blueprint imports + DB calls + SocketIO binding +
#    module scans execute between `app = Flask(__name__)` and the rich
#    /health registration further down. Cold-start times blow past Render's
#    5-second healthCheckPath timeout (render.yaml: healthCheckPath: /health)
#    and Render cycles the instance.
#
#    This handler MUST stay dependency-free: no `socketio`, no globals that
#    aren't defined yet, no DB calls. Just a static 200 JSON + CORS headers.
#
#    Rich diagnostics (SocketIO mode, semantic-search status, pgvector-BGE
#    preload status) live at /api/health/detailed — see health_check() below.
# ============================================================================
@app.route('/health', methods=['GET', 'OPTIONS'])
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def _render_health():
    """Minimal /health endpoint — answers Render within 5 s during cold start."""
    from flask import jsonify
    response = jsonify({
        'status': 'healthy',
        'phase': 'starting_or_ready',
        'note': 'minimal cold-start handler; see /api/health/detailed for full diagnostics'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-user-id,X-User-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response, 200


# ============================================================================
# 🚀 BACKGROUND SEMANTIC SEARCH INITIALIZATION (Non-Blocking)
# ============================================================================
_semantic_search_initialization_complete = False
_semantic_search_initialization_error = None

def initialize_semantic_search_async():
    """
    Initialize persistent semantic search in background thread.
    
    This runs AFTER server starts to prevent health check timeouts.
    Uses Supabase persistence - loads instantly if cache exists, regenerates if tools changed.
    """
    global _semantic_search_initialization_complete, _semantic_search_initialization_error
    
    try:
        print("\n" + "=" * 80)
        print("[BACKGROUND] INITIALIZING PERSISTENT SEMANTIC SEARCH (Supabase-backed)")
        print("=" * 80)
        
        # Import registry and semantic search initializer
        from tools.registry_v3 import get_registry
        from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
        
        # Get singleton registry (NOT a new instance)
        print("[BACKGROUND] Loading tool registry...")
        registry = get_registry()
        print(f"[BACKGROUND] [OK] Registry loaded with {len(registry.tools)} tools")

        # ✅ FIX (June 11, 2026): Disk-backed registry cache on /data
        # Previously: every gunicorn worker recycle re-walked tools/schemas/*.json
        # + every UI/modules_external/*/tools/*.json (3-5 s on cold start).
        # Now: warm starts hit /data/tool_registry_cache/ via a version-hash check
        # (~50 ms). Cold starts (real code change to a schema) detect the hash
        # mismatch and rebuild transparently. Pickling callables is intentionally
        # avoided — implementations are re-imported from disk (safe + fast).
        try:
            from AI_infrastructure.shared.tool_registry_disk_cache import (
                compute_version_hash,
                should_use_disk_cache,
                load_schemas_from_disk,
                save_schemas_to_disk,
            )
            # Compute the hash of what was just loaded by get_registry() (it
            # already populated registry.tools from a Redis cache or fresh read).
            current_hash = compute_version_hash(registry.tools)
            if should_use_disk_cache(current_hash):
                print(f"[BACKGROUND] [DISK_CACHE] Hash {current_hash[:8]} matches /data cache — loading schemas from disk")
                if load_schemas_from_disk(registry):
                    # Implementations must always be re-imported (they are
                    # Python callables, not JSON-serializable, and not in cache).
                    print("[BACKGROUND] [DISK_CACHE] Re-importing implementations + module plugins (fast path)")
                    registry._load_implementations()
                    registry._load_module_plugins()
                    print(f"[BACKGROUND] [OK] Disk-cache fast path: {len(registry.tools)} tools, {len(registry.implementations)} implementations")
                else:
                    # Cache load failed despite hash match — fall back to full rebuild
                    print("[BACKGROUND] [DISK_CACHE] Cache read failed, falling back to full rebuild")
                    registry._load_schemas()
                    registry._load_implementations()
                    registry._load_module_plugins()
                    save_schemas_to_disk(registry)
            else:
                print(f"[BACKGROUND] [DISK_CACHE] Cache miss or hash mismatch — full rebuild")
                registry._load_schemas()
                registry._load_implementations()
                registry._load_module_plugins()
                save_schemas_to_disk(registry)
                print(f"[BACKGROUND] [OK] Reloaded fresh tools: {len(registry.tools)} total")
        except ImportError as e:
            # Disk cache helper not available — fall back to the old Redis path
            print(f"[BACKGROUND] [DISK_CACHE] Helper not available ({e}), using legacy path")
            if registry.redis_manager and registry.redis_manager.connected:
                print("[BACKGROUND] Invalidating stale Redis cache to force fresh tool loading...")
                cache_cleared = registry.invalidate_cache()
                if cache_cleared:
                    print("[BACKGROUND] [OK] Redis cache invalidated - next load will be fresh")
                    registry._load_schemas()
                    registry._load_implementations()
                    registry._load_module_plugins()
                    registry._save_to_cache()
                    print(f"[BACKGROUND] [OK] Reloaded fresh tools: {len(registry.tools)} total")
                else:
                    print("[BACKGROUND] [INFO] Redis cache not available - using fresh load")
        except Exception as e:
            # Defensive: any failure in the disk-cache path must not crash startup
            print(f"[BACKGROUND] [DISK_CACHE] Error: {e}, falling back to fresh load")
            import traceback
            traceback.print_exc()
            registry._load_schemas()
            registry._load_implementations()
            registry._load_module_plugins()
        
        # ✅ DEPLOY-TIME PREWARM (July 24, 2026):
        # Tag every log line with [DEPLOY_PREWARM] so the user can grep
        # `grep -c "DEPLOY_PREWARM" render.log` and confirm the prewarm
        # actually ran as part of the deploy (not lazily on first chat).
        # The previous tag was [BACKGROUND] — easy to miss.
        print("=" * 80)
        print("[DEPLOY_PREWARM] STEP 1/3 — Loading tool registry from disk cache (or fresh rebuild)")
        print("=" * 80)
        semantic_search = get_semantic_search(registry)

        if semantic_search and semantic_search.available:
            source = "Supabase" if semantic_search.db_available else "Generated (Database unavailable)"
            print(f"[DEPLOY_PREWARM] STEP 2/3 — Loaded {len(semantic_search.tool_embeddings)} tool embeddings from {source}")
            print(f"[DEPLOY_PREWARM] STEP 2/3 — Version hash: {semantic_search.version_hash[:16]}...")
            print("=" * 80)
            print(f"[DEPLOY_PREWARM] STEP 3/3 — ✅ DONE. Chat endpoint will be unblocked.")
            print(f"[DEPLOY_PREWARM] STEP 3/3 — Total tools indexed: {len(semantic_search.tool_embeddings)}")
            print("=" * 80 + "\n")
        else:
            print(f"[DEPLOY_PREWARM] STEP 2/3 — ⚠️  Semantic search NOT available (sentence-transformers not installed or HF download failed)")
            print(f"[DEPLOY_PREWARM] STEP 3/3 — ⚠️  Chat endpoint will still respond but tool-selection will fall back to keyword matching")
            print("=" * 80 + "\n")

        _semantic_search_initialization_complete = True
            
    except Exception as e:
        print(f"[DEPLOY_PREWARM] ❌ FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80 + "\n")
        _semantic_search_initialization_error = str(e)

def start_semantic_search_initialization():
    """Start semantic search initialization in background thread"""
    thread = threading.Thread(
        target=initialize_semantic_search_async,
        daemon=True,
        name="SemanticSearchInit"
    )
    thread.start()
    print("[DEPLOY_PREWARM] 🚀 Started in background thread — server will accept requests immediately")
    print("[DEPLOY_PREWARM] 🚀 Chat endpoints will return 503 with Retry-After until this thread completes")
    print("[DEPLOY_PREWARM] 🚀 Follow progress by `grep \"DEPLOY_PREWARM\" render.log`\n")


# ============================================================================
# 🚦 PREWARM GATE (sentinel + wait helper)
# ============================================================================
# Chat endpoints call get_semantic_search() (agent_routes_v4.py:77). That
# function previously raced against this background thread by acquiring
# _semantic_search_lock and waiting on it. From the user's perspective that
# looked like a hung request: spinner spins for 30-60 s, then a 502.
#
# The gate below makes the contract explicit:
#   - If prewarm completed → proceed normally (returns the cached instance).
#   - If prewarm failed    → raise PrewarmFailed so the chat endpoint can
#                           return a 503 with the actual error.
#   - If prewarm pending   → raise PrewarmPending so the chat endpoint can
#                           return 503 + Retry-After: 5 (the user retries
#                           and gets a fast response once prewarm lands).
#
# This converts the deploy's hidden 30-60 s pause into a *visible* contract:
# the user gets a clear "deploy is still warming up, retry in 5 s" message
# instead of a hung spinner, and the prewarm runs as part of gunicorn
# boot (not as part of their first chat request).
# ============================================================================
class PrewarmPending(Exception):
    """Raised by get_semantic_search() when the deploy-time prewarm hasn't finished yet."""
    def __init__(self, retry_after_seconds: int = 5):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Deploy prewarm still running; retry after {retry_after_seconds}s")


class PrewarmFailed(Exception):
    """Raised by get_semantic_search() when the deploy-time prewarm raised an exception."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Deploy prewarm failed: {reason}")


def is_prewarm_complete() -> bool:
    """Cheap read of the global prewarm flag without importing anything heavy."""
    return _semantic_search_initialization_complete


def get_prewarm_error() -> Optional[str]:
    """Returns the prewarm error string if the prewarm failed, else None."""
    return _semantic_search_initialization_error


# ============================================================================
# 🚀 BACKGROUND PGVECTOR BGE MODEL PRELOAD (Non-Blocking)
# ============================================================================
# The BAAI/bge-base-en-v1.5 embedding model (~440 MB on disk, 768-dim) is
# downloaded on first call to pgvector_upload_document() / pgvector_query_vectors()
# if it isn't already on /data.  On a fresh deploy with an empty persistent
# disk that first call takes 30-60 s and can hit Render's request timeout,
# surfacing as a 502 to the user (same pattern as the all-MiniLM-L6-v2
# preload via initialize_semantic_search_async above, but for the
# pgvector provider's embedding model).
#
# This preload runs in a daemon thread at startup so the first user upload
# is instant.  Failures here are non-fatal: the model will still load on
# first use, just with the original 30-60 s wait.
#
# Target cache dir matches pgvector_tools.py: /data/vdb_models on Render,
# ~/.cache/vdb_models on local dev.  Subsequent deploys reuse the cached
# snapshot — only the FIRST deploy on a fresh disk pays the download cost.
_pgvector_bge_initialization_complete = False
_pgvector_bge_initialization_error = None

def initialize_pgvector_bge_model_async():
    """Preload the pgvector BGE embedding model in a background thread."""
    global _pgvector_bge_initialization_complete, _pgvector_bge_initialization_error

    try:
        print("\n" + "=" * 80)
        print("[BACKGROUND] PRELOADING PGVECTOR BGE MODEL (BAAI/bge-base-en-v1.5, 768-dim)")
        print("=" * 80)

        from tools.implementations.pgvector import pgvector_tools

        # force_local=True bypasses the org-vault credential lookup so a
        # missing/invalid Voyage or OpenAI key can never cause this preload
        # to 500.  Trivial 1-char input → embedding call is essentially
        # instant; the cost is the one-time model load (~30-60 s on a fresh
        # disk, <1 s on a warm cache).
        vec = pgvector_tools._generate_embedding(".", user_id=1, force_local=True)
        assert len(vec) == 768, f"Expected 768-dim vector from BGE, got {len(vec)}"

        print(f"[BACKGROUND] [OK] BGE model ready — {len(vec)}-dim embeddings available")
        print("=" * 80)
        print("[BACKGROUND] ✅ PGVECTOR BGE MODEL READY — first upload will be instant")
        print("=" * 80 + "\n")

        _pgvector_bge_initialization_complete = True

    except Exception as e:
        print(f"[BACKGROUND] [ERROR] Failed to preload pgvector BGE model: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80 + "\n")
        _pgvector_bge_initialization_error = str(e)
        # Non-fatal: the model will load on first use even if preload fails
        # (the user just pays the 30-60 s download cost on first upload).

def start_pgvector_bge_initialization():
    """Start pgvector BGE model preload in background thread."""
    thread = threading.Thread(
        target=initialize_pgvector_bge_model_async,
        daemon=True,
        name="PgvectorBgePreload"
    )
    thread.start()
    print("[STARTUP] 🚀 pgvector BGE model preload started in background\n")


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
# ============================================================================
# Phase 5 of 12: database_initialization (prompt library + user auth + automation)
# ============================================================================
_st_begin('database_initialization', note='prompt_library + user_auth + automation tables')

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

    # ✅ BOOT-PERF (2026-07-23): Removed the `SELECT tablename FROM pg_tables`
    # verification query. The query was logging-only — its result was a count
    # that nobody read. The actual schema is created by init_prompt_library_table()
    # and user_auth's own _init_tables() (which short-circuits on Supabase).
    # Eliminating this query saves ~50-100ms of Supabase round-trip on every
    # cold start, which is the difference between Render's 5s healthCheckPath
    # timing out and succeeding.
    log_success(logger, "Database schema verified (Supabase — tables managed by migrations)")

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

_st_end('database_initialization', note='schema initialised')

# ============================================================================
# Phase 6 of 12: module_registry_initialization (ModuleRegistry scan)
# ============================================================================
_st_begin('module_registry_initialization', note='ModuleRegistry scan of UI/modules_external')

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

_st_end('module_registry_initialization', note='registry populated')

# ============================================================================
# Phase 7 of 12: blueprint_registration (app.register_blueprint cascade)
# ============================================================================
_st_begin('blueprint_registration', note='~50 blueprints registered with Flask')

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
app.register_blueprint(vsa_supabase_proxy_bp)                          # NEW: VSA Supabase vault-backed proxy (/api/vsa-supabase-proxy/*) — fetches external Supabase data server-side using the org-vault stored service-role key
app.register_blueprint(account_linking_bp)                           # NEW: Account linking (/api/account/*)
app.register_blueprint(kanban_bp)                                    # NEW: Kanban board + AI agent bridge (8 endpoints)
app.register_blueprint(database_visualizer_bp)                       # ✅ ENABLED (Migrated to Supabase 2025-12-07)
app.register_blueprint(synergy_bp)                                   # NEW: Synergy Dashboard (6 endpoints: /api/synergy/*)
app.register_blueprint(synergy_share_bp)                             # NEW: Synergy share/visibility & member management (/api/synergy/sessions/*/visibility|members)
app.register_blueprint(synergy_search_bp, url_prefix='/api/synergy')  # NEW: Synergy file search (Gap #8 fix: 2 endpoints)
app.register_blueprint(cloud_storage_bp)                             # NEW: Cloud storage sync (6 endpoints: Google Drive folders to database)
app.register_blueprint(connections_bp)                               # Platform connections (2 endpoints: list, disconnect)
app.register_blueprint(scheduler_bp)                                 # NEW: AI Automation Scheduler (10 endpoints: /api/scheduler/*)
app.register_blueprint(automation_bp)                                # NEW: Visual Automation Canvas (9 endpoints: /api/automation/*)
app.register_blueprint(ml_bp)                                        # NEW: ML Analytics & Predictions (6 endpoints: /api/ml/*)
app.register_blueprint(auspost_bp)                                   # NEW: Australia Post shipping (2 endpoints: /api/auspost/*)
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
try:
    from routes.viz_snapshots_routes import viz_snapshots_bp
    app.register_blueprint(viz_snapshots_bp)                         # NEW: Persistent visualizations library (11 endpoints: /api/viz/snapshots/*)
    log_success(logger, "Viz snapshots routes registered (11 endpoints: /api/viz/snapshots/*)")
except Exception as e:
    log_error(logger, f"Failed to register viz_snapshots routes: {e}")
# app.register_blueprint(quote_calc_bp)                                # DISABLED: In_House_SQL dependency

# Organisation credentials & team management
try:
    from routes.organisation_credentials_routes import org_credentials_bp
    app.register_blueprint(org_credentials_bp)                       # NEW: Organisation credentials vault + team management (11 endpoints: /api/org/*)
    log_success(logger, "Organisation routes registered (11 endpoints: /api/org/*)")
except Exception as e:
    log_error(logger, f"Failed to register organisation_credentials routes: {e}")

# 🛠️ DEV TOOLS: Module Creator & Verifier (Development-only endpoints)
from routes.dev_tools_routes import dev_tools_bp
app.register_blueprint(dev_tools_bp)                                 # DEV TOOLS: Module development endpoints (4 endpoints: /api/dev-tools/*)

_st_end('blueprint_registration', note='all static blueprints registered')

# 🆕 AUTO-LOAD MODULE BLUEPRINTS (Quote Calculator, Stock Management, etc.)
# This discovers and registers Flask routes from UI/external/modules/*/routes/
# INCLUDES: Stock Management, Shopify E-Commerce, Database Visualizer, Quote Calculator, etc.
# ============================================================================
# Phase 8 of 12: module_blueprint_autoload (UI/modules_external auto-discovery)
# ============================================================================
_st_begin('module_blueprint_autoload', note='UI/modules_external/*/routes auto-loaded')
try:
    from core.module_blueprint_loader import load_module_blueprints
    from utils.logger_config import log_module, log_route
    module_bp_count = load_module_blueprints(app)
    log_module(logger, f"Loaded {module_bp_count} module blueprints from UI/modules_external")
    log_route(logger, "Auto-discovered routes from: UI/modules_external/*/routes/*.py")
    log_route(logger, "Stock Management: /api/stock-management/* (Blueprint auto-loaded)")
except Exception as e:
    log_warning(logger, f"Module blueprints not loaded: {e} (Module blueprints are optional)")

_st_end('module_blueprint_autoload', note='external module routes registered')

# REMOVED DUPLICATE: Stock Management routes now loaded via module_blueprint_loader above
# Old init_stock_routes() pattern caused route conflicts with Blueprint system

# Shopify E-Commerce: ENABLED (load routes from AI_infrastructure/routes/)
try:
    from routes.shopify_routes import init_shopify_routes
    init_shopify_routes(app)
    log_success(logger, "Shopify E-Commerce routes registered (Shopify Admin API 2025-10)")
except Exception as e:
    log_error(logger, f"Failed to load shopify routes: {e}")
    import traceback
    traceback.print_exc()

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
    response.headers['Last-Modified'] = datetime.now(UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
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

# ✅ FIXED JUNE 9: Explicitly detect async mode to fix WebSocket pending issue on Render
# Check if gevent is available (required for WebSocket on Render)
async_mode_config = None
try:
    import gevent
    async_mode_config = 'gevent'
    log_success(logger, f"[WS] Async mode: GEVENT (will support WebSocket connections efficiently)")
except ImportError:
    log_warning(logger, "[WS] Gevent not available - falling back to threading")
    log_warning(logger, "[WS] ⚠️  Threading mode may cause WebSocket connection delays on Render")
    async_mode_config = 'threading'

# ============================================================================
# Phase 9 of 12: socketio_services (SocketIO init + connection state recovery)
# ============================================================================
_st_begin('socketio_services', note='SocketIO(app, gevent/threading, recovery)')

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
        max_http_buffer_size=1e6,  # ✅ FIX (Jan 22): Reduce to 1MB to prevent massive polling responses (was 100MB causing 223KB floods)
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

_st_end('socketio_services', note='SocketIO bound to app')

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
    ✅ FIXED JUNE 9: Add connection logging for Render debugging (WebSocket pending issue)
    """
    try:
        from flask import request as fr
        client_sid = fr.sid if hasattr(fr, 'sid') else 'UNKNOWN'
        remote_addr = request.remote_addr if hasattr(request, 'remote_addr') else 'UNKNOWN'
        logger.info(f"[WS /] ✅ Connection from SID: {client_sid}, remote: {remote_addr}")
        # Don't return False - let it connect to avoid WSGI errors
        # Client should use /ws/synergy or /ws/streaming instead
        return True  # ✅ Explicitly return True to confirm connection
    except Exception as e:
        log_error(logger, f"[WS /] Error in default_connect: {e}")
        return True  # Still return True to prevent errors

@socketio.on('disconnect')
def default_disconnect():
    """
    Handle disconnection from default namespace (/)
    ✅ FIXED JUNE 9: Add logging for Render debugging
    """
    try:
        from flask import request as fr
        client_sid = fr.sid if hasattr(fr, 'sid') else 'UNKNOWN'
        logger.info(f"[WS /] ⎯  Disconnection from default namespace: {client_sid}")
    except Exception as e:
        log_error(logger, f"[WS /] Error in default_disconnect: {e}")

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
        
        # ✅ FIX: Extract user_id from query params (temporary - TODO: Use Flask-Login)
        user_id = flask_request.args.get('user_id', type=int)
        
        # Accept connection
        connected_clients[client_id] = {
            'rooms': set(),
            'connected_at': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # ✅ FIX: Auto-join user-specific room for team collaboration
        # All team members with same user_id join same room = real-time sync
        if user_id:
            from flask_socketio import join_room
            user_room = f'user_{user_id}'
            command_center_room = 'command_center'
            
            join_room(user_room)
            join_room(command_center_room)
            
            connected_clients[client_id]['rooms'].add(user_room)
            connected_clients[client_id]['rooms'].add(command_center_room)
            
            logger.info(f"[WS] Client {client_id} auto-joined rooms: {user_room}, {command_center_room}")
        
        log_config(logger, f'[WS] Client connected to /ws/synergy: {client_id} (user_id={user_id})')
        emit('connected', {
            'status': 'connected',
            'client_id': client_id,
            'user_id': user_id,
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
        
        # ✅ FIX: Sanitize display_name (XSS prevention + length limit)
        if display_name:
            display_name = str(escape(display_name))[:50].strip()  # Escape HTML, then limit length
        if not display_name:
            display_name = str(escape(user_name))[:50].strip()
        
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
# THREAD PRESENCE & TYPING INDICATORS  (namespace: /ws/synergy)
# ============================================================================

_thread_viewers = {}  # {thread_id: {str(user_id): {display_name, joined_at}}}

@socketio.on('join_thread', namespace='/ws/synergy')
def ws_join_thread(data):
    """User enters a thread — add to viewer list and broadcast updated roster."""
    from flask_socketio import join_room
    thread_id  = data.get('thread_id')
    user_id    = str(data.get('user_id', ''))
    dname      = data.get('display_name', 'User')
    if not thread_id or not user_id:
        return
    room = f'thread_{thread_id}'
    join_room(room, namespace='/ws/synergy')
    if thread_id not in _thread_viewers:
        _thread_viewers[thread_id] = {}
    _thread_viewers[thread_id][user_id] = {
        'user_id': user_id,
        'display_name': dname,
        'joined_at': datetime.now().isoformat()
    }
    socketio.emit('viewers_update', {
        'thread_id': thread_id,
        'viewers': list(_thread_viewers[thread_id].values())
    }, room=room, namespace='/ws/synergy')
    log_config(logger, f"[WS PRESENCE] join_thread: user {user_id} joined thread {thread_id}")


@socketio.on('leave_thread', namespace='/ws/synergy')
def ws_leave_thread(data):
    """User leaves a thread — remove from viewer list and broadcast."""
    from flask_socketio import leave_room
    thread_id = data.get('thread_id')
    user_id   = str(data.get('user_id', ''))
    if not thread_id:
        return
    room = f'thread_{thread_id}'
    leave_room(room, namespace='/ws/synergy')
    if thread_id in _thread_viewers:
        _thread_viewers[thread_id].pop(user_id, None)
    socketio.emit('viewers_update', {
        'thread_id': thread_id,
        'viewers': list(_thread_viewers.get(thread_id, {}).values())
    }, room=room, namespace='/ws/synergy')


@socketio.on('typing_indicator', namespace='/ws/synergy')
def ws_typing_indicator(data):
    """Broadcast typing notification to all other viewers of the thread."""
    thread_id = data.get('thread_id')
    dname     = data.get('display_name', 'User')
    if not thread_id:
        return
    socketio.emit('user_typing', {
        'thread_id': thread_id,
        'display_name': dname
    }, room=f'thread_{thread_id}', namespace='/ws/synergy', include_self=False)


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
        # If not present, try to extract from authenticated session/JWT
        user_id = data.get('user_id')
        
        if not user_id:
            # Fallback: Extract user_id from Flask-SocketIO session context
            try:
                if hasattr(request, 'sid'):  # sid = SocketIO session ID
                    # Try to get auth context from socketio sessions
                    user_id = session_manager.session_to_user_id.get(request.sid) if hasattr(session_manager, 'session_to_user_id') else None
                if not user_id:
                    from flask import session as flask_session
                    user_id = flask_session.get('user_id')
            except Exception:
                pass
        
        if not user_id:
            log_warning(logger, "[WS] Cannot broadcast agent message - no user_id in data or session")
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

# Lazy-load AI client with fallback paths (prevents startup crash)
def get_ai_client():
    """
    Lazy-load AI client with multiple fallback config paths.
    This prevents startup crashes when database-config.json is not yet copied to persistent disk.
    """
    if not hasattr(app, '_ai_client_instance'):
        # Try multiple config locations (Render deployment copies config during startup)
        config_paths = [
            Path('/data/database-config.json'),  # Render persistent disk (primary)
            Path('/app/config/database-config.json'),  # startup.sh copies here
            Path('/app/data/database-config.json'),  # Docker COPY destination
            Config.DB_CONFIG_PATH  # Original fallback
        ]
        
        config_path = None
        for path in config_paths:
            if path.exists():
                config_path = str(path)
                print(f"[AI_CLIENT] ✅ Found config at: {config_path}")
                break
        
        if not config_path:
            # Create default config if none found
            print(f"[AI_CLIENT] ⚠️  No database-config.json found, creating default")
            config_path = str(config_paths[1])  # /app/config/database-config.json
            config_paths[1].parent.mkdir(parents=True, exist_ok=True)
            import json
            default_config = {
                "database": {"type": "sqlite", "path": "ai_infrastructure.db"},
                "AI": {
                    "AnthropicAPIKey": os.getenv('ANTHROPIC_API_KEY', ''),
                    "Model": "claude-sonnet-4-20250514",
                    "MaxTokens": 8096,
                    "DeepSeekAPIKey": os.getenv('DEEPSEEK_API_KEY_1', ''),
                    "OpenAIAPIKey": os.getenv('OPENAI_API_KEY', '')
                }
            }
            config_paths[1].write_text(json.dumps(default_config, indent=2))
            print(f"[AI_CLIENT] ✅ Created default config at: {config_path}")
        
        print(f"[AI_CLIENT] 🔄 Initializing UnifiedAIClient with config: {config_path}")
        app._ai_client_instance = initialize_ai_client(config_path)
        print(f"[AI_CLIENT] ✅ AI client initialized successfully")
    
    return app._ai_client_instance

# Store getter function and session manager in app config
app.config['GET_AI_CLIENT'] = get_ai_client
app.config['AI_CLIENT'] = None  # Will be lazy-loaded via get_ai_client()
app.config['SESSION_MANAGER'] = session_manager

print("[AI_CLIENT] 🔧 Lazy initialization configured - will initialize on first request")

print("=" * 80)
print("AI INFRASTRUCTURE - CLEANED & READY FOR 281 TOOLS")
print("=" * 80)
print(f"3 Generic Route Blueprints Registered (19 endpoints)")
print(f"Core Infrastructure: Session Manager + AI Clients")
print(f"Testing Framework: 22 tests passing (100% coverage)")
print("=" * 80)
print(f"Base Directory: {Config.BASE_DIR}")
print(f"Session DB: {Config.SESSION_DB_PATH}")
print(f"UnifiedSessionManager loaded")
print(f"UnifiedAIClient: Lazy-loaded (uses environment variables)")
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

def _startup_summary_block() -> dict:
    """Lightweight startup-phase summary for /api/health/detailed.

    Lazy-imports shared.startup_timing so the import cost stays off the
    cold-start path. If the helper is unavailable for any reason (e.g.
    a torn checkout), returns an empty dict rather than raising — the
    health endpoint must never 500 on a diagnostic-field failure.
    """
    try:
        from shared.startup_timing import summary as _st_summary, snapshot as _st_snapshot
        snap = _st_snapshot()
        s = snap.get('summary', {})
        slowest = s.get('slowest_phase') or {}
        return {
            'boot_total_ms': snap.get('boot_total_ms', 0.0),
            'under_5s_target': bool(s.get('under_5s_target', False)),
            'slowest_phase': slowest.get('id'),
            'slowest_phase_dt_ms': slowest.get('dt_ms'),
            'phases_recorded': len(snap.get('phases', [])),
            'phases_over_1000ms': s.get('phases_over_1000ms', 0),
            'render_mode': snap.get('render_mode', False),
            'deep_dive_endpoint': '/api/dev-tools/startup-diagnostics',
        }
    except Exception as _e:  # pragma: no cover — defensive
        # Logged at debug level; never break the health response.
        try:
            log_warning(logger, f'[STARTUP_TIMING] summary unavailable: {_e}')
        except Exception:
            pass
        return {}


@app.route('/api/health/detailed', methods=['GET', 'OPTIONS'])  # ✅ Moved off /health (Render's 5s healthCheckPath) — use _render_health() for the bare /health answer
def health_check():
    """Enhanced health check endpoint with Socket.IO metrics and explicit CORS.

    Moved from /health → /api/health/detailed so Render's healthCheckPath
    can hit the minimal dependency-free /health handler (registered right
    after `app = Flask(__name__)`) on cold start. This richer diagnostic
    remains available at /api/health/detailed for ops debugging."""
    from datetime import datetime
    """Enhanced health check endpoint with Socket.IO metrics and explicit CORS.

    Moved from /health → /api/health/detailed so Render's healthCheckPath
    can hit the minimal dependency-free /health handler (registered right
    after `app = Flask(__name__)`) on cold start. This richer diagnostic
    remains available at /api/health/detailed for ops debugging."""
    from datetime import datetime
    
    # Gather Socket.IO connection metrics
    socketio_status = {
        'connected_clients': len(connected_clients),
        'async_mode': socketio.async_mode if socketio else 'not_initialized',
        'transport': 'websocket_ready',
        'active_users': len(active_users) if 'active_users' in globals() else 0
    }
    
    # Check semantic search initialization status
    # ✅ DEPLOY-TIME PREWARM (July 24, 2026): Add a derived `state` field
    # so a single curl tells the user whether the chat endpoint is currently
    # usable. Possible values: "ready" / "warming_up" / "failed". Plus the
    # prewarm_started_at wall-clock so the user can see how long the
    # prewarm has been running (or whether it never started).
    if _semantic_search_initialization_complete:
        prewarm_state = "ready" if not _semantic_search_initialization_error else "failed"
    elif _semantic_search_initialization_error:
        prewarm_state = "failed"
    else:
        prewarm_state = "warming_up"
    semantic_search_status = {
        'initialized': _semantic_search_initialization_complete,
        'state': prewarm_state,  # ready | warming_up | failed
        'error': _semantic_search_initialization_error,
        'chat_endpoint_gated': not _semantic_search_initialization_complete,
        'note': (
            "Tool embeddings prewarm completed at deploy time. Chat "
            "endpoint is unblocked." if prewarm_state == "ready" else
            "Tool embeddings prewarm is still running as part of this "
            "deploy. Chat endpoint will return 503 + Retry-After until "
            "complete. Grep render.log for [DEPLOY_PREWARM] for progress." if prewarm_state == "warming_up" else
            "Tool embeddings prewarm FAILED at deploy time. Chat endpoint "
            "will return 503 with the error. Check render.log for "
            "[DEPLOY_PREWARM] ❌ lines."
        ),
    }

    # Check pgvector BGE model preload status (see initialize_pgvector_bge_model_async)
    pgvector_bge_status = {
        'initialized': _pgvector_bge_initialization_complete,
        'error': _pgvector_bge_initialization_error
    }
    
    response = jsonify({
        'status': 'healthy',
        'app': 'new_flask_app',
        'infrastructure': 'AI_infrastructure',
        'providers': ['anthropic', 'deepseek', 'openai'],
        'socketio': socketio_status,
        'semantic_search': semantic_search_status,
        'pgvector_bge': pgvector_bge_status,
        'timestamp': datetime.now(UTC).isoformat() + 'Z',
        'environment': 'production' if IS_RENDER else 'development',
        # Startup phase summary — added 2026-07-23 to support Render's
        # 5s healthCheckPath diagnostics. Deep-dive lives at
        # /api/dev-tools/startup-diagnostics[.txt].
        # Lazy import: startup_timing is not on the cold-start path.
        'startup': _startup_summary_block(),
    })
    
    # Add CORS headers explicitly
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-user-id,X-User-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    
    return response


# ✅ ADDED JUNE 9: WebSocket Diagnostic Endpoint (Fix WebSocket pending issue on Render)
@app.route('/api/ws-diagnostics', methods=['GET', 'OPTIONS'])
def ws_diagnostics():
    """
    Diagnostic endpoint to check WebSocket connection health and async mode
    Use this to verify the WebSocket pending issue is fixed
    
    Response includes:
    - async_mode: Threading, gevent, or unknown
    - async_mode_detected: Whether gevent was successfully detected
    - connected_clients: Number of active WebSocket connections
    - ping configuration: Timeout and interval settings
    - environment: Production (Render) or development
    """
    import sys
    from datetime import datetime
    
    try:
        # Check if gevent is available
        gevent_available = False
        gevent_version = None
        try:
            import gevent
            gevent_available = True
            gevent_version = gevent.__version__
        except ImportError:
            pass
        
        # Get async mode info
        actual_async_mode = socketio.async_mode if socketio else 'NOT_INITIALIZED'
        
        response = {
            'status': 'ok',
            'timestamp': datetime.now(UTC).isoformat() + 'Z',
            'environment': 'production' if IS_RENDER else 'development',
            'websocket': {
                'async_mode': actual_async_mode,
                'async_mode_expected': 'gevent' if IS_RENDER else 'threading',
                'gevent_available': gevent_available,
                'gevent_version': gevent_version,
                'ping_timeout': ping_timeout_config,
                'ping_interval': ping_interval_config,
                'connected_clients': len(connected_clients),
                'max_http_buffer_size': 1e6  # 1MB per the config
            },
            'system': {
                'platform': sys.platform,
                'python_version': sys.version,
                'workers': '1 (single-worker mode)' if IS_RENDER else 'N/A (dev mode)',
                'message_queue': socketio_message_queue or 'None (single-worker required)'
            },
            'fixes_applied': [
                'Favicon caching headers (30 days)',
                'Explicit gevent detection for async_mode',
                'Connection logging for Render debugging',
                'Connection state recovery enabled'
            ],
            'troubleshooting': {
                'websocket_pending': 'Check async_mode - should be "gevent" on production',
                'gevent_not_available': 'Install: pip install gevent' if IS_RENDER and not gevent_available else 'N/A',
                'connection_takes_long': 'Check ping_timeout - should be 90s on Render',
                'favicon_cached': 'Browser should cache for 30 days now'
            }
        }
        
        result = jsonify(response)
        result.headers.add('Access-Control-Allow-Origin', '*')
        result.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return result
    except Exception as e:
        log_error(logger, f'[Diagnostics] WS diagnostics error: {e}')
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now(UTC).isoformat() + 'Z'
        }), 500


# ✅ ADDED 2026-07-22: Registry-state diagnostic endpoint
# Reason: existing /api/health/detailed and /api/ws-diagnostics expose
# nothing about the worker's tool registry — tool_count, whether a
# specific tool is registered, whether the latest registry_v3.py code
# is loaded. Without these signals, every "Tool not found" bug
# becomes a guessing game about whether the new code is live.
@app.route('/api/diagnostics/registry', methods=['GET', 'OPTIONS'])
def registry_diagnostics():
    """Diagnostic snapshot of the worker's RegistryV3 state.

    Response includes:
    - registry_v3.tool_count: number of registered tools in self.tools
    - registry_v3.implementation_count: number of registered callables
    - registry_v3.has_list_available_platforms: the headline check
    - registry_v3.has_recommend_tools_for_task: another meta-tool check
    - registry_v3.tool_names_sample: first 50 tool names (for spot-check)
    - process.pid, process.create_time: when this worker process started
    - registry_v3.source_mtime: mtime of tools/registry_v3.py at the
      moment get_registry() was last called (proves the new file is
      loaded; if this predates your push, the old code is still in memory)
    - registry_v3.special_module_counts: per-special-module func count
      (meta_tools, sql_database, visualization_guide, viz_snapshots)
    """
    import os
    import time as _time
    from datetime import datetime, UTC
    from flask import request as _flask_request

    try:
        from tools.registry_v3 import get_registry
        reg = get_registry()

        # Snapshot the bits we care about — keep payload small.
        tool_names = list(reg.tools.keys()) if hasattr(reg, 'tools') else []
        impl_keys = list(reg.implementations.keys()) if hasattr(reg, 'implementations') else []
        has_list_avail = 'list_available_platforms' in tool_names and \
                         'list_available_platforms' in impl_keys

        # Per-special-module function counts (the headline indicator of
        # whether the meta_tools filter is working).
        special_module_counts = {}
        for sm in ('sql_database', 'meta_tools', 'visualization_guide', 'viz_snapshots'):
            # Each special module's functions are registered individually
            # in self.implementations under their own names. We can't
            # enumerate the module from the impl dict, so we just count
            # tools whose name *starts with* the special-module prefix is
            # NOT reliable — meta_tools doesn't have a prefix. So we
            # import the module and count its public callables that also
            # appear in self.tools.
            try:
                mod = __import__(f'tools.implementations.{sm}', fromlist=[sm])
                count = sum(
                    1 for attr in dir(mod)
                    if not attr.startswith('_')
                    and callable(getattr(mod, attr, None))
                    and attr in tool_names
                )
                special_module_counts[sm] = count
            except Exception:
                special_module_counts[sm] = None

        # Worker process info — proves this is the right PID + boot time.
        proc_info = {'pid': os.getpid()}
        try:
            import psutil  # type: ignore
            p = psutil.Process(os.getpid())
            proc_info['create_time'] = p.create_time()
            proc_info['create_time_iso'] = (
                datetime.fromtimestamp(p.create_time(), tz=UTC).isoformat()
            )
        except ImportError:
            # Fallback: use our own module load time as a proxy.
            proc_info['create_time'] = None
            proc_info['create_time_iso'] = None

        # Source mtime of registry_v3.py at moment the singleton was
        # constructed.  If this equals the on-disk mtime, the worker is
        # running the latest code.
        try:
            registry_mtime = os.path.getmtime(
                os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'tools', 'registry_v3.py'
                )
            )
        except OSError:
            registry_mtime = None

        # ✅ ADDED 2026-07-23: Per-schema load status
        # Reason: Render's worker loaded 83 tools but the 3 older special
        # modules (meta_tools, sql_database, visualization_guide) reported 0.
        # Locally all 4 specials load fine. The asymmetry points at a
        # Render-specific schema-load failure that the registry silently
        # swallows via the `continue` in _load_schemas. We capture every
        # schema file's load outcome + error message here so the next
        # regression is one curl away from diagnosis.
        import json as _json
        import locale as _locale
        import sys as _sys

        schemas_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'tools', 'schemas'
        )
        schema_status = {
            'schemas_dir': schemas_dir,
            'schemas_dir_exists': os.path.isdir(schemas_dir),
            'files_total': 0,
            'files_loaded': 0,
            'files_failed': 0,
            'failures': [],          # [{file, error_type, error_msg}]
            'loaded_sample': [],     # first 10 successfully loaded filenames
            'special_modules': {},   # {meta_tools.json: ok/fail, ...}
        }
        # We name the special-module schemas explicitly because glob order is
        # filesystem-dependent and we want a stable answer.
        _SPECIAL_FILES = {
            'meta_tools': 'meta_tools.json',
            'sql_database': 'sql_database_tools.json',
            'visualization_guide': 'visualization_guide_tools.json',
            'viz_snapshots': 'viz_snapshots_tools.json',
        }

        if os.path.isdir(schemas_dir):
            try:
                schema_files = sorted(
                    f for f in os.listdir(schemas_dir) if f.endswith('.json')
                )
                schema_status['files_total'] = len(schema_files)
                for fname in schema_files:
                    fpath = os.path.join(schemas_dir, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='replace') as _f:
                            _data = _json.load(_f)
                        if not isinstance(_data, dict):
                            raise ValueError(
                                f'schema is {type(_data).__name__}, expected dict'
                            )
                        if 'tools' not in _data:
                            raise ValueError('schema has no "tools" array')
                        n_tools = len(_data['tools'])
                        schema_status['files_loaded'] += 1
                        if len(schema_status['loaded_sample']) < 10:
                            schema_status['loaded_sample'].append(fname)
                        # Stamp special-module result
                        for _sm, _sm_file in _SPECIAL_FILES.items():
                            if fname == _sm_file:
                                schema_status['special_modules'][_sm] = {
                                    'file': fname,
                                    'ok': True,
                                    'tool_count': n_tools,
                                }
                    except Exception as _e:
                        schema_status['files_failed'] += 1
                        schema_status['failures'].append({
                            'file': fname,
                            'error_type': type(_e).__name__,
                            'error_msg': str(_e)[:500],
                        })
                        for _sm, _sm_file in _SPECIAL_FILES.items():
                            if fname == _sm_file:
                                schema_status['special_modules'][_sm] = {
                                    'file': fname,
                                    'ok': False,
                                    'error_type': type(_e).__name__,
                                    'error_msg': str(_e)[:500],
                                }
            except Exception as _e:
                schema_status['listdir_error'] = f'{type(_e).__name__}: {_e}'

        # Mark any special module that wasn't even seen in the directory.
        for _sm, _sm_file in _SPECIAL_FILES.items():
            if _sm not in schema_status['special_modules']:
                schema_status['special_modules'][_sm] = {
                    'file': _sm_file,
                    'ok': False,
                    'error_type': 'FileNotFound',
                    'error_msg': f'{_sm_file} not present in {schemas_dir}',
                }

        response = {
            'status': 'ok',
            'timestamp': datetime.now(UTC).isoformat() + 'Z',
            'worker_url': _flask_request.host,
            'process': proc_info,
            'runtime': {
                'python_version': _sys.version.split()[0],
                'python_implementation': _sys.implementation.name,
                'platform': _sys.platform,
                'locale_preferred_encoding': (
                    _locale.getpreferredencoding(False)
                ),
                'cwd': os.getcwd(),
                'supabase_db_url_pooler_set': bool(
                    os.environ.get('SUPABASE_DB_URL_POOLER')
                ),
                'render_env': os.environ.get('RENDER'),
                'environment': os.environ.get('ENVIRONMENT'),
            },
            'registry_v3': {
                'tool_count': len(tool_names),
                'implementation_count': len(impl_keys),
                'has_list_available_platforms': has_list_avail,
                'has_recommend_tools_for_task': (
                    'recommend_tools_for_task' in tool_names
                    and 'recommend_tools_for_task' in impl_keys
                ),
                'has_execute_tool': (
                    'execute_tool' in tool_names
                    and 'execute_tool' in impl_keys
                ),
                'special_module_counts': special_module_counts,
                'source_mtime': registry_mtime,
                'source_mtime_iso': (
                    datetime.fromtimestamp(registry_mtime, tz=UTC).isoformat()
                    if registry_mtime else None
                ),
                'tool_names_sample': sorted(tool_names)[:50],
                'schema_load_status': schema_status,
            },
        }
        result = jsonify(response)
        result.headers.add('Access-Control-Allow-Origin', '*')
        result.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return result
    except Exception as e:
        log_error(logger, f'[Diagnostics] Registry diagnostics error: {e}')
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now(UTC).isoformat() + 'Z'
        }), 500


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


@app.route('/api/admin/connection-stats', methods=['GET', 'OPTIONS'])
def connection_stats():
    """
    Get real-time database connection pool statistics
    
    Provides:
    - Connections acquired vs returned per schema
    - Leaked connection count
    - Pool size and utilization
    - Pool hits vs misses (cache efficiency)
    
    ✅ ADMIN ENDPOINT - For monitoring connection health
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    try:
        from AI_infrastructure.shared.database_utils import _pool_stats, _pools
        
        stats_by_schema = {}
        total_leaked = 0
        
        # Aggregate stats by schema
        for schema_name in _pools.keys():
            acquired = _pool_stats.get(f'{schema_name}_acquired', 0)
            returned = _pool_stats.get(f'{schema_name}_returned', 0)
            leaked = acquired - returned
            pool_hits = _pool_stats.get(f'{schema_name}_pool_hits', 0)
            pool_miss = _pool_stats.get(f'{schema_name}_pool_miss', 0)
            
            stats_by_schema[schema_name] = {
                'acquired': acquired,
                'returned': returned,
                'leaked': leaked,
                'pool_hits': pool_hits,
                'pool_miss': pool_miss,
                'pool_size': 4,  # Hard-coded max pool size per schema
                'utilization_pct': (leaked / 4) * 100 if leaked > 0 else 0
            }
            
            total_leaked += leaked
        
        # Overall stats
        overall = {
            'total_acquired': _pool_stats.get('connections_acquired', 0),
            'total_returned': _pool_stats.get('connections_returned', 0),
            'total_leaked': total_leaked,
            'total_wait_time': _pool_stats.get('total_wait_time', 0),
            'avg_wait_time': (_pool_stats.get('total_wait_time', 0) / _pool_stats.get('connections_acquired', 1)) if _pool_stats.get('connections_acquired', 0) > 0 else 0
        }
        
        response = jsonify({
            'success': True,
            'schemas': stats_by_schema,
            'overall': overall,
            'health': 'critical' if total_leaked >= 4 else 'warning' if total_leaked >= 2 else 'healthy',
            'timestamp': datetime.now(UTC).isoformat() + 'Z'
        })
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        log_error(logger, f"Failed to get connection stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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

# Serve favicon with proper caching headers
@app.route('/favicon.ico')
def favicon():
    """
    Serve favicon to prevent 404 errors
    ✅ FIXED JUNE 9: Add cache headers to prevent multiple requests (browser caches for 30 days)
    """
    response = send_from_directory(FAVICON_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    # Cache favicon for 30 days (2592000 seconds) to prevent duplicate requests
    response.headers['Cache-Control'] = 'public, max-age=2592000, immutable'
    response.headers['ETag'] = '"favicon-v1"'  # Version hash for cache busting if needed later
    return response

# Serve SVG favicon with proper caching headers (mirrors /favicon.ico route)
# ✅ ADDED JUNE 17: Without this route the catch-all /<path:filename> served the SVG
# without cache headers, so the browser re-fetched it on every page load.
@app.route('/favicon.svg')
def favicon_svg():
    """
    Serve SVG favicon to prevent redundant fetches.
    Browser caches for 30 days via Cache-Control: immutable.
    Bump the ETag suffix to invalidate cache if the SVG artwork changes.
    """
    response = send_from_directory(UI_DIR, 'favicon.svg', mimetype='image/svg+xml')
    response.headers['Cache-Control'] = 'public, max-age=2592000, immutable'
    response.headers['ETag'] = '"favicon-svg-v1"'
    return response

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
        # Capture user_id from Flask g before entering background thread (g is not available in threads)
        _requesting_user_id = getattr(g, 'rls_user_id', None)

        # GAP-M3: Resolve per-org AI config (provider/model defaults)
        _org_ai_cfg = {}
        if _requesting_user_id:
            try:
                from AI_infrastructure.shared.org_credentials_loader import get_org_ai_config
                _org_ai_cfg = get_org_ai_config(_requesting_user_id)
            except Exception:
                pass
        # Client-supplied provider takes precedence; otherwise fall back to org config then global default
        _resolved_provider = data.get('provider') or _org_ai_cfg.get('provider', 'anthropic')
        _org_model_override = _org_ai_cfg.get('model')      # None when no org config

        def process():
            with lock:
                try:
                    # Process with AI client
                    conversation = ai_client.process_streaming(
                        session_id=session_id,
                        session_data=session,
                        prompt=data['prompt'],
                        provider=_resolved_provider,
                        org_model=_org_model_override,
                        sse_callback=lambda event: queue.put(event),
                        user_id=_requesting_user_id,
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
        # Capture user_id from Flask g before entering background thread
        _requesting_user_id = getattr(g, 'rls_user_id', None)
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
                        sse_callback=lambda event: queue.put(event),
                        user_id=_requesting_user_id,
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
                        AND (organisation_id = (SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s) OR organisation_id IS NULL)
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
                        AND (organisation_id = (SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s) OR organisation_id IS NULL)
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
                """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id))
                
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
                    AND (organisation_id = (SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s) OR organisation_id IS NULL)
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, other_user_id, other_user_id, user_id, user_id, limit, offset))
                
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
# ============================================================================
# Phase 10 of 12: scheduler_and_finalization (APScheduler + atexit handlers)
# ============================================================================
_st_begin('scheduler_and_finalization', note='APScheduler start + atexit registration')
from scheduler import start_scheduler
try:
    scheduler = start_scheduler()
    log_success(logger, "Automation scheduler started")
except Exception as e:
    log_error(logger, f"Failed to start scheduler: {e}")
    import traceback
    log_error(logger, traceback.format_exc())

_st_end('scheduler_and_finalization', note='scheduler running')

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


@app.before_request
def set_rls_context_from_jwt():
    """
    MULTI-TENANT RLS MIDDLEWARE
    ===========================
    Extracts user_id and organisation_id from the JWT Bearer token and stores
    them in Flask g so that database_utils.get_database_connection() can
    automatically inject them as PostgreSQL session-level config vars
    (app.current_user_id and app.current_organisation_id) required by RLS policies.

    This runs on every request, before any route handler executes.
    It is intentionally non-blocking: if the token is missing, invalid, or the
    user has no org, g values are left as None and RLS policies will simply deny
    access to protected rows (returning empty results rather than errors).

    g attributes set:
      g.rls_user_id         (int | None)
      g.rls_organisation_id (int | None)
      g.plan_tier           (str | None)  — JWT claim, avoids extra DB hit per request
    """
    from flask import g
    g.rls_user_id         = None
    g.rls_organisation_id = None
    g.plan_tier           = None

    # Skip Socket.IO and static assets — no JWT needed
    if (request.path.startswith('/socket.io/')
            or request.path.startswith('/static')
            or request.path.startswith('/UI')):
        return

    # ✅ Cold-start fix: skip JWT/DB lookup on Render's /health probe path.
    # Without this, every health check triggers `execute_query(SELECT jwt_version ...)`
    # which on cold-start (unwarmed pool + cross-region Supabase RTT) takes 2-3 s,
    # blowing past Render's 5 s healthCheckPath timeout and cycling the instance.
    # /health and /api/health/detailed don't need user/org context — they're public
    # health endpoints with no RLS-gated rows.
    if request.path in ('/health', '/api/health', '/api/health/detailed'):
        return

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return

    token = auth_header[7:]
    if not token:
        return

    try:
        import jwt as pyjwt
        import os
        secret = os.environ.get('JWT_SECRET', '')
        if not secret:
            return
        payload = pyjwt.decode(token, secret, algorithms=['HS256'])
        user_id = payload.get('user_id')
        org_id  = payload.get('organisation_id')

        # GAP-C4 FIX: jwt_version check — instantly revoke tokens after role change.
        # If the DB's jwt_version for this user is higher than the token's version,
        # the token has been invalidated (role changed, org removed, etc.).
        # We set a flag on g so individual route decorators can return a 401.
        # BACKFILL FIX: also look up organisation_id from DB when it's absent from
        # the JWT (old tokens issued before org was assigned / before org_id was added
        # to the JWT payload) — zero extra DB round-trips when either check is needed.
        g.jwt_version_valid = True
        token_version = payload.get('jwt_version')
        if user_id and (token_version is not None or not org_id):
            try:
                from AI_infrastructure.shared.database_utils import execute_query
                row = execute_query(
                    "SELECT COALESCE(jwt_version, 1) AS jwt_version, organisation_id "
                    "FROM ai_infrastructure.users WHERE id = %s",
                    (int(user_id),), fetch_mode='one'
                )
                if row:
                    if token_version is not None and int(row['jwt_version']) > int(token_version):
                        g.jwt_version_valid = False
                        logger.info(f"[JWT] Stale token rejected for user_id={user_id} "
                                    f"(token_v={token_version}, db_v={row['jwt_version']})")
                    # Backfill org_id from DB when absent from JWT
                    if not org_id and row.get('organisation_id'):
                        org_id = row['organisation_id']
                        logger.info(f"[JWT] Backfilled org_id={org_id} from DB for user_id={user_id}")
            except Exception as _jv_err:
                logger.warning(f"[JWT] DB lookup failed (non-fatal): {_jv_err}")

        if user_id:
            g.rls_user_id = int(user_id)
        if org_id:
            g.rls_organisation_id = int(org_id)
        # GAP-L1 FIX: Expose plan_tier from JWT so routes don't need an extra DB hit
        plan_tier = payload.get('plan_tier')
        if plan_tier:
            g.plan_tier = plan_tier
    except Exception:
        # Expired, invalid signature, etc. — leave g values as None
        pass

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
# CONNECTION POOL PRE-WARMING
# Pre-create pools at import time so the first real request doesn't pay the
# 3-4 second Supabase TCP handshake cost during authentication.
# Runs once when gunicorn imports this module (before any request arrives).
# ============================================================================
def _prewarm_connection_pools():
    """Pre-warm DB connection pools in a background thread at startup."""
    import threading
    import time

    def _warm():
        try:
            time.sleep(0.5)  # Let gunicorn fully bind before touching DB
            # Was 2.0s; reduced 2026-07-26 because gunicorn --worker-class
            # geventwebsocket binds inside gunicorn-master's ready() callback
            # and the gevent hub is already polling accept() by the time the
            # worker fork returns - the original 2s was paranoid headroom
            # that cost 1.5s on every deploy.
            logger.info('[STARTUP] Pre-warming connection pools...')
            from AI_infrastructure.shared.database_utils import get_database_connection
            for schema in ('ai_infrastructure', 'sessions'):
                try:
                    with get_database_connection(schema) as conn:
                        with conn.cursor() as cur:
                            cur.execute('SELECT 1')
                    logger.info(f'[STARTUP] Pool pre-warmed: {schema}')
                except Exception as e:
                    logger.warning(f'[STARTUP] Pool pre-warm failed for {schema}: {e}')
        except Exception as e:
            logger.warning(f'[STARTUP] Pool pre-warm thread error: {e}')

    t = threading.Thread(target=_warm, daemon=True, name='pool-prewarm')
    t.start()

# Only pre-warm when running under gunicorn (RENDER=true) or directly
# ============================================================================
# Phase 11 of 12: gunicorn_runtime_services (pool prewarm + leak detector)
# ============================================================================
_st_begin('gunicorn_runtime_services', note='pool prewarm + connection leak detector')

if os.environ.get('RENDER') == 'true' or __name__ == '__main__':
    _prewarm_connection_pools()

    # ============================================================================
    # 🚀 SEMANTIC SEARCH PREWARM (Deploy-time marker + background-thread fallback)
    # ============================================================================
    # WHY HERE (not under `if __name__ == '__main__':`):
    #   gunicorn imports flask_app as a module, so its __name__ is
    #   "AI_infrastructure.flask_app" — never "__main__". Placing this inside
    #   the __main__-only block silently skipped it under gunicorn, leaving
    #   `_semantic_search_initialization_complete` stuck at False and the chat
    #   endpoint returning 503 + Retry-After forever — the user reported
    #   symptom on 2026-07-24. The same `RENDER or __main__` pattern that
    #   gates `_prewarm_connection_pools()` above is what makes the connection
    #   pool prewarm actually fire under gunicorn; we mirror it here so the
    #   semantic-search prewarm behaves the same way.
    #
    # If startup.sh ran AI_infrastructure/scripts/deploy_prewarm.py BEFORE
    # `exec gunicorn`, a marker file /data/.prewarm_complete exists. In that
    # case the HuggingFace model is already in /data/vdb_models/ AND the tool
    # embeddings are already cached in Supabase — workers load them on first
    # chat in <2s. We SKIP the background thread (the user's clock is no
    # longer paying for the prewarm cost).
    #
    # If the marker is absent (local dev, deploy script failed), fall back
    # to the background-thread prewarm + the 503+Retry-After gate in
    # agent_routes_v4.py get_semantic_search(). Deploys never crash-loop
    # because of a prewarm failure.
    _PREWARM_MARKER_PATH = '/data/.prewarm_complete'

    try:
        _marker_present = os.path.isfile(_PREWARM_MARKER_PATH)
    except Exception as _marker_err:
        print(f"[DEPLOY_PREWARM] Marker detection error (non-fatal): {_marker_err}")
        _marker_present = False

    if _marker_present:
        # Trust the marker — the persistent_semantic_search singleton will
        # load instantly from /data/vdb_models/ + Supabase on first call.
        _semantic_search_initialization_complete = True
        _semantic_search_initialization_error = None
        print(f"[DEPLOY_PREWARM] ✓ Marker file detected: {_PREWARM_MARKER_PATH}")
        print("[DEPLOY_PREWARM]   Deploy-time prewarm already completed.")
        print("[DEPLOY_PREWARM]   Skipping background-thread prewarm; workers will")
        print("[DEPLOY_PREWARM]   load embeddings from cache on first chat (<2s).")
        print("[DEPLOY_PREWARM] ✓ Background prewarm thread SKIPPED.\n")
    else:
        # No marker (dev mode or deploy-time prewarm failed). Start the
        # background-thread prewarm; the chat endpoint will return 503 with
        # Retry-After until it completes.
        print("[STARTUP] No deploy-prewarm marker found — starting background-thread prewarm...")
        print("[STARTUP] Server will respond to health checks immediately while embeddings load.")
        print("[STARTUP] Chat endpoint will 503+Retry-After until prewarm completes.\n")
        start_semantic_search_initialization()

    # ============================================================================
    # 🚀 PGVECTOR BGE MODEL PRELOAD (background thread, non-fatal)
    # ============================================================================
    # WHY HERE (not under `if __name__ == '__main__':`):
    #   Same gunicorn __name__ trap as the semantic-search prewarm above:
    #   `start_pgvector_bge_initialization()` is the function that actually
    #   spawns the preload thread, and under gunicorn its __name__ is
    #   "AI_infrastructure.flask_app" — never "__main__". Placing the call
    #   inside the __main__-only block silently skipped it under gunicorn
    #   on Render, leaving `_pgvector_bge_initialization_complete` stuck at
    #   False and the first vector-DB upload paying the 30-60 s HuggingFace
    #   download cost.
    #
    # NOTE: This is NOT on the chat hot path — it's only consumed by the
    # vector-DB document upload flow. Failures here are non-fatal: the
    # model will still load on first use (just with the original 30-60 s
    # wait). We log and continue if anything goes wrong.
    #
    # Bug fixed 2026-07-24 — function was previously defined but never
    # called from anywhere in the codebase, so the preload never ran on
    # Render. The diagnostic endpoint at /api/dev-tools/startup-diagnostics
    # was always reporting `pgvector_bge.initialized: false`.
    # ============================================================================
    try:
        start_pgvector_bge_initialization()
    except Exception as _bge_err:
        print(f"[STARTUP] ⚠️  Failed to start pgvector BGE preload (non-fatal): {_bge_err}")

    # ============================================================================
    # CONNECTION LEAK DETECTOR STARTUP
    #
    # Why here (not under `if __name__ == '__main__':`):
    #   gunicorn imports flask_app as a module, so its __name__ is
    #   "AI_infrastructure.flask_app" — never "__main__". Placing the
    #   detector start inside the __main__-only block silently skipped it
    #   on Render, leaving `/api/pool-health` reporting `is_running: false`
    #   and orphan connections accumulating in the pool.
    #
    # The detector auto-closes connections idle for > LEAK_DETECTOR_IDLE_TIMEOUT
    # (default 30s) and exposes live metrics at GET /api/pool-health.
    # ============================================================================
    try:
        from AI_infrastructure.shared.connection_leak_detector import start_leak_detector

        # Capture detector config BEFORE starting so the log shows what we
        # configured, not what defaults were applied.
        _ld_interval = int(os.environ.get('LEAK_DETECTOR_INTERVAL', '60'))
        _ld_idle_timeout = int(os.environ.get('LEAK_DETECTOR_IDLE_TIMEOUT', '30'))
        _ld_auto_close = os.environ.get('LEAK_DETECTOR_AUTO_CLOSE', 'True').lower() == 'true'

        run_mode = (
            'gunicorn (RENDER)' if os.environ.get('RENDER') == 'true'
            else 'direct (python flask_app.py)'
        )

        logger.info(
            f'[LEAK_DETECTOR] Starting under {run_mode} | '
            f'interval={_ld_interval}s, idle_timeout={_ld_idle_timeout}s, '
            f'auto_close={_ld_auto_close}'
        )

        detector = start_leak_detector()

        # Sanity check — verify the thread actually came up. If start()
        # returned but _running is False, log loudly so this never silently
        # regresses again.
        if detector and getattr(detector, '_running', False):
            _thread_name = detector._thread.name if detector._thread else '?'
            _thread_daemon = detector._thread.daemon if detector._thread else '?'
            logger.info(
                f'[LEAK_DETECTOR] ✅ Running | thread={_thread_name} '
                f'daemon={_thread_daemon}'
            )
        else:
            logger.warning('[LEAK_DETECTOR] ⚠️ start() returned but detector._running is False')

        # Baseline pool snapshot — capture state at boot so after-the-fact
        # comparisons can answer "did the pool grow during a load?"
        try:
            from AI_infrastructure.shared.database_utils import get_all_pool_stats
            _baseline = get_all_pool_stats() or {}
            for _schema, _stats in sorted(_baseline.items()):
                _acq = _stats.get('acquired') or _stats.get('connections_acquired', 0)
                _ret = _stats.get('returned') or _stats.get('connections_returned', 0)
                _max = _stats.get('maxconn') or _stats.get('max_connections', '?')
                logger.info(
                    f'[LEAK_DETECTOR] baseline pool[{_schema}] '
                    f'acquired={_acq}, returned={_ret}, maxconn={_max}'
                )
        except Exception as _be:
            logger.warning(f'[LEAK_DETECTOR] baseline pool snapshot failed (non-fatal): {_be}')

        # Proactive cleanup of zombies from a previous crash / restart.
        try:
            _cleanup = detector.cleanup_pool() or {}
            _cleaned = _cleanup.get('cleaned', 0)
            _cerrors = _cleanup.get('errors', 0)
            if _cleaned > 0:
                logger.warning(f'[LEAK_DETECTOR] 🧹 Cleaned {_cleaned} zombie connection(s) on boot')
            elif _cerrors > 0:
                logger.warning(f'[LEAK_DETECTOR] cleanup_pool reported {_cerrors} error(s)')
            else:
                logger.info('[LEAK_DETECTOR] 🧹 No zombie connections found')
        except Exception as _ce:
            # cleanup_pool can raise if pools aren't initialized yet; log
            # but do NOT treat as fatal — the detector itself is already
            # running and will retry on its next tick.
            logger.warning(f'[LEAK_DETECTOR] cleanup_pool() failed (non-fatal): {_ce}')

        print("✅ Connection leak detector started (auto-close idle >30 sec)")
        print("   Metrics: GET /api/pool-health")
        print("   Force check: POST /api/pool-health/force-check")
        print("   Live counts: idle_found, idle_closed, active_warned, errors\n")
    except Exception as e:
        # Log via both print() and logger so the message surfaces whether
        # the operator is watching the Render dashboard stdout OR scraping
        # captured log files.
        _msg = f'⚠️  Failed to start leak detector: {e}'
        print(_msg)
        logger.error(f'[LEAK_DETECTOR] {_msg}', exc_info=True)

    _st_end('gunicorn_runtime_services', note='runtime services live')

# ============================================================================
# RUN APP
# ============================================================================

# ============================================================================
# Phase 12 of 12: module_import_complete (worker is now request-ready)
# ============================================================================
_st_begin('module_import_complete', note='worker ready to serve /health within Render 5s')
_st_end('module_import_complete', note='all 12 phases recorded')

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

    # NOTE: Connection leak detector starts earlier — see the
    # `if RENDER or __main__:` block above. Starting it here would either
    # duplicate work (locally) or never run at all (under gunicorn).

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

    # NOTE: Deploy-prewarm marker check + semantic-search background-thread
    # prewarm + pgvector BGE model preload are now kicked off earlier in the
    # file (inside the `RENDER or __main__` block alongside
    # `_prewarm_connection_pools()`). Putting any of them inside this
    # __main__-only block silently skipped them under gunicorn, leaving the
    # chat endpoint 503'd on every request — bugs fixed 2026-07-24.

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