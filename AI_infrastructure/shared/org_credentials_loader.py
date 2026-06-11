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
    platform = platform.lower().strip()

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
    # TIER 1.5: Sub-user → parent user credential inheritance
    # Team IDs (is_sub_user=TRUE) share their creator's platform credentials.
    # ------------------------------------------------------------------
    parent_id = _get_parent_user_id(user_id)
    if parent_id:
        parent_user_cred = _get_user_credential(parent_id, platform, bypass_cache)
        if parent_user_cred:
            parent_user_cred['_source'] = 'parent_user'
            logger.info(
                f"[ORG_CREDS_LOADER] ✅ Resolved {platform} from PARENT user credential "
                f"(Tier 1.5, sub_user_id={user_id}, parent_user_id={parent_id}, "
                f"key={_preview(_extract_key(parent_user_cred))})"
            )
            return parent_user_cred

    # ------------------------------------------------------------------
    # TIER 2: Organisation-level credential
    # _get_org_credential already handles sub-user → parent org fallback
    # internally, so this covers both normal users and sub-users.
    # ------------------------------------------------------------------
    org_cred = _get_org_credential(user_id, platform, bypass_cache)
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
            # Sub-users created before the organisation_id fix may have NULL org.
            # Fall back to the parent user's organisation so their team members
            # can still resolve org-level platform credentials.
            parent_id = _get_parent_user_id(user_id)
            if parent_id:
                org_id = execute_query(
                    "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                    (parent_id,),
                    fetch_mode='value'
                )
                if org_id:
                    logger.debug(
                        f"[ORG_CREDS_LOADER] Sub-user {user_id} has no org, using parent "
                        f"{parent_id}'s org_id={org_id}"
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