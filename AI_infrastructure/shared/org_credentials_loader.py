"""
FILE: AI_infrastructure/shared/org_credentials_loader.py

PURPOSE:
    Organisation-aware credential loader.
    Resolves an API key for a given platform by checking in priority order:
        1. User-specific key  (user_platform_credentials WHERE user_id = X)
        2. Org-level key      (organisation_platform_credentials WHERE org_id = org of user)
        3. Environment var    (os.getenv, last-resort legacy fallback)

WHEN TO USE:
    Replace direct calls to get_user_credentials(1, 'anthropic') or os.getenv()
    with resolve_credentials(user_id, 'anthropic').

    The caller never needs to know where the key came from.

EXAMPLES:
    # In any tool implementation:
    from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

    creds = resolve_credentials(user_id, 'anthropic')
    api_key = creds.get('api_key') or creds.get('credential_value')

    # Force org-level only (skip user-specific):
    creds = resolve_credentials(user_id, 'auspost', prefer_user=False)

    # With fallback env var name:
    creds = resolve_credentials(user_id, 'auspost', env_fallback='AUSPOST_API_KEY')

PLATFORM NAME CONVENTIONS:
    anthropic    → Anthropic Claude AI
    openai       → OpenAI GPT / embeddings
    auspost      → Australia Post shipping
    stripe       → Stripe payments
    xero         → Xero accounting (usually user-specific OAuth but can be org API key)
    shopify      → Shopify admin API
    assemblyai   → AssemblyAI speech-to-text
    twilio       → Twilio SMS / voice
    sendgrid     → SendGrid email
    pinecone     → Pinecone vector DB
    deepseek     → DeepSeek language models
    MiniMax  → MiniMax M-series (M3, M2.7, M2.5, M2.1, M2)

AUTHOR: GitHub Copilot
DATE: March 2026
"""

import os
import json
import logging
from typing import Optional, Dict, Any

from AI_infrastructure.shared.database_utils import execute_query

logger = logging.getLogger(__name__)

# ============================================================================
# PLATFORM → ENV VAR MAPPING
# Used as the final fallback when no DB credential exists.
# ============================================================================

PLATFORM_ENV_VARS: Dict[str, str] = {
    'anthropic':    'ANTHROPIC_API_KEY',
    'openai':       'OPENAI_API_KEY',
    'auspost':      'AUSPOST_API_KEY',
    'stripe':       'STRIPE_SECRET_KEY',
    'assemblyai':   'ASSEMBLYAI_API_KEY',
    'twilio':       'TWILIO_AUTH_TOKEN',
    'sendgrid':     'SENDGRID_API_KEY',
    'pinecone':     'PINECONE_API_KEY',
    'deepseek':     'DEEPSEEK_API_KEY',
    'MiniMax':  'MINIMAX_API_KEY',
    'deepgram':     'DEEPGRAM_API_KEY',
    'speechmatics': 'SPEECHMATICS_API_KEY',
}


# ============================================================================
# CANONICAL PLATFORM NAMES (read-side casing normalisation)
# ============================================================================
# Some platforms are stored in the DB with non-lowercase canonical forms
# (e.g. 'MiniMax' PascalCase — matches chk_organisations_ai_provider and
# organisation_platform_credentials.platform values). Callers may pass any
# case ('MiniMax', 'minimax', 'MINIMAX'), so we normalise before any DB
# lookup. The DB stores these exactly as listed below.
# ---------------------------------------------------------------------------
_PLATFORM_CANONICAL: Dict[str, str] = {
    'MiniMax': 'MiniMax',   # only PascalCase outlier — others are lowercase
}


def _canonicalize_platform(platform: str) -> str:
    """Normalise a caller-supplied platform name to the form stored in the DB.

    Lookup is case-insensitive: any of 'MiniMax' / 'minimax' / 'MINIMAX' resolves
    to 'MiniMax'. Unknown platforms fall back to lowercase (which matches the
    storage convention for anthropic / openai / pinecone / etc.).

    Args:
        platform: Caller-supplied platform name (any case).

    Returns:
        Canonical platform name suitable for SQL `platform = %s` lookup.
    """
    if not platform:
        return ''
    key = platform.strip()
    if key in _PLATFORM_CANONICAL:
        return _PLATFORM_CANONICAL[key]
    # Case-insensitive lookup so 'minimax' / 'MINIMAX' both resolve to 'MiniMax'
    key_lower = key.lower()
    for canonical_name in _PLATFORM_CANONICAL:
        if canonical_name.lower() == key_lower:
            return canonical_name
    return key_lower


# ============================================================================
# INTERNAL: PARALLEL PAIR HELPER (module-level)
# ============================================================================
# Added 2026-07-26 (Change 2): runs two zero-arg callables concurrently via
# gevent when available, sequentially otherwise. Used by resolve_credentials()
# to parallelise Tier 1.5 (parent_id + parent_user_cred) against Tier 2
# (org_id + org_cred). Cold-path time on Render dropped from ~9.5s to ~4.5s.
#
# gevent is detected lazily on first call (not at module load) so local dev
# works without gevent installed. The existing inner _spawn_pair inside
# resolve_api_keys_batch is left untouched — this helper is only consumed by
# resolve_credentials() to preserve the batch function's already-parallel
# Phase 1 + Phase 2 path.
# ============================================================================

_GEVENT = None
_GEVENT_DETECTED = False


def _spawn_pair(coro_a, coro_b, timeout=5.0):
    """Run two zero-arg callables concurrently via gevent if available;
    otherwise sequentially. Returns (val_a, val_b). Exceptions inside the
    callables are swallowed inside each callable; if a greenlet dies
    unexpectedly we return None for that branch."""
    global _GEVENT, _GEVENT_DETECTED
    if not _GEVENT_DETECTED:
        try:
            import gevent as _g
            _GEVENT = _g
        except Exception:
            _GEVENT = None
        _GEVENT_DETECTED = True

    if _GEVENT is not None:
        ga = _GEVENT.spawn(coro_a)
        gb = _GEVENT.spawn(coro_b)
        _GEVENT.joinall([ga, gb], timeout=timeout)
        va = ga.value if not ga.dead else None
        vb = gb.value if not gb.dead else None
        if ga.dead and ga.exception:
            logger.debug(f"[ORG_CREDS] greenlet A died: {ga.exception}")
        if gb.dead and gb.exception:
            logger.debug(f"[ORG_CREDS] greenlet B died: {gb.exception}")
        return va, vb

    return coro_a(), coro_b()


# ============================================================================
# INTERNAL: SUB-USER PARENT LOOKUP
# ============================================================================

def _get_parent_user_id(user_id: int) -> Optional[int]:
    """
    If user_id belongs to a sub-user (is_sub_user=TRUE), return parent_user_id.
    Returns None for normal (top-level) users.
    Used so team IDs inherit credentials from the account that created them.
    """
    try:
        row = execute_query(
            """
            SELECT parent_user_id
            FROM ai_infrastructure.users
            WHERE id = %s AND is_sub_user = TRUE
            """,
            (user_id,),
            fetch_mode='one'
        )
        if row:
            return row.get('parent_user_id')
    except Exception as e:
        logger.debug(f"[ORG_CREDS_LOADER] parent_user_id lookup failed for user_id={user_id}: {e}")
    return None


def _get_org_id_for_user(user_id: int) -> Optional[int]:
    """Reusable: org_id lookup with sub-user -> parent-org fallback.

    Returns the user's organisation_id, or — when the user is a sub-user
    without a direct org — the parent user's organisation_id. Returns None
    when neither has an org.

    Used by resolve_credentials() (Phase-1 parallel pair) and by
    _get_org_credential() (when no org_id is supplied by the caller).
    The original sub-user debug log line is preserved here so behavioural
    parity with the pre-Change-2 _get_org_credential holds.
    """
    try:
        org_id = execute_query(
            "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
            (user_id,),
            fetch_mode='value',
        )
        if not org_id:
            parent_id = _get_parent_user_id(user_id)
            if parent_id:
                org_id = execute_query(
                    "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                    (parent_id,),
                    fetch_mode='value',
                )
                if org_id:
                    logger.debug(
                        f"[ORG_CREDS_LOADER] Sub-user {user_id} has no org, using parent "
                        f"{parent_id}'s org_id={org_id}"
                    )
        return org_id or None
    except Exception as e:
        logger.debug(f"[ORG_CREDS_LOADER] org_id lookup failed for user_id={user_id}: {e}")
    return None


# ============================================================================
# MAIN RESOLVER
# ============================================================================

def resolve_credentials(
    user_id: int,
    platform: str,
    prefer_user: bool = True,
    env_fallback: Optional[str] = None,
    bypass_cache: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Resolve API credentials for a platform using a 4-tier lookup:
        1.  User-specific credential         (personal OAuth tokens, personal API keys)
        1.5 Sub-user inherits parent creds   (sub-user has no personal creds → inherit from parent)
        2.  Org-level credential             (shared across the entire organisation)
        3.  Environment variable             (legacy fallback, no per-org billing isolation)

    Args:
        user_id:      The authenticated user making the request.
        platform:     Platform name (e.g. 'anthropic', 'openai', 'auspost').
        prefer_user:  If True (default), try user-specific first.
                      If False, go straight to org level.
                      Useful for org-shared platforms like AusPost where no user
                      would ever have a personal account.
        env_fallback: Override the env var name to fall back to.
                      If None, uses PLATFORM_ENV_VARS mapping.
        bypass_cache: Skip Redis cache and force fresh DB reads.

    Returns:
        Dict with at minimum one of:
            { 'credential_value': 'sk-ant-...' }         ← simple key
            { 'credentials': { 'api_key': '...' } }      ← complex multi-field
            { 'api_key': '...' }                          ← normalised shorthand
        Returns None only if absolutely nothing is found.

    Source tagging:
        The returned dict always includes '_source' key with value:
            'user'  → came from user_platform_credentials
            'org'   → came from organisation_platform_credentials
            'env'   → came from environment variable (legacy)
    """
    platform = _canonicalize_platform(platform)

    def _preview(raw: str) -> str:
        """Safe masked preview: first 6 + … + last 4 (or '***' for short/empty)."""
        if not raw:
            return '***'
        if len(raw) <= 14:
            return '***'
        return f"{raw[:6]}…{raw[-4:]}"

    def _extract_key(cred: Optional[Dict[str, Any]]) -> str:
        if not cred:
            return ''
        return (
            cred.get('credential_value')
            or cred.get('api_key')
            or (cred.get('credentials') or {}).get('api_key')
            or (cred.get('credentials') or {}).get('access_token')
            or (cred.get('credentials') or {}).get('secret_key')
            or ''
        )

    # ------------------------------------------------------------------
    # TIER 1: User-specific credential
    # ------------------------------------------------------------------
    if prefer_user:
        user_cred = _get_user_credential(user_id, platform, bypass_cache)
        if user_cred:
            user_cred['_source'] = 'user'
            logger.info(
                f"[ORG_CREDS_LOADER] ✅ Resolved {platform} from USER credential "
                f"(Tier 1, user_id={user_id}, key={_preview(_extract_key(user_cred))})"
            )
            return user_cred

    # ------------------------------------------------------------------
    # TIER 1.5 + TIER 2: parallelised (2026-07-26, Change 2)
    # Team IDs (is_sub_user=TRUE) share their creator's platform
    # credentials; org credentials additionally fall back to the parent
    # user's org when the sub-user has no direct org_id.
    #
    # Two parallel phases (module-level _spawn_pair):
    #   Phase 1: _get_parent_user_id || _get_org_id_for_user   (2 PK lookups)
    #   Phase 2: Tier 1.5 (parent creds) || Tier 2 (org creds) (2 platform lookups)
    # Net: ~4 effective round-trips with parallelism instead of 4 serial.
    # Behaviour preserved: prefer_user is honoured; env_fallback (Tier 3)
    # and the post-Tier-2 'prefer_user=False' user retry are unchanged.
    # ------------------------------------------------------------------

    def _p1_parent():
        return _get_parent_user_id(user_id)
    def _p1_org():
        return _get_org_id_for_user(user_id)
    parent_id, org_id = _spawn_pair(_p1_parent, _p1_org)

    def _p2_parent_cred():
        if not parent_id:
            return None
        try:
            return _get_user_credential(parent_id, platform, bypass_cache)
        except Exception as e:
            logger.debug(f"[ORG_CREDS_LOADER] Tier 1.5 DB error: {e}")
            return None
    def _p2_org_cred():
        if not org_id:
            return None
        try:
            # 2026-07-26 Change 2: pass the pre-resolved org_id through so we
            # don't re-query users.organisation_id inside _get_org_credential.
            return _get_org_credential(user_id, platform, bypass_cache, org_id=org_id)
        except Exception as e:
            logger.debug(f"[ORG_CREDS_LOADER] Tier 2 DB error: {e}")
            return None
    parent_user_cred, org_cred = _spawn_pair(_p2_parent_cred, _p2_org_cred)

    if parent_user_cred:
        parent_user_cred['_source'] = 'parent_user'
        logger.info(
            f"[ORG_CREDS_LOADER] ✅ Resolved {platform} from PARENT user credential "
            f"(Tier 1.5, sub_user_id={user_id}, parent_user_id={parent_id}, "
            f"key={_preview(_extract_key(parent_user_cred))})"
        )
        return parent_user_cred

    if org_cred:
        org_cred['_source'] = 'org'
        logger.info(
            f"[ORG_CREDS_LOADER] ✅ Resolved {platform} from ORG credential "
            f"(Tier 2, user_id={user_id}, key={_preview(_extract_key(org_cred))})"
        )
        return org_cred

    # If prefer_user=False we haven't tried user yet — try it as second option
    if not prefer_user:
        user_cred = _get_user_credential(user_id, platform, bypass_cache)
        if user_cred:
            user_cred['_source'] = 'user'
            logger.info(
                f"[ORG_CREDS_LOADER] ✅ Resolved {platform} from USER credential "
                f"(Tier 1 fallback, user_id={user_id}, key={_preview(_extract_key(user_cred))})"
            )
            return user_cred

    # ------------------------------------------------------------------
    # TIER 3: Environment variable fallback
    # ------------------------------------------------------------------
    # Case-insensitive lookup: the dict uses canonical names (some capitalised,
    # some not — e.g. 'MiniMax') but callers may pass either case.
    env_key = env_fallback
    if not env_key:
        env_key = PLATFORM_ENV_VARS.get(platform)
        if not env_key:
            for k, v in PLATFORM_ENV_VARS.items():
                if k.lower() == platform:
                    env_key = v
                    break
    if env_key:
        env_val = os.getenv(env_key)
        if env_val:
            logger.warning(
                f"[ORG_CREDS_LOADER] ⚠️  Using env var {env_key} for platform={platform} "
                f"(Tier 3, user_id={user_id}, key={_preview(env_val)}). "
                f"Per-org billing isolation is NOT enforced — migrate to org credentials."
            )
            return {
                '_source':      'env',
                '_env_var':     env_key,
                'credential_value': env_val,
                'api_key':      env_val,
            }

    logger.warning(
        f"[ORG_CREDS_LOADER] ❌ No credential found for platform={platform}, user_id={user_id}. "
        f"Check org or user credentials in the admin panel."
    )
    return None


# ============================================================================
# CONVENIENCE SHORTHAND
# ============================================================================

def resolve_api_key(
    user_id: int,
    platform: str,
    prefer_user: bool = True,
) -> Optional[str]:
    """
    Convenience wrapper that returns just the API key string, or None.
    Checks credential_value → credentials.api_key → credentials.access_token in that order.

    Usage:
        api_key = resolve_api_key(user_id, 'anthropic')
        if not api_key:
            return {"error": "Anthropic API key not configured for this organisation"}
    """
    cred = resolve_credentials(user_id, platform, prefer_user=prefer_user)
    if not cred:
        return None

    return (
        cred.get('credential_value')
        or cred.get('api_key')
        or (cred.get('credentials') or {}).get('api_key')
        or (cred.get('credentials') or {}).get('access_token')
        or (cred.get('credentials') or {}).get('secret_key')
    )


# ============================================================================
# BATCH RESOLVER - resolve_api_keys_batch
# ============================================================================
# Added 2026-07-26 (fix #2 for /api/transcription/engines-status).
#
# The /engines-status route previously called resolve_api_key() in a loop,
# once per platform (openai, assemblyai, deepgram, speechmatics). Each
# call cost:
#   - 1 Redis lookup + 1 SQL round-trip to user_platform_credentials (Tier 1)
#   - 1 SQL round-trip for parent_user_id if sub-user (Tier 1.5)
#   - 1 SQL round-trip to users.organisation_id + 1 to
#     organisation_platform_credentials (Tier 2)
#   - env-var dict lookup (Tier 3, free)
# For 4 platforms that's ~12 round-trips on a cold cache; gevent single-
# worker on Render Starter serialises them and the user sees ~30s wall-
# clock per status tick.
#
# This batched variant keeps the 4-tier resolution semantics (with the
# same prefer_user default) but consolidates to:
#   - 1 SQL round-trip per tier using `WHERE platform = ANY(%s)`
#   - 1 lookup for parent_user_id if needed
#   - 1 lookup for organisation_id if needed
# Net: at most ~4 SQL round-trips for N platforms (independent of N).
#
# The decryption (Fernet) per row still happens via _normalise_row - that
# cost is unavoidable. Returns a {canonical_platform: api_key_or_None}
# dict. The canonical form is the DB storage form (lowercase except
# 'MiniMax').

def _extract_api_key_from_norm(norm):
    """Extract the API key string from an already-normalised credential
    dict. Mirrors resolve_api_key()'s fallback chain without re-deriving
    _source. Returns '' when no key is present.
    """
    if not norm:
        return ''
    return (
        norm.get('credential_value')
        or norm.get('api_key')
        or (norm.get('credentials') or {}).get('api_key')
        or (norm.get('credentials') or {}).get('access_token')
        or (norm.get('credentials') or {}).get('secret_key')
        or ''
    )


def resolve_api_keys_batch(user_id, platforms, prefer_user=True):
    """Batched version of resolve_api_key - resolves N platform keys
    at once via single SQL queries per tier (vs N per-platform queries).

    Resolution order matches resolve_credentials():
        Tier 1    - user_platform_credentials (with Redis cache per-plat)
        Tier 1.5  - sub-user -> parent_user_credentials
        Tier 2    - organisation_platform_credentials (org_id once)
        Tier 3    - PLATFORM_ENV_VARS / os.getenv() fallback

    Args:
        user_id:    Authenticated user making the request.
        platforms:  Iterable of platform names (any case; canonicalised).
        prefer_user: See resolve_credentials().

    Returns:
        Dict mapping *canonical* platform name -> API key string or None.

    Parallelism (2026-07-26, fix #2b for /api/transcription/engines-status):
        On Render (gevent single-worker + Supabase pooler, 15-conn limit) the
        four SQL round-trips - Tier 1 DB, _get_parent_user_id, users.org_id
        lookup, Tier 1.5 DB, Tier 2 DB - serialise behind the same event loop
        and each one waits ~2-3s at pool.getconn(). That made the cold path
        ~9.57s in practice despite the prior batched-SQL optimisation.

        This variant runs the independent ID lookups (parent_user_id and
        users.organisation_id) in parallel greenlets, then runs the two
        remaining tier queries (parent creds and org creds) in parallel
        after those IDs are resolved. Falls back to sequential execution
        when gevent is not importable (e.g. local dev server).

    Graceful degradation:
        - Each greenlet pair has a 5.0s joinall timeout; slow queries fall
          through as empty results instead of blocking the route.
        - Each tier's own try/except still swallows DB errors and logs at
          debug; the caller never sees a credential-resolver exception.
    """
    if not platforms:
        return {}
    canonicals = []
    seen = set()
    for p in platforms:
        c = _canonicalize_platform(p)
        if c and c not in seen:
            seen.add(c)
            canonicals.append(c)
    if not canonicals:
        return {}

    result = {p: None for p in canonicals}
    missing = list(canonicals)

    # Detect gevent once per call. Cheaper than hoisting to module scope
    # and avoids triggering the import at module load (gevent is only
    # installed in the gunicorn-geventworker runtime, not local dev).
    try:
        import gevent
        _HAS_GEVENT = True
    except Exception:
        gevent = None
        _HAS_GEVENT = False

    def _spawn_pair(coro_a, coro_b, timeout=5.0):
        """Run two zero-arg callables concurrently via gevent if available;
        otherwise sequentially. Returns (val_a, val_b). Exceptions inside
        the callables are swallowed inside each callable; if a greenlet
        dies unexpectedly we return None for that branch."""
        if _HAS_GEVENT:
            ga = gevent.spawn(coro_a)
            gb = gevent.spawn(coro_b)
            gevent.joinall([ga, gb], timeout=timeout)
            va = ga.value if not ga.dead else None
            vb = gb.value if not gb.dead else None
            if ga.dead and ga.exception:
                logger.debug(f"[ORG_CREDS_BATCH] greenlet A died: {ga.exception}")
            if gb.dead and gb.exception:
                logger.debug(f"[ORG_CREDS_BATCH] greenlet B died: {gb.exception}")
            return va, vb
        return coro_a(), coro_b()

    # ----- Tier 1: user_platform_credentials (cache -> DB) -----
    if prefer_user and missing:
        # Per-platform Redis cache lookup stays sequential (microsecond range,
        # no I/O wait - geventing it would add overhead, not save any).
        try:
            from AI_infrastructure.utils.cache_utils import get_cached_platform_credentials
        except Exception:
            get_cached_platform_credentials = None

        if get_cached_platform_credentials is not None:
            still_missing = []
            for p in missing:
                try:
                    cached = get_cached_platform_credentials(user_id, p)
                    key = _extract_api_key_from_norm(cached) if cached else ''
                    if key:
                        result[p] = key
                    else:
                        still_missing.append(p)
                except Exception:
                    still_missing.append(p)
            missing = still_missing

        # Tier 1 DB: single batched query (already O(1) round-trips vs N).
        if missing:
            try:
                rows = execute_query(
                    """
                    SELECT platform, credential_type, credential_key,
                           credential_value, credentials, metadata
                    FROM ai_infrastructure.user_platform_credentials
                    WHERE user_id = %s
                      AND platform = ANY(%s)
                      AND is_active = TRUE
                    ORDER BY platform, updated_at DESC
                    """,
                    (user_id, missing),
                    fetch_mode='all',
                ) or []
                seen_p = set()
                for row in rows:
                    p = row.get('platform') if isinstance(row, dict) else None
                    if not p or p in seen_p:
                        continue
                    seen_p.add(p)
                    norm = _normalise_row(dict(row))
                    key = _extract_api_key_from_norm(norm)
                    if key:
                        result[p] = key
                missing = [p for p in missing if result.get(p) is None]
            except Exception as e:
                logger.debug(f"[ORG_CREDS_BATCH] Tier 1 DB error: {e}")

    if not missing:
        return result

    # ----- Phase 1 (parallel): parent_user_id + users.organisation_id -----
    # Both are PK lookups on users; independent. Sequential cost ~2 * pool-
    # wait (~5-6s on Render). Parallel cost ~1 * pool-wait (~2-3s).
    def _lookup_parent():
        return _get_parent_user_id(user_id)

    def _lookup_org():
        try:
            return execute_query(
                "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                (user_id,),
                fetch_mode='value',
            )
        except Exception as e:
            logger.debug(f"[ORG_CREDS_BATCH] org_id lookup failed: {e}")
            return None

    parent_id, org_id = _spawn_pair(_lookup_parent, _lookup_org)

    # ----- Phase 2 (parallel): Tier 1.5 (parent creds) + Tier 2 (org creds) -----
    # Tier 2 needs org_id; if user has none, fall back to parent_user's org
    # (matches original behaviour). The fallback itself is one extra query
    # but only when needed; we still parallelise the two tier queries.

    def _tier_15_query():
        if not parent_id:
            return {}
        try:
            rows = execute_query(
                """
                SELECT platform, credential_type, credential_key,
                       credential_value, credentials, metadata
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s
                  AND platform = ANY(%s)
                  AND is_active = TRUE
                ORDER BY platform, updated_at DESC
                """,
                (parent_id, missing),
                fetch_mode='all',
            ) or []
            seen_p = set()
            out = {}
            for row in rows:
                p = row.get('platform') if isinstance(row, dict) else None
                if not p or p in seen_p:
                    continue
                seen_p.add(p)
                norm = _normalise_row(dict(row))
                k = _extract_api_key_from_norm(norm)
                if k:
                    out[p] = k
            return out
        except Exception as e:
            logger.debug(f"[ORG_CREDS_BATCH] Tier 1.5 DB error: {e}")
            return {}

    def _tier_2_query():
        org = org_id
        if not org and parent_id:
            try:
                org = execute_query(
                    "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                    (parent_id,),
                    fetch_mode='value',
                )
            except Exception as e:
                logger.debug(f"[ORG_CREDS_BATCH] Tier 2 parent org_id fallback failed: {e}")
                org = None
        if not org:
            return {}
        try:
            rows = execute_query(
                """
                SELECT platform, credential_value, credentials,
                       display_name, environment, last_used_at
                FROM ai_infrastructure.organisation_platform_credentials
                WHERE organisation_id = %s
                  AND platform = ANY(%s)
                  AND is_active = TRUE
                ORDER BY platform,
                         environment = 'production' DESC,
                         updated_at DESC
                """,
                (org, missing),
                fetch_mode='all',
            ) or []
            seen_p = set()
            out = {}
            for row in rows:
                p = row.get('platform') if isinstance(row, dict) else None
                if not p or p in seen_p:
                    continue
                seen_p.add(p)
                norm = _normalise_row(dict(row))
                k = _extract_api_key_from_norm(norm)
                if k:
                    out[p] = k
            return out
        except Exception as e:
            logger.debug(f"[ORG_CREDS_BATCH] Tier 2 DB error: {e}")
            return {}

    tier15_res, tier2_res = _spawn_pair(_tier_15_query, _tier_2_query)

    # Merge in tier-priority order: Tier 1.5 wins over Tier 2 if both hit.
    for p, k in (tier15_res or {}).items():
        if result.get(p) is None:
            result[p] = k
    for p, k in (tier2_res or {}).items():
        if result.get(p) is None:
            result[p] = k
    missing = [p for p in missing if result.get(p) is None]

    # ----- Tier 3: env var fallback (in-process, no DB) -----
    for p in missing:
        env_key = PLATFORM_ENV_VARS.get(p)
        if not env_key:
            for k, v in PLATFORM_ENV_VARS.items():
                if k.lower() == p:
                    env_key = v
                    break
        if env_key:
            val = os.getenv(env_key)
            if val:
                result[p] = val
                logger.warning(
                    f"[ORG_CREDS_BATCH] Using env var {env_key} for {p} "
                    f"(Tier 3 - legacy, no per-org isolation)"
                )

    return result


# ============================================================================
# INTERNAL: FETCH FROM user_platform_credentials
# ============================================================================

def _get_user_credential(
    user_id: int,
    platform: str,
    bypass_cache: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Fetch a user-specific credential row from user_platform_credentials.
    Returns normalised dict or None.
    """
    # Try Redis cache first (unless bypassed)
    if not bypass_cache:
        try:
            from AI_infrastructure.utils.cache_utils import get_cached_platform_credentials
            cached = get_cached_platform_credentials(user_id, platform)
            if cached:
                return cached
        except Exception:
            pass  # Cache unavailable — fall through to DB

    try:
        row = execute_query(
            """
            SELECT platform, credential_type, credential_key,
                   credential_value, credentials, metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s
              AND platform = %s
              AND is_active = TRUE
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (user_id, platform),
            fetch_mode='one'
        )
    except Exception as e:
        logger.error(f"[ORG_CREDS_LOADER] DB error fetching user credential: {e}")
        return None

    if not row:
        return None

    return _normalise_row(row)


# ============================================================================
# INTERNAL: FETCH FROM organisation_platform_credentials
# ============================================================================

def _get_org_credential(
    user_id: int,
    platform: str,
    bypass_cache: bool = False,
    org_id: Optional[int] = None,   # NEW 2026-07-26 (Change 2): when provided, skip the users.organisation_id SELECT
) -> Optional[Dict[str, Any]]:
    """
    Fetch the active org-level credential for a platform.
    Looks up the user's organisation_id (unless the caller already has it),
    then fetches the credential from organisation_platform_credentials.

    Args:
        org_id: If supplied by the caller (e.g. resolve_credentials' Phase-1
                parallel pair already resolved it), skip the org_id lookup
                to save a duplicate round-trip in the same request. When
                None, falls back to _get_org_id_for_user() which handles
                the sub-user -> parent-org fallback.

    Returns normalised dict or None.
    """
    try:
        # 2026-07-26 Change 2: trust pre-resolved org_id from caller; otherwise
        # fall back to the helper that handles sub-user->parent-org fallback.
        if org_id is None:
            org_id = _get_org_id_for_user(user_id)
        if not org_id:
            return None

        # Fetch the most recently updated active credential for this platform
        row = execute_query(
            """
            SELECT
                platform,
                credential_value,
                credentials,
                display_name,
                environment,
                last_used_at
            FROM ai_infrastructure.organisation_platform_credentials
            WHERE organisation_id = %s
              AND platform = %s
              AND is_active = TRUE
            ORDER BY
                environment = 'production' DESC,  -- prefer production keys
                updated_at DESC
            LIMIT 1
            """,
            (org_id, platform),
            fetch_mode='one'
        )
    except Exception as e:
        logger.error(f"[ORG_CREDS_LOADER] DB error fetching org credential: {e}")
        return None

    if not row:
        return None

    # Update last_used_at (non-blocking — ignore failures)
    try:
        execute_query(
            """
            UPDATE ai_infrastructure.organisation_platform_credentials
            SET last_used_at = NOW()
            WHERE organisation_id = (
                SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s
            ) AND platform = %s AND is_active = TRUE
            """,
            (user_id, platform)
        )
    except Exception:
        pass

    return _normalise_row(row)


# ============================================================================
# INTERNAL: NORMALISE A DATABASE ROW
# ============================================================================

def _normalise_row(row: dict) -> Dict[str, Any]:
    """
    Convert a raw DB row into a unified credential dict.
    Works for both user_platform_credentials and organisation_platform_credentials rows.
    """
    result = dict(row)

    # GAP-L7: decrypt credential_value if it was stored encrypted
    try:
        from AI_infrastructure.shared.credential_crypto import decrypt_credential
        if result.get('credential_value'):
            result['credential_value'] = decrypt_credential(result['credential_value'])
    except Exception:
        pass  # passthrough if module unavailable

    # Parse JSONB credentials if it came back as a string
    credentials = row.get('credentials')
    if isinstance(credentials, str):
        try:
            credentials = json.loads(credentials)
        except Exception:
            credentials = {}
    result['credentials'] = credentials or {}

    # Shorthand: expose api_key at top level if buried in credentials
    if not result.get('api_key') and result['credentials'].get('api_key'):
        result['api_key'] = result['credentials']['api_key']

    if not result.get('credential_value') and result['credentials'].get('api_key'):
        result['credential_value'] = result['credentials']['api_key']

    return result


# ============================================================================
# DIAGNOSTIC / TESTING
# ============================================================================

def get_credential_source_info(user_id: int, platform: str) -> dict:
    """
    Diagnostic helper: shows where a credential would come from
    without actually returning the sensitive value.
    Useful for admin dashboards and debugging.

    Returns:
        {
            'platform': 'anthropic',
            'user_has_personal_key':  False,
            'org_has_key':           True,
            'env_var_available':     True,
            'resolution_source':     'org',   # what resolve_credentials would use
            'org_name':              'Acme Corp',
        }
    """
    platform = _canonicalize_platform(platform)
    has_user = bool(_get_user_credential(user_id, platform))

    org_id = execute_query(
        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (user_id,),
        fetch_mode='value'
    )
    has_org = False
    org_name = None
    if org_id:
        org_row = execute_query(
            """
            SELECT c.id, o.name
            FROM ai_infrastructure.organisation_platform_credentials c
            JOIN ai_infrastructure.organisations o ON o.id = c.organisation_id
            WHERE c.organisation_id = %s AND c.platform = %s AND c.is_active = TRUE
            LIMIT 1
            """,
            (org_id, platform),
            fetch_mode='one'
        )
        has_org = bool(org_row)
        org_name = org_row.get('name') if org_row else None

    env_key = PLATFORM_ENV_VARS.get(platform)
    has_env = bool(env_key and os.getenv(env_key))

    if has_user:
        source = 'user'
    elif has_org:
        source = 'org'
    elif has_env:
        source = 'env'
    else:
        source = 'none'

    return {
        'platform':               platform,
        'user_has_personal_key':  has_user,
        'org_has_key':            has_org,
        'env_var_available':      has_env,
        'env_var_name':           env_key,
        'resolution_source':      source,
        'org_name':               org_name,
    }

# ============================================================================
# GAP-M3: PER-ORG AI PROVIDER / MODEL CONFIG
# ============================================================================

def get_provider_for_model(model_id: str) -> str:
    """Infer the API provider from a model identifier.

    Used when user selects a model in the UI without explicitly choosing a
    provider.  Lookup order:
      1. ai_model_catalog DB table (most accurate)
      2. Regex prefix fallback (always succeeds)

    Returns one of: 'anthropic', 'openai', 'deepseek', 'MiniMax'
    """
    import re
    if not model_id:
        return 'anthropic'

    # Fast prefix-based detection (no DB hit required)
    if model_id.startswith('claude-'):
        return 'anthropic'
    if model_id.startswith(('gpt-', 'chatgpt-', 'text-davinci', 'davinci')) or \
       re.match(r'^o[0-9]', model_id):
        return 'openai'
    if model_id.startswith('deepseek-'):
        return 'deepseek'
    if model_id.startswith(('MiniMax-', 'M2-her', 'M2.7-', 'M2.5-', 'M2.1-')):
        return 'MiniMax'

    # Fallback: try the catalog table for exotic model names
    try:
        row = execute_query(
            "SELECT provider FROM ai_infrastructure.ai_model_catalog WHERE model_id = %s LIMIT 1",
            (model_id,),
            fetch_mode='one'
        )
        if row:
            return row['provider']
    except Exception:
        pass

    return 'anthropic'


# Provider → default model fallbacks used when the org row has no model set
_PROVIDER_DEFAULT_MODELS: Dict[str, str] = {
    'anthropic': 'claude-sonnet-4-6',   # Claude Sonnet 4.6 — recommended (no date suffix)
    'openai':    'gpt-5.4',
    'deepseek':  'deepseek-chat',
    'MiniMax':   'MiniMax-M3',          # Frontier 1M-context model
}

_PROVIDER_DEFAULT_MAX_TOKENS: Dict[str, int] = {
    'anthropic': 8192,
    'openai':    4096,
    'deepseek':  8192,
    'MiniMax':   8192,
}


def get_org_ai_config(user_id: int) -> Dict[str, Any]:
    """
    Return the AI provider, model, and max_tokens configured for the user's
    organisation.  Falls back to sensible defaults if the columns are missing
    (e.g. migration 031 not yet applied) or the user has no org.

    Returns:
        {
            'provider':   'anthropic',                    # str
            'model':      'claude-sonnet-4-5-20250929',   # str
            'max_tokens': 8192,                           # int
        }

    Usage (in flask_app.py / process_streaming):
        from AI_infrastructure.shared.org_credentials_loader import get_org_ai_config
        ai_cfg = get_org_ai_config(user_id)
        provider = ai_cfg['provider']
        model    = ai_cfg['model']
    """
    default = {
        'provider':   'anthropic',
        'model':      _PROVIDER_DEFAULT_MODELS['anthropic'],
        'max_tokens': _PROVIDER_DEFAULT_MAX_TOKENS['anthropic'],
    }

    if not user_id:
        return default

    try:
        row = execute_query(
            """
            SELECT o.ai_provider, o.ai_model, o.ai_max_tokens
            FROM ai_infrastructure.users u
            JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
            WHERE u.id = %s
            LIMIT 1
            """,
            (user_id,),
            fetch_mode='one'
        )
        if not row:
            return default

        provider = (row.get('ai_provider') or 'anthropic').lower()
        model    = row.get('ai_model') or _PROVIDER_DEFAULT_MODELS.get(provider, 'claude-sonnet-4-6')
        max_tok  = row.get('ai_max_tokens') or _PROVIDER_DEFAULT_MAX_TOKENS.get(provider, 8192)

        # Validate provider is known
        if provider not in _PROVIDER_DEFAULT_MODELS:
            logger.warning(f"[ORG_AI_CONFIG] Unknown provider '{provider}' for user {user_id}, defaulting to anthropic")
            provider = 'anthropic'
            model    = _PROVIDER_DEFAULT_MODELS['anthropic']

        return {
            'provider':   provider,
            'model':      model,
            'max_tokens': int(max_tok),
        }

    except Exception as e:
        logger.warning(f"[ORG_AI_CONFIG] Could not load org AI config for user {user_id}: {e} – using defaults")
        return default


# ---------------------------------------------------------------------------
# GAP-M1: Per-org module access helper
# ---------------------------------------------------------------------------

def get_org_enabled_modules(user_id: int) -> set:
    """
    Return the set of module_name strings that are enabled for the organisation
    that *user_id* belongs to.

    Resolution order:
        1. Explicit overrides in org_module_access (is_enabled=TRUE/FALSE).
        2. Plan-tier defaults from plan_modules (for modules NOT in overrides).

    Returns an empty set on any error (fail-open: callers must handle gracefully).
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query

        # Look up the org's plan tier
        org_row = execute_query(
            """
            SELECT o.id AS org_id, o.plan_tier
            FROM   ai_infrastructure.users u
            JOIN   ai_infrastructure.organisations o ON o.id = u.organisation_id
            WHERE  u.id = %s
            LIMIT 1
            """,
            (user_id,),
            fetch_mode='one'
        )
        if not org_row:
            return set()

        org_id    = org_row['org_id']
        plan_tier = (org_row.get('plan_tier') or 'free').lower()

        # Fetch plan defaults for this tier (plan_modules table added in migration 038)
        try:
            plan_rows = execute_query(
                """
                SELECT module_name
                FROM   ai_infrastructure.plan_modules
                WHERE  plan_tier = %s
                """,
                (plan_tier,),
                fetch_mode='all'
            ) or []
            enabled = {r['module_name'] for r in plan_rows}
        except Exception as plan_err:
            logger.warning(f"[ORG_MODULES] plan_modules table not found (migration 038 pending): {plan_err}")
            enabled = set()

        # Apply per-org overrides
        override_rows = execute_query(
            """
            SELECT module_name, is_enabled
            FROM   ai_infrastructure.org_module_access
            WHERE  organisation_id = %s
            """,
            (org_id,),
            fetch_mode='all'
        ) or []
        for r in override_rows:
            if r['is_enabled']:
                enabled.add(r['module_name'])
            else:
                enabled.discard(r['module_name'])

        return enabled

    except Exception as e:
        logger.warning(f"[ORG_MODULES] Could not load module access for user {user_id}: {e}")
        return set()


def get_user_enabled_modules(user_id: int) -> set:
    """
    Return the set of module_name strings that are effectively enabled for
    a specific user, applying BOTH org-level enablement and per-user restrictions.

    Resolution order:
        0. Owner role  → ALL active modules (bypass plan / org / user restrictions).
        1. Start with org-enabled modules  (from get_org_enabled_modules)
        2. Remove any modules where user_module_access.is_enabled = FALSE

    Key constraint: user overrides can only RESTRICT.
    A user can never access a module their organisation has disabled.
    Absence of a user_module_access row = inherit the org setting.

    Falls back to get_org_enabled_modules() if the user_module_access table
    does not yet exist (pre-migration 039), so this function is always safe to call.
    """
    try:
        # ── Layer 0: platform_developer / admin / owner bypass ALL restrictions ─
        # Check both system-level role (users.role) and org-level role (users.org_role)
        role_row = execute_query(
            "SELECT org_role, role AS system_role FROM ai_infrastructure.users WHERE id = %s",
            (user_id,),
            fetch_mode='one'
        )
        is_super = (
            role_row and (
                role_row.get('system_role') in ('platform_developer', 'admin')
                or role_row.get('org_role') == 'owner'
            )
        )
        if is_super:
            all_modules = execute_query(
                "SELECT module_name FROM ai_infrastructure.module_catalog WHERE is_active = TRUE",
                fetch_mode='all'
            ) or []
            effective = role_row.get('system_role') or role_row.get('org_role')
            logger.debug(f"[USER_MODULES] Super user {user_id} ({effective}) — returning all {len(all_modules)} active modules")
            return {r['module_name'] for r in all_modules}
    except Exception as e:
        logger.warning(f"[USER_MODULES] Role check failed for user {user_id}: {e}")
        # Fall through to normal resolution

    try:
        org_enabled = get_org_enabled_modules(user_id)
        if not org_enabled:
            return set()

        restriction_rows = execute_query(
            """
            SELECT module_name
            FROM   ai_infrastructure.user_module_access
            WHERE  user_id    = %s
              AND  is_enabled = FALSE
            """,
            (user_id,),
            fetch_mode='all'
        ) or []

        for r in restriction_rows:
            org_enabled.discard(r['module_name'])

        return org_enabled

    except Exception as e:
        # Graceful fallback: if table doesn't exist yet, return org-level modules
        logger.warning(
            f"[USER_MODULES] user_module_access unavailable for user {user_id} "
            f"(migration 039 pending?): {e}"
        )
        return get_org_enabled_modules(user_id)