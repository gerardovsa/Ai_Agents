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
    'anthropic':  'ANTHROPIC_API_KEY',
    'openai':     'OPENAI_API_KEY',
    'auspost':    'AUSPOST_API_KEY',
    'stripe':     'STRIPE_SECRET_KEY',
    'assemblyai': 'ASSEMBLYAI_API_KEY',
    'twilio':     'TWILIO_AUTH_TOKEN',
    'sendgrid':   'SENDGRID_API_KEY',
    'pinecone':   'PINECONE_API_KEY',
    'deepseek':   'DEEPSEEK_API_KEY',
}


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
    Resolve API credentials for a platform using a 3-tier lookup:
        1. User-specific credential  (personal OAuth tokens, personal API keys)
        2. Org-level credential      (shared across the entire organisation)
        3. Environment variable      (legacy fallback, no per-org billing isolation)

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
    platform = platform.lower().strip()

    # ------------------------------------------------------------------
    # TIER 1: User-specific credential
    # ------------------------------------------------------------------
    if prefer_user:
        user_cred = _get_user_credential(user_id, platform, bypass_cache)
        if user_cred:
            user_cred['_source'] = 'user'
            logger.debug(f"[ORG_CREDS_LOADER] Resolved {platform} from user credential (user_id={user_id})")
            return user_cred

    # ------------------------------------------------------------------
    # TIER 2: Organisation-level credential
    # ------------------------------------------------------------------
    org_cred = _get_org_credential(user_id, platform, bypass_cache)
    if org_cred:
        org_cred['_source'] = 'org'
        logger.debug(f"[ORG_CREDS_LOADER] Resolved {platform} from org credential (user_id={user_id})")
        return org_cred

    # If prefer_user=False we haven't tried user yet — try it as second option
    if not prefer_user:
        user_cred = _get_user_credential(user_id, platform, bypass_cache)
        if user_cred:
            user_cred['_source'] = 'user'
            logger.debug(f"[ORG_CREDS_LOADER] Resolved {platform} from user credential (fallback, user_id={user_id})")
            return user_cred

    # ------------------------------------------------------------------
    # TIER 3: Environment variable fallback
    # ------------------------------------------------------------------
    env_key = env_fallback or PLATFORM_ENV_VARS.get(platform)
    if env_key:
        env_val = os.getenv(env_key)
        if env_val:
            logger.warning(
                f"[ORG_CREDS_LOADER] Using env var {env_key} for platform={platform}. "
                f"Consider migrating to org credentials for proper per-org isolation. "
                f"(user_id={user_id})"
            )
            return {
                '_source':      'env',
                '_env_var':     env_key,
                'credential_value': env_val,
                'api_key':      env_val,
            }

    logger.warning(
        f"[ORG_CREDS_LOADER] No credential found for platform={platform}, user_id={user_id}. "
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
) -> Optional[Dict[str, Any]]:
    """
    Fetch the active org-level credential for a platform.
    Looks up the user's organisation_id, then fetches the credential from
    organisation_platform_credentials.

    Returns normalised dict or None.
    """
    try:
        # Get the user's organisation
        org_id = execute_query(
            "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
            (user_id,),
            fetch_mode='value'
        )
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

# Provider → default model fallbacks used when the org row has no model set
_PROVIDER_DEFAULT_MODELS: Dict[str, str] = {
    'anthropic': 'claude-sonnet-4-5-20250929',
    'openai':    'gpt-4o',
    'deepseek':  'deepseek-chat',
}

_PROVIDER_DEFAULT_MAX_TOKENS: Dict[str, int] = {
    'anthropic': 8192,
    'openai':    4096,
    'deepseek':  8192,
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
        model    = row.get('ai_model') or _PROVIDER_DEFAULT_MODELS.get(provider, 'claude-sonnet-4-5-20250929')
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

        # Fetch plan defaults for this tier
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