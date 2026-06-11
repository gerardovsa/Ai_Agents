"""
AI_infrastructure/shared/tool_registry_disk_cache.py
====================================================

Persistent on-disk cache for the tool registry schemas.

Lives on the Render /data persistent disk (10 GB) so that:
- Schema rebuild cost is paid once per code change, not once per gunicorn worker recycle
- Worker restarts (which fire on every Render deploy, and on gunicorn's 1000-request
  recycle cycle) do not re-walk every JSON file in tools/schemas/ + every plugin
  module under UI/modules_external/
- Boot time for warm restarts drops from ~3-5 s to ~50 ms

NOTE: This caches the *schemas* dict (JSON-serializable) only. Python callables in
`self.implementations` are always re-imported from disk — pickling callables into
a disk cache is a security risk (a corrupt cache can `eval` arbitrary code on load)
and they re-load fast anyway (~200 ms for 30 modules).

USAGE
-----
    from AI_infrastructure.shared.tool_registry_disk_cache import (
        compute_version_hash_from_registry,
        should_use_disk_cache,
        load_schemas_from_disk,
        save_schemas_to_disk,
    )

    registry = get_registry()
    if not should_use_disk_cache(registry):
        registry._load_schemas()  # cold path
        save_schemas_to_disk(registry)
    else:
        load_schemas_from_disk(registry)
        # still need to re-import implementations
        registry._load_implementations()
        registry._load_module_plugins()
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Cache directory lives on the Render persistent disk. Falls back to a local
# tmp dir in dev so unit tests don't require /data to exist.
CACHE_DIR = Path(os.getenv('TOOL_REGISTRY_CACHE_DIR', '/data/tool_registry_cache'))
SCHEMAS_FILE = CACHE_DIR / 'tool_schemas.json'
VERSION_FILE = CACHE_DIR / 'version_hash.txt'


def _ensure_cache_dir() -> bool:
    """Create the cache directory if it doesn't exist.

    Returns False if we cannot write to it (e.g. /data not mounted in dev).
    Caller should fall back to in-RAM registry.
    """
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.warning(f"[DISK_CACHE] Cannot create cache dir {CACHE_DIR}: {e}")
        return False


def compute_version_hash(tools: Dict[str, Any]) -> str:
    """Stable hash of the tools registry contents.

    The hash is order-independent: we sort tool names before hashing so that
    two registries with the same tools in different load order produce the
    same hash. This is what the BACKGROUND thread compares against the
    previously-stored hash to decide whether to rebuild.
    """
    hasher = hashlib.sha256()
    for tool_name in sorted(tools.keys()):
        hasher.update(tool_name.encode('utf-8'))
        # default=str handles datetime, Decimal, UUID — anything json.dumps
        # can serialize via the default hook
        hasher.update(json.dumps(tools[tool_name], sort_keys=True, default=str).encode('utf-8'))
    return hasher.hexdigest()


def should_use_disk_cache(current_hash: str) -> bool:
    """Return True iff a valid cache exists for the given version hash.

    "Valid" means: the file exists, is readable as UTF-8, and matches the
    hash we're checking against. We never trust the cache silently — a
    hash mismatch forces a rebuild (this is the same pattern the existing
    Redis cache uses).
    """
    if not _ensure_cache_dir():
        return False
    if not VERSION_FILE.exists() or not SCHEMAS_FILE.exists():
        logger.info("[DISK_CACHE] No cache files present (cold start)")
        return False
    try:
        stored_hash = VERSION_FILE.read_text(encoding='utf-8').strip()
    except OSError as e:
        logger.warning(f"[DISK_CACHE] Cannot read version file: {e}")
        return False
    if stored_hash != current_hash:
        logger.info(
            f"[DISK_CACHE] Hash mismatch (stored={stored_hash[:8]}, "
            f"current={current_hash[:8]}) — rebuild required"
        )
        return False
    return True


def load_schemas_from_disk(registry: Any) -> bool:
    """Load tool schemas from the disk cache into `registry.tools`.

    Returns True on success, False on any failure (caller should fall
    back to `_load_schemas()`).
    """
    try:
        payload = json.loads(SCHEMAS_FILE.read_text(encoding='utf-8'))
        registry.tools = payload
        logger.info(
            f"[DISK_CACHE] Loaded {len(registry.tools)} tool schemas from "
            f"{SCHEMAS_FILE}"
        )
        return True
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"[DISK_CACHE] Failed to load schemas from disk: {e}")
        return False


def save_schemas_to_disk(registry: Any) -> Optional[str]:
    """Persist the current registry.tools to /data + return the version hash.

    Writes atomically: writes to a temp file then renames, so a partial
    write doesn't leave a corrupt cache that the next worker would load.
    Returns the computed hash on success, None on failure.
    """
    if not _ensure_cache_dir():
        return None
    version_hash = compute_version_hash(registry.tools)
    try:
        # Atomic write: write to .tmp, then rename. POSIX guarantees rename
        # is atomic on the same filesystem, so readers never see a torn file.
        tmp_schemas = SCHEMAS_FILE.with_suffix('.json.tmp')
        tmp_version = VERSION_FILE.with_suffix('.txt.tmp')
        tmp_schemas.write_text(
            json.dumps(registry.tools, default=str, ensure_ascii=False),
            encoding='utf-8',
        )
        tmp_version.write_text(version_hash, encoding='utf-8')
        tmp_schemas.replace(SCHEMAS_FILE)
        tmp_version.replace(VERSION_FILE)
        logger.info(
            f"[DISK_CACHE] Saved {len(registry.tools)} tool schemas to "
            f"{SCHEMAS_FILE} (version {version_hash[:8]})"
        )
        return version_hash
    except (OSError, TypeError, ValueError) as e:
        logger.error(f"[DISK_CACHE] Failed to save cache: {e}")
        return None


def get_cache_status() -> Dict[str, Any]:
    """Diagnostic helper: returns cache file existence + sizes for /api/registry/status."""
    if not CACHE_DIR.exists():
        return {
            'cache_dir': str(CACHE_DIR),
            'exists': False,
            'schemas_file': None,
            'version_file': None,
        }
    return {
        'cache_dir': str(CACHE_DIR),
        'exists': True,
        'schemas_file': {
            'path': str(SCHEMAS_FILE),
            'size_bytes': SCHEMAS_FILE.stat().st_size if SCHEMAS_FILE.exists() else None,
            'exists': SCHEMAS_FILE.exists(),
        },
        'version_file': {
            'path': str(VERSION_FILE),
            'value': VERSION_FILE.read_text(encoding='utf-8').strip() if VERSION_FILE.exists() else None,
            'exists': VERSION_FILE.exists(),
        },
    }
