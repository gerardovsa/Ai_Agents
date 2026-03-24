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

from AI_infrastructure.shared.database_utils import execute_query

logger = logging.getLogger(__name__)

org_credentials_bp = Blueprint('org_credentials', __name__, url_prefix='/api/org')

# ============================================================================
# ROLE HIERARCHY
# ============================================================================

ROLE_LEVELS = {
    'viewer':  1,
    'member':  2,
    'manager': 3,
    'admin':   4,
    'owner':   5,
}


def role_level(role_name: str) -> int:
    return ROLE_LEVELS.get(role_name, 0)


# ============================================================================
# AUTH / PERMISSION DECORATORS
# ============================================================================

def require_auth(f):
    """JWT authentication decorator. Sets g.user_id and g.user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        from AI_infrastructure.auth.user_auth import UserAuthManager
        token = None

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        try:
            auth_manager = UserAuthManager()
            user = auth_manager.verify_token(token)
            if not user:
                return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
            g.user_id = user['id']
            g.user = user
        except Exception as e:
            logger.error(f"[ORG_CREDS] Auth error: {e}")
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401

        return f(*args, **kwargs)
    return decorated


def get_user_org_context(user_id: int) -> Optional[dict]:
    """Fetch the user's org membership + role. Returns None if no org."""
    row = execute_query(
        """
        SELECT
            u.organisation_id,
            u.org_role,
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
    return row if row and row.get('organisation_id') else None


def require_org_role(minimum_role: str):
    """Decorator factory. Enforces minimum org_role. Apply AFTER @require_auth."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ctx = get_user_org_context(g.user_id)
            if not ctx:
                return jsonify({
                    'success': False,
                    'error': 'You are not a member of any organisation'
                }), 403

            if role_level(ctx['org_role']) < role_level(minimum_role):
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
    raw_cred_value = row.get('credential_value') or ''
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
# ROUTES: ORGANISATION INFO
# ============================================================================

@org_credentials_bp.route('/info', methods=['GET'])
@require_auth
@require_org_role('member')
def get_org_info():
    """GET /api/org/info — Org details for any org member."""
    ctx = g.org_ctx

    org = execute_query(
        """
        SELECT id, name, slug, plan_tier, display_name, logo_url,
               timezone, country_code, is_active, created_at
        FROM ai_infrastructure.organisations WHERE id = %s
        """,
        (ctx['organisation_id'],),
        fetch_mode='one'
    )
    if not org:
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
        },
        'your_role': ctx['org_role'],
    })


@org_credentials_bp.route('/info', methods=['PUT'])
@require_auth
@require_org_role('owner')
def update_org_info():
    """PUT /api/org/info — Update org metadata. Owner only."""
    ctx = g.org_ctx
    data = request.get_json() or {}
    allowed = ['display_name', 'logo_url', 'timezone', 'country_code']
    updates = {k: v for k, v in data.items() if k in allowed}

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
        SELECT id, username, email, org_role, is_active, last_login, created_at
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
                'last_login': m['last_login'].isoformat() if m.get('last_login') else None,
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

    if new_role not in ROLE_LEVELS:
        return jsonify({
            'success': False,
            'error': f'Invalid role. Must be one of: {", ".join(ROLE_LEVELS)}'
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
        "UPDATE ai_infrastructure.users SET org_role = %s WHERE id = %s",
        (new_role, target_user_id)
    )
    return jsonify({
        'success': True,
        'message': f'Role updated to {new_role}',
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

    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id = NULL, org_role = 'member' WHERE id = %s",
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
            credential_value or None,
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
# INVITATION ROUTES  (migration 026)
# ============================================================================

@org_credentials_bp.route('/invite', methods=['POST'])
@require_auth
@require_org_role('admin')
def send_invite():
    """
    POST /api/org/invite — Send an invitation to join the organisation.
    Body: { email, role? }   role defaults to 'member'.
    Requires admin+ org role.
    """
    ctx  = g.org_ctx
    data = request.get_json() or {}

    email = (data.get('email') or '').strip().lower()
    role  = (data.get('role') or 'member').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Valid email address required'}), 400

    valid_roles = ('viewer', 'member', 'manager', 'admin')
    if role not in valid_roles:
        return jsonify({'success': False, 'error': f'Invalid role. Must be one of: {valid_roles}'}), 400

    # Owners cannot be invited — they create the org directly
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
        # Upsert: revoke any existing pending invite for this email in this org,
        # then insert a fresh one with a new token and expiry.
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
        expires_at   = row['expires_at'].isoformat() if row.get('expires_at') else None

        # Build accept URL (frontend handles this route)
        base_url     = request.host_url.rstrip('/')
        accept_url   = f"{base_url}/?accept_invite={invite_token}"

        logger.info(f"[ORG_INVITE] Invite created: org={ctx['organisation_id']} "
                    f"email={email} role={role} token={invite_token[:8]}...")

        # TODO: Send actual email via SendGrid / SMTP when email service is configured.
        # For now, return the accept URL so it can be manually shared.
        return jsonify({
            'success':    True,
            'message':    f'Invitation created for {email}',
            'invite_id':  row['id'],
            'accept_url': accept_url,
            'expires_at': expires_at,
            'email_sent': False,   # flip to True once email service is wired
        }), 201

    except Exception as e:
        logger.error(f"[ORG_INVITE] Error creating invite: {e}")
        return jsonify({'success': False, 'error': 'Failed to create invitation'}), 500


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
