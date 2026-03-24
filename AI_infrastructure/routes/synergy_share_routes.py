"""
Synergy Session Share & Visibility Routes
=========================================
REST API endpoints for session visibility control and member management.
Called by the "Share & Visibility" popup on the Synergy board (synergy-board-init.js).

Endpoints:
  PATCH  /api/synergy/sessions/<session_id>/visibility   — set private/shared/team
  GET    /api/synergy/sessions/<session_id>/members       — list invited members
  POST   /api/synergy/sessions/<session_id>/members       — invite a user by username/email
  DELETE /api/synergy/sessions/<session_id>/members/<uid> — remove a member

Multi-tenancy rules enforced:
  - Only the session OWNER or a session ADMIN-member can change visibility or manage members.
  - Team visibility is only allowed when the session has an organisation_id set.
  - OWNER can always access their own sessions regardless of visibility setting.

DB requirements:
  Migration 025 (025_synergy_sessions_multitenancy.sql) must be applied in Supabase.
  Tables used:
    synergy_sessions.synergy_sessions  (organisation_id, visibility, owner_user_id)
    synergy_sessions.session_members   (session_id, user_id, role, added_by)
    ai_infrastructure.users            (id, username, email, organisation_id)
"""

from flask import Blueprint, request, jsonify, g
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database_utils import get_database_connection, convert_sql_placeholders

synergy_share_bp = Blueprint('synergy_share', __name__, url_prefix='/api/synergy/sessions')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_session_or_404(cursor, session_id: str):
    """Fetch session row or return None."""
    sql, params = convert_sql_placeholders(
        "SELECT session_id, owner_user_id, organisation_id, visibility "
        "FROM synergy_sessions WHERE session_id = %s",
        (session_id,)
    )
    cursor.execute(sql, params)
    return cursor.fetchone()


def _is_session_admin(cursor, session_id: str, user_id: int, owner_user_id) -> bool:
    """Return True if user_id is the session owner OR an admin-role session member."""
    if user_id == owner_user_id:
        return True
    sql, params = convert_sql_placeholders(
        "SELECT 1 FROM session_members WHERE session_id = %s AND user_id = %s AND role = 'admin'",
        (session_id, user_id)
    )
    cursor.execute(sql, params)
    return cursor.fetchone() is not None


def _require_auth() -> tuple:
    """Return (user_id, org_id) from g or (None, None)."""
    user_id = getattr(g, 'rls_user_id', None)
    org_id  = getattr(g, 'rls_organisation_id', None)
    return user_id, org_id


# ---------------------------------------------------------------------------
# PATCH /api/synergy/sessions/<session_id>/visibility
# ---------------------------------------------------------------------------

@synergy_share_bp.route('/<session_id>/visibility', methods=['PATCH'])
def update_visibility(session_id: str):
    """
    Change the visibility of a session.

    Body: { "visibility": "private" | "shared" | "team" }

    Rules:
      - Only owner or session-admin can change visibility.
      - 'team' requires the session to have an organisation_id.
    """
    user_id, org_id = _require_auth()
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    data = request.get_json(silent=True) or {}
    visibility = data.get('visibility')
    if visibility not in ('private', 'shared', 'team'):
        return jsonify({
            'success': False,
            'error': "visibility must be 'private', 'shared', or 'team'"
        }), 400

    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                session = _get_session_or_404(cursor, session_id)
                if not session:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                owner = session.get('owner_user_id')
                if not _is_session_admin(cursor, session_id, user_id, owner):
                    return jsonify({
                        'success': False,
                        'error': 'Only the session owner or an admin member can change visibility'
                    }), 403

                # Team visibility requires an organisation
                if visibility == 'team' and not session.get('organisation_id'):
                    # Auto-assign caller's org if available
                    if org_id:
                        sql, params = convert_sql_placeholders(
                            "UPDATE synergy_sessions "
                            "SET visibility = %s, organisation_id = %s, updated_at = %s "
                            "WHERE session_id = %s",
                            (visibility, org_id, datetime.now().isoformat(), session_id)
                        )
                    else:
                        return jsonify({
                            'success': False,
                            'error': "Cannot set 'team' visibility — session has no organisation. "
                                     "Assign an organisation_id first."
                        }), 409
                else:
                    sql, params = convert_sql_placeholders(
                        "UPDATE synergy_sessions SET visibility = %s, updated_at = %s "
                        "WHERE session_id = %s",
                        (visibility, datetime.now().isoformat(), session_id)
                    )

                cursor.execute(sql, params)
                conn.commit()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'visibility': visibility,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
# GET /api/synergy/sessions/<session_id>/members
# ---------------------------------------------------------------------------

@synergy_share_bp.route('/<session_id>/members', methods=['GET'])
def list_members(session_id: str):
    """
    List all users explicitly invited to a session.
    Returns: list of { user_id, username, email, role, added_at }
    """
    user_id, _ = _require_auth()
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                session = _get_session_or_404(cursor, session_id)
                if not session:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                # Caller must be owner or an existing member to see the member list
                owner = session.get('owner_user_id')
                is_member_sql, is_member_params = convert_sql_placeholders(
                    "SELECT 1 FROM session_members WHERE session_id = %s AND user_id = %s",
                    (session_id, user_id)
                )
                cursor.execute(is_member_sql, is_member_params)
                is_member = cursor.fetchone() is not None

                if user_id != owner and not is_member:
                    return jsonify({'success': False, 'error': 'Access denied'}), 403

                # Join with ai_infrastructure.users for display info
                sql, params = convert_sql_placeholders(
                    """
                    SELECT
                        sm.user_id,
                        sm.role,
                        sm.added_at,
                        u.username,
                        u.email
                    FROM session_members sm
                    LEFT JOIN ai_infrastructure.users u ON u.id = sm.user_id
                    WHERE sm.session_id = %s
                    ORDER BY sm.added_at ASC
                    """,
                    (session_id,)
                )
                cursor.execute(sql, params)
                rows = cursor.fetchall()

        members = [dict(r) for r in (rows or [])]
        return jsonify({'success': True, 'members': members, 'total': len(members)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
# POST /api/synergy/sessions/<session_id>/members
# ---------------------------------------------------------------------------

@synergy_share_bp.route('/<session_id>/members', methods=['POST'])
def invite_member(session_id: str):
    """
    Invite a user to a shared session.

    Body: { "user_id": 12 }
       OR { "username": "bob" }
       OR { "email": "bob@example.com" },
    Optional: { "role": "viewer" | "editor" | "admin" }  — defaults to 'viewer'

    Rules:
      - Only the session owner or an admin-member can invite.
      - User must exist in ai_infrastructure.users.
      - Duplicate invites are silently ignored (upsert on role).
    """
    user_id, org_id = _require_auth()
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    data = request.get_json(silent=True) or {}
    role = data.get('role', 'viewer')
    if role not in ('viewer', 'editor', 'admin'):
        role = 'viewer'

    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                session = _get_session_or_404(cursor, session_id)
                if not session:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                owner = session.get('owner_user_id')
                if not _is_session_admin(cursor, session_id, user_id, owner):
                    return jsonify({
                        'success': False,
                        'error': 'Only the session owner or an admin member can invite users'
                    }), 403

                # Resolve the invite target to a user row
                target_user = None
                if data.get('user_id'):
                    sql, params = convert_sql_placeholders(
                        "SELECT id, username, email FROM ai_infrastructure.users WHERE id = %s",
                        (int(data['user_id']),)
                    )
                    cursor.execute(sql, params)
                    target_user = cursor.fetchone()
                elif data.get('username'):
                    sql, params = convert_sql_placeholders(
                        "SELECT id, username, email FROM ai_infrastructure.users WHERE username = %s",
                        (data['username'],)
                    )
                    cursor.execute(sql, params)
                    target_user = cursor.fetchone()
                elif data.get('email'):
                    sql, params = convert_sql_placeholders(
                        "SELECT id, username, email FROM ai_infrastructure.users WHERE email = %s",
                        (data['email'],)
                    )
                    cursor.execute(sql, params)
                    target_user = cursor.fetchone()
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Provide user_id, username, or email to identify the invitee'
                    }), 400

                if not target_user:
                    return jsonify({'success': False, 'error': 'User not found'}), 404

                target_id = target_user['id'] if isinstance(target_user, dict) else target_user[0]

                # Cannot invite yourself as the owner
                if target_id == owner:
                    return jsonify({
                        'success': False,
                        'error': 'The session owner is already the primary administrator'
                    }), 409

                # Upsert: add or update role if already a member
                sql, params = convert_sql_placeholders(
                    """
                    INSERT INTO session_members (session_id, user_id, role, added_by, added_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (session_id, user_id) DO UPDATE SET role = EXCLUDED.role
                    """,
                    (session_id, target_id, role, user_id, datetime.now().isoformat())
                )
                cursor.execute(sql, params)
                conn.commit()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id':    target_id,
            'username':   (target_user.get('username') if isinstance(target_user, dict)
                           else None),
            'role':       role,
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
# DELETE /api/synergy/sessions/<session_id>/members/<target_user_id>
# ---------------------------------------------------------------------------

@synergy_share_bp.route('/<session_id>/members/<int:target_user_id>', methods=['DELETE'])
def remove_member(session_id: str, target_user_id: int):
    """
    Remove a user from a session's member list.

    Rules:
      - Session owner or admin-member can remove anyone.
      - A non-admin member can remove themselves only.
    """
    user_id, _ = _require_auth()
    if not user_id:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    try:
        with get_database_connection('synergy_sessions') as conn:
            with conn.cursor() as cursor:
                session = _get_session_or_404(cursor, session_id)
                if not session:
                    return jsonify({'success': False, 'error': 'Session not found'}), 404

                owner = session.get('owner_user_id')
                is_admin = _is_session_admin(cursor, session_id, user_id, owner)
                is_self  = (user_id == target_user_id)

                if not is_admin and not is_self:
                    return jsonify({
                        'success': False,
                        'error': 'You can only remove yourself, or be the owner/admin to remove others'
                    }), 403

                sql, params = convert_sql_placeholders(
                    "DELETE FROM session_members WHERE session_id = %s AND user_id = %s",
                    (session_id, target_user_id)
                )
                cursor.execute(sql, params)
                removed = cursor.rowcount > 0
                conn.commit()

        if not removed:
            return jsonify({'success': False, 'error': 'User is not a member of this session'}), 404

        return jsonify({'success': True, 'session_id': session_id, 'removed_user_id': target_user_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
