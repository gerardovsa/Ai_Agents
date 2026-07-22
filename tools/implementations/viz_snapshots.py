"""
FILE: tools/implementations/viz_snapshots.py
PURPOSE: AI tool wrappers for the 'My Visualizations' library.

         Each function is a thin HTTP client that calls the Flask routes
         registered at /api/viz/snapshots/* (see
         AI_infrastructure/routes/viz_snapshots_routes.py). The wrapper
         pattern matches tools/implementations/automation.py:
           * API base URL detected from env (API_BASE_URL >
             RENDER_EXTERNAL_URL > http://localhost:5001)
           * JWT forwarded via kwargs['jwt_token']
           * Structured {success, ...} return shape per CLAUDE.md §10

DEPENDENCIES:
- requests - HTTP client

EXPORTS (12 tools):
- viz_create          - POST   /api/viz/snapshots/
- viz_update          - PATCH  /api/viz/snapshots/<id>
- viz_save            - alias of viz_create / viz_update (idempotent by title)
- viz_search          - GET    /api/viz/snapshots/
- viz_get             - GET    /api/viz/snapshots/<id>
- viz_delete          - DELETE /api/viz/snapshots/<id>
- viz_get_thread      - composition (viz_get + /api/threads/<id>/load + messages)
- viz_read_thread     - composition (viz_get + /api/threads/messages/get)
- viz_add_note        - POST   /api/viz/snapshots/<id>/notes
- viz_list_notes      - GET    /api/viz/snapshots/<id>/notes
- viz_link_synergy    - POST   /api/viz/snapshots/<id>/link-synergy
- viz_unlink_synergy  - POST   /api/viz/snapshots/<id>/unlink-synergy

USED BY:
- tools/registry_v3.py (special_modules list at line 415)
- AI agents via the unified tool dispatcher

RELATED FILES:
- tools/schemas/viz_snapshots_tools.json (12 JSON Schemas)
- AI_infrastructure/routes/viz_snapshots_routes.py
- AI_infrastructure/migrations/057_viz_snapshots.sql + 058_viz_snapshot_notes.sql
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add AI_infrastructure to path so this module can resolve sibling packages
# if a future wrapper needs to call execute_query() directly. (Not required
# today — all calls go over HTTP — but matches automation.py convention.)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))

VIZ_BASE_PATH = '/api/viz/snapshots'


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_api_url() -> str:
    """Resolve the backend base URL.

    Priority (mirrors tools/implementations/automation.py):
        1. API_BASE_URL env var (explicit override)
        2. RENDER_EXTERNAL_URL env var (Render auto-injected)
        3. http://localhost:5001 (local Flask dev default)
    """
    return (
        os.getenv('API_BASE_URL')
        or os.getenv('RENDER_EXTERNAL_URL')
        or 'http://localhost:5001'
    )


def _headers(kwargs: Dict[str, Any]) -> Dict[str, str]:
    """Build Authorization + Content-Type headers from kwargs.

    The tool dispatcher injects `jwt_token` (the user's JWT) plus a few
    internal keys (`_user_id`, `_org_id`, `_agent_id`). We forward the
    bearer token only — never echo the user/org into headers.
    """
    token = kwargs.get('jwt_token') or kwargs.get('access_token')
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}' if token else '',
    }


def _request(method: str, path: str, *, params: Optional[dict] = None,
             json_body: Optional[dict] = None, kwargs: Optional[dict] = None,
             timeout: int = 15) -> Dict[str, Any]:
    """Issue an HTTP request and normalise the response.

    Returns a {success, ...} dict. Never raises on HTTP errors — the
    route's error body is preserved as `error` so the model can decide.
    """
    url = f"{_get_api_url()}{path}"
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_body,
            headers=_headers(kwargs or {}),
            timeout=timeout,
        )
        # 2xx
        if response.ok:
            try:
                return response.json()
            except ValueError:
                return {'success': True, 'raw': response.text}
        # Non-2xx — try to extract backend error body
        try:
            body = response.json()
        except ValueError:
            body = {'error': response.text[:500]}
        return {
            'success': False,
            'status_code': response.status_code,
            'error': body.get('error') or f'HTTP {response.status_code}',
            'details': body.get('details'),
        }
    except requests.exceptions.Timeout:
        return {'success': False, 'error': f'Request to {path} timed out after {timeout}s'}
    except requests.exceptions.RequestException as exc:
        return {'success': False, 'error': f'HTTP error: {exc}'}
    except Exception as exc:  # noqa: BLE001 — surface anything else
        return {'success': False, 'error': f'Unexpected error: {exc}'}


# ---------------------------------------------------------------------------
# Tool implementations (12)
# ---------------------------------------------------------------------------

def viz_create(title: str,
               jsx_source: str,
               css_source: Optional[str] = None,
               tags: Optional[List[str]] = None,
               uses_lucide: bool = False,
               uses_recharts: bool = False,
               uses_tailwind: bool = False,
               thread_id: Optional[int] = None,
               assistant_message_id: Optional[int] = None,
               synergy_session_id: Optional[str] = None,
               **kwargs) -> Dict[str, Any]:
    """Save a React visualization into the user's 'My Visualizations' library.

    The backend auto-fills org_id + owner_user_id from the JWT context and
    stamps share_token + created_at + updated_at. Returns the new id (UUID)
    so follow-up tools (viz_link_synergy, viz_add_note) can reference it.
    """
    if not title or not jsx_source:
        return {'success': False, 'error': 'title and jsx_source are required'}

    body = {
        'title': title,
        'jsx_source': jsx_source,
        'uses_lucide': bool(uses_lucide),
        'uses_recharts': bool(uses_recharts),
        'uses_tailwind': bool(uses_tailwind),
    }
    if css_source is not None:
        body['css_source'] = css_source
    if tags is not None:
        body['tags'] = tags
    if thread_id is not None:
        body['thread_id'] = int(thread_id)
    if assistant_message_id is not None:
        body['assistant_message_id'] = int(assistant_message_id)
    if synergy_session_id:
        body['synergy_session_id'] = synergy_session_id

    return _request('POST', VIZ_BASE_PATH + '/', json_body=body, kwargs=kwargs)


def viz_update(snapshot_id: str,
               title: Optional[str] = None,
               tags: Optional[List[str]] = None,
               is_public: Optional[bool] = None,
               css_source: Optional[str] = None,
               synergy_session_id: Optional[str] = None,
               **kwargs) -> Dict[str, Any]:
    """Patch mutable metadata on an existing snapshot (owner only).

    jsx_source is intentionally NOT patchable here — to change the rendered
    code, save a new snapshot with viz_create.
    """
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}

    body: Dict[str, Any] = {}
    if title is not None:
        body['title'] = title
    if tags is not None:
        body['tags'] = tags
    if is_public is not None:
        body['is_public'] = bool(is_public)
    if css_source is not None:
        body['css_source'] = css_source
    if synergy_session_id is not None:
        body['synergy_session_id'] = synergy_session_id

    if not body:
        return {'success': False, 'error': 'no fields to update'}

    return _request('PATCH', f'{VIZ_BASE_PATH}/{snapshot_id}', json_body=body, kwargs=kwargs)


def viz_save(title: str,
             jsx_source: str,
             snapshot_id: Optional[str] = None,
             tags: Optional[List[str]] = None,
             css_source: Optional[str] = None,
             uses_lucide: bool = False,
             uses_recharts: bool = False,
             uses_tailwind: bool = False,
             thread_id: Optional[int] = None,
             assistant_message_id: Optional[int] = None,
             synergy_session_id: Optional[str] = None,
             **kwargs) -> Dict[str, Any]:
    """Create-or-update convenience alias.

    * If snapshot_id is supplied → route the call to PATCH /<id> (update).
    * Otherwise → POST / (insert).

    Use this from the Tier-1 toolbar 'Save' button so the click is safe to
    repeat (idempotent).
    """
    if snapshot_id:
        result = viz_update(
            snapshot_id=snapshot_id,
            title=title,
            tags=tags,
            css_source=css_source,
            synergy_session_id=synergy_session_id,
            **kwargs,
        )
        if result.get('success'):
            result['action'] = 'updated'
        return result
    result = viz_create(
        title=title,
        jsx_source=jsx_source,
        css_source=css_source,
        tags=tags,
        uses_lucide=uses_lucide,
        uses_recharts=uses_recharts,
        uses_tailwind=uses_tailwind,
        thread_id=thread_id,
        assistant_message_id=assistant_message_id,
        synergy_session_id=synergy_session_id,
        **kwargs,
    )
    if result.get('success'):
        result['action'] = 'created'
    return result


def viz_search(q: Optional[str] = None,
               tag: Optional[str] = None,
               mine: bool = True,
               synergy_session_id: Optional[str] = None,
               limit: int = 20,
               offset: int = 0,
               **kwargs) -> Dict[str, Any]:
    """List or search saved visualizations.

    Returns summaries only (NO jsx_source, NO thumbnail_png — those are
    heavy and excluded by the route's _serialize_summary helper).
    """
    params: Dict[str, Any] = {
        'mine': 'true' if mine else 'false',
        'limit': max(1, min(int(limit), 100)),
        'offset': max(0, int(offset)),
    }
    if q:
        params['q'] = q
    if tag:
        params['tag'] = tag
    if synergy_session_id:
        params['synergy_session_id'] = synergy_session_id

    return _request('GET', VIZ_BASE_PATH + '/', params=params, kwargs=kwargs)


def viz_get(snapshot_id: str,
            include_payload: bool = False,
            **kwargs) -> Dict[str, Any]:
    """Fetch a single snapshot's full record.

    Non-owners receive a redacted summary (title + tags + summary fields
    only) unless the snapshot is_public=true. The route enforces this;
    pass include_payload=true to force-include jsx_source (requires admin
    role on the backend).
    """
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}

    params = {}
    if include_payload:
        params['include_payload'] = 'true'

    return _request('GET', f'{VIZ_BASE_PATH}/{snapshot_id}', params=params, kwargs=kwargs)


def viz_delete(snapshot_id: str, **kwargs) -> Dict[str, Any]:
    """Soft-delete a snapshot (owner only). Idempotent — already-deleted rows still return success."""
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}
    return _request('DELETE', f'{VIZ_BASE_PATH}/{snapshot_id}', kwargs=kwargs)


def viz_get_thread(snapshot_id: str,
                   message_limit: int = 6,
                   **kwargs) -> Dict[str, Any]:
    """Return the originating thread metadata + the last N messages.

    Composes three calls:
      1. viz_get          → discover thread_id from the snapshot row.
      2. /api/threads/<id>/load → thread title + slug.
      3. /api/threads/messages/get?thread_id=<id>&limit=N → recent messages.

    If the snapshot has no thread_id (was saved outside a chat), returns
    success:true with thread:null.
    """
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}

    snap = viz_get(snapshot_id, **kwargs)
    if not snap.get('success'):
        return snap
    snapshot = snap.get('snapshot') or {}
    thread_id = snapshot.get('thread_id')
    if not thread_id:
        return {
            'success': True,
            'snapshot_id': snapshot_id,
            'thread': None,
            'messages': [],
            'note': 'snapshot has no originating thread (saved outside a chat)',
        }

    limit = max(1, min(int(message_limit), 20))
    base = _get_api_url()

    # Thread metadata
    try:
        meta_resp = requests.get(
            f'{base}/api/threads/{thread_id}/load',
            headers=_headers(kwargs),
            timeout=15,
        )
        meta = meta_resp.json() if meta_resp.ok else {}
    except Exception as exc:  # noqa: BLE001
        meta = {'error': str(exc)}

    thread_block = None
    if isinstance(meta, dict) and meta.get('success'):
        thread_data = meta.get('thread') or meta
        thread_block = {
            'id': thread_data.get('id') or thread_id,
            'title': thread_data.get('title'),
            'slug': thread_data.get('slug'),
        }

    # Recent messages
    msgs: List[Dict[str, Any]] = []
    try:
        msg_resp = requests.get(
            f'{base}/api/threads/messages/get',
            params={'thread_id': thread_id, 'limit': limit},
            headers=_headers(kwargs),
            timeout=15,
        )
        if msg_resp.ok:
            msg_body = msg_resp.json()
            # Backend may return {messages: [...]} or a bare list
            raw_msgs = msg_body.get('messages') if isinstance(msg_body, dict) else msg_body
            if isinstance(raw_msgs, list):
                for m in raw_msgs:
                    content = m.get('content') if isinstance(m, dict) else None
                    if isinstance(content, (dict, list)):
                        content = json.dumps(content)
                    if isinstance(content, str) and len(content) > 400:
                        content = content[:397] + '...'
                    msgs.append({
                        'role': m.get('role') if isinstance(m, dict) else None,
                        'content_preview': content,
                        'created_at': m.get('created_at') or m.get('timestamp') if isinstance(m, dict) else None,
                    })
    except Exception as exc:  # noqa: BLE001
        msgs = [{'error': str(exc)}]

    return {
        'success': True,
        'snapshot_id': snapshot_id,
        'thread': thread_block,
        'messages': msgs,
    }


def viz_read_thread(snapshot_id: str,
                    max_messages: int = 50,
                    max_chars_per_message: int = 2000,
                    include_tool_calls: bool = False,
                    **kwargs) -> Dict[str, Any]:
    """Return the full transcript of the originating thread.

    Truncates each message body to max_chars_per_message to keep the
    payload manageable. Set include_tool_calls=true to forward the raw
    tool_calls array (useful when the next agent needs to reproduce a
    multi-tool sequence).
    """
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}

    snap = viz_get(snapshot_id, **kwargs)
    if not snap.get('success'):
        return snap
    snapshot = snap.get('snapshot') or {}
    thread_id = snapshot.get('thread_id')
    if not thread_id:
        return {
            'success': True,
            'snapshot_id': snapshot_id,
            'thread_id': None,
            'messages': [],
            'truncated': False,
            'note': 'snapshot has no originating thread',
        }

    cap = max(1, min(int(max_messages), 200))
    char_cap = max(100, min(int(max_chars_per_message), 16000))

    base = _get_api_url()
    try:
        resp = requests.get(
            f'{base}/api/threads/messages/get',
            params={'thread_id': thread_id, 'limit': cap},
            headers=_headers(kwargs),
            timeout=20,
        )
    except Exception as exc:  # noqa: BLE001
        return {'success': False, 'error': f'messages request failed: {exc}'}

    if not resp.ok:
        return {
            'success': False,
            'status_code': resp.status_code,
            'error': f'failed to read thread {thread_id}',
        }

    body = resp.json()
    raw_msgs = body.get('messages') if isinstance(body, dict) else body
    if not isinstance(raw_msgs, list):
        raw_msgs = []

    truncated = False
    out: List[Dict[str, Any]] = []
    for m in raw_msgs:
        if not isinstance(m, dict):
            continue
        content = m.get('content')
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
        if isinstance(content, str) and len(content) > char_cap:
            content = content[:char_cap] + '...'
            truncated = True
        entry: Dict[str, Any] = {
            'id': m.get('id'),
            'role': m.get('role'),
            'content': content,
            'created_at': m.get('created_at') or m.get('timestamp'),
        }
        if include_tool_calls:
            entry['tool_calls'] = m.get('tool_calls') or []
        out.append(entry)

    return {
        'success': True,
        'snapshot_id': snapshot_id,
        'thread_id': thread_id,
        'messages': out,
        'truncated': truncated,
        'count': len(out),
    }


def viz_add_note(snapshot_id: str,
                 note: str,
                 note_kind: str = 'comment',
                 author_kind: str = 'human',
                 author_agent_id: Optional[str] = None,
                 metadata: Optional[dict] = None,
                 **kwargs) -> Dict[str, Any]:
    """Attach a note to a snapshot.

    note_kind: comment | todo | handoff | data_update
    author_kind: human | ai  (set author_agent_id when author_kind='ai')
    """
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}
    if not note:
        return {'success': False, 'error': 'note is required'}

    body: Dict[str, Any] = {
        'note': note,
        'note_kind': note_kind,
        'author_kind': author_kind,
    }
    if author_agent_id:
        body['author_agent_id'] = author_agent_id
    if metadata is not None:
        body['metadata'] = metadata

    return _request('POST', f'{VIZ_BASE_PATH}/{snapshot_id}/notes', json_body=body, kwargs=kwargs)


def viz_list_notes(snapshot_id: str,
                   limit: int = 50,
                   offset: int = 0,
                   author_kind_filter: Optional[str] = None,
                   note_kind_filter: Optional[str] = None,
                   **kwargs) -> Dict[str, Any]:
    """List notes on a snapshot, oldest first (natural handoff reading order)."""
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}

    params: Dict[str, Any] = {
        'limit': max(1, min(int(limit), 200)),
        'offset': max(0, int(offset)),
    }
    if author_kind_filter:
        params['author_kind'] = author_kind_filter
    if note_kind_filter:
        params['note_kind'] = note_kind_filter

    return _request('GET', f'{VIZ_BASE_PATH}/{snapshot_id}/notes', params=params, kwargs=kwargs)


def viz_link_synergy(snapshot_id: str,
                     synergy_session_id: str,
                     label: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
    """Attach a snapshot to a Synergy Kanban session (atomic, two-sided)."""
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}
    if not synergy_session_id:
        return {'success': False, 'error': 'synergy_session_id is required'}

    body: Dict[str, Any] = {'synergy_session_id': synergy_session_id}
    if label:
        body['label'] = label

    return _request('POST', f'{VIZ_BASE_PATH}/{snapshot_id}/link-synergy', json_body=body, kwargs=kwargs)


def viz_unlink_synergy(snapshot_id: str, **kwargs) -> Dict[str, Any]:
    """Detach a snapshot from its current Synergy link (atomic, two-sided)."""
    if not snapshot_id:
        return {'success': False, 'error': 'snapshot_id is required'}
    return _request('POST', f'{VIZ_BASE_PATH}/{snapshot_id}/unlink-synergy', json_body={}, kwargs=kwargs)
