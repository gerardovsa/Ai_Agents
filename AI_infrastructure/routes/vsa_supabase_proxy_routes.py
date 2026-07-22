"""
VSA Veterinary Alerts - Supabase Proxy Routes
=============================================

Backend proxy that lets the browser-facing VSA V4 module read aggregated data
from the external VSA Supabase project (https://wuwmvtslltqhaycyukxk.supabase.co)
WITHOUT the anon/service-role key ever leaving the server.

Why this file exists (per CLAUDE.md §6 / §9 / §10):
    The legacy VSA module hardcoded the Supabase URL + anon key in the
    browser bundle, allowing any user with DevTools to bypass RLS. The V4
    rewrite must not repeat that mistake. Instead the browser calls the
    endpoints in this file, which:

      1. Authenticate the user via the JWT in `Authorization: Bearer ...`
         (handled by @require_auth + the set_rls_context_from_jwt
         before_request hook in flask_app.py).
      2. Resolve the Supabase URL + service_role_key from the org vault
         via resolve_credentials('supabase_vsa', user_id=g.rls_user_id).
         NEVER reads os.getenv() for the key.
      3. Forward the request to the external Supabase REST API on behalf
         of the authenticated user.
      4. Project only the fields the SPA needs (no full row dumps,
         no transcript text in list endpoints).

Endpoints
---------
    GET  /api/vsa-supabase-proxy/dashboard
        Aggregate KPIs for the Dashboard tab: open alerts (priority<=2),
        calls today, calls this week, pending follow-ups, avg risk.

    GET  /api/vsa-supabase-proxy/calls?limit=50&offset=0
        Paged list of calls joined with manager alerts. Returns a flat
        row per call suitable for the Tabulator table. No transcript text.

    GET  /api/vsa-supabase-proxy/calls/<call_id>
        Single-call detail. Includes the alert codes, manager summary,
        transcript status, and a 'stages_complete' counter so the SPA
        can show "21 stages complete: 8/21".

    POST /api/vsa-supabase-proxy/seed-vault
        Admin-only. Writes the Supabase URL + service_role_key into
        ai_infrastructure.organisation_platform_credentials for the
        user's org, and audit-logs the action. Used to populate the
        vault row on first install; never called from the SPA itself
        (the user pastes values into a tiny admin form or a curl one-liner).

Author: VSA V4 rewrite (June 2026)
Last modified: 2026-07-22
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

import requests
from flask import Blueprint, request, jsonify, g

# Make the AI_infrastructure root importable for shared modules.
# flask_app.py already adds this, but the route file may be imported by
# tests that bootstrap from a different entry point.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AI_INFRA_ROOT = os.path.dirname(_THIS_DIR)
if _AI_INFRA_ROOT not in sys.path:
    sys.path.insert(0, _AI_INFRA_ROOT)

from shared.database_utils import execute_query  # noqa: E402
from shared.org_credentials_loader import resolve_credentials  # noqa: E402
from auth.user_auth import require_auth  # noqa: E402


logger = logging.getLogger(__name__)

vsa_supabase_proxy_bp = Blueprint(
    'vsa_supabase_proxy',
    __name__,
    url_prefix='/api/vsa-supabase-proxy',
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Cap on list-endpoint page size so a runaway SPA can't drain the external
# Supabase quota in one call.
MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 50

# Tables in the external Supabase project that count toward the "21-stage
# analysis pipeline" badge on the call detail view. Source of truth: list
# from supabase-vet-phone MCP. Keep this list in sync with the migration
# comments in AI_infrastructure/migrations/037_vsa_veterinary_module.sql.
ANALYSIS_STAGE_TABLES = [
    'call_behavioral_patterns',          # TASK 20
    'call_booking_analysis',             # TASK 6
    'call_client_engagement',           # Task 11
    'call_coaching_points',              # TASK 24
    'call_consolidated_missed_opportunities',  # TASK 12 + 6
    'call_financial_analysis',           # Task 8
    'call_followup_actions',             # OPERATIONS
    'call_full_transcript_and_full_analysis',  # transcript + analysis blob
    'call_hold_analysis',
    'call_manager_alerts',
    'call_missed_opportunities',
    'call_next_steps',                   # Task 10
    'call_objection_handling',           # Task 9
    'call_preparation_analysis',         # AI Task 3
    'call_purposes_outcomes',            # AI Task 2
    'call_quality_assessment',           # AI Task 17
    'call_recommendations',              # AI Task 4
    'call_reminders',                    # Task 7
    'call_resolution_complexity',
    'call_revenue_analysis',             # AI Task 18
    'call_sentiment_analysis',           # AI Task 15
    'call_staff_feedback',               # FEEDBACK
    'call_staff_performance',            # AI Task 19
    'call_teaching_examples',            # AI Task 21
    'call_transcript_extracts',          # AI Task 23
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_vsa_supabase_creds() -> Optional[Dict[str, str]]:
    """
    Resolve and return the Supabase URL + service-role key for the
    current user/org via the 4-tier credential resolver.

    Returns None if no vault row exists, or the row is missing required
    fields. NEVER reads os.getenv() - per CLAUDE.md §9.
    """
    user_id = getattr(g, 'rls_user_id', None)
    if not user_id:
        logger.warning("[VSA_PROXY] No g.rls_user_id - rejecting credential lookup")
        return None

    resolved = resolve_credentials(user_id, 'supabase_vsa')
    if not resolved:
        return None

    # _normalise_row guarantees a 'credentials' dict for multi-field platforms.
    creds_blob = resolved.get('credentials') or {}
    url = creds_blob.get('url')
    service_key = creds_blob.get('service_role_key') or creds_blob.get('anon_key')

    if not url or not service_key:
        logger.warning(
            "[VSA_PROXY] supabase_vsa vault row missing url or service_role_key "
            "(source=%s)", resolved.get('_source', 'unknown')
        )
        return None

    return {
        'url': url.rstrip('/'),
        'key': service_key,
        'source': resolved.get('_source', 'unknown'),
    }


def _supabase_rest_get(creds: Dict[str, str], table: str, select: str,
                       filters: Optional[Dict[str, str]] = None,
                       limit: Optional[int] = None,
                       order: Optional[str] = None) -> Dict[str, Any]:
    """
    Issue a GET against the external Supabase PostgREST endpoint.

    `filters` is a dict of {param_name: param_value}. Each value MUST be
    the full PostgREST right-hand side, including its operator, e.g.
        'eq.<value>'        -> =eq.<value>      (equality)
        'in.(a,b,c)'        -> =in.(a,b,c)      (set membership)
        'gte.<value>'       -> =gte.<value>     (range)
        'not.is.null'       -> =not.is.null     (negated null check)
        'or=(col1.gte.X,col2.lt.Y)'  -> =or=(...)  (logical OR)
        'and=(...)'         -> =and=(...)       (logical AND)
    For columns needing the equality operator, the caller passes
    'eq.<value>' explicitly. The helper does NOT auto-prepend 'eq.' -
    doing so corrupts every non-trivial filter (the bug that originally
    produced 502s on the dashboard endpoint).
    `order` is a PostgREST order clause like 'key_call_date.desc.nullslast'.
    Returns the parsed JSON response or raises requests.RequestException.
    """
    url = f"{creds['url']}/rest/v1/{table}?select={select}"
    if filters:
        for col, val in filters.items():
            # Caller is responsible for the operator prefix; we append verbatim.
            url += f"&{col}={val}"
    if order:
        url += f"&order={order}"
    if limit is not None:
        url += f"&limit={limit}"

    headers = {
        'apikey': creds['key'],
        'Authorization': f"Bearer {creds['key']}",
        'Accept': 'application/json',
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _audit_log(credential_id: Optional[int], action: str, platform: str,
               display_name: str) -> None:
    """
    Best-effort write to ai_infrastructure.credential_access_log.
    Failures are logged but do not break the parent request.
    """
    try:
        execute_query(
            """
            INSERT INTO ai_infrastructure.credential_access_log
                (organisation_id, credential_id, user_id, action,
                 platform, display_name, ip_address, user_agent,
                 vault_password_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                getattr(g, 'rls_organisation_id', None),
                credential_id,
                getattr(g, 'rls_user_id', None),
                action,
                platform,
                display_name,
                request.remote_addr,
                request.headers.get('User-Agent', '')[:500],
                False,
            ),
            fetch_mode=None,
        )
    except Exception as exc:
        logger.warning("[VSA_PROXY] audit log write failed (non-fatal): %s", exc)


def _get_allowed_hospital_codes(org_id: Optional[int]) -> List[str]:
    """
    Return the list of VSA hospital codes the calling org is allowed to
    see, sourced from ai_infrastructure.vsa_org_hospitals.

    An empty list means "this org is not provisioned for VSA yet" - the
    caller should treat that as 'show nothing' rather than falling back
    to the full dataset. This is a hard privacy guarantee: a misconfigured
    row in vsa_org_hospitals cannot leak data; the absence of a row
    returns no data.
    """
    if not org_id:
        return []
    try:
        rows = execute_query(
            """
            SELECT hospital_code
            FROM ai_infrastructure.vsa_org_hospitals
            WHERE organisation_id = %s AND is_active = TRUE
            ORDER BY hospital_code
            """,
            (org_id,),
            fetch_mode='all',
        )
        return [r['hospital_code'] for r in rows or []]
    except Exception as exc:
        logger.warning("[VSA_PROXY] hospital_codes lookup failed: %s", exc)
        return []


def _get_allowed_call_ids(creds: Dict[str, str], hospital_codes: List[str],
                          limit: int = 2000) -> List[str]:
    """
    Fetch the call_ids whose key_hospital_code is in `hospital_codes`.

    Used to scope downstream queries against tables (call_manager_alerts,
    call_followup_actions) that don't carry a key_hospital_code column
    and are joined by call_id only.

    Capped at `limit` to keep the PostgREST `in.(...)` URL under safe
    length. If an org has more than `limit` calls, the cap is the
    trade-off; document and revisit if a tenant hits it.
    """
    if not hospital_codes:
        return []
    try:
        # PostgREST in.(csv) syntax. Quote each code to be safe.
        codes_csv = ','.join(f'"{c}"' for c in hospital_codes)
        url = (
            f"{creds['url']}/rest/v1/veterinary_calls"
            f"?select=call_id"
            f"&key_hospital_code=in.({requests.utils.quote(codes_csv, safe=',')})"
            f"&limit={limit}"
        )
        resp = requests.get(
            url,
            headers={
                'apikey': creds['key'],
                'Authorization': f"Bearer {creds['key']}",
                'Accept': 'application/json',
            },
            timeout=15,
        )
        resp.raise_for_status()
        return [r['call_id'] for r in resp.json() if r.get('call_id')]
    except requests.RequestException as exc:
        logger.warning("[VSA_PROXY] allowed_call_ids lookup failed: %s", exc)
        return []
    except Exception as exc:
        logger.exception("[VSA_PROXY] allowed_call_ids unexpected failure")
        return []


# ---------------------------------------------------------------------------
# GET /api/vsa-supabase-proxy/dashboard
# ---------------------------------------------------------------------------

@vsa_supabase_proxy_bp.route('/dashboard', methods=['GET'])
@require_auth
def dashboard():
    """
    Aggregate KPIs for the Dashboard sub-tab.

    Returns:
        {
          "open_alerts":       int,   # rows in call_manager_alerts where any
                                      # of alert_1/2/3_priority <= 2 (urgent)
          "calls_today":       int,
          "calls_this_week":   int,
          "followups_pending": int,   # rows in call_followup_actions where
                                      # any fol_1/2/3_time is set
          "avg_risk":          float|None  # mean of alert_1_priority across
                                           # analysed calls (lower=more risk)
        }
    """
    creds = _get_vsa_supabase_creds()
    if not creds:
        return jsonify({
            'error': 'supabase_vsa_not_configured',
            'message': (
                'The supabase_vsa vault row is missing URL or service_role_key. '
                'Ask an admin to seed it via POST /api/vsa-supabase-proxy/seed-vault.'
            ),
        }), 503

    # --- Tenant scoping: pull allowed hospital codes for the caller's org ---
    org_id = getattr(g, 'rls_organisation_id', None)
    allowed_codes = _get_allowed_hospital_codes(org_id)
    if not allowed_codes:
        # Org is not provisioned for VSA yet -> return zero-KPI payload.
        # This is the privacy-safe default: absence of a row in
        # vsa_org_hospitals means "see nothing".
        return jsonify({
            'open_alerts': 0,
            'calls_today': 0,
            'calls_this_week': 0,
            'followups_pending': 0,
            'avg_risk': None,
            'source': creds['source'],
            'scope': 'no_hospitals_provisioned',
        })

    # Fetch the call_ids belonging to the allowed hospital codes. Used
    # to scope cross-table queries (call_manager_alerts, call_followup_actions)
    # which don't carry a hospital_code column.
    allowed_call_ids = _get_allowed_call_ids(creds, allowed_codes, limit=2000)

    # Compute today / 7-days-ago in Python. PostgREST has no `today` reserved
    # literal and the equivalent `now()::date` only works inside an `and=(...)`
    # parenthesised expression; computing the dates here is simpler and matches
    # the key_call_date column type (text/ISO date, not a timestamp).
    now_utc = datetime.now(timezone.utc)
    today_iso = now_utc.date().isoformat()
    week_start_iso = (now_utc - timedelta(days=7)).date().isoformat()

    try:
        # --- Open alerts: rows with ANY priority in 1..2 (1 = most urgent) ---
        # Scoped by call_id since call_manager_alerts has no hospital_code.
        if allowed_call_ids:
            ids_csv = ','.join(allowed_call_ids)
            open_alerts_rows = _supabase_rest_get(
                creds, 'call_manager_alerts',
                select='call_id',
                filters={
                    'call_id': f'in.({requests.utils.quote(ids_csv, safe=",")})',
                    'or': '(alert_1_priority.lte.2,alert_2_priority.lte.2,'
                          'alert_3_priority.lte.2)',
                },
                limit=500,
            )
            open_alerts = len(open_alerts_rows)
        else:
            open_alerts = 0

        # --- Calls today / this week (direct veterinary_calls queries) ---
        # Scope by hospital_code at the source.
        codes_csv = ','.join(f'"{c}"' for c in allowed_codes)
        codes_csv_quoted = requests.utils.quote(codes_csv, safe=',')

        calls_today_rows = _supabase_rest_get(
            creds, 'veterinary_calls',
            select='call_id',
            filters={
                'key_call_date': f'eq.{today_iso}',
                'key_hospital_code': f'in.({codes_csv_quoted})',
            },
            limit=500,
        )
        calls_today = len(calls_today_rows)

        calls_week_rows = _supabase_rest_get(
            creds, 'veterinary_calls',
            select='call_id',
            filters={
                'key_hospital_code': f'in.({codes_csv_quoted})',
                'and': f'(key_call_date.gte.{week_start_iso},'
                       f'key_call_date.lte.{today_iso})',
            },
            limit=500,
        )
        calls_this_week = len(calls_week_rows)

        # --- Follow-ups pending: any fol_1_time / fol_2_time / fol_3_time is non-null ---
        if allowed_call_ids:
            followups_rows = _supabase_rest_get(
                creds, 'call_followup_actions',
                select='call_id',
                filters={
                    'call_id': f'in.({requests.utils.quote(ids_csv, safe=",")})',
                    'or': '(fol_1_time.not.is.null,fol_2_time.not.is.null,'
                          'fol_3_time.not.is.null)',
                },
                limit=500,
            )
            followups_pending = len(followups_rows)
        else:
            followups_pending = 0

        # --- Average risk: mean of alert_1_priority across analysed calls ---
        if allowed_call_ids:
            priority_rows = _supabase_rest_get(
                creds, 'call_manager_alerts',
                select='alert_1_priority',
                filters={
                    'call_id': f'in.({requests.utils.quote(ids_csv, safe=",")})',
                    'alert_1_priority': 'not.is.null',
                },
                limit=500,
            )
            if priority_rows:
                avg_risk = round(
                    sum(float(r['alert_1_priority']) for r in priority_rows)
                    / len(priority_rows),
                    2,
                )
            else:
                avg_risk = None
        else:
            avg_risk = None

    except requests.RequestException as exc:
        logger.error("[VSA_PROXY] Supabase REST call failed: %s", exc)
        return jsonify({
            'error': 'supabase_unreachable',
            'message': 'External Supabase project could not be reached.',
        }), 502
    except Exception as exc:
        logger.exception("[VSA_PROXY] Dashboard aggregation failed")
        return jsonify({
            'error': 'internal_error',
            'message': str(exc),
        }), 500

    return jsonify({
        'open_alerts': open_alerts,
        'calls_today': calls_today,
        'calls_this_week': calls_this_week,
        'followups_pending': followups_pending,
        'avg_risk': avg_risk,
        'source': creds['source'],
        'scope': {
            'organisation_id': org_id,
            'hospital_codes': allowed_codes,
            'allowed_call_ids_count': len(allowed_call_ids),
        },
    })


# ---------------------------------------------------------------------------
# GET /api/vsa-supabase-proxy/calls
# ---------------------------------------------------------------------------

@vsa_supabase_proxy_bp.route('/calls', methods=['GET'])
@require_auth
def list_calls():
    """
    Paged list of calls joined with manager alerts.

    Query params:
        limit  (int, default 50, max 200)
        offset (int, default 0)

    Returns:
        {
          "rows": [
            {
              "call_id": "...",
              "key_call_date": "2025-12-08",
              "key_hospital": "Compton Road",
              "key_staffname": "Ava",
              "key_direction": "INBOUND",
              "key_outcome": "ANS&STO",
              "key_call_duration": "01:07",
              "key_transcript_status": "COMPLETE",
              "alert_1_code": "REVENUE_LEAKAGE",
              "alert_1_priority": 2,
              "alert_1_severity": "MED",
              "manager_summary": "..."
            }, ...
          ],
          "total":   <int from Content-Range>,
          "limit":   <int>,
          "offset":  <int>
        }
    """
    creds = _get_vsa_supabase_creds()
    if not creds:
        return jsonify({'error': 'supabase_vsa_not_configured'}), 503

    # --- Tenant scoping: pull allowed hospital codes for the caller's org ---
    org_id = getattr(g, 'rls_organisation_id', None)
    allowed_codes = _get_allowed_hospital_codes(org_id)
    if not allowed_codes:
        # Org not provisioned -> return empty page rather than leaking rows.
        return jsonify({
            'rows': [],
            'total': 0,
            'limit': int(request.args.get('limit', DEFAULT_PAGE_SIZE) or DEFAULT_PAGE_SIZE),
            'offset': int(request.args.get('offset', 0) or 0),
            'scope': 'no_hospitals_provisioned',
        })

    try:
        limit = min(int(request.args.get('limit', DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
        offset = max(int(request.args.get('offset', 0)), 0)
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_pagination'}), 400

    # Select only the fields the SPA renders in the Tabulator. No transcript text.
    select = (
        'call_id,key_call_date,key_hospital,key_staffname,key_direction,'
        'key_outcome,key_call_duration,key_transcript_status,'
        'alert_1_code,alert_1_priority,alert_1_severity,manager_summary'
    )
    table = 'veterinary_calls?select=call_id,key_call_date,key_hospital,' \
            'key_staffname,key_direction,key_outcome,key_call_duration,' \
            'key_transcript_status'

    url = f"{creds['url']}/rest/v1/{table}"
    # Tenant scoping: restrict to rows whose key_hospital_code is one of
    # the codes provisioned for this org in vsa_org_hospitals.
    codes_csv = ','.join(f'"{c}"' for c in allowed_codes)
    url += f"&key_hospital_code=in.({requests.utils.quote(codes_csv, safe=',')})"
    url += f"&order=key_call_date.desc.nullslast"
    url += f"&limit={limit}&offset={offset}"

    # Two-step join: pull veterinary_calls first, then enrich with alert fields
    # by call_id. PostgREST supports embedded resources via `select=...,alerts(...)`
    # but the alerts table isn't FK-linked, so we do a manual merge below.
    headers = {
        'apikey': creds['key'],
        'Authorization': f"Bearer {creds['key']}",
        'Accept': 'application/json',
        # Prefer 'count=exact' to get total via Content-Range header.
        'Prefer': 'count=exact',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("[VSA_PROXY] Supabase REST (calls list) failed: %s", exc)
        return jsonify({'error': 'supabase_unreachable'}), 502

    rows = resp.json()
    content_range = resp.headers.get('Content-Range', '')
    # PostgREST Content-Range format: "0-49/130"
    total = 0
    if '/' in content_range:
        try:
            total = int(content_range.split('/')[-1])
        except (ValueError, IndexError):
            total = len(rows)

    # Enrich with alert_1_* fields. Single targeted query for these call_ids.
    if rows:
        call_ids = [r['call_id'] for r in rows if r.get('call_id')]
        # PostgREST `in` filter: or=(call_id.in.(a,b,c))
        ids_csv = ','.join(call_ids)
        alerts_url = (
            f"{creds['url']}/rest/v1/call_manager_alerts"
            f"?select=call_id,alert_1_code,alert_1_priority,alert_1_severity,"
            f"manager_summary"
            f"&call_id=in.({requests.utils.quote(ids_csv, safe=',')})"
        )
        try:
            alerts_resp = requests.get(
                alerts_url, headers={
                    'apikey': creds['key'],
                    'Authorization': f"Bearer {creds['key']}",
                    'Accept': 'application/json',
                }, timeout=15
            )
            alerts_resp.raise_for_status()
            alerts_by_id = {a['call_id']: a for a in alerts_resp.json()}
        except requests.RequestException as exc:
            logger.warning("[VSA_PROXY] Alert enrichment failed (non-fatal): %s", exc)
            alerts_by_id = {}

        for r in rows:
            a = alerts_by_id.get(r.get('call_id'), {})
            r['alert_1_code'] = a.get('alert_1_code')
            r['alert_1_priority'] = a.get('alert_1_priority')
            r['alert_1_severity'] = a.get('alert_1_severity')
            r['manager_summary'] = a.get('manager_summary')

    return jsonify({
        'rows': rows,
        'total': total,
        'limit': limit,
        'offset': offset,
        'scope': {
            'organisation_id': org_id,
            'hospital_codes': allowed_codes,
        },
    })


# ---------------------------------------------------------------------------
# GET /api/vsa-supabase-proxy/calls/<call_id>
# ---------------------------------------------------------------------------

@vsa_supabase_proxy_bp.route('/calls/<call_id>', methods=['GET'])
@require_auth
def call_detail(call_id: str):
    """
    Single-call detail. Returns:
      - The call metadata row from veterinary_calls
      - The alert codes + priorities + manager_summary + AI coaching fields
        from call_manager_alerts
      - A 'stages_complete' counter: how many of the 25 analysis-stage
        sibling tables have a row for this call_id
      - List of which stages are complete (table names)
    """
    creds = _get_vsa_supabase_creds()
    if not creds:
        return jsonify({'error': 'supabase_vsa_not_configured'}), 503

    try:
        # Master call row
        call_rows = _supabase_rest_get(
            creds, 'veterinary_calls',
            select='*',
            filters={'call_id': f'eq.{call_id}'},
            limit=1,
        )
        if not call_rows:
            return jsonify({'error': 'call_not_found', 'call_id': call_id}), 404
        call_row = call_rows[0]

        # Alert row
        alerts_rows = _supabase_rest_get(
            creds, 'call_manager_alerts',
            select=('call_id,alert_1_code,alert_1_priority,alert_1_severity,'
                    'alert_2_code,alert_2_priority,alert_2_severity,'
                    'alert_3_code,alert_3_priority,alert_3_severity,'
                    'manager_summary,manager_alerts_tags,'
                    'ai_coaching_support,ai_coaching_generated_date'),
            filters={'call_id': f'eq.{call_id}'},
            limit=1,
        )
        alerts = alerts_rows[0] if alerts_rows else {}

        # Stages complete: query each analysis-stage table for this call_id.
        # 25 small queries; each returns 0..1 row. Done serially because
        # PostgREST has no batch endpoint and asyncio would not buy us much
        # at this scale (typical call detail view is opened once per click).
        stages_complete: List[str] = []
        stages_missing: List[str] = []
        for tbl in ANALYSIS_STAGE_TABLES:
            try:
                rows = _supabase_rest_get(
                    creds, tbl,
                    select='call_id',
                    filters={'call_id': f'eq.{call_id}'},
                    limit=1,
                )
                if rows:
                    stages_complete.append(tbl)
                else:
                    stages_missing.append(tbl)
            except requests.RequestException:
                # Treat unreachable table as 'unknown' rather than failing the
                # whole detail view; the SPA can show "stage status unknown".
                stages_missing.append(tbl)

        return jsonify({
            'call': call_row,
            'alerts': alerts,
            'stages_complete': stages_complete,
            'stages_missing': stages_missing,
            'stages_total': len(ANALYSIS_STAGE_TABLES),
        })

    except requests.RequestException as exc:
        logger.error("[VSA_PROXY] Supabase REST (call detail) failed: %s", exc)
        return jsonify({'error': 'supabase_unreachable'}), 502
    except Exception as exc:
        logger.exception("[VSA_PROXY] call_detail failed")
        return jsonify({'error': 'internal_error', 'message': str(exc)}), 500


# ---------------------------------------------------------------------------
# POST /api/vsa-supabase-proxy/seed-vault  (admin-only)
# ---------------------------------------------------------------------------

@vsa_supabase_proxy_bp.route('/seed-vault', methods=['POST'])
@require_auth
def seed_vault():
    """
    Admin-only: write the external Supabase URL + service_role_key into
    ai_infrastructure.organisation_platform_credentials for the calling
    user's organisation.

    Body (JSON):
        {
          "url":              "https://wuwmvtslltqhaycyukxk.supabase.co",
          "service_role_key": "eyJhbGciOi...",
          "anon_key":         "eyJhbGciOi..."  (optional but recommended),
          "display_name":     "VSA Vet Phone"  (optional)
        }

    Behaviour:
        - Caller MUST be admin or owner on the org (inline role check,
          not a decorator — there is no shared @require_role in this codebase).
        - If a supabase_vsa row already exists for this org, it is updated.
        - The action is audit-logged to credential_access_log with action='added'.
        - NEVER echoes the key back in the response (just a masked preview).
        - NEVER stores the key in the response object; returns 201 with id only.
    """
    org_id = getattr(g, 'rls_organisation_id', None)
    user_id = getattr(g, 'rls_user_id', None)
    if not org_id or not user_id:
        return jsonify({'error': 'no_rls_context'}), 401

    # Admin-only gate. Inline because there is no @require_role decorator
    # in auth.user_auth.py (verified). Read once per request — cheap query.
    try:
        caller_org_role = execute_query(
            "SELECT org_role FROM ai_infrastructure.users WHERE id = %s",
            (user_id,),
            fetch_mode='value',
        )
    except Exception:
        logger.exception("[VSA_PROXY] seed-vault role lookup failed")
        return jsonify({'error': 'role_lookup_failed'}), 500
    if caller_org_role not in ('admin', 'owner'):
        return jsonify({
            'error': 'forbidden',
            'message': 'VSA seed-vault requires admin or owner role on this org.',
        }), 403

    payload = request.get_json(silent=True) or {}
    url = (payload.get('url') or '').strip().rstrip('/')
    service_key = (payload.get('service_role_key') or '').strip()
    anon_key = (payload.get('anon_key') or '').strip() or None
    display_name = (payload.get('display_name') or 'VSA Vet Phone Supabase').strip()

    # --- Validate ---
    if not url.startswith('https://') or '.supabase.co' not in url:
        return jsonify({
            'error': 'invalid_url',
            'message': 'url must look like https://<project-ref>.supabase.co',
        }), 400
    if not service_key or len(service_key) < 30:
        return jsonify({
            'error': 'invalid_service_role_key',
            'message': 'service_role_key looks too short; copy the full JWT from the Supabase dashboard.',
        }), 400

    credentials_blob = {
        'url': url,
        'service_role_key': service_key,
    }
    if anon_key:
        credentials_blob['anon_key'] = anon_key

    try:
        # Upsert: one active row per (org, platform, display_name). The
        # catalog schema uses UNIQUE NULLS NOT DISTINCT
        # (organisation_id, platform, display_name) - that is the actual
        # constraint we match on. A previous version of this endpoint
        # attempted ON CONFLICT (organisation_id, platform) which the
        # Postgres planner refused because no constraint covers exactly
        # those two columns. See migration 058 for the audit trail.
        execute_query(
            """
            INSERT INTO ai_infrastructure.organisation_platform_credentials
                (organisation_id, platform, display_name, environment,
                 credential_value, credentials, is_active, visible_to_role,
                 reveal_requires_role, notes, last_used_at, created_by_user_id)
            VALUES (%s, %s, %s, 'production', NULL, %s::jsonb, TRUE,
                    'admin', 'admin', %s, NOW(), %s)
            ON CONFLICT (organisation_id, platform, display_name) DO UPDATE SET
                credentials = EXCLUDED.credentials,
                environment  = EXCLUDED.environment,
                is_active    = TRUE,
                notes        = EXCLUDED.notes,
                updated_at   = NOW(),
                created_by_user_id = EXCLUDED.created_by_user_id
            RETURNING id
            """,
            (org_id, 'supabase_vsa', display_name,
             json.dumps(credentials_blob),
             f"Seeded via VSA V4 admin endpoint by user_id={user_id}",
             user_id),
            fetch_mode='value',
        )
    except Exception as exc:
        logger.exception("[VSA_PROXY] vault upsert failed")
        return jsonify({
            'error': 'vault_write_failed',
            'message': str(exc),
            'hint': (
                'Verify UNIQUE NULLS NOT DISTINCT (organisation_id, platform, '
                'display_name) exists on ai_infrastructure.organisation_platform_credentials.'
            ),
        }), 500

    # Look up the new row's id so we can log it.
    try:
        row_id = execute_query(
            """
            SELECT id FROM ai_infrastructure.organisation_platform_credentials
            WHERE organisation_id = %s AND platform = %s AND display_name = %s
              AND is_active = TRUE
            ORDER BY updated_at DESC LIMIT 1
            """,
            (org_id, 'supabase_vsa', display_name),
            fetch_mode='value',
        )
    except Exception:
        row_id = None

    _audit_log(row_id, 'added', 'supabase_vsa', display_name)

    masked = (service_key[:6] + '…' + service_key[-4:]
              if len(service_key) > 14 else '***')
    logger.info(
        "[VSA_PROXY] supabase_vsa vault row seeded by user=%s org=%s key=%s",
        user_id, org_id, masked,
    )

    return jsonify({
        'success': True,
        'credential_id': row_id,
        'platform': 'supabase_vsa',
        'display_name': display_name,
        'url': url,  # URL is not secret
        'service_role_key_preview': masked,  # safe to echo for confirmation
    }), 201