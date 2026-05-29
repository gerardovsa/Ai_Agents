"""
FILE: AI_infrastructure/routes/organisation_credentials_routes.py

PURPOSE:
    Organisation-level credential management API.
    Handles listing, adding, editing, deleting, and REVEALING org API keys.

ROLE-BASED ACCESS CONTROL:
    viewer   → No access (403)
    member   → No access (403)
    manager  → GET /credentials  (masked display only)
    admin    → GET/POST/PUT/DELETE /credentials  (still masked)
    owner    → All above + POST /credentials/<id>/reveal + vault password management

ENDPOINT SUMMARY:
    GET    /api/org/info                          → Org details (member+)
    PUT    /api/org/info                          → Update org (owner)
    GET    /api/org/members                       → List members (manager+)
    PUT    /api/org/members/<user_id>/role        → Change role (admin+)
    DELETE /api/org/members/<user_id>             → Remove member (owner)
    GET    /api/org/credentials                   → List credentials masked (manager+)
    POST   /api/org/credentials                   → Add credential (admin+)
    PUT    /api/org/credentials/<id>              → Edit credential (admin+)
    DELETE /api/org/credentials/<id>              → Soft-delete (admin+)
    POST   /api/org/credentials/<id>/reveal       → Reveal plaintext (admin+ + vault pwd)
    GET    /api/org/credentials/audit-log         → Audit trail (admin+)
    POST   /api/org/vault-password                → Set/change vault password (owner)
    DELETE /api/org/vault-password                → Remove vault password (owner)
    GET    /api/org/platforms                     → Platform catalog (member+)
    GET    /api/org/modules                       → Enabled modules for this org (member+)
    GET    /api/org/modules/catalog               → Full module catalog + enabled state (member+)
    PUT    /api/org/modules/<module_name>         → Enable/disable module override (admin+)
    POST   /api/org/invite                        → Send invitation email (admin+)
    GET    /api/org/invite/pending                → List pending invitations (admin+)
    DELETE /api/org/invite/<id>                   → Revoke invitation (admin+)

REGISTRATION (in flask_app.py):
    from routes.organisation_credentials_routes import org_credentials_bp
    app.register_blueprint(org_credentials_bp)

LAST MODIFIED: March 2026
"""

import bcrypt
import json
import logging
from datetime import datetime
from functools import wraps
from typing import Optional

from flask import Blueprint, request, jsonify, g

from shared.database_utils import execute_query
from shared.credential_crypto import encrypt_credential, decrypt_credential

logger = logging.getLogger(__name__)

org_credentials_bp = Blueprint('org_credentials', __name__, url_prefix='/api/org')

# ============================================================================
# ROLE HIERARCHY
# ============================================================================

ROLE_LEVELS = {
    'viewer':             1,
    'member':             2,
    'manager':            3,
    'admin':              4,
    'owner':              5,
    'platform_developer': 10,   # system-level super role; stored in users.role, not org_role
}

# Values permitted in users.org_role (DB CHECK constraint)
VALID_ORG_ROLES = {'viewer', 'member', 'manager', 'admin', 'owner'}

# System-level roles stored in users.role that bypass all org-level restrictions
SYSTEM_SUPER_ROLES = {'platform_developer'}


def role_level(role_name: str) -> int:
    return ROLE_LEVELS.get(role_name, 0)


# ============================================================================
# AUTH / PERMISSION DECORATORS
# ============================================================================

def require_auth(f):
    """JWT authentication decorator. Sets g.user_id and g.user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from auth.user_auth import UserAuthManager
        token = None

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        # GAP-C4 FIX: Reject stale tokens that were invalidated by a role change.
        # The before_request middleware in flask_app.py sets g.jwt_version_valid.
        if not getattr(g, 'jwt_version_valid', True):
            return jsonify({
                'success': False,
                'error': 'Session expired due to a permission change — please log in again.'
            }), 401

        try:
            auth_manager = UserAuthManager()
            user = auth_manager.verify_token(token)
            if not user:
                return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
            # verify_token returns the JWT payload which uses 'user_id' key, not 'id'
            g.user_id = user.get('user_id') or user.get('id')
            g.user = user
        except Exception as e:
            logger.error(f"[ORG_CREDS] Auth error: {e}")
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401

        return f(*args, **kwargs)
    return decorated


def get_user_org_context(user_id: int) -> Optional[dict]:
    """Fetch the user's org membership + role. Returns None if no org.
    Also surfaces the system-level 'role' column so callers can detect
    platform_developer super-users.
    """
    row = execute_query(
        """
        SELECT
            u.organisation_id,
            u.org_role,
            u.role             AS system_role,
            o.name             AS org_name,
            o.slug             AS org_slug,
            o.vault_password_hash
        FROM ai_infrastructure.users u
        LEFT JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
        WHERE u.id = %s
        """,
        (user_id,),
        fetch_mode='one'
    )
    logger.info(f"[ORG_DEBUG] get_user_org_context(user_id={user_id}): row={row}")
    if not row:
        return None
    # Platform developers bypass org membership requirement
    if row.get('system_role') in SYSTEM_SUPER_ROLES:
        result = dict(row)
        result['org_role'] = 'platform_developer'  # virtual org_role for decorators
        logger.info(f"[ORG_DEBUG] platform_developer super-user — bypassing org membership")
        return result
    result = row if row.get('organisation_id') else None
    logger.info(f"[ORG_DEBUG] get_user_org_context returning: {result}")
    return result


def require_org_role(minimum_role: str):
    """Decorator factory. Enforces minimum org_role. Apply AFTER @require_auth.
    platform_developer (system_role) bypasses all org-role checks.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ctx = get_user_org_context(g.user_id)
            if not ctx:
                return jsonify({
                    'success': False,
                    'error': 'You are not a member of any organisation'
                }), 403

            # Platform developers have effective level 10 — pass all role gates
            effective_level = role_level(ctx['org_role'])
            if effective_level < role_level(minimum_role):
                return jsonify({
                    'success': False,
                    'error': f'Requires {minimum_role}+ role. Your role: {ctx["org_role"]}'
                }), 403

            g.org_ctx = ctx
            return f(*args, **kwargs)
        return decorated
    return decorator


# ============================================================================
# HELPERS
# ============================================================================

def mask_value(value: str) -> str:
    if not value or len(value) < 12:
        return '****'
    return value[:12] + '****...****' + value[-4:]


def mask_credentials_dict(creds: dict) -> dict:
    if not creds:
        return {}
    return {k: mask_value(v) if isinstance(v, str) and len(v) > 8 else v for k, v in creds.items()}


def log_credential_access(
    organisation_id: int,
    user_id: int,
    action: str,
    credential_id: int = None,
    platform: str = None,
    display_name: str = None,
    vault_password_used: bool = False
):
    """Write an audit entry to credential_access_log."""
    try:
        ip = request.remote_addr or 'unknown'
        ua = request.headers.get('User-Agent', '')[:500]
        execute_query(
            """
            INSERT INTO ai_infrastructure.credential_access_log
                (organisation_id, credential_id, user_id, action, platform,
                 display_name, ip_address, user_agent, vault_password_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (organisation_id, credential_id, user_id, action, platform,
             display_name, ip, ua, vault_password_used)
        )
    except Exception as e:
        logger.warning(f"[ORG_CREDS] Failed to write audit log: {e}")


def format_credential_row(row: dict, reveal: bool = False) -> dict:
    # GAP-L7: decrypt on read so masking / reveal both operate on plaintext
    raw_cred_value  = decrypt_credential(row.get('credential_value') or '')
    raw_credentials = row.get('credentials') or {}
    if isinstance(raw_credentials, str):
        try:
            raw_credentials = json.loads(raw_credentials)
        except Exception:
            raw_credentials = {}

    return {
        'id':                   row['id'],
        'platform':             row['platform'],
        'display_name':         row.get('display_name') or row['platform'],
        'environment':          row.get('environment', 'production'),
        'is_active':            row.get('is_active', True),
        'notes':                row.get('notes'),
        'visible_to_role':      row.get('visible_to_role', 'manager'),
        'reveal_requires_role': row.get('reveal_requires_role', 'admin'),
        'expires_at':           row['expires_at'].isoformat() if row.get('expires_at') else None,
        'rotation_due_at':      row['rotation_due_at'].isoformat() if row.get('rotation_due_at') else None,
        'last_used_at':         row['last_used_at'].isoformat() if row.get('last_used_at') else None,
        'created_at':           row['created_at'].isoformat() if row.get('created_at') else None,
        'updated_at':           row['updated_at'].isoformat() if row.get('updated_at') else None,
        'credential_value':     raw_cred_value if reveal else mask_value(raw_cred_value),
        'credentials':          raw_credentials if reveal else mask_credentials_dict(raw_credentials),
        'has_credential_value': bool(raw_cred_value),
        'has_credentials_json': bool(raw_credentials),
        'is_revealed':          reveal,
    }


# ============================================================================
# ROUTES: ORGANISATION CREATION
# ============================================================================

@org_credentials_bp.route('/create', methods=['POST'])
@require_auth
def create_organisation():
    """POST /api/org/create — Create a new organisation and assign caller as owner.
    Caller must not already be a member of an organisation.
    """
    import re
    user_id = g.user_id

    # Reject if user already has an org
    existing = execute_query(
        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (user_id,), fetch_mode='one'
    )
    if existing and existing.get('organisation_id'):
        return jsonify({'success': False, 'error': 'You are already a member of an organisation'}), 409

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Organisation name is required'}), 400

    # Auto-generate slug from name if not provided
    raw_slug = data.get('slug') or name
    slug = re.sub(r'[^a-z0-9]+', '-', raw_slug.lower()).strip('-')
    if not slug:
        return jsonify({'success': False, 'error': 'Could not generate a valid slug from the name'}), 400

    # Check slug uniqueness
    existing_slug = execute_query(
        "SELECT id FROM ai_infrastructure.organisations WHERE slug = %s",
        (slug,), fetch_mode='one'
    )
    if existing_slug:
        return jsonify({'success': False, 'error': f'Slug "{slug}" is already taken. Please choose a different name.'}), 409

    # Create the organisation
    new_org = execute_query(
        """INSERT INTO ai_infrastructure.organisations (name, slug, plan_tier, is_active)
           VALUES (%s, %s, 'free', TRUE) RETURNING id, name, slug, plan_tier""",
        (name, slug), fetch_mode='one'
    )
    if not new_org:
        return jsonify({'success': False, 'error': 'Failed to create organisation'}), 500

    # Assign the creating user as owner
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = %s, org_role = 'owner' WHERE id = %s",
        (new_org['id'], user_id)
    )

    logger.info(f"[ORG_CREDS] User {user_id} created org '{name}' (id={new_org['id']}, slug={slug})")

    return jsonify({'success': True, 'organisation': dict(new_org)}), 201


# ============================================================================
# ROUTES: ORGANISATION INFO
# ============================================================================

@org_credentials_bp.route('/info', methods=['GET'])
@require_auth
@require_org_role('member')
def get_org_info():
    """GET /api/org/info — Org details for any org member."""
    ctx = g.org_ctx
    logger.info(f"[ORG_DEBUG] get_org_info(): ctx={ctx}")

    org = execute_query(
        """
        SELECT id, name, slug, plan_tier, display_name, logo_url,
               timezone, country_code, is_active, created_at, updated_at,
               vault_password_hash, metadata,
               description, visibility, allowed_domains,
               ai_provider, ai_model, ai_max_tokens,
               COALESCE(is_personal_org, FALSE) AS is_personal_org
        FROM ai_infrastructure.organisations WHERE id = %s
        """,
        (ctx['organisation_id'],),
        fetch_mode='one'
    )
    logger.info(f"[ORG_DEBUG] get_org_info() query result: org={org}")
    if not org:
        logger.error(f"[ORG_DEBUG] Organisation not found for org_id={ctx['organisation_id']}")
        return jsonify({'success': False, 'error': 'Organisation not found'}), 404

    member_count = execute_query(
        "SELECT COUNT(*) FROM ai_infrastructure.users WHERE organisation_id = %s",
        (ctx['organisation_id'],),
        fetch_mode='value'
    ) or 0

    vault_hash = execute_query(
        "SELECT vault_password_hash FROM ai_infrastructure.organisations WHERE id = %s",
        (ctx['organisation_id'],),
        fetch_mode='value'
    )

    return jsonify({
        'success': True,
        'organisation': {
            'id':                 org['id'],
            'name':               org['name'],
            'slug':               org['slug'],
            'display_name':       org.get('display_name'),
            'logo_url':           org.get('logo_url'),
            'plan_tier':          org.get('plan_tier'),
            'timezone':           org.get('timezone', 'UTC'),
            'country_code':       org.get('country_code'),
            'is_active':          org.get('is_active', True),
            'member_count':       member_count,
            'has_vault_password': bool(vault_hash),
            'created_at':         org['created_at'].isoformat() if org.get('created_at') else None,
            'description':        org.get('description'),
            'visibility':         org.get('visibility', 'private'),
            'allowed_domains':    org.get('allowed_domains') or [],
            'ai_provider':        org.get('ai_provider') or 'anthropic',
            'ai_model':           org.get('ai_model') or '',
            'ai_max_tokens':      org.get('ai_max_tokens') or 8192,
            'is_personal_org':    bool(org.get('is_personal_org', False)),
        },
        'your_role': ctx['org_role'],
    })


@org_credentials_bp.route('/info', methods=['PUT'])
@require_auth
@require_org_role('admin')
def update_org_info():
    """PUT /api/org/info — Update org metadata. Admin+."""
    ctx = g.org_ctx
    data = request.get_json() or {}

    # Simple scalar fields (all optional except name validation)
    simple_allowed = ['display_name', 'logo_url', 'timezone', 'country_code', 'description']
    updates = {k: v for k, v in data.items() if k in simple_allowed}

    # name: non-empty string required if provided
    if 'name' in data:
        name = str(data['name']).strip()
        if not name:
            return jsonify({'success': False, 'error': 'Organisation name cannot be empty'}), 400
        updates['name'] = name

    # visibility: must be a known value
    if 'visibility' in data:
        visibility = str(data['visibility']).strip().lower()
        if visibility not in ('private', 'unlisted', 'public'):
            return jsonify({'success': False, 'error': 'visibility must be private, unlisted, or public'}), 400
        updates['visibility'] = visibility

    # allowed_domains: list of lowercase domain strings (GAP-M6)
    if 'allowed_domains' in data:
        raw = data['allowed_domains']
        if not isinstance(raw, list):
            return jsonify({'success': False, 'error': 'allowed_domains must be an array'}), 400
        # Validate and normalise each domain
        import re as _re
        domain_re = _re.compile(r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?)+$')
        cleaned = []
        for d in raw:
            d = str(d).strip().lower()
            if d and domain_re.match(d):
                cleaned.append(d)
        updates['allowed_domains'] = cleaned  # stored as TEXT[] in Postgres

    # ai_provider: must be one of the supported providers (GAP-M3)
    if 'ai_provider' in data:
        provider = str(data['ai_provider']).strip().lower()
        if provider not in ('anthropic', 'openai', 'deepseek'):
            return jsonify({'success': False, 'error': 'ai_provider must be anthropic, openai, or deepseek'}), 400
        updates['ai_provider'] = provider

    # ai_model: free-form model string (GAP-M3)
    if 'ai_model' in data:
        model = str(data.get('ai_model') or '').strip()
        updates['ai_model'] = model or None

    # ai_max_tokens: integer 1024-32768 (GAP-M3)
    if 'ai_max_tokens' in data:
        try:
            max_tokens = int(data['ai_max_tokens'])
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'ai_max_tokens must be an integer'}), 400
        if not (1024 <= max_tokens <= 32768):
            return jsonify({'success': False, 'error': 'ai_max_tokens must be between 1024 and 32768'}), 400
        updates['ai_max_tokens'] = max_tokens

    if not updates:
        return jsonify({'success': False, 'error': 'No valid fields to update'}), 400

    set_clause = ', '.join(f"{k} = %s" for k in updates)
    execute_query(
        f"UPDATE ai_infrastructure.organisations SET {set_clause}, updated_at = NOW() WHERE id = %s",
        list(updates.values()) + [ctx['organisation_id']]
    )
    return jsonify({'success': True, 'message': 'Organisation updated'})


# ============================================================================
# ROUTES: ORG MEMBERS
# ============================================================================

@org_credentials_bp.route('/members', methods=['GET'])
@require_auth
@require_org_role('manager')
def list_members():
    """GET /api/org/members — List org members by role. Requires manager+."""
    ctx = g.org_ctx
    members = execute_query(
        """
        SELECT id, username, email, org_role, is_active, last_active, created_at
        FROM ai_infrastructure.users
        WHERE organisation_id = %s
        ORDER BY
            CASE org_role
                WHEN 'owner'   THEN 1 WHEN 'admin'   THEN 2
                WHEN 'manager' THEN 3 WHEN 'member'  THEN 4
                WHEN 'viewer'  THEN 5 ELSE 6
            END, username
        """,
        (ctx['organisation_id'],),
        fetch_mode='all'
    ) or []

    return jsonify({
        'success': True,
        'members': [
            {
                'id':        m['id'],
                'username':  m['username'],
                'email':     m['email'],
                'org_role':  m['org_role'],
                'is_active': m['is_active'],
                'last_login': m['last_active'].isoformat() if m.get('last_active') else None,
                'joined_at': m['created_at'].isoformat() if m.get('created_at') else None,
            }
            for m in members
        ],
        'total': len(members),
    })


@org_credentials_bp.route('/members/<int:target_user_id>/role', methods=['PUT'])
@require_auth
@require_org_role('admin')
def update_member_role(target_user_id: int):
    """PUT /api/org/members/<user_id>/role — Change a member's org_role. Admin+."""
    ctx = g.org_ctx
    data = request.get_json() or {}
    new_role = data.get('role', '').strip()

    if new_role not in VALID_ORG_ROLES:
        return jsonify({
            'success': False,
            'error': f'Invalid org role. Must be one of: {", ".join(sorted(VALID_ORG_ROLES))}. '
                     f'(platform_developer is a system role set separately)'
        }), 400

    if target_user_id == g.user_id:
        return jsonify({'success': False, 'error': 'Cannot change your own role'}), 400

    target = execute_query(
        "SELECT id, org_role, organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (target_user_id,),
        fetch_mode='one'
    )
    if not target or target.get('organisation_id') != ctx['organisation_id']:
        return jsonify({'success': False, 'error': 'User not found in your organisation'}), 404

    if target['org_role'] == 'owner' or new_role == 'owner':
        if ctx['org_role'] != 'owner':
            return jsonify({
                'success': False,
                'error': 'Only an owner can assign or remove the owner role'
            }), 403

    execute_query(
        "UPDATE ai_infrastructure.users SET org_role = %s, jwt_version = COALESCE(jwt_version, 1) + 1 WHERE id = %s",
        (new_role, target_user_id)
    )
    return jsonify({
        'success': True,
        'message': f'Role updated to {new_role} — user must log in again for the change to take effect',
        'user_id': target_user_id,
        'new_role': new_role,
    })


@org_credentials_bp.route('/members/<int:target_user_id>', methods=['DELETE'])
@require_auth
@require_org_role('owner')
def remove_member(target_user_id: int):
    """DELETE /api/org/members/<user_id> — Remove a member from the org. Owner only."""
    ctx = g.org_ctx

    if target_user_id == g.user_id:
        return jsonify({'success': False, 'error': 'Cannot remove yourself'}), 400

    target = execute_query(
        "SELECT id, org_role, organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (target_user_id,),
        fetch_mode='one'
    )
    if not target or target.get('organisation_id') != ctx['organisation_id']:
        return jsonify({'success': False, 'error': 'User not found in your organisation'}), 404

    # GAP-C4 FIX: Increment jwt_version to invalidate all existing tokens for this user
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = NULL, org_role = 'member', "
        "jwt_version = COALESCE(jwt_version, 1) + 1 WHERE id = %s",
        (target_user_id,)
    )
    return jsonify({'success': True, 'message': 'Member removed from organisation'})


# ============================================================================
# ROUTES: ORG CREDENTIALS
# ============================================================================

@org_credentials_bp.route('/credentials', methods=['GET'])
@require_auth
@require_org_role('manager')
def list_credentials():
    """GET /api/org/credentials — List credentials (masked). Requires manager+."""
    ctx = g.org_ctx
    user_lvl = role_level(ctx['org_role'])

    rows = execute_query(
        """
        SELECT * FROM ai_infrastructure.organisation_platform_credentials
        WHERE organisation_id = %s AND is_active = TRUE
        ORDER BY platform, display_name
        """,
        (ctx['organisation_id'],),
        fetch_mode='all'
    ) or []

    visible = [r for r in rows if user_lvl >= role_level(r.get('visible_to_role', 'manager'))]

    log_credential_access(ctx['organisation_id'], g.user_id, 'listed', platform='all')

    return jsonify({
        'success':      True,
        'credentials':  [format_credential_row(r) for r in visible],
        'total':        len(visible),
        'your_role':    ctx['org_role'],
        'can_add_edit': user_lvl >= role_level('admin'),
        'can_reveal':   user_lvl >= role_level('owner'),
    })


@org_credentials_bp.route('/credentials', methods=['POST'])
@require_auth
@require_org_role('admin')
def add_credential():
    """POST /api/org/credentials — Add a new credential. Admin+."""
    ctx = g.org_ctx
    data = request.get_json() or {}

    platform = data.get('platform', '').strip().lower()
    if not platform:
        return jsonify({'success': False, 'error': 'platform is required'}), 400

    # Validate platform against platform_catalog table (migration 036).
    # Falls back to the legacy hardcoded set so the route works before the
    # migration has been run (e.g. local dev without the new table yet).
    platform_valid = False
    try:
        row = execute_query(
            "SELECT platform_name FROM ai_infrastructure.platform_catalog WHERE platform_name = %s AND is_active = TRUE",
            (platform,),
            fetch_mode='one'
        )
        platform_valid = row is not None
        if not platform_valid:
            # Provide a helpful list from the catalog
            catalog_names = execute_query(
                "SELECT platform_name FROM ai_infrastructure.platform_catalog WHERE is_active = TRUE ORDER BY platform_name",
                fetch_mode='all'
            ) or []
            allowed_list = sorted(r['platform_name'] for r in catalog_names)
            return jsonify({
                'success': False,
                'error': f'Unknown platform "{platform}". Allowed values: {allowed_list}'
            }), 400
    except Exception:
        # platform_catalog table not yet created — fall back to hardcoded set
        LEGACY_ALLOWED_PLATFORMS = {
            'anthropic', 'openai', 'deepseek', 'assemblyai', 'pinecone',
            'shopify', 'xero', 'sendgrid', 'twilio', 'auspost', 'stripe',
            'google', 'microsoft', 'gmail_oauth', 'outlook_oauth',
            'supabase', 'supabase_vsa', 'kajabi', 'hunter',
        }
        if platform not in LEGACY_ALLOWED_PLATFORMS:
            return jsonify({
                'success': False,
                'error': f'Unknown platform "{platform}". Allowed values: {sorted(LEGACY_ALLOWED_PLATFORMS)}'
            }), 400

    credential_value = data.get('credential_value', '').strip()
    credentials_json = data.get('credentials', {})

    if not credential_value and not credentials_json:
        return jsonify({
            'success': False,
            'error': 'Either credential_value or credentials dict is required'
        }), 400

    display_name         = (data.get('display_name') or platform).strip()
    environment          = data.get('environment', 'production').strip()
    notes                = data.get('notes', '').strip() or None
    visible_to_role      = data.get('visible_to_role', 'manager')
    reveal_requires_role = data.get('reveal_requires_role', 'admin')
    expires_at           = data.get('expires_at')
    rotation_due_at      = data.get('rotation_due_at')

    for field, val in [('visible_to_role', visible_to_role), ('reveal_requires_role', reveal_requires_role)]:
        if val not in ROLE_LEVELS:
            return jsonify({'success': False, 'error': f'Invalid {field}: {val}'}), 400

    existing = execute_query(
        """
        SELECT id FROM ai_infrastructure.organisation_platform_credentials
        WHERE organisation_id = %s AND platform = %s AND display_name = %s
        """,
        (ctx['organisation_id'], platform, display_name),
        fetch_mode='one'
    )
    if existing:
        return jsonify({
            'success': False,
            'error': f'A credential named "{display_name}" for {platform} already exists.'
        }), 409

    # GAP-L7: encrypt credential at rest before storing
    encrypted_value = encrypt_credential(credential_value) if credential_value else None

    new_id = execute_query(
        """
        INSERT INTO ai_infrastructure.organisation_platform_credentials
            (organisation_id, platform, display_name, environment,
             credential_value, credentials, visible_to_role, reveal_requires_role,
             notes, expires_at, rotation_due_at, created_by_user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            ctx['organisation_id'], platform, display_name, environment,
            encrypted_value,
            json.dumps(credentials_json) if credentials_json else None,
            visible_to_role, reveal_requires_role,
            notes, expires_at, rotation_due_at, g.user_id
        ),
        fetch_mode='value'
    )

    log_credential_access(
        ctx['organisation_id'], g.user_id, 'added',
        credential_id=new_id, platform=platform, display_name=display_name
    )

    return jsonify({
        'success': True,
        'message': f'Credential "{display_name}" added for {platform}',
        'credential_id': new_id,
    }), 201


@org_credentials_bp.route('/credentials/<int:cred_id>', methods=['PUT'])
@require_auth
@require_org_role('admin')
def edit_credential(cred_id: int):
    """PUT /api/org/credentials/<id> — Edit a credential. Admin+."""
    ctx = g.org_ctx
    data = request.get_json() or {}

    existing = execute_query(
        "SELECT * FROM ai_infrastructure.organisation_platform_credentials WHERE id = %s AND organisation_id = %s",
        (cred_id, ctx['organisation_id']),
        fetch_mode='one'
    )
    if not existing:
        return jsonify({'success': False, 'error': 'Credential not found'}), 404

    updatable = [
        'display_name', 'environment', 'notes', 'visible_to_role',
        'reveal_requires_role', 'expires_at', 'rotation_due_at',
        'is_active', 'credential_value', 'credentials'
    ]
    updates = {k: v for k, v in data.items() if k in updatable}
    if not updates:
        return jsonify({'success': False, 'error': 'No valid fields to update'}), 400

    if 'credentials' in updates and isinstance(updates['credentials'], dict):
        updates['credentials'] = json.dumps(updates['credentials'])

    # GAP-L7: encrypt any new credential_value before storing
    if 'credential_value' in updates and updates['credential_value']:
        updates['credential_value'] = encrypt_credential(updates['credential_value'])

    set_clause = ', '.join(f"{k} = %s" for k in updates)
    execute_query(
        f"UPDATE ai_infrastructure.organisation_platform_credentials "
        f"SET {set_clause}, updated_at = NOW() WHERE id = %s AND organisation_id = %s",
        list(updates.values()) + [cred_id, ctx['organisation_id']]
    )

    log_credential_access(
        ctx['organisation_id'], g.user_id, 'edited',
        credential_id=cred_id, platform=existing['platform'], display_name=existing.get('display_name')
    )
    return jsonify({'success': True, 'message': 'Credential updated'})


@org_credentials_bp.route('/credentials/<int:cred_id>', methods=['DELETE'])
@require_auth
@require_org_role('admin')
def delete_credential(cred_id: int):
    """DELETE /api/org/credentials/<id> — Soft-delete. Admin+."""
    ctx = g.org_ctx

    existing = execute_query(
        "SELECT id, platform, display_name FROM ai_infrastructure.organisation_platform_credentials "
        "WHERE id = %s AND organisation_id = %s",
        (cred_id, ctx['organisation_id']),
        fetch_mode='one'
    )
    if not existing:
        return jsonify({'success': False, 'error': 'Credential not found'}), 404

    execute_query(
        "UPDATE ai_infrastructure.organisation_platform_credentials SET is_active = FALSE, updated_at = NOW() WHERE id = %s",
        (cred_id,)
    )

    log_credential_access(
        ctx['organisation_id'], g.user_id, 'deleted',
        credential_id=cred_id, platform=existing['platform'], display_name=existing.get('display_name')
    )
    return jsonify({'success': True, 'message': 'Credential deleted'})


# ============================================================================
# ROUTE: TEST CREDENTIAL CONNECTIVITY (GAP-L3)
# ============================================================================

@org_credentials_bp.route('/credentials/<int:cred_id>/test', methods=['POST'])
@require_auth
@require_org_role('manager')
def test_credential(cred_id: int):
    """
    POST /api/org/credentials/<id>/test
    Makes a minimal live API call to verify the credential is valid.
    Supported platforms: anthropic, openai, deepseek, auspost, shopify, xero_*.
    """
    ctx = g.org_ctx

    row = execute_query(
        "SELECT id, platform, credential_value, display_name "
        "FROM ai_infrastructure.organisation_platform_credentials "
        "WHERE id = %s AND organisation_id = %s AND is_active = TRUE",
        (cred_id, ctx['organisation_id']),
        fetch_mode='one'
    )
    if not row:
        return jsonify({'success': False, 'error': 'Credential not found'}), 404

    platform      = row['platform']
    cred_value    = decrypt_credential(row['credential_value'] or '')  # GAP-L7 decrypt
    display_name  = row.get('display_name') or platform

    if not cred_value:
        return jsonify({'success': False, 'error': 'Credential has no value stored'}), 400

    result = _test_platform_credential(platform, cred_value)

    log_credential_access(
        ctx['organisation_id'], g.user_id,
        'tested_ok' if result['success'] else 'tested_fail',
        credential_id=cred_id, platform=platform, display_name=display_name
    )

    return jsonify(result), 200 if result['success'] else 400


def _test_platform_credential(platform: str, cred_value: str) -> dict:
    """
    Perform a minimal connectivity test for the given platform credential.
    Returns {'success': bool, 'message': str, 'latency_ms': int}.
    """
    import time

    t0 = time.monotonic()

    try:
        # ---- Anthropic -------------------------------------------------------
        if platform == 'anthropic':
            import anthropic
            client = anthropic.Anthropic(api_key=cred_value)
            client.messages.create(
                model='claude-haiku-4-5',
                max_tokens=1,
                messages=[{'role': 'user', 'content': 'ping'}]
            )
            return {'success': True, 'message': 'Anthropic API key is valid',
                    'latency_ms': int((time.monotonic() - t0) * 1000)}

        # ---- OpenAI ----------------------------------------------------------
        elif platform == 'openai':
            import openai
            client = openai.OpenAI(api_key=cred_value)
            client.models.list()
            return {'success': True, 'message': 'OpenAI API key is valid',
                    'latency_ms': int((time.monotonic() - t0) * 1000)}

        # ---- DeepSeek --------------------------------------------------------
        elif platform == 'deepseek':
            import requests as rq
            resp = rq.get(
                'https://api.deepseek.com/models',
                headers={'Authorization': f'Bearer {cred_value}'},
                timeout=8
            )
            if resp.status_code == 200:
                return {'success': True, 'message': 'DeepSeek API key is valid',
                        'latency_ms': int((time.monotonic() - t0) * 1000)}
            return {'success': False, 'message': f'DeepSeek returned HTTP {resp.status_code}',
                    'latency_ms': int((time.monotonic() - t0) * 1000)}

        # ---- AusPost ---------------------------------------------------------
        elif platform == 'auspost':
            import requests as rq
            resp = rq.get(
                'https://digitalapi.auspost.com.au/postage/stamp/domestic/variable.json',
                headers={'AUTH-KEY': cred_value},
                timeout=8
            )
            if resp.status_code == 200:
                return {'success': True, 'message': 'AusPost API key is valid',
                        'latency_ms': int((time.monotonic() - t0) * 1000)}
            return {'success': False, 'message': f'AusPost returned HTTP {resp.status_code}',
                    'latency_ms': int((time.monotonic() - t0) * 1000)}

        # ---- Unsupported platform -------------------------------------------
        else:
            return {'success': False,
                    'message': f'Connectivity test not supported for platform "{platform}"',
                    'latency_ms': 0}

    except Exception as exc:
        latency = int((time.monotonic() - t0) * 1000)
        logger.warning(f"[CRED_TEST] Test failed for platform={platform}: {exc}")
        return {'success': False, 'message': str(exc), 'latency_ms': latency}


# ============================================================================
# ROUTE: REVEAL ACTUAL KEY VALUE
# ============================================================================

@org_credentials_bp.route('/credentials/<int:cred_id>/reveal', methods=['POST'])
@require_auth
@require_org_role('admin')
def reveal_credential(cred_id: int):
    """
    POST /api/org/credentials/<id>/reveal
    Returns the plaintext credential. Requires admin+ + vault password (if set).
    Every reveal is logged in credential_access_log.
    """
    ctx = g.org_ctx
    data = request.get_json() or {}
    supplied_password = data.get('vault_password', '')

    row = execute_query(
        "SELECT * FROM ai_infrastructure.organisation_platform_credentials "
        "WHERE id = %s AND organisation_id = %s AND is_active = TRUE",
        (cred_id, ctx['organisation_id']),
        fetch_mode='one'
    )
    if not row:
        return jsonify({'success': False, 'error': 'Credential not found'}), 404

    # Role check vs credential-specific requirement
    if role_level(ctx['org_role']) < role_level(row.get('reveal_requires_role', 'admin')):
        return jsonify({
            'success': False,
            'error': f'Revealing this credential requires the "{row["reveal_requires_role"]}" role. '
                     f'Your role: {ctx["org_role"]}'
        }), 403

    # Vault password check
    vault_hash = execute_query(
        "SELECT vault_password_hash FROM ai_infrastructure.organisations WHERE id = %s",
        (ctx['organisation_id'],),
        fetch_mode='value'
    )

    vault_password_used = False
    if vault_hash:
        if not supplied_password:
            return jsonify({
                'success': False,
                'error': 'This organisation has a vault password. Provide vault_password to reveal credentials.',
                'requires_vault_password': True,
            }), 403

        if not bcrypt.checkpw(
            supplied_password.encode('utf-8'),
            vault_hash if isinstance(vault_hash, bytes) else vault_hash.encode('utf-8')
        ):
            log_credential_access(
                ctx['organisation_id'], g.user_id, 'reveal_failed_wrong_password',
                credential_id=cred_id, platform=row['platform'],
                display_name=row.get('display_name'), vault_password_used=True
            )
            return jsonify({'success': False, 'error': 'Incorrect vault password'}), 403

        vault_password_used = True

    log_credential_access(
        ctx['organisation_id'], g.user_id, 'revealed',
        credential_id=cred_id, platform=row['platform'],
        display_name=row.get('display_name'), vault_password_used=vault_password_used
    )

    return jsonify({
        'success':    True,
        'credential': format_credential_row(row, reveal=True),
        'revealed_by': g.user_id,
        'revealed_at': datetime.utcnow().isoformat(),
        'warning':    'This value is now visible. Close this dialog when done.',
    })


# ============================================================================
# ROUTES: VAULT PASSWORD
# ============================================================================

@org_credentials_bp.route('/vault-password', methods=['POST'])
@require_auth
@require_org_role('owner')
def set_vault_password():
    """POST /api/org/vault-password — Set or change vault password. Owner only."""
    ctx = g.org_ctx
    data = request.get_json() or {}
    new_password = data.get('new_password', '').strip()

    if len(new_password) < 8:
        return jsonify({'success': False, 'error': 'Vault password must be at least 8 characters'}), 400

    existing_hash = execute_query(
        "SELECT vault_password_hash FROM ai_infrastructure.organisations WHERE id = %s",
        (ctx['organisation_id'],),
        fetch_mode='value'
    )

    if existing_hash:
        current_password = data.get('current_password', '').strip()
        if not current_password:
            return jsonify({
                'success': False,
                'error': 'A vault password is already set. Provide current_password to change it.'
            }), 400
        if not bcrypt.checkpw(
            current_password.encode('utf-8'),
            existing_hash if isinstance(existing_hash, bytes) else existing_hash.encode('utf-8')
        ):
            return jsonify({'success': False, 'error': 'Incorrect current vault password'}), 403

    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    execute_query(
        "UPDATE ai_infrastructure.organisations SET vault_password_hash = %s WHERE id = %s",
        (new_hash, ctx['organisation_id'])
    )

    log_credential_access(ctx['organisation_id'], g.user_id, 'vault_password_changed')
    action = 'changed' if existing_hash else 'set'
    return jsonify({'success': True, 'message': f'Vault password {action} successfully.'})


@org_credentials_bp.route('/vault-password', methods=['DELETE'])
@require_auth
@require_org_role('owner')
def remove_vault_password():
    """DELETE /api/org/vault-password — Remove vault password. Owner only."""
    ctx = g.org_ctx
    data = request.get_json() or {}
    current_password = data.get('current_password', '').strip()

    existing_hash = execute_query(
        "SELECT vault_password_hash FROM ai_infrastructure.organisations WHERE id = %s",
        (ctx['organisation_id'],),
        fetch_mode='value'
    )
    if not existing_hash:
        return jsonify({'success': False, 'error': 'No vault password is set'}), 400

    if not bcrypt.checkpw(
        current_password.encode('utf-8'),
        existing_hash if isinstance(existing_hash, bytes) else existing_hash.encode('utf-8')
    ):
        return jsonify({'success': False, 'error': 'Incorrect current vault password'}), 403

    execute_query(
        "UPDATE ai_infrastructure.organisations SET vault_password_hash = NULL WHERE id = %s",
        (ctx['organisation_id'],)
    )

    log_credential_access(ctx['organisation_id'], g.user_id, 'vault_password_removed')
    return jsonify({'success': True, 'message': 'Vault password removed.'})


# ============================================================================
# ROUTE: AUDIT LOG
# ============================================================================

@org_credentials_bp.route('/credentials/audit-log', methods=['GET'])
@require_auth
@require_org_role('admin')
def get_audit_log():
    """GET /api/org/credentials/audit-log — View audit trail. Admin+."""
    ctx = g.org_ctx
    limit    = min(int(request.args.get('limit', 100)), 500)
    platform = request.args.get('platform')

    query = """
        SELECT l.id, l.action, l.platform, l.display_name,
               l.vault_password_used, l.ip_address, l.performed_at,
               u.username, u.email
        FROM ai_infrastructure.credential_access_log l
        JOIN ai_infrastructure.users u ON u.id = l.user_id
        WHERE l.organisation_id = %s
    """
    params = [ctx['organisation_id']]
    if platform:
        query += " AND l.platform = %s"
        params.append(platform)
    query += " ORDER BY l.performed_at DESC LIMIT %s"
    params.append(limit)

    rows = execute_query(query, params, fetch_mode='all') or []

    return jsonify({
        'success': True,
        'log': [
            {
                'id':                  r['id'],
                'action':              r['action'],
                'platform':            r.get('platform'),
                'display_name':        r.get('display_name'),
                'vault_password_used': r.get('vault_password_used', False),
                'ip_address':          r.get('ip_address'),
                'performed_at':        r['performed_at'].isoformat() if r.get('performed_at') else None,
                'by_username':         r.get('username'),
                'by_email':            r.get('email'),
            }
            for r in rows
        ],
        'total': len(rows),
    })


# ============================================================================
# ROUTE: ORG MODULE ACCESS (GAP-M1)
# ============================================================================

@org_credentials_bp.route('/modules', methods=['GET'])
@require_auth
@require_org_role('member')
def get_org_modules():
    """GET /api/org/modules — Return the enabled module set for the requesting user.
    Applies both org-level enablement and per-user restrictions (migration 039).
    Any org member can call this; used by the frontend to gate UI panels.

    Response includes:
        modules         — full module objects (module_name, display_name, icon_class,
                          icon_color, category) for use by initModulesFromOrg()
        enabled_modules — sorted list of module_name strings (backward compat)
    """
    ctx = g.org_ctx
    try:
        from AI_infrastructure.shared.org_credentials_loader import get_user_enabled_modules
        enabled = get_user_enabled_modules(g.user_id)
    except Exception as e:
        logger.warning(f"[ORG_MODULES] Could not load enabled modules: {e}")
        enabled = set()

    # Fetch full module metadata for enabled modules so the frontend can render
    # sidebar icons without a second round-trip.
    modules = []
    if enabled:
        try:
            rows = execute_query(
                """
                SELECT module_name, display_name, icon_class, icon_color,
                       category, description, sort_order
                FROM   ai_infrastructure.module_catalog
                WHERE  module_name = ANY(%s)
                  AND  is_active   = TRUE
                ORDER  BY sort_order, module_name
                """,
                (list(enabled),),
                fetch_mode='all'
            ) or []
            modules = [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"[ORG_MODULES] Could not fetch module metadata: {e}")
            modules = [{'module_name': m} for m in sorted(enabled)]

    return jsonify({
        'success':         True,
        'modules':         modules,           # full objects for initModulesFromOrg()
        'enabled_modules': sorted(enabled),   # backward-compat list of strings
        'your_role':       ctx['org_role'],
        'organisation_id': ctx['organisation_id'],
    })


# ============================================================================
# AI MODEL CATALOG  (migration 037)
# GET /api/org/models — Return every active model grouped by provider.
# No secrets involved; any authenticated member can fetch this.
# ============================================================================

# Fallback hardcoded list used when the ai_model_catalog table doesn't exist yet
_FALLBACK_MODEL_CATALOG = [
    # Anthropic — source: https://docs.anthropic.com/en/docs/about-claude/models/overview
    {'provider': 'anthropic', 'model_id': 'claude-opus-4-6',
     'display_name': 'Claude Opus 4.6', 'tier': 'powerful',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 5},
    {'provider': 'anthropic', 'model_id': 'claude-sonnet-4-6',
     'display_name': 'Claude Sonnet 4.6', 'tier': 'balanced',
     'is_recommended': True,  'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 10},
    {'provider': 'anthropic', 'model_id': 'claude-haiku-4-5-20251001',
     'display_name': 'Claude Haiku 4.5', 'tier': 'fast',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 30},
    {'provider': 'anthropic', 'model_id': 'claude-sonnet-4-5-20250929',
     'display_name': 'Claude Sonnet 4.5', 'tier': 'balanced',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 40},
    {'provider': 'anthropic', 'model_id': 'claude-3-7-sonnet-20250219',
     'display_name': 'Claude 3.7 Sonnet', 'tier': 'powerful',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 50},
    # OpenAI — source: https://developers.openai.com/api/docs/models
    {'provider': 'openai', 'model_id': 'gpt-5.4',
     'display_name': 'GPT-5.4', 'tier': 'powerful',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 100},
    {'provider': 'openai', 'model_id': 'gpt-5.1',
     'display_name': 'GPT-5.1', 'tier': 'powerful',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 105},
    {'provider': 'openai', 'model_id': 'gpt-5-mini',
     'display_name': 'GPT-5 Mini', 'tier': 'fast',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': False, 'sort_order': 108},
    {'provider': 'openai', 'model_id': 'gpt-4o',
     'display_name': 'GPT-4o', 'tier': 'balanced',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': False, 'sort_order': 110},
    {'provider': 'openai', 'model_id': 'gpt-4o-mini',
     'display_name': 'GPT-4o Mini', 'tier': 'fast',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': False, 'sort_order': 120},
    {'provider': 'openai', 'model_id': 'o3',
     'display_name': 'OpenAI o3', 'tier': 'reasoning',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 130},
    {'provider': 'openai', 'model_id': 'o4-mini',
     'display_name': 'OpenAI o4-mini', 'tier': 'reasoning',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': True,
     'supports_thinking': True, 'sort_order': 135},
    {'provider': 'openai', 'model_id': 'o3-mini',
     'display_name': 'OpenAI o3-mini', 'tier': 'reasoning',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': False,
     'supports_thinking': True, 'sort_order': 140},
    {'provider': 'openai', 'model_id': 'o1',
     'display_name': 'OpenAI o1', 'tier': 'reasoning',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': False,
     'supports_thinking': True, 'sort_order': 150},
    # DeepSeek — source: https://api-docs.deepseek.com/quick_start/pricing
    {'provider': 'deepseek', 'model_id': 'deepseek-chat',
     'display_name': 'DeepSeek Chat (V3.2)', 'tier': 'fast',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': False,
     'supports_thinking': False, 'sort_order': 210},
    {'provider': 'deepseek', 'model_id': 'deepseek-reasoner',
     'display_name': 'DeepSeek Reasoner (V3.2)', 'tier': 'reasoning',
     'is_recommended': False, 'supports_tools': True, 'supports_vision': False,
     'supports_thinking': True, 'sort_order': 220},
]


@org_credentials_bp.route('/models', methods=['GET'])
@require_auth
@require_org_role('member')
def get_model_catalog():
    """GET /api/org/models — Full AI model catalog grouped by provider.
    Returns every active model with display metadata for populating the
    model selector. No secrets; any org member can read it.
    """
    try:
        rows = execute_query(
            """
            SELECT provider, model_id, display_name, description, tier,
                   context_window, is_recommended, supports_tools,
                   supports_vision, supports_thinking, sort_order
            FROM ai_infrastructure.ai_model_catalog
            WHERE is_active = TRUE
            ORDER BY sort_order, display_name
            """,
            fetch_mode='all'
        ) or []

        if not rows:
            rows = _FALLBACK_MODEL_CATALOG

        by_provider: dict = {}
        for r in rows:
            prov = r['provider'] if isinstance(r, dict) else r.get('provider', 'anthropic')
            if prov not in by_provider:
                by_provider[prov] = []
            by_provider[prov].append(dict(r))

        return jsonify({
            'success':     True,
            'models':      [dict(r) for r in rows],
            'by_provider': by_provider,
        })
    except Exception as e:
        logger.warning(f"[ORG_MODELS] ai_model_catalog not yet created, using fallback: {e}")
        by_provider: dict = {}
        for r in _FALLBACK_MODEL_CATALOG:
            prov = r['provider']
            if prov not in by_provider:
                by_provider[prov] = []
            by_provider[prov].append(r)
        return jsonify({
            'success':     True,
            'models':      _FALLBACK_MODEL_CATALOG,
            'by_provider': by_provider,
            'source':      'fallback',
        })


@org_credentials_bp.route('/platforms', methods=['GET'])
@require_auth
@require_org_role('member')
def get_platform_catalog():
    """GET /api/org/platforms — Return the full platform catalog with field definitions.
    Used by the frontend to dynamically render the Add Connection modal.
    Any org member can fetch this; it contains no secrets.
    """
    try:
        rows = execute_query(
            """
            SELECT platform_name, display_name, icon_class, icon_color,
                   category, auth_type, required_fields, description,
                   docs_url, sort_order
            FROM ai_infrastructure.platform_catalog
            WHERE is_active = TRUE
            ORDER BY sort_order, display_name
            """,
            fetch_mode='all'
        ) or []

        # Group by category for convenient frontend consumption
        by_category: dict = {}
        for r in rows:
            cat = r['category']
            if cat not in by_category:
                by_category[cat] = []
            entry = dict(r)
            # required_fields may arrive as a string depending on psycopg2 version
            if isinstance(entry.get('required_fields'), str):
                import json as _json
                entry['required_fields'] = _json.loads(entry['required_fields'])
            by_category[cat].append(entry)

        return jsonify({
            'success':     True,
            'platforms':   rows,          # flat list (full detail)
            'by_category': by_category,   # grouped for modal sections
        })
    except Exception as e:
        logger.warning(f"[ORG_PLATFORMS] platform_catalog not yet created: {e}")
        # Graceful fallback: return the legacy hardcoded list so the UI
        # still works before migration 036 has been run.
        fallback = [
            {'platform_name': p, 'display_name': p.replace('_', ' ').title(),
             'icon_class': 'fas fa-plug', 'icon_color': '#6B7280',
             'category': 'other', 'auth_type': 'api_key',
             'required_fields': [{'name': 'api_key', 'label': 'API Key',
                                   'type': 'password', 'required': True}],
             'description': None, 'docs_url': None, 'sort_order': 100}
            for p in sorted([
                'anthropic', 'openai', 'deepseek', 'assemblyai', 'pinecone',
                'shopify', 'xero', 'sendgrid', 'twilio', 'auspost', 'stripe',
                'google', 'microsoft', 'gmail_oauth', 'outlook_oauth',
                'supabase', 'supabase_vsa', 'kajabi', 'hunter',
            ])
        ]
        return jsonify({'success': True, 'platforms': fallback, 'by_category': {'other': fallback}})


@org_credentials_bp.route('/modules/catalog', methods=['GET'])
@require_auth
@require_org_role('member')
def get_module_catalog():
    """GET /api/org/modules/catalog — Full module catalog with metadata.
    Returns every module with its display info, required platforms, and whether
    this org currently has it enabled.  Any member can read it.
    """
    ctx = g.org_ctx
    try:
        from AI_infrastructure.shared.org_credentials_loader import get_org_enabled_modules
        enabled = get_org_enabled_modules(g.user_id)
    except Exception:
        enabled = set()

    try:
        rows = execute_query(
            """
            SELECT mc.module_name, mc.display_name, mc.description,
                   mc.icon_class, mc.icon_color, mc.category,
                   mc.min_plan_tier, mc.required_platforms, mc.sort_order,
                   -- per-org override (NULL = using plan default)
                   oma.is_enabled AS org_override
            FROM ai_infrastructure.module_catalog mc
            LEFT JOIN ai_infrastructure.org_module_access oma
                   ON oma.module_name     = mc.module_name
                  AND oma.organisation_id = %s
            WHERE mc.is_active = TRUE
            ORDER BY mc.sort_order, mc.display_name
            """,
            (ctx['organisation_id'],),
            fetch_mode='all'
        ) or []

        catalog = []
        for r in rows:
            entry = dict(r)
            entry['is_enabled']     = r['module_name'] in enabled
            entry['has_org_override'] = r['org_override'] is not None
            catalog.append(entry)

        return jsonify({'success': True, 'modules': catalog})
    except Exception as e:
        logger.warning(f"[ORG_MODULE_CATALOG] module_catalog not yet created: {e}")
        return jsonify({'success': True, 'modules': [], 'warning': 'Module catalog not yet available'})


@org_credentials_bp.route('/modules/<module_name>', methods=['PUT'])
@require_auth
@require_org_role('admin')
def toggle_org_module(module_name: str):
    """PUT /api/org/modules/<module_name> — Enable or disable a module for this org.
    Body: { "enabled": true|false }
    Admins+ can override the plan defaults at org level.
    """
    ctx  = g.org_ctx
    data = request.get_json() or {}

    if 'enabled' not in data:
        return jsonify({'success': False, 'error': '"enabled" boolean is required'}), 400

    is_enabled = bool(data['enabled'])

    # Validate module exists
    module = execute_query(
        "SELECT module_name, min_plan_tier FROM ai_infrastructure.module_catalog WHERE module_name = %s",
        (module_name,),
        fetch_mode='one'
    )
    # Graceful: if catalog table not yet created (pre-036) just trust the name
    if module is None:
        # Check against plan_modules as fallback
        known = execute_query(
            "SELECT module_name FROM ai_infrastructure.plan_modules WHERE module_name = %s LIMIT 1",
            (module_name,),
            fetch_mode='one'
        )
        if not known:
            return jsonify({'success': False, 'error': f'Unknown module: {module_name}'}), 404

    # Upsert org override
    execute_query(
        """
        INSERT INTO ai_infrastructure.org_module_access
            (organisation_id, module_name, is_enabled, enabled_at, enabled_by)
        VALUES (%s, %s, %s, NOW(), %s)
        ON CONFLICT (organisation_id, module_name)
        DO UPDATE SET is_enabled = EXCLUDED.is_enabled,
                      enabled_at = NOW(),
                      enabled_by = EXCLUDED.enabled_by
        """,
        (ctx['organisation_id'], module_name, is_enabled, g.user_id)
    )

    action = 'enabled' if is_enabled else 'disabled'
    logger.info(
        f"[ORG_MODULE] Module '{module_name}' {action} for org {ctx['organisation_id']} "
        f"by user {g.user_id}"
    )

    return jsonify({
        'success':     True,
        'module_name': module_name,
        'is_enabled':  is_enabled,
        'message':     f'Module {module_name} {action} for this organisation.',
    })


# ============================================================================
# PER-USER MODULE ACCESS  (migration 039)
# Admins can restrict individual members from org-enabled modules.
# Semantics: user override can only restrict, never grant beyond org level.
# ============================================================================

@org_credentials_bp.route('/members/<int:target_user_id>/modules', methods=['GET'])
@require_auth
@require_org_role('admin')
def get_member_modules(target_user_id: int):
    """GET /api/org/members/<id>/modules
    Returns every org-enabled module annotated with whether this specific
    member has been restricted from it.  Admin+ only.
    """
    ctx = g.org_ctx
    org_id = ctx['organisation_id']

    # Verify target user belongs to this org
    target = execute_query(
        "SELECT id, username, email FROM ai_infrastructure.users "
        "WHERE id = %s AND organisation_id = %s",
        (target_user_id, org_id),
        fetch_mode='one'
    )
    if not target:
        return jsonify({'success': False, 'error': 'Member not found in this organisation'}), 404

    # Get org-enabled modules
    try:
        from AI_infrastructure.shared.org_credentials_loader import get_org_enabled_modules
        org_enabled = get_org_enabled_modules(target_user_id)
    except Exception:
        org_enabled = set()

    if not org_enabled:
        return jsonify({'success': True, 'user_id': target_user_id,
                        'username': target['username'], 'modules': []})

    # Get user-level restrictions
    try:
        restriction_rows = execute_query(
            "SELECT module_name FROM ai_infrastructure.user_module_access "
            "WHERE user_id = %s AND is_enabled = FALSE",
            (target_user_id,),
            fetch_mode='all'
        ) or []
        restricted = {r['module_name'] for r in restriction_rows}
    except Exception:
        restricted = set()  # table may not exist yet (pre-039)

    # Fetch display metadata for org-enabled modules
    try:
        meta_rows = execute_query(
            """
            SELECT module_name, display_name, icon_class, icon_color, category
            FROM ai_infrastructure.module_catalog
            WHERE module_name = ANY(%s) AND is_active = TRUE
            ORDER BY sort_order, display_name
            """,
            (list(org_enabled),),
            fetch_mode='all'
        ) or []
        meta_by_name = {r['module_name']: dict(r) for r in meta_rows}
    except Exception:
        meta_by_name = {}

    modules = []
    for mod_name in sorted(org_enabled):
        meta = meta_by_name.get(mod_name, {})
        user_restricted = mod_name in restricted
        modules.append({
            'module_name':     mod_name,
            'display_name':    meta.get('display_name', mod_name.replace('_', ' ').title()),
            'icon_class':      meta.get('icon_class', 'fas fa-cube'),
            'icon_color':      meta.get('icon_color', '#6B7280'),
            'category':        meta.get('category', 'other'),
            'org_enabled':     True,
            'user_restricted': user_restricted,
            'effective':       not user_restricted,
        })

    return jsonify({
        'success':  True,
        'user_id':  target_user_id,
        'username': target['username'],
        'modules':  modules,
    })


@org_credentials_bp.route('/members/<int:target_user_id>/modules/<module_name>', methods=['PUT'])
@require_auth
@require_org_role('admin')
def set_member_module(target_user_id: int, module_name: str):
    """PUT /api/org/members/<id>/modules/<module_name>
    Body: { "enabled": true | false }
    - enabled=true:  removes restriction (user inherits org access)
    - enabled=false: restricts this user from an org-enabled module
    Admin+ only.  Cannot grant access to org-disabled modules.
    """
    ctx  = g.org_ctx
    data = request.get_json() or {}

    if 'enabled' not in data:
        return jsonify({'success': False, 'error': '"enabled" boolean is required'}), 400

    is_enabled = bool(data['enabled'])
    org_id     = ctx['organisation_id']

    # Verify target belongs to this org
    target = execute_query(
        "SELECT id FROM ai_infrastructure.users WHERE id = %s AND organisation_id = %s",
        (target_user_id, org_id), fetch_mode='one'
    )
    if not target:
        return jsonify({'success': False, 'error': 'Member not found in this organisation'}), 404

    # Prevent self-restriction
    if target_user_id == g.user_id:
        return jsonify({'success': False, 'error': 'Cannot modify your own module access'}), 403

    if is_enabled:
        # Remove any restriction row (restore org default = full access)
        execute_query(
            "DELETE FROM ai_infrastructure.user_module_access "
            "WHERE user_id = %s AND module_name = %s",
            (target_user_id, module_name)
        )
        action = 're-enabled'
    else:
        # Upsert a restriction row
        execute_query(
            """
            INSERT INTO ai_infrastructure.user_module_access
                (user_id, organisation_id, module_name, is_enabled, set_at, set_by)
            VALUES (%s, %s, %s, FALSE, NOW(), %s)
            ON CONFLICT (user_id, module_name)
            DO UPDATE SET is_enabled = FALSE, set_at = NOW(), set_by = EXCLUDED.set_by
            """,
            (target_user_id, org_id, module_name, g.user_id)
        )
        action = 'restricted'

    logger.info(
        f"[USER_MODULE] Module '{module_name}' {action} for user {target_user_id} "
        f"in org {org_id} by admin {g.user_id}"
    )
    return jsonify({
        'success':     True,
        'module_name': module_name,
        'user_id':     target_user_id,
        'is_enabled':  is_enabled,
        'message':     f'Module {module_name} {action} for this member.',
    })


@org_credentials_bp.route('/members/<int:target_user_id>/modules', methods=['DELETE'])
@require_auth
@require_org_role('admin')
def reset_member_modules(target_user_id: int):
    """DELETE /api/org/members/<id>/modules
    Removes ALL per-user module overrides for this member, restoring
    them to the org defaults.  Useful when re-onboarding a member.
    Admin+ only.
    """
    ctx    = g.org_ctx
    org_id = ctx['organisation_id']

    target = execute_query(
        "SELECT id FROM ai_infrastructure.users WHERE id = %s AND organisation_id = %s",
        (target_user_id, org_id), fetch_mode='one'
    )
    if not target:
        return jsonify({'success': False, 'error': 'Member not found in this organisation'}), 404

    execute_query(
        "DELETE FROM ai_infrastructure.user_module_access WHERE user_id = %s",
        (target_user_id,)
    )
    logger.info(
        f"[USER_MODULE] All overrides reset for user {target_user_id} "
        f"in org {org_id} by admin {g.user_id}"
    )
    return jsonify({'success': True, 'message': 'All module overrides reset to org defaults.'})


# ============================================================================
# INVITATION ROUTES  (migration 026)
# ============================================================================

@org_credentials_bp.route('/invite/<int:invite_id>/send-email', methods=['POST'])
@require_auth
@require_org_role('admin')
def send_invite_email(invite_id: int):
    """
    POST /api/org/invite/<id>/send-email
    Body: { provider }   — 'gmail' or 'outlook'
    Sends the invitation email using the caller's connected OAuth account.
    Requires admin+ org role.
    """
    ctx  = g.org_ctx
    data = request.get_json() or {}
    provider = (data.get('provider') or 'gmail').lower()

    # Verify invite belongs to this org and is still pending
    inv = execute_query(
        """
        SELECT id, invited_email, invited_role, invite_token, expires_at, status
        FROM ai_infrastructure.org_invitations
        WHERE id = %s AND organisation_id = %s
        """,
        (invite_id, ctx['organisation_id']),
        fetch_mode='one'
    )
    if not inv:
        return jsonify({'success': False, 'error': 'Invitation not found'}), 404
    if inv['status'] != 'pending':
        return jsonify({'success': False, 'error': f'Cannot send email for a {inv["status"]} invitation'}), 400

    # Build accept URL and email content
    base_url   = request.host_url.rstrip('/')
    accept_url = f"{base_url}/?accept_invite={inv['invite_token']}"
    org_name   = ctx.get('org_name') or ctx.get('org_slug') or 'our organisation'
    role       = inv['invited_role']
    to_email   = inv['invited_email']

    subject = f"You're invited to join {org_name}"
    body    = (
        f"Hi,\n\n"
        f"You've been invited to join {org_name} on our AI platform as a {role}.\n\n"
        f"Click the link below to accept your invitation:\n\n"
        f"{accept_url}\n\n"
        f"This link expires on "
        f"{inv['expires_at'].strftime('%d %b %Y') if inv.get('expires_at') else 'in 7 days'}.\n\n"
        f"If you didn't expect this invitation, you can safely ignore this email.\n\nThanks"
    )

    try:
        # Always use Gmail (Outlook method currently saves as draft)
        from google_workspace.gmail import gmail_send_email
        gmail_send_email(
            to=to_email,
            subject=subject,
            body=body,
            _user_id=g.user_id,
            _injected_credentials=True
        )
        
        # Update invitation with email_sent status
        execute_query(
            """
            UPDATE ai_infrastructure.org_invitations
            SET email_sent = TRUE, email_sent_at = NOW(), email_sent_provider = %s
            WHERE id = %s
            """,
            ('gmail', invite_id)
        )

    except Exception as e:
        logger.error(f'[ORG_INVITE] send-email failed: {e}', exc_info=True)
        return jsonify({'success': False, 'error': f'Failed to send email: {e}'}), 500

    logger.info(f'[ORG_INVITE] Invite {invite_id} email sent via {provider} to {to_email} by user {g.user_id}')
    return jsonify({'success': True, 'provider': provider, 'sent_to': to_email})


@org_credentials_bp.route('/invite', methods=['POST'])
@require_auth
@require_org_role('admin')
def send_invite():
    """
    POST /api/org/invite — Create an invitation and optionally send it via email.
    Body: { email, role?, provider? }
      role     — 'viewer'|'member'|'manager'|'admin'  (default: 'member')
      provider — 'gmail'|'outlook'  (optional; if set, email is sent automatically)
    Requires admin+ org role.
    """
    ctx  = g.org_ctx
    data = request.get_json() or {}

    email    = (data.get('email') or '').strip().lower()
    role     = (data.get('role') or 'member').strip().lower()
    provider = (data.get('provider') or '').strip().lower() or None

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Valid email address required'}), 400

    valid_roles = ('viewer', 'member', 'manager', 'admin')
    if role not in valid_roles:
        return jsonify({'success': False, 'error': f'Invalid role. Must be one of: {valid_roles}'}), 400

    if role == 'owner':
        return jsonify({'success': False, 'error': 'Cannot invite someone as owner'}), 400

    # Check if this email already belongs to an existing org member
    existing_user = execute_query(
        "SELECT id, organisation_id FROM ai_infrastructure.users WHERE email = %s",
        (email,), fetch_mode='one'
    )
    if existing_user and existing_user.get('organisation_id') == ctx['organisation_id']:
        return jsonify({'success': False, 'error': 'This user is already a member of your organisation'}), 409

    try:
        # Revoke any existing pending invite for this email in this org
        execute_query(
            """
            UPDATE ai_infrastructure.org_invitations
            SET status = 'revoked'
            WHERE organisation_id = %s AND invited_email = %s AND status = 'pending'
            """,
            (ctx['organisation_id'], email)
        )

        row = execute_query(
            """
            INSERT INTO ai_infrastructure.org_invitations
                (organisation_id, invited_email, invited_role, invited_by)
            VALUES (%s, %s, %s, %s)
            RETURNING id, invite_token, expires_at
            """,
            (ctx['organisation_id'], email, role, g.user_id),
            fetch_mode='one'
        )

        if not row:
            return jsonify({'success': False, 'error': 'Failed to create invitation'}), 500

        invite_token = str(row['invite_token'])
        invite_id    = row['id']
        expires_at   = row['expires_at'].isoformat() if row.get('expires_at') else None

        base_url   = request.host_url.rstrip('/')
        accept_url = f"{base_url}/?accept_invite={invite_token}"

        logger.info(f"[ORG_INVITE] Invite created: org={ctx['organisation_id']} "
                    f"email={email} role={role} token={invite_token[:8]}...")

        # Attempt email sending if a provider was specified
        email_sent  = False
        email_error = None

        if provider in ('gmail', 'outlook'):
            try:
                org_name = ctx.get('org_name') or ctx.get('org_slug') or 'our organisation'
                subject  = f"You're invited to join {org_name}"
                body     = (
                    f"Hi,\n\n"
                    f"You've been invited to join {org_name} on our AI platform as a {role}.\n\n"
                    f"Click the link below to accept your invitation:\n\n"
                    f"{accept_url}\n\n"
                    f"This link expires in 7 days.\n\n"
                    f"If you didn't expect this invitation, you can safely ignore this email.\n\nThanks"
                )

                # Always use Gmail if provider specified (Outlook method currently saves as draft)
                from google_workspace.gmail import gmail_send_email
                gmail_send_email(
                    to=email, subject=subject, body=body,
                    _user_id=g.user_id, _injected_credentials=True
                )
                email_sent = True
                
                # Update invitation with email_sent status
                execute_query(
                    """
                    UPDATE ai_infrastructure.org_invitations
                    SET email_sent = TRUE, email_sent_at = NOW(), email_sent_provider = %s
                    WHERE id = %s
                    """,
                    ('gmail', invite_id)
                )
                logger.info(f"[ORG_INVITE] Invitation email sent to {email}")

            except Exception as mail_err:
                email_error = str(mail_err)
                logger.error(f"[ORG_INVITE] Email send failed (invite still created): {mail_err}", exc_info=True)

        return jsonify({
            'success':     True,
            'message':     f'Invitation created for {email}',
            'invite_id':   invite_id,
            'accept_url':  accept_url,
            'expires_at':  expires_at,
            'email_sent':  email_sent,
            'email_error': email_error,
        }), 201

    except Exception as e:
        logger.error(f"[ORG_INVITE] Error creating invite: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'Failed to create invitation: {e}'}), 500


@org_credentials_bp.route('/invite/pending', methods=['GET'])
@require_auth
@require_org_role('admin')
def list_pending_invites():
    """GET /api/org/invite/pending — List non-revoked invitations. Admin+."""
    ctx = g.org_ctx

    rows = execute_query(
        """
        SELECT
            i.id,
            i.invited_email,
            i.invited_role,
            i.status,
            i.invite_token,
            i.expires_at,
            i.created_at,
            i.email_sent,
            i.email_sent_at,
            i.email_sent_provider,
            u.username  AS invited_by_username,
            u.email     AS invited_by_email
        FROM ai_infrastructure.org_invitations i
        LEFT JOIN ai_infrastructure.users u ON u.id = i.invited_by
        WHERE i.organisation_id = %s
          AND i.status IN ('pending', 'accepted')
        ORDER BY i.created_at DESC
        LIMIT 200
        """,
        (ctx['organisation_id'],),
        fetch_mode='all'
    ) or []

    return jsonify({
        'success': True,
        'invitations': [
            {
                'id':                   r['id'],
                'invited_email':        r['invited_email'],
                'invited_role':         r['invited_role'],
                'status':               r['status'],
                'invite_token':         str(r['invite_token']),
                'expires_at':           r['expires_at'].isoformat() if r.get('expires_at') else None,
                'created_at':           r['created_at'].isoformat() if r.get('created_at') else None,
                'email_sent':           r.get('email_sent', False),
                'email_sent_at':        r['email_sent_at'].isoformat() if r.get('email_sent_at') else None,
                'email_sent_provider':  r.get('email_sent_provider'),
                'invited_by_username':  r.get('invited_by_username'),
                'invited_by_email':     r.get('invited_by_email'),
            }
            for r in rows
        ],
        'total': len(rows),
    })


@org_credentials_bp.route('/invite/<int:invite_id>', methods=['DELETE'])
@require_auth
@require_org_role('admin')
def revoke_invite(invite_id: int):
    """DELETE /api/org/invite/<id> — Revoke a pending invitation. Admin+."""
    ctx = g.org_ctx

    row = execute_query(
        "SELECT id, status FROM ai_infrastructure.org_invitations "
        "WHERE id = %s AND organisation_id = %s",
        (invite_id, ctx['organisation_id']),
        fetch_mode='one'
    )

    if not row:
        return jsonify({'success': False, 'error': 'Invitation not found'}), 404

    if row['status'] != 'pending':
        return jsonify({'success': False, 'error': f'Cannot revoke a {row["status"]} invitation'}), 400

    execute_query(
        "UPDATE ai_infrastructure.org_invitations SET status = 'revoked' WHERE id = %s",
        (invite_id,)
    )

    logger.info(f"[ORG_INVITE] Invite {invite_id} revoked by user {g.user_id}")
    return jsonify({'success': True, 'message': 'Invitation revoked'})


@org_credentials_bp.route('/invite/accept', methods=['GET'])
def accept_invite_info():
    """
    GET /api/org/invite/accept?token=<uuid>
    Validate a token and return invite details (org name, role, expiry).
    Called by frontend before showing the accept confirmation page.
    No auth required — the token IS the credential.
    """
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'success': False, 'error': 'Token required'}), 400

    row = execute_query(
        """
        SELECT
            i.id, i.invited_email, i.invited_role, i.status, i.expires_at,
            o.name AS org_name, o.slug AS org_slug, o.display_name AS org_display_name
        FROM ai_infrastructure.org_invitations i
        JOIN ai_infrastructure.organisations o ON o.id = i.organisation_id
        WHERE i.invite_token = %s
        """,
        (token,),
        fetch_mode='one'
    )

    if not row:
        return jsonify({'success': False, 'error': 'Invalid invitation token'}), 404

    if row['status'] == 'accepted':
        return jsonify({'success': False, 'error': 'This invitation has already been accepted'}), 409
    if row['status'] in ('expired', 'revoked'):
        return jsonify({'success': False, 'error': f'This invitation has been {row["status"]}'}), 410
    if row['expires_at'] and row['expires_at'] < datetime.now(row['expires_at'].tzinfo):
        return jsonify({'success': False, 'error': 'This invitation has expired'}), 410

    return jsonify({
        'success':          True,
        'invited_email':    row['invited_email'],
        'invited_role':     row['invited_role'],
        'org_name':         row.get('org_display_name') or row.get('org_name'),
        'org_slug':         row['org_slug'],
        'expires_at':       row['expires_at'].isoformat() if row.get('expires_at') else None,
    })


@org_credentials_bp.route('/invite/accept', methods=['POST'])
@require_auth
def accept_invite():
    """
    POST /api/org/invite/accept
    Body: { token }   — accepts the invitation, links user to the org.
    Requires the user to already be logged in (authenticated).
    """
    data  = request.get_json() or {}
    token = (data.get('token') or '').strip()

    if not token:
        return jsonify({'success': False, 'error': 'Token required'}), 400

    row = execute_query(
        """
        SELECT i.id, i.organisation_id, i.invited_email, i.invited_role,
               i.status, i.expires_at
        FROM ai_infrastructure.org_invitations i
        WHERE i.invite_token = %s
        """,
        (token,),
        fetch_mode='one'
    )

    if not row:
        return jsonify({'success': False, 'error': 'Invalid invitation token'}), 404
    if row['status'] != 'pending':
        return jsonify({'success': False, 'error': f'Invitation is {row["status"]}'}), 409
    if row['expires_at'] and row['expires_at'] < datetime.now(row['expires_at'].tzinfo):
        return jsonify({'success': False, 'error': 'Invitation has expired'}), 410

    # Verify the logged-in user's email matches the invite
    user_row = execute_query(
        "SELECT id, email, organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (g.user_id,), fetch_mode='one'
    )
    if not user_row:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if user_row['email'].lower() != row['invited_email'].lower():
        return jsonify({
            'success': False,
            'error': f'This invitation was sent to {row["invited_email"]}. '
                     f'You are logged in as {user_row["email"]}. '
                     'Please log in with the invited email address.'
        }), 403

    if user_row.get('organisation_id'):
        return jsonify({'success': False, 'error': 'You are already a member of an organisation'}), 409

    # Link the user to the org and mark invite accepted
    execute_query(
        "UPDATE ai_infrastructure.users "
        "SET organisation_id = %s, org_role = %s "
        "WHERE id = %s",
        (row['organisation_id'], row['invited_role'], g.user_id)
    )
    execute_query(
        "UPDATE ai_infrastructure.org_invitations "
        "SET status = 'accepted', accepted_by = %s, accepted_at = NOW() "
        "WHERE id = %s",
        (g.user_id, row['id'])
    )

    logger.info(f"[ORG_INVITE] User {g.user_id} accepted invite {row['id']} "
                f"→ org {row['organisation_id']} as {row['invited_role']}")

    return jsonify({
        'success':      True,
        'message':      'You have joined the organisation.',
        'org_role':     row['invited_role'],
    })
