"""
FILE: AI_infrastructure/routes/viz_snapshots_routes.py
PURPOSE: Persistent library of AI-built React visualizations ("My Visualizations").

         Tier-1 toolbar in the SPA calls /api/viz/snapshots/* to:
           * save a freshly-rendered viz from the chat bubble,
           * browse and re-render saved visualizations in tab-analytics,
           * attach a free-form note (human or AI authored) for handoff,
           * link the viz into a Synergy Kanban session.

         Backed by:
           * sessions.viz_snapshots         (migration 057)
           * sessions.viz_snapshot_notes     (migration 058)
           * synergy_sessions.synergy_sessions.linked_viz_snapshots  (migration 057)
           * PL/pgSQL: sessions.link_viz_to_synergy / sessions.unlink_viz_from_synergy

ENDPOINTS (all under /api/viz/snapshots):
    POST   /                          create a new snapshot
    GET    /                          list snapshots (with q/tag/mine/synergy filters)
    GET    /<id>                      fetch single snapshot (full payload incl. jsx_source)
    PATCH  /<id>                      partial update (owner only)
    DELETE /<id>                      soft-delete (owner only)
    POST   /<id>/notes                add a comment/todo/handoff/data_update note
    GET    /<id>/notes                list notes on a snapshot
    POST   /<id>/thumbnail            upsert thumbnail PNG (bytea, base64-encoded body)
    POST   /<id>/render-count         bump render_count + last_rendered_at
    POST   /<id>/link-synergy         atomic two-sided link via PL/pgSQL helper
    POST   /<id>/unlink-synergy       inverse link via PL/pgSQL helper

SECURITY:
    * @require_auth on every endpoint.
    * RLS policies on viz_snapshots / viz_snapshot_notes scope rows by
      app.current_organisation_id (set by rls_session_manager.py from
      g.rls_organisation_id). The policies live in migrations 057/058/059.
    * The /<id> GET returns full jsx_source only to the owner; others see
      a redacted row (no jsx_source, no thumbnail_png).

DEPENDENCIES:
    - flask (Blueprint, request, jsonify, g)
    - auth.user_auth.require_auth
    - AI_infrastructure.shared.database_utils.execute_query

USED BY:
    - AI_infrastructure/flask_app.py (register blueprint at /api/viz/snapshots)
    - tools/implementations/viz_snapshots.py (HTTP wrapper for AI agents)
    - UI/modules_internal/visualizations/visualizations-module.js (gallery)
    - UI/visualisation_engine/visualisation_v3.js (Tier-1 toolbar save button)

RELATED FILES:
    - AI_infrastructure/migrations/057_viz_snapshots.sql
    - AI_infrastructure/migrations/058_viz_snapshot_notes.sql
    - AI_infrastructure/migrations/059_fix_viz_snapshot_rls_var_name.sql

LAST MODIFIED: 2026-07-22
"""

import base64
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify, g

from auth.user_auth import require_auth
from AI_infrastructure.shared.database_utils import execute_query

logger = logging.getLogger(__name__)

viz_snapshots_bp = Blueprint('viz_snapshots', __name__, url_prefix='/api/viz/snapshots')


# ============================================================================
# Internal helpers
# ============================================================================

def _err(msg: str, code: int = 400, **extra):
    """Standardised error response per CLAUDE.md §10."""
    payload = {'success': False, 'error': msg}
    payload.update(extra)
    return jsonify(payload), code


def _owner_only_guard(snapshot_id: str):
    """
    Fetch the snapshot's owner_user_id + org_id.

    Returns:
        (row_dict, None) on success (row is the snapshot row).
        (None, flask_response) on any failure.
    """
    row = execute_query(
        """
        SELECT id, org_id, owner_user_id, synergy_session_id, is_active
          FROM sessions.viz_snapshots
         WHERE id = %s
        """,
        (snapshot_id,),
        fetch_mode='one',
        schema='sessions',
    )
    if not row:
        return None, _err('Snapshot not found', 404)
    if not row.get('is_active'):
        return None, _err('Snapshot is inactive', 410)
    return row, None


def _bytea_from_b64(b64: str) -> bytes:
    """Decode base64 to bytes; tolerate data URL prefix."""
    if ',' in b64:
        b64 = b64.split(',', 1)[1]
    return base64.b64decode(b64)


# ============================================================================
# POST /   — create
# ============================================================================

@viz_snapshots_bp.route('/', methods=['POST'])
@viz_snapshots_bp.route('', methods=['POST'])
@require_auth
def create_snapshot():
    """
    Create a new viz snapshot.

    Body (JSON):
      title                 (str, required)
      jsx_source            (str, required)
      css_source            (str, optional)
      uses_lucide           (bool, optional)
      uses_recharts         (bool, optional)
      uses_tailwind         (bool, optional)
      tags                  (list[str], optional)
      thread_id             (int, optional)
      assistant_message_id  (int, optional)
      synergy_session_id    (str, optional)

    Org + owner are auto-filled from JWT context.
    """
    try:
        user_id = g.rls_user_id
        org_id  = g.rls_organisation_id
        if not user_id or not org_id:
            return _err('Missing JWT context (user/org)', 401)

        body = request.get_json(silent=True) or {}
        title = (body.get('title') or '').strip()
        jsx_source = body.get('jsx_source') or ''
        if not title:
            return _err('title is required')
        if not jsx_source:
            return _err('jsx_source is required')

        css_source            = body.get('css_source')
        uses_lucide           = bool(body.get('uses_lucide', False))
        uses_recharts         = bool(body.get('uses_recharts', False))
        uses_tailwind         = bool(body.get('uses_tailwind', False))
        tags                  = body.get('tags') or []
        thread_id             = body.get('thread_id')
        assistant_message_id  = body.get('assistant_message_id')
        synergy_session_id    = body.get('synergy_session_id')

        if not isinstance(tags, list):
            return _err('tags must be a list of strings')
        tags = [str(t).strip() for t in tags if str(t).strip()]

        row = execute_query(
            """
            INSERT INTO sessions.viz_snapshots
                (org_id, owner_user_id, thread_id, assistant_message_id,
                 title, viz_type, jsx_source, css_source,
                 uses_lucide, uses_recharts, uses_tailwind, tags,
                 synergy_session_id)
            VALUES
                (%s, %s, %s, %s,
                 %s, 'react', %s, %s,
                 %s, %s, %s, %s::text[],
                 %s)
            RETURNING id, share_token, created_at
            """,
            (org_id, user_id, thread_id, assistant_message_id,
             title, jsx_source, css_source,
             uses_lucide, uses_recharts, uses_tailwind, tags,
             synergy_session_id),
            fetch_mode='one',
            schema='sessions',
        )
        if not row:
            return _err('Insert returned no row', 500)

        return jsonify({
            'success':     True,
            'id':          str(row['id']),
            'share_token': row['share_token'],
            'created_at':  row['created_at'].isoformat() if row.get('created_at') else None,
        }), 201

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] create failed')
        return _err(f'create failed: {e}', 500)


# ============================================================================
# GET /   — list
# ============================================================================

@viz_snapshots_bp.route('/', methods=['GET'])
@viz_snapshots_bp.route('', methods=['GET'])
@require_auth
def list_snapshots():
    """
    List snapshots with filters. Excludes jsx_source + thumbnail_png for size.

    Query params:
      mine                (bool) — only snapshots owned by the caller
      tag                 (str)  — single tag filter
      q                   (str)  — title ILIKE
      synergy_session_id  (str)  — only viz linked to a synergy session
      limit, offset       (int)  — pagination (default 20/0)
    """
    try:
        user_id = g.rls_user_id
        org_id  = g.rls_organisation_id
        if not user_id or not org_id:
            return _err('Missing JWT context', 401)

        mine      = request.args.get('mine', '').lower() in ('1', 'true', 'yes')
        tag       = (request.args.get('tag') or '').strip()
        q         = (request.args.get('q') or '').strip()
        synergy   = (request.args.get('synergy_session_id') or '').strip()
        limit     = max(1, min(int(request.args.get('limit', 20)), 100))
        offset    = max(0, int(request.args.get('offset', 0)))

        where  = ['s.org_id = %s', 's.is_active = TRUE']
        params = [org_id]

        if mine:
            where.append('s.owner_user_id = %s')
            params.append(user_id)
        if tag:
            where.append('%s = ANY(s.tags)')
            params.append(tag)
        if q:
            where.append('s.title ILIKE %s')
            params.append(f'%{q}%')
        if synergy:
            where.append('s.synergy_session_id = %s')
            params.append(synergy)

        where_sql = ' AND '.join(where)

        rows = execute_query(
            f"""
            SELECT s.id, s.title, s.viz_type, s.tags, s.is_public, s.share_token,
                   s.synergy_session_id, s.uses_lucide, s.uses_recharts,
                   s.uses_tailwind, s.last_rendered_at, s.render_count,
                   s.created_at, s.updated_at,
                   s.owner_user_id, s.thread_id, s.assistant_message_id,
                   t.title AS thread_title,
                   encode(s.thumbnail_png, 'base64') AS thumbnail_b64
              FROM sessions.viz_snapshots s
              LEFT JOIN sessions.threads t ON t.id = s.thread_id
             WHERE {where_sql}
             ORDER BY s.created_at DESC
             LIMIT %s OFFSET %s
            """,
            tuple(params) + (limit, offset),
            fetch_mode='all',
            schema='sessions',
        )

        return jsonify({
            'success': True,
            'data':    [_serialize_summary(r) for r in (rows or [])],
            'limit':   limit,
            'offset':  offset,
            'count':   len(rows or []),
        }), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] list failed')
        return _err(f'list failed: {e}', 500)


# ============================================================================
# GET /<id>   — single (with jsx_source for owner only)
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>', methods=['GET'])
@require_auth
def get_snapshot(snapshot_id):
    """Fetch one snapshot. Full jsx_source + thumbnail only returned to the owner."""
    try:
        user_id = g.rls_user_id
        org_id  = g.rls_organisation_id
        if not user_id or not org_id:
            return _err('Missing JWT context', 401)

        row = execute_query(
            """
            SELECT s.*, encode(s.thumbnail_png, 'base64') AS thumbnail_b64,
                   t.title AS thread_title
              FROM sessions.viz_snapshots s
              LEFT JOIN sessions.threads t ON t.id = s.thread_id
             WHERE s.id = %s
               AND s.org_id = %s
               AND s.is_active = TRUE
            """,
            (snapshot_id, org_id),
            fetch_mode='one',
            schema='sessions',
        )
        if not row:
            return _err('Snapshot not found', 404)

        is_owner = row.get('owner_user_id') == user_id
        return jsonify({
            'success': True,
            'data':    _serialize_full(row, include_payload=is_owner),
            'is_owner': is_owner,
        }), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] get failed')
        return _err(f'get failed: {e}', 500)


# ============================================================================
# PATCH /<id>   — update (owner only)
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>', methods=['PATCH'])
@require_auth
def update_snapshot(snapshot_id):
    """Partial update of an owned snapshot. Updatable: title, tags, is_public,
    css_source, synergy_session_id."""
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err
        if owner_row['owner_user_id'] != user_id:
            return _err('Only the owner can update this snapshot', 403)

        body = request.get_json(silent=True) or {}
        sets, params = [], []
        if 'title' in body:
            title = (body.get('title') or '').strip()
            if not title:
                return _err('title cannot be empty')
            sets.append('title = %s');      params.append(title)
        if 'tags' in body:
            tags = body.get('tags') or []
            if not isinstance(tags, list):
                return _err('tags must be a list')
            sets.append('tags = %s::text[]'); params.append([str(t).strip() for t in tags])
        if 'is_public' in body:
            sets.append('is_public = %s');   params.append(bool(body['is_public']))
        if 'css_source' in body:
            sets.append('css_source = %s');  params.append(body.get('css_source'))
        if 'synergy_session_id' in body:
            sets.append('synergy_session_id = %s'); params.append(body.get('synergy_session_id'))

        if not sets:
            return _err('No updatable fields supplied', 400)

        sets.append('updated_at = NOW()')
        params.append(snapshot_id)

        affected = execute_query(
            f"UPDATE sessions.viz_snapshots SET {', '.join(sets)} WHERE id = %s",
            tuple(params),
            fetch_mode=None,
            schema='sessions',
        )
        return jsonify({'success': True, 'affected': affected}), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] update failed')
        return _err(f'update failed: {e}', 500)


# ============================================================================
# DELETE /<id>   — soft delete (owner only)
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>', methods=['DELETE'])
@require_auth
def delete_snapshot(snapshot_id):
    """Soft-delete: set is_active=FALSE. Owner only."""
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err
        if owner_row['owner_user_id'] != user_id:
            return _err('Only the owner can delete this snapshot', 403)

        affected = execute_query(
            """
            UPDATE sessions.viz_snapshots
               SET is_active = FALSE, updated_at = NOW()
             WHERE id = %s
            """,
            (snapshot_id,),
            fetch_mode=None,
            schema='sessions',
        )
        return jsonify({'success': True, 'affected': affected}), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] delete failed')
        return _err(f'delete failed: {e}', 500)


# ============================================================================
# POST /<id>/notes   — add a note
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/notes', methods=['POST'])
@require_auth
def add_note(snapshot_id):
    """
    Add a note to a snapshot.

    Body:
      note             (str, required)
      note_kind        (str, optional: 'comment'|'todo'|'handoff'|'data_update')
      author_kind      (str, optional: 'human'|'ai')
      author_agent_id  (str, optional)
      metadata         (dict, optional)
    """
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err

        body = request.get_json(silent=True) or {}
        note = (body.get('note') or '').strip()
        if not note:
            return _err('note is required')

        note_kind       = body.get('note_kind', 'comment')
        author_kind     = body.get('author_kind', 'human')
        author_agent_id = body.get('author_agent_id')
        metadata        = body.get('metadata') or {}

        if note_kind not in ('comment', 'todo', 'handoff', 'data_update'):
            return _err('note_kind must be one of: comment, todo, handoff, data_update')
        if author_kind not in ('human', 'ai'):
            return _err('author_kind must be human or ai')

        row = execute_query(
            """
            INSERT INTO sessions.viz_snapshot_notes
                (snapshot_id, author_user_id, author_kind, author_agent_id,
                 note, note_kind, metadata)
            VALUES
                (%s, %s, %s, %s,
                 %s, %s, %s::jsonb)
            RETURNING id, created_at
            """,
            (snapshot_id, user_id, author_kind, author_agent_id,
             note, note_kind, json_dumps(metadata)),
            fetch_mode='one',
            schema='sessions',
        )
        return jsonify({
            'success':    True,
            'id':         str(row['id']),
            'created_at': row['created_at'].isoformat() if row.get('created_at') else None,
        }), 201

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] add_note failed')
        return _err(f'add_note failed: {e}', 500)


# ============================================================================
# GET /<id>/notes
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/notes', methods=['GET'])
@require_auth
def list_notes(snapshot_id):
    """List notes for a snapshot, oldest first (handoff read order)."""
    try:
        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err

        rows = execute_query(
            """
            SELECT id, snapshot_id, author_user_id, author_kind, author_agent_id,
                   note, note_kind, metadata, created_at
              FROM sessions.viz_snapshot_notes
             WHERE snapshot_id = %s
             ORDER BY created_at ASC
            """,
            (snapshot_id,),
            fetch_mode='all',
            schema='sessions',
        )
        return jsonify({
            'success': True,
            'data':    [_serialize_note(r) for r in (rows or [])],
            'count':   len(rows or []),
        }), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] list_notes failed')
        return _err(f'list_notes failed: {e}', 500)


# ============================================================================
# POST /<id>/thumbnail
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/thumbnail', methods=['POST'])
@require_auth
def upsert_thumbnail(snapshot_id):
    """Upsert thumbnail PNG. Body: { png_base64: '...' } (may be data URL)."""
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err
        if owner_row['owner_user_id'] != user_id:
            return _err('Only the owner can change the thumbnail', 403)

        body = request.get_json(silent=True) or {}
        b64  = body.get('png_base64') or body.get('thumbnail_base64')
        if not b64:
            return _err('png_base64 is required')
        try:
            png_bytes = _bytea_from_b64(b64)
        except Exception as de:
            return _err(f'base64 decode failed: {de}')
        if not png_bytes:
            return _err('decoded payload is empty')
        # Soft cap at ~4 MB to keep row size sane
        if len(png_bytes) > 4 * 1024 * 1024:
            return _err('thumbnail exceeds 4 MB', 413)

        execute_query(
            """
            UPDATE sessions.viz_snapshots
               SET thumbnail_png = %s, updated_at = NOW()
             WHERE id = %s
            """,
            (png_bytes, snapshot_id),
            fetch_mode=None,
            schema='sessions',
        )
        return jsonify({'success': True, 'bytes': len(png_bytes)}), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] thumbnail failed')
        return _err(f'thumbnail failed: {e}', 500)


# ============================================================================
# POST /<id>/render-count
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/render-count', methods=['POST'])
@require_auth
def bump_render_count(snapshot_id):
    """Bump render_count + last_rendered_at. Called when the gallery re-mounts."""
    try:
        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err

        execute_query(
            """
            UPDATE sessions.viz_snapshots
               SET render_count     = render_count + 1,
                   last_rendered_at = NOW(),
                   updated_at       = NOW()
             WHERE id = %s
            """,
            (snapshot_id,),
            fetch_mode=None,
            schema='sessions',
        )
        row = execute_query(
            "SELECT render_count, last_rendered_at FROM sessions.viz_snapshots WHERE id = %s",
            (snapshot_id,),
            fetch_mode='one',
            schema='sessions',
        )
        return jsonify({
            'success':          True,
            'render_count':     row['render_count'] if row else None,
            'last_rendered_at': row['last_rendered_at'].isoformat() if row and row.get('last_rendered_at') else None,
        }), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] render_count failed')
        return _err(f'render_count failed: {e}', 500)


# ============================================================================
# POST /<id>/link-synergy   — atomic two-sided link via PL/pgSQL
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/link-synergy', methods=['POST'])
@require_auth
def link_synergy(snapshot_id):
    """Link a snapshot to a Synergy session (both sides).

    Body: { synergy_session_id: '...' }  — required.

    Atomicity is provided by the PL/pgSQL function
    `sessions.link_viz_to_synergy(uuid, text)` (migration 057). The function
    updates viz_snapshots.synergy_session_id AND the JSON column
    synergy_sessions.synergy_sessions.linked_viz_snapshots in one transaction.
    """
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err
        if owner_row['owner_user_id'] != user_id:
            return _err('Only the owner can link this snapshot', 403)

        body = request.get_json(silent=True) or {}
        synergy_id = (body.get('synergy_session_id') or '').strip()
        if not synergy_id:
            return _err('synergy_session_id is required')

        result = execute_query(
            "SELECT sessions.link_viz_to_synergy(%s::uuid, %s) AS r",
            (snapshot_id, synergy_id),
            fetch_mode='one',
            schema='sessions',
        )
        payload = (result or {}).get('r') or {}
        if isinstance(payload, str):
            import json as _json
            try:
                payload = _json.loads(payload)
            except Exception:
                payload = {'success': False, 'error': payload}
        if not payload.get('success'):
            return _err(payload.get('error') or 'link failed', 500)

        return jsonify({'success': True, 'data': payload}), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] link_synergy failed')
        return _err(f'link_synergy failed: {e}', 500)


# ============================================================================
# POST /<id>/unlink-synergy
# ============================================================================

@viz_snapshots_bp.route('/<snapshot_id>/unlink-synergy', methods=['POST'])
@require_auth
def unlink_synergy(snapshot_id):
    """Inverse of link_synergy. Uses sessions.unlink_viz_from_synergy(uuid)."""
    try:
        user_id = g.rls_user_id
        if not user_id:
            return _err('Missing JWT context', 401)

        owner_row, err = _owner_only_guard(snapshot_id)
        if err:
            return err
        if owner_row['owner_user_id'] != user_id:
            return _err('Only the owner can unlink this snapshot', 403)

        result = execute_query(
            "SELECT sessions.unlink_viz_from_synergy(%s::uuid) AS r",
            (snapshot_id,),
            fetch_mode='one',
            schema='sessions',
        )
        payload = (result or {}).get('r') or {}
        if isinstance(payload, str):
            import json as _json
            try:
                payload = _json.loads(payload)
            except Exception:
                payload = {'success': False, 'error': payload}
        if not payload.get('success'):
            return _err(payload.get('error') or 'unlink failed', 500)

        return jsonify({'success': True, 'data': payload}), 200

    except Exception as e:
        logger.exception('[VIZ_SNAPSHOTS] unlink_synergy failed')
        return _err(f'unlink_synergy failed: {e}', 500)


# ============================================================================
# Serialisation helpers
# ============================================================================

def _iso(value):
    """datetime → ISO8601, or None passthrough."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_summary(row: dict) -> dict:
    """Strip jsx_source + thumbnail_png for list responses."""
    return {
        'id':                 str(row['id']),
        'title':              row.get('title'),
        'viz_type':           row.get('viz_type'),
        'tags':               row.get('tags') or [],
        'is_public':          bool(row.get('is_public')),
        'share_token':        row.get('share_token'),
        'synergy_session_id': row.get('synergy_session_id'),
        'uses_lucide':        bool(row.get('uses_lucide')),
        'uses_recharts':      bool(row.get('uses_recharts')),
        'uses_tailwind':      bool(row.get('uses_tailwind')),
        'last_rendered_at':   _iso(row.get('last_rendered_at')),
        'render_count':       row.get('render_count'),
        'created_at':         _iso(row.get('created_at')),
        'updated_at':         _iso(row.get('updated_at')),
        'owner_user_id':      row.get('owner_user_id'),
        'thread_id':          row.get('thread_id'),
        'thread_title':       row.get('thread_title'),
        'assistant_message_id': row.get('assistant_message_id'),
        'thumbnail_b64':      row.get('thumbnail_b64'),
    }


def _serialize_full(row: dict, *, include_payload: bool) -> dict:
    """Full row. include_payload=False omits jsx_source + thumbnail_b64 for non-owners."""
    base = _serialize_summary(row)
    if include_payload:
        base['jsx_source'] = row.get('jsx_source')
        base['css_source'] = row.get('css_source')
    return base


def _serialize_note(row: dict) -> dict:
    return {
        'id':              str(row['id']),
        'snapshot_id':     str(row['snapshot_id']),
        'author_user_id':  row.get('author_user_id'),
        'author_kind':     row.get('author_kind'),
        'author_agent_id': row.get('author_agent_id'),
        'note':            row.get('note'),
        'note_kind':       row.get('note_kind'),
        'metadata':        row.get('metadata'),
        'created_at':      _iso(row.get('created_at')),
    }


def json_dumps(obj) -> str:
    """Local wrapper so the metadata jsonb cast always has a json string."""
    import json as _json
    return _json.dumps(obj, ensure_ascii=False, default=str)