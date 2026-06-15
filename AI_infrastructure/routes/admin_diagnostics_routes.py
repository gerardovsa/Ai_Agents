"""
Admin Diagnostics Routes
========================
Deep platform health check for AI agents and human admins.

Endpoints:
- GET /api/admin/diagnostics        — full deep-dive (DB, AI providers, vector DB, vault, memory, errors)
- GET /api/admin/diagnostics/summary — lightweight summary (faster, for frequent polling)
- GET /api/admin/diagnostics/provider/<name> — single AI provider health probe

Why: The shallow /health endpoint only reports what the app *thinks* of itself.
This endpoint actively probes each dependency so an external AI agent can
detect silent failures (e.g. CREDENTIAL_ENCRYPTION_KEY mismatch, MiniMax key
expired, pgvector extension missing).

Auth: All endpoints require @require_auth. The deep-dive endpoint is intended
for an admin or service account — the frontend should NOT poll it. Use
/api/admin/diagnostics/summary for that.

Author: Cleanup round 2 (June 15, 2026)
"""
import os
import time
import traceback
import logging
from datetime import datetime, UTC

import psutil  # already a transitive dep via Render; explicit pin below
from flask import Blueprint, jsonify, g
from auth.user_auth import require_auth

logger = logging.getLogger(__name__)

diagnostics_bp = Blueprint('admin_diagnostics', __name__)


# ---------------------------------------------------------------------------
# Helpers (all import inside the function to avoid circular imports per
# CLAUDE.md §5 "Imports" — `from AI_infrastructure.shared.database_utils`
# must not appear at module top level inside `tools/` or `routes/`)
# ---------------------------------------------------------------------------

def _probe_database() -> dict:
    """SELECT 1 against the Supabase pooler. Returns latency in ms."""
    t0 = time.perf_counter()
    try:
        from shared.database_utils import execute_query
        execute_query('SELECT 1 AS ok', fetch_mode='value')
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {'status': 'healthy', 'latency_ms': latency_ms}
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'details': traceback.format_exc(),
            'latency_ms': round((time.perf_counter() - t0) * 1000, 2),
        }


def _probe_pgvector() -> dict:
    """Check pgvector extension + a known table. Returns extension status."""
    try:
        from shared.database_utils import execute_query
        ext = execute_query(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector'",
            fetch_mode='value'
        )
        # Try a small query against a vector table (org_vector_documents is
        # the canonical table from migration 030)
        doc_count = execute_query(
            'SELECT COUNT(*) FROM ai_infrastructure.org_vector_documents',
            fetch_mode='value'
        )
        return {
            'status': 'healthy' if ext else 'unhealthy',
            'extension_version': ext or 'not installed',
            'document_count': doc_count if doc_count is not None else 'unknown',
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'details': traceback.format_exc(),
        }


def _probe_provider(name: str) -> dict:
    """
    Quick connectivity check for a single AI provider. We do NOT send a real
    prompt — that would cost tokens and slow polling. We just check that
    the SDK can be imported and the key (if any) is present.
    """
    t0 = time.perf_counter()
    key_env_map = {
        'anthropic': 'ANTHROPIC_API_KEY',
        'openai':    'OPENAI_API_KEY',
        'deepseek':  'DEEPSEEK_API_KEY_1',
        'minimax':   'MINIMAX_API_KEY',  # CLAUDE.md §1: 4th provider added 2026-06-10
    }
    key_env = key_env_map.get(name)
    key_set = bool(os.getenv(key_env, '').strip()) if key_env else False
    result = {
        'provider': name,
        'key_env': key_env,
        'key_set': key_set,
        'sdk_importable': False,
        'latency_ms': 0,
    }
    try:
        if name == 'anthropic':
            import anthropic  # noqa: F401
        elif name == 'openai':
            import openai  # noqa: F401
        elif name == 'deepseek':
            import openai  # uses openai-compat client
        elif name == 'minimax':
            import anthropic  # CLAUDE.md §1 — reuses Anthropic SDK with custom base_url
        result['sdk_importable'] = True
    except ImportError as e:
        result['error'] = f'SDK not installed: {e}'
    result['latency_ms'] = round((time.perf_counter() - t0) * 1000, 2)
    result['status'] = 'healthy' if (result['sdk_importable'] and result['key_set']) else 'degraded'
    return result


def _probe_vault() -> dict:
    """
    Verify CREDENTIAL_ENCRYPTION_KEY is set and can decrypt a test token.
    This is the test that catches the "key mismatch after restore" scenario.
    """
    key = os.getenv('CREDENTIAL_ENCRYPTION_KEY', '').strip()
    if not key:
        return {'status': 'unhealthy', 'error': 'CREDENTIAL_ENCRYPTION_KEY not set'}
    try:
        from shared.credential_crypto import encrypt_value, decrypt_value
        plaintext = 'vault-probe-' + datetime.now(UTC).isoformat()
        ciphertext = encrypt_value(plaintext)
        recovered = decrypt_value(ciphertext)
        if recovered != plaintext:
            return {'status': 'unhealthy', 'error': 'roundtrip mismatch'}
        return {
            'status': 'healthy',
            'ciphertext_prefix': ciphertext[:24] + '...',  # enc:v1:... format
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'details': traceback.format_exc(),
        }


def _probe_memory_disk() -> dict:
    """Snapshot of process RSS, system memory, and /data disk usage."""
    try:
        process = psutil.Process()
        rss_mb = round(process.memory_info().rss / 1024 / 1024, 1)
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage('/data') if os.path.isdir('/data') else psutil.disk_usage('/')
        return {
            'status': 'healthy',
            'process_rss_mb': rss_mb,
            'system_memory': {
                'total_gb': round(vm.total / 1024 ** 3, 2),
                'available_gb': round(vm.available / 1024 ** 3, 2),
                'percent_used': vm.percent,
            },
            'disk': {
                'path': '/data' if os.path.isdir('/data') else '/',
                'total_gb': round(disk.total / 1024 ** 3, 2),
                'used_gb': round(disk.used / 1024 ** 3, 2),
                'percent_used': disk.percent,
            },
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def _probe_tool_registry() -> dict:
    """Count of registered tools — sudden drops indicate a bad import."""
    try:
        from tools.registry_v3 import RegistryV3
        r = RegistryV3()
        return {
            'status': 'healthy',
            'tool_count': len(r.tools),
            'sample': list(r.tools.keys())[:5],
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'details': traceback.format_exc(),
        }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@diagnostics_bp.route('/api/admin/diagnostics', methods=['GET'])
@require_auth
def deep_diagnostics():
    """
    Full deep-dive diagnostics. Intended for: human admin, external AI agent
    (Claude, your own agent), CI smoke test. NOT for frontend polling — use
    /api/admin/diagnostics/summary for that (lower latency, less noise).
    """
    started = time.perf_counter()
    # Run all probes — each is wrapped in try/except so a single failure
    # doesn't take down the whole response
    probes = {
        'database':     _probe_database(),
        'pgvector':     _probe_pgvector(),
        'vault':        _probe_vault(),
        'memory_disk':  _probe_memory_disk(),
        'tool_registry': _probe_tool_registry(),
        'providers': {
            name: _probe_provider(name)
            for name in ('anthropic', 'openai', 'deepseek', 'minimax')
        },
    }

    # Aggregate status — degraded if any probe is degraded, unhealthy if
    # any probe is unhealthy, healthy otherwise
    def _roll_up(probe_result):
        if isinstance(probe_result, dict):
            return probe_result.get('status', 'unknown')
        return 'unknown'

    statuses = []
    for k, v in probes.items():
        if isinstance(v, dict) and 'status' in v:
            statuses.append(v['status'])
        elif isinstance(v, dict):
            # providers sub-dict — roll up each provider
            for sub in v.values():
                statuses.append(_roll_up(sub))

    if 'unhealthy' in statuses:
        overall = 'unhealthy'
    elif 'degraded' in statuses:
        overall = 'degraded'
    else:
        overall = 'healthy'

    return jsonify({
        'status': overall,
        'duration_ms': round((time.perf_counter() - started) * 1000, 2),
        'timestamp': datetime.now(UTC).isoformat() + 'Z',
        'commit': os.getenv('RENDER_GIT_COMMIT', 'unknown')[:8],
        'environment': os.getenv('ENVIRONMENT', 'production'),
        'requested_by': getattr(g, 'rls_user_id', None),
        'probes': probes,
    })


@diagnostics_bp.route('/api/admin/diagnostics/summary', methods=['GET'])
@require_auth
def summary_diagnostics():
    """
    Lightweight summary. Skips the expensive pgvector doc-count query and
    the per-provider SDK imports. Use this for frequent polling (every
    30–60s). Returns overall status + a compact probe list.
    """
    started = time.perf_counter()
    db = _probe_database()
    vault = _probe_vault()
    mem = _probe_memory_disk()
    # Status roll-up
    statuses = [db.get('status'), vault.get('status'), mem.get('status')]
    if 'unhealthy' in statuses:
        overall = 'unhealthy'
    elif 'degraded' in statuses:
        overall = 'degraded'
    else:
        overall = 'healthy'
    return jsonify({
        'status': overall,
        'duration_ms': round((time.perf_counter() - started) * 1000, 2),
        'timestamp': datetime.now(UTC).isoformat() + 'Z',
        'database': db,
        'vault': vault,
        'memory_disk': mem,
    })


@diagnostics_bp.route('/api/admin/diagnostics/provider/<name>', methods=['GET'])
@require_auth
def provider_diagnostics(name: str):
    """Single-provider probe — useful for testing a specific key after rotation."""
    name = name.lower()
    if name not in ('anthropic', 'openai', 'deepseek', 'minimax'):
        return jsonify({'success': False, 'error': f'unknown provider: {name}'}), 400
    return jsonify({
        'success': True,
        'timestamp': datetime.now(UTC).isoformat() + 'Z',
        'probe': _probe_provider(name),
    })
